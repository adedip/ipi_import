import csv
from .parameters import ACTOR_IMPORT_FILE_DICT, USERS_PATH, ID_MAP_PATH, ACTORS_ERR_FILE, ID_FIELD_DICT
import re


class ResPartner:
    def __init__(self, client, company, import_type):
        self.file_delimiter = ","
        self.encoding = "utf8"
        self.client = client
        self.company = company
        self.import_type = import_type

    def get_geolocation(self, kind, ipi_id):
        geo_dict = {
            'city': self.client.ResCity,
            'region': self.client.ResCountryRegion,
            'province': self.client.ResCountryState,
        }
        result = geo_dict[kind].search([('ipi_id', '=', ipi_id)], limit=1)
        return result[0] if result else False

    def format_cf_piva(self, kind, code):
        """Kind can be 'cf' of 'piva' """
        if not code:
            return False
        if kind == 'cf':
            return code.ljust(16, '.')
        else:
            num_code = code[:11] if code[:2] != 'IT' else code[2:13]
            return "IT" + num_code.ljust(11, '0')

    def create_iban(self, partner, code):
        bank_obj = self.client.ResPartnerBank
        if not bank_obj.search([('acc_number', '=', code)]):
            bank_obj.create({
                'acc_number': code,
                'partner_id': partner.id,
            })

    def get_m2o_name(self, model, name, field='name'):
        """Returns the ID of the searched item """
        domain = [(field, "=", name)]
        res_model = getattr(self.client, model)
        if 'active' in res_model._fields:
            domain += ['|', ('active', '=', True), ('active', '=', False)]
        result = getattr(self.client, model).search(domain, limit=1)
        return result[0] if result else False

    def format_string(self, string):
        if not string or string == "NULL":
            return False
        else:
            return string

    def format_boolean(self, string):
        return True if string == 'True' else False

    def get_job_position(self, position):
        model = 'ResPartnerJob_Position'
        result = self.get_m2o_name(model, position)
        if not result:
            result = getattr(self.client, model).create({
                'name': position,
            })
        return result

    def get_client(self, row, name, odoo_id):
        """Returns the ID of the partner, it also updates it ID"""
        # if importing from Odoo bkp
        partner, child, child_name = False, False, False
        if self.import_type == 'all':
            return self.get_m2o_name('ResPartner', odoo_id, field="ref")
        # if not an Odoo import, check by id
        partner = self.get_m2o_name('ResPartner', int(row["id"]),
                                    field=ID_FIELD_DICT[self.import_type])

        if not partner:
            piva = self.format_cf_piva('piva', row['piva'])
            partner = self.get_m2o_name('ResPartner', piva, field="vat")
        if not partner:
            if re.search(", Sede", name, flags=re.IGNORECASE):
                parent_name, child_name = re.split(", Sede", name, flags=re.IGNORECASE)
                parent = self.get_m2o_name('ResPartner', parent_name, field="name")
                if parent:
                    parent_id = self.client.ResPartner.browse(parent)
                    child = parent_id.child_ids.filtered(lambda c: c.name == f"Sede {child_name}")
                    partner_id = child.id if child else parent_id
            else:
                partner = self.get_m2o_name('ResPartner', name, field="name")

        # update the ID field of the partner
        id_field = ID_FIELD_DICT[self.import_type]
        if partner:
            partner_id = self.client.ResPartner.browse(partner)
            if not getattr(partner_id, ID_FIELD_DICT[self.import_type]):
                vals = {id_field: int(row['id'])}
                if not partner_id.ref:
                    vals.update({
                        'ref': f"__{id_field}_{partner}",
                    })
                partner_id.write(vals)

        return True if partner or child else False

    def import_data(self):
        import_file = ACTOR_IMPORT_FILE_DICT[self.import_type]
        with open(import_file, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            error_file = open(ACTORS_ERR_FILE, 'w')
            error_writer = csv.DictWriter(error_file, delimiter=',', quotechar='"',
                                          fieldnames=spam_reader.fieldnames + ['error'])
            error_writer.writeheader()
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    odoo_id = f"__odoo_id_{row['id']}"
                    rp_obj = self.client.ResPartner
                    name = row['name']
                    if rp_obj.search([('ref', "=", odoo_id)]):
                        print('Partner ' + name + " already exists!")
                        continue
                    country_id = self.get_m2o_name('ResCountry', 'Italy')
                    vals = ({
                        # 'id': odoo_id,
                        'ref': odoo_id,
                        'name': name,
                        'website': self.format_string(row['website']),
                        'fax': self.format_string(row['fax']),
                        'email': self.format_string(row['email']),
                    })

                    if self.import_type == "dm1104":
                        fatturapa_vals = {}
                        if row['sdi_code'] and row['sdi_code'] != 'NULL':
                            fatturapa_vals = {
                                'codice_destinatario': row['sdi_code'],
                                'electronic_invoice_no_contact_update': True,
                                'electronic_invoice_subjected': True,
                                'electronic_invoice_obliged_subject': True,
                            }
                            partner_type = self.return_type(row['type'])

                        vals.update({
                            **fatturapa_vals,
                            'type': partner_type,
                            'is_company': self.format_boolean(row['is_company']),
                            'street': self.format_string(row['street']),
                            'street2': self.format_string(row['street2']),
                            'zip': self.format_string(row['zip']),
                            'city': self.format_string(row['city']),
                            'state_id': self.get_m2o_name('ResCountryState', row['state_id']),
                            'phone': self.format_string(row['phone']),
                            'pec_mail': self.format_string(row['pec_mail']),
                            'lang': row['lang'],
                            # rating
                            # target audience
                            'target_audience': row['target_audience'] if row['target_audience'] != "NULL" else False,
                            'comment': self.format_string(row['comment']),
                            'vat': self.format_string(row['vat']),
                            'fiscalcode': self.format_string(row['fiscalcode']),
                            # trust
                            # split payment
                            # sex
                            'mobile': self.format_string(row['mobile'].replace("'","")),
                            # 'job_position_id': self.get_job_position(row['job_position_id']),
                            # function
                            'country_id': country_id,
                            'team_id': self.get_m2o_name('CrmTeam', row['team_id']),
                            # user_id
                            # segment_id
                            # campagna_id
                            # 'property_payment_term_id': self.get_m2o_name('AccountPaymentTerm', row['property_payment_term_id/id/name']),
                            # 'property_account_position_id': self.get_m2o_name('AccountFiscalPosition', row['property_account_position_id/name']),
                            # 'property_account_payable_id': self.get_m2o_name('AccountAccount', row['property_account_payable_id/code'], field='code'),
                            # 'property_account_receivable_id': self.get_m2o_name('AccountAccount', row['property_account_receivable_id/code'], field='code'),
                            # default_ipi_crm_password
                            # 'active': self.format_boolean(row['active']), : TODO: eseguire questo alla fine!
                            # parent_di TODO: provare a settare il PARENT subito?
                            # 'type': partner_type,
                            'is_condominium': self.format_boolean(row['is_apartment_building']),
                            'is_competitor': self.format_boolean(row['is_competitor']),
                            # is_segnalatore_commerciale
                            'competitor_type': row['competitor_type'],

                            # condo
                            # trader
                            # lr (legale rappresentante)?
                        })


                    if self.import_type == "dpr162":
                        city = self.get_m2o_name('ResCity', row['city_id'], field='name')
                        vals.update({
                            'street': self.format_string(row['address']),
                            'zip': self.format_string(row['zipcode']),
                            'city': city.name if city else "",
                            'state_id': self.get_m2o_name('ResCountryState', row['province_id']),
                            'phone': self.format_string(row['tel']),
                            'pec_mail': self.format_string(row['pec']),
                            # condo
                            # trader
                            # lr (legale rappresentante)?
                            # 'active': self.format_boolean(row['state']) ?
                        })
                    # TODO: legale rappr già tra i contatti? [lr_name, lr_surname]
                    # TODO: sede legale già tra i contatti? [sl_name, ]
                    # check vat, else put it in comments
                    # vat = self.format_cf_piva('piva', row['piva'])
                    # if rp_obj.simple_vat_check('IT', vat):
                    #     vals.update({'vat': vat})
                    # else:
                    #     vals['comment'] += "\nVAT NUM: {}".format(vat)
                    partner = rp_obj.create(vals)

                    # creating related models (seems not possible to use tuples..)
                    if row['iban']:
                        self.create_iban(partner, row['iban'])
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Line {file_line}: {e.faultCode}")
                    row['error'] = e.faultCode
                    error_writer.writerow(row)

        print("\n Partners have been imported!")

    def setting_parent(self):
        import_file = ACTOR_IMPORT_FILE_DICT[self.import_type]
        with open(import_file, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    if not row['parent_id'] or row['parent_id'] == "NULL":
                        continue
                    parent = self.get_m2o_name('ResPartner', f"__odoo_id_{row['parent_id']}",
                                         field='ref')
                    partner_id = self.get_m2o_name('ResPartner', f"__odoo_id_{row['id']}",
                                         field='ref')
                    if partner_id and parent:
                        partner_id = self.client.ResPartner.browse(partner_id)
                        partner_id.parent_id = int(parent)
                    else:
                        print(f"{file_line} Parent __odoo_id_{row['parent_id']} or partner __odoo_id_{row['id']} not found! ")
                    print(file_line)
                except Exception as e:
                    print(f"Error at line: {file_line}")

        print("\n Partners have been imported!")

    def map_ids(self):
        with open(ID_MAP_PATH, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    if not row['res_partner_id'] or row['ipi_id'] in [
                               "0", "NULL"]:
                        continue
                    rp_obj = self.client.ResPartner
                    partner_id = rp_obj.browse([
                        ('ref', "=", f"__odoo_id_{row['res_partner_id']}"),
                        ('ipi_id', "!=", True),
                    ], limit=1)
                    if partner_id:
                        # if row['crmname'] == 'dm1104':
                        #     if partner_id[0].ipi_id != row['ipi_id']:
                        #         print(f"Line {file_line}: Partner {partner_id.id} shall be {row['ipi_id']}")
                        #     print(f"Line {file_line}: Partner {partner_id.id} esists")
                        #     continue
                        id_field = ID_FIELD_DICT[row['crmname']]
                        vals = ({ id_field: int(row['ipi_id'])})
                        partner_id[0].write(vals)
                        print(f"Line {file_line}: {id_field} {partner_id} - {odoo_id} - updated with {row['ipi_id']}!")
                        x = "test"
                    else:
                        print(f"Line {file_line}: Partner {partner_id} not found!")
                except Exception as e:
                    print(f"Line {file_line}: error")
                    # row['error'] = e.faultCode

        print("\n Partner IDS have been mapped!")

    def import_users(self):
        with open(USERS_PATH, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    # finding the partner
                    login = row['login']
                    ru_obj = self.client.ResUsers
                    user = ru_obj.search([('login', "=", login)], limit=1)
                    if user:
                        print(f"User {login} exists!")
                        continue
                    vals = {
                        'login': login,
                        'name': row['name'],
                        'lang': row['lang'],
                        'tz': row['tz'],
                    }

                    rp_obj = self.client.ResPartner
                    partner = rp_obj.search([('email', "=", login)], limit=1)
                    if partner:
                        vals.update({'partner_id': partner[0]})
                    ru_obj.create(vals)
                    # partner[0].type_company = partner_type
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Line {file_line}: {e.faultCode}")

        print("\n Users have been created!")

    """
    INTEGRATION SCRIPTS
    """

    def integrate_data(self):
        import_file = ACTOR_IMPORT_FILE_DICT[self.import_type]
        with open(import_file, 'r', encoding='utf8') as csvfile:

            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    if self.import_type == 'dm1104':
                        self._integrate_partners(row)
                    if self.import_type == 'dpr162':
                        self._map_dpr162(row)
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Line {file_line}: {e}")

        print("\n Partners have been updated!")

    def _map_dpr162(self, row):
        rp_obj = self.client.ResPartner
        partner = rp_obj.search([('name', "=", row['company_name'])], limit=1)
        if not partner:
            print(f"Partner {row['company_name']} not found!")
            return True
        partner = rp_obj.browse(partner[0])
        vals = {'ipi162_id': int(row['id'])}
        partner.write(vals)

    def _integrate_partners(self, row):
        # finding the partner
        if row['active'] == "True":
            return True
        odoo_id = f"__odoo_id_{row['id']}"
        rp_obj = self.client.ResPartner
        partner = rp_obj.search([('ref', "=", odoo_id)], limit=1)
        if not partner:
            print(f"Partner {row['name']} not found!")
            return True
        partner = rp_obj.browse(partner[0])
        # preparing data to update
        partner_type = self.return_type(row['type'])
        vals = {
            'active': self.format_boolean(row['active']),
            # 'type': partner_type,
            # 'is_company': self.format_boolean(row['is_company']),
            # 'is_condominium': self.format_boolean(row['is_apartment_building']),
            # 'is_competitor': self.format_boolean(row['is_competitor']),
        }
        partner.write(vals)
        # partner[0].type_company = partner_type

    def return_type(self, cell):
        if cell == 'sede-amministrativa':
            return 'administrative_office'
        else:
            return cell

    def clean_field(self, field):
        return False if field in ['NULL', '', 0, 0.0] else field

    def clean_data(self):
        partners = self.client.ResPartner.browse([('id', '!=', False)])
        total = len(partners)
        file_line = 1
        for partner in partners:
            file_line += 1
            try:
                vals = {
                    'fiscalcode': self.clean_field(partner.fiscalcode),
                    'vat': self.clean_field(partner.vat),
                    'mobile': self.clean_field(partner.mobile),
                    'phone': self.clean_field(partner.phone),
                    'street2': self.clean_field(partner.street2),
                    'email': self.clean_field(partner.email),
                    'website': self.clean_field(partner.website),
                }
                partner.write(vals)
                print(f"{file_line} - partner {partner.name} updated! ")
            except:
                print(f"{file_line} - partner {partner.name} error found! ")

