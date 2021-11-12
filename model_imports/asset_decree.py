import csv

MAIN_PATH = "import_files/"
MACH_TYPE_FILE = MAIN_PATH + "machine_types.csv"
MACH_IDENTIFICATION = MAIN_PATH + "machines_specific_details.csv"
ASSETS_FILE = MAIN_PATH + "customer_machines_medium.csv"

ERROR_PATH = "error_files/"
MACH_ERR_FILE = ERROR_PATH + "machines_error.csv"

MACH_TYPE_DICT = {
    'Piattaforme': 'PeopleLiftingDm1104',
    'Sollevatori': 'PeopleLiftingDm1104',
    'Carro': 'PeopleLiftingDm1104',
    'Scala': 'PeopleLiftingDm1104',
    'Ponti': 'PeopleLiftingDm1104',
    'Carrelli': 'EquipmentLiftingDm1104',
    'Idroestrattori': 'EquipmentLiftingDm1104',
    'Gru': 'EquipmentLiftingDm1104',
    'Autogru': 'EquipmentLiftingDm1104',
    'Altro': 'EquipmentLiftingDm1104',
    'Recipienti Gas e vapore d\'acqua': 'PressureEquipmentDm1104',
    'Generatori di vapore con superficie riscaldata fino a 300 mq': 'PressureEquipmentDm1104',
    'Generatori di vapore con superficie riscaldata oltre i 300 mq': 'PressureEquipmentDm1104',
    'Tubazioni': 'PressureEquipmentDm1104',
    'Impianti di Riscaladamento oltre 116 kW': 'PressureEquipmentDm1104',
    'Messa a terra': 'GroundingDpr462',
    'Scariche atmosferiche': 'AtmosphericDischargesDpr462',
    'Pericolo esplosione': 'DangerExplosionDpr462',
    'Passo e contatto': 'StepContactDpr462',
    'Impianto Elettrico': 'LiftsDpr162',
    'Impianto Idraulico': 'LiftsDpr162',
}


class AssetDecree:
    def __init__(self, client, company):
        self.client = client
        self.company = company
        self.file_delimiter = ","

    def get_client(self, ipi_id):
        client = self.client.ResPartnersearch([
            ('ipi_id', "=", ipi_id )])
        return client[0] if client else False

    def get_many2one(self, model, ipi_id):
        return getattr(self.client, model).search([
            ('ipi_id', "=", ipi_id)], limit=1)

    def import_data(self):
        with open(ASSETS_FILE, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            error_file = open(MACH_ERR_FILE, 'w')
            error_writer = csv.DictWriter(error_file, delimiter=',', quotechar='"',
                                          fieldnames=spam_reader.fieldnames)
            error_writer.writeheader()
            usage_dict, su_obj = {}, self.client.SectorUsage
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    # checking if the contact already exists
                    rp_obj = self.client.AssetDecrees
                    if rp_obj.search([('ipi_id', "=", int(row['id']))]):
                        print('Asset ' + row['factory_number'] + " already exists!")
                        continue

                    city = self.get_many2one('ResCity', row['city'])
                    if city:
                        city_name = self.client.ResCity.browse(city[0]).name
                    region = self.get_many2one('ResCountryRegion', row['region'])
                    province = self.get_many2one('ResCountryState', row['province'])
                    customer = self.get_many2one('ResPartner', row['customer_id'])
                    detail = self.get_many2one('DetailConfig', row['machine_type_id'])
                    identification = self.get_many2one('DetailIdentification', row['machine_type_id'])
                    equipment_type = self.client.DetailConfig.browse(detail[0]).equipment_type if detail else False
                    if isinstance(row['usage'],str):
                        usage = usage_dict.get(row['usage'], False)
                        if not usage:
                            usage_id = su_obj.search([('name', '=', row['usage'])])
                            usage = su_obj.browse(usage_id[0]) if usage_id else su_obj.create({'name': row['usage']})
                            usage_dict[row['usage']] = usage
                    vals = ({
                        'name': f"Machine num: {row['factory_number']}",
                        'ipi_id': int(row['id']),
                        'customer_id': customer[0] if customer else False,
                        'detail_id': detail[0] if detail else False,
                        'identification_id': identification[0] if identification else False,
                        'equipment_type': equipment_type if equipment_type else False,
                        'model': row['model'],
                        # 'serial_number': row['registration_number'],
                        'brand_maker': row['vendor'],
                        'factory_number': row['factory_number'],
                        'registration_year': row['registration_year'],
                        'built_year': row['construction_year'],
                        'ce_marking': True if row['ce'] == 'SI' else False,
                        'street': row['address'],
                        'zip': row['zipcode'],
                        'city': city_name if city else False,
                        'state_id': province[0] if province else False,
                        'region_id': region[0] if region else False,
                        'first_check_date': row['first_audit_at'],
                        'previous_audit_date': row['last_audit_at'],
                        'audit_date': row['next_audit_at'],
                        # notified_organism_id: seems unused
                        'ps_bar': row['ps_bar'],
                        'fluid': row['fluid'] if row['fluid'] != 'NULL' else False,
                        # producibility?
                        'sector_of_use': usage.id,
                        # customer_machine_code?
                        # note?
                        # state?
                    })
                    rp_obj.create(vals)
                    print(f"{file_line}")
                except:
                    print(f"Error at line: {file_line}")
                    error_writer.writerow(row)


    def map_machine_type(self):
        with open(MACH_TYPE_FILE, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                dc_obj = self.client.DetailConfig
                mtype_id = dc_obj.search([('name', "=", row['description'])], limit=1)
                if mtype_id:
                    dc_obj.browse(mtype_id[0]).ipi_id = int(row['id'])
                elif not mtype_id and row['description']:
                    print("Machine Type {} was not found!".format(row['description']))
                    dc_obj.create({
                        'name': row['description'],
                        'ipi_id': int(row['id']),
                        'equipment_type': MACH_TYPE_DICT[row['description']],
                    })
                    continue
        print("\nMachine types have been mapped!")

    def map_identification(self):
        with open(MACH_IDENTIFICATION, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                di_obj = self.client.DetailIdentification
                mtype_id = di_obj.search([('name', "=", row['description'])], limit=1)
                if not mtype_id:
                    # TODO: create or skipping? now it is creating new ones
                    print("Machine Indentification {} was not found!".format(row['description']))
                    detail = self.get_many2one('DetailConfig', int(row['machine_type_detail_id']))
                    di_obj.create({
                        'name': row['description'],
                        'ipi_id': int(row['id']),
                        'detail_id': detail[0] if detail else False,
                         })
                    continue

                # adding the identification to the machine type
                record = di_obj.browse(mtype_id[0])
                record.ipi_id = int(row['id'])
                record.detail_id = int(row['machine_type_detail_id'])

        print("\nMachine identifications have been mapped!")
