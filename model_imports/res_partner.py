import csv

# ACTORS_PATH = "import_files/all_actors.csv"
ACTORS_PATH = "import_files/odoo_ipi_contacts.csv"
ERROR_PATH = "error_files/"
ACTORS_ERR_FILE = ERROR_PATH + "actors_error.csv"


class ResPartner:
    def __init__(self, client, company):
        self.file_delimiter = ","
        self.encoding = "utf8"
        self.client = client
        self.company = company

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
        result = getattr(self.client, model).search([
            (field, "=", name)], limit=1)
        return result[0] if result else False

    def import_data(self):
        with open(ACTORS_PATH, 'r', encoding='utf8') as csvfile:
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
                    rp_obj = self.client.ResPartner
                    name = row['name']
                    if rp_obj.search([('ipi_id', "=", row['id'])]):
                        print('Partner ' + name + " already exists!")
                        continue
                    country_id = self.get_m2o_name('ResCountry', 'Italy')
                    fatturapa_vals = {}
                    if row['sdi_code']:
                        fatturapa_vals = {
                            'codice_destinatario': row['sdi_code'],
                            'electronic_invoice_no_contact_update': True,
                            'electronic_invoice_subjected': True,
                            'electronic_invoice_obliged_subject': True,
                        }
                    vals = ({
                        'ipi_id': row['id'],
                        'is_company': row['is_company'],
                        'name': name,
                        'street': row['street'],
                        'street2': row['street2'],
                        'zip': row['zip'],
                        'city': row['city'],
                        'website': row['website'],
                        **fatturapa_vals,
                        'phone': row['phone'],
                        'fax': row['fax'],
                        'email': row['email'],
                        'pec_mail': row['pec_mail'],
                        'lang': row['lang'],
                        # rating
                        # target audience
                        'comment': row['comment'],
                        'vat': row['vat'],
                        'fiscalcode': row['fiscalcode'],
                        # trust
                        # split payment
                        # type
                        # sex
                        'mobile': row['mobile'],
                        # 'job_position_id': self.get_m2o_name('ResPartnerJob_Position', row['job_position_id/name']),
                        # function
                        'state_id': self.get_m2o_name('ResCountryState', row['state_id/name']),
                        'country_id': country_id,
                        'team_id': self.get_m2o_name('CrmTeam', row['team_id/name']),
                        # user_id
                        # segment_id
                        # campagna_id
                        'property_account_position_id': self.get_m2o_name('AccountFiscalPosition', row['property_account_position_id/name']),
                        'property_account_payable_id': self.get_m2o_name('AccountAccount', row['property_account_payable_id/code'], field='code'),
                        'property_account_receivable_id': self.get_m2o_name('AccountAccount', row['property_account_receivable_id/code'], field='code'),
                        # default_ipi_crm_password
                        'is_condominium': row['is_apartment_building'],
                        # is_segnalatore_commerciale
                        'is_competitor': row['is_competitor'],
                        'comment': row['comment'],

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
        with open(ACTORS_PATH, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    if not row['master_company_name']:
                        continue
                    rp_obj = self.client.ResPartner
                    partner_id = rp_obj.browse([('ipi_id', "=", row['id'])], limit=1)
                    parent = rp_obj.search([
                        ('name', "=", row['master_company_name'])], limit=1)
                    if partner_id and parent:
                        partner_id[0].update({
                            'parent_id': parent[0],
                            'company_type': 'person',
                            'type': 'contact',
                        })
                except:
                    print(f"Error at line: {file_line}")

        print("\n Partners have been imported!")


