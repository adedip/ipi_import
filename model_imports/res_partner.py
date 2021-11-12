import csv

ACTORS_PATH = "import_files/all_actors.csv"
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

    def import_data(self):
        with open(ACTORS_PATH, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            error_file = open(ACTORS_ERR_FILE, 'w')
            error_writer = csv.DictWriter(error_file, delimiter=',', quotechar='"',
                                          fieldnames=spam_reader.fieldnames)
            error_writer.writeheader()
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    rp_obj = self.client.ResPartner
                    name = row['company_name']
                    if rp_obj.search([('ipi_id', "=", int(row['id']))]):
                        print('Partner ' + name + " already exists!")
                        continue

                    vals = ({
                        'ipi_id': int(row['id']),
                        'company_type': "company",
                        'name': name,
                        'street': row['address'],
                        'zip': row['zipcode'],
                        'fiscalcode': self.format_cf_piva('cf', row['cf']),
                        'city': self.get_geolocation('city', row['city_id']),
                        'state_id': self.get_geolocation('province', row['province_id']),
                        'website': row['website'],
                        'email': row['email'],
                        'pec_mail': row['pec'],
                        'phone': row['tel'],
                        'fax': row['fax'],
                        'comment': row['note'] if row['note'] != 'NULL' else '',

                    })
                    # TODO: legale rappr già tra i contatti? [lr_name, lr_surname]
                    # TODO: sede legale già tra i contatti? [sl_name, ]
                    # check vat, else put it in comments
                    vat = self.format_cf_piva('piva', row['piva'])
                    if rp_obj.simple_vat_check('IT', vat):
                        vals.update({'vat': vat})
                    else:
                        vals['comment'] += "\nVAT NUM: {}".format(vat)
                    partner = rp_obj.create(vals)

                    # creating related models (seems not possible to use tuples..)
                    if row['iban']:
                        self.create_iban(partner, row['iban'])
                    print(f"{file_line}")
                except:
                    print(f"Error at line: {file_line}")
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


