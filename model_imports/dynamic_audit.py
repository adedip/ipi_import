import csv
from .parameters import ACTOR_IMPORT_FILE_DICT, USERS_PATH, ID_MAP_PATH, \
    ACTORS_ERR_FILE, ID_FIELD_DICT,AUDITS_IMPORT_FILE_DICT


class DynamicAudit:
    def __init__(self, client, company, import_type):
        self.client = client
        self.company = company
        self.import_type = import_type
        self.file_delimiter = ","

    def get_client(self, ipi_id):
        client = self.client.ResPartnersearch([
            ('ipi_id', "=", ipi_id )])
        return client[0] if client else False

    def get_m2o_name(self, model, name, field='name'):
        """Returns the ID of the searched item """
        domain = [(field, "=", name)]
        res_model = getattr(self.client, model)
        if 'active' in res_model._fields:
            domain += ['|', ('active', '=', True), ('active', '=', False)]
        result = getattr(self.client, model).search(domain, limit=1)
        return result[0] if result else False

    def import_data(self):
        import_file = AUDITS_IMPORT_FILE_DICT[self.import_type]

        with open(import_file, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            # error_file = open(MACH_ERR_FILE, 'w')
            # error_writer = csv.DictWriter(error_file, delimiter=',', quotechar='"',
            #                               fieldnames=spam_reader.fieldnames + ['error'])
            # error_writer.writeheader()
            usage_dict, su_obj = {}, self.client.SectorUsage
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    # checking if the asset already exists and its clients
                    da_obj = self.client.DynamicAudit
                    ipi_field = ID_FIELD_DICT[self.import_type]
                    ipi_id = f"__{ipi_field}_id_{row['id']}"
                    if da_obj.search([('ipi_id', "=", ipi_id)]):
                        print('Audit ' + row['factory_number'] + " already exists!")
                        continue
                    customer = self.get_m2o_name('ResPartner', row['customer_id'], ipi_field)
                    if not customer:
                        print("No client")
                        continue

                    # city, province, region and other fields computation
                    city = self.get_m2o_name('ResCity', row['customer_id'])
                    if city:
                        city_name = self.client.ResCity.browse(city[0]).name
                    region_param = 'region' if self.import_type == 'dm1104' else 'location_region_id'
                    region = self.get_m2o_name('ResCountryRegion', region_param)
                    province_param = 'province' if self.import_type == 'dm1104' else 'location_province_id'
                    province = self.get_m2o_name('ResCountryState', province_param)

                    # TODO: maybe error, check machiine type config , check fields mapping!!
                    detail = self.get_m2o_name('DetailConfig', row['machine_type_detail_id'])
                    # TODO: identification pass via tariffplan
                    identification = self.get_m2o_name('DetailIdentification', row['machine_type_detail_id'])
                    equipment_type = self.client.DetailConfig.browse(detail[0]).equipment_type if detail else False
                    if isinstance(row['usage'],str):
                        usage = usage_dict.get(row['usage'], False)
                        if not usage:
                            usage_id = su_obj.search([('name', '=', row['usage'])])
                            usage = su_obj.browse(usage_id[0]) if usage_id else su_obj.create({'name': row['usage']})
                            usage_dict[row['usage']] = usage
                    asset = self.get_m2o_name('AssetDecrees', row['machine_id'], 'ipi_id')
                    if not asset:
                        print(f"Asset {row['machine_id']} not found!")
                        continue
                    asset_id = self.client.AssetDecrees.browse(asset)
                    xx = False
                    vals = ({
                        'machine_id': asset_id.id,
                        # 'holder_id': xx,
                        'customer_id': asset_id.customer_id.id,
                        # 'supplier_id': xx,
                        # 'engeener_id': xx,
                        'audit_date': self.format_date(row['audit_planned_start']),
                        #'audit_planned_end': xx,
                        'audit_date': self.format_date(row['audit_deadline_at']),
                        # 'audit_started_at': xx,
                        # 'audit_ended_at': xx,
                        # 'report_file_signed_dt': xx,
                        # 'report_file_signed': xx,
                        'street': row['audit_location_address'],
                        'street': row['audit_location_address'],
                        'audit_location_zipcode': xx,
                        'audit_location_region': xx,
                        'audit_location_province': xx,
                        'audit_location_city': xx,
                        'audit_location_company': xx,
                        'audit_regime': xx,
                        'audit_protocol': xx,
                        'audit_protocol_date': xx,
                        'type_audit_code': xx,
                        'customer_user_id': xx,
                        'supplier_inspection_user_id': xx,
                        'notes': xx,
                        'audit_request_file': xx,
                        'holder_nomination_file': xx,
                        'comunication_file': xx,
                        'report_file': xx,
                        'report_number': xx,
                        'supplier_rate': xx,
                        'holder_rate': xx,
                        'invoice_date': xx,
                        'invoice_number': xx,
                        'invoice_amount': xx,
                        'gross_margin_percentage': xx,
                        'report_maintenance_status': xx,
                        'report_principal_organs_status': xx,
                        'report_behavior_in_test': xx,
                        'report_configurations_in_test': xx,
                        'report_is_available': xx,
                        'report_is_not_available_causes': xx,
                        'report_note_5': xx,
                        'machine_type_id': xx,
                        'machine_type_detail_id': xx,
                        'machine_tariffplan_id': xx,
                        'state': xx,
                        'contract_id': xx,
                        'manager_id': xx,
                        'bu_id': xx,
                        'previous_audit_id_suspended': xx,
                        'previous_audit_id_rejected': xx,
                        'previous_audit_id_break': xx,
                        'price_first_audit': xx,
                        'price_next_audit': xx,
                        'report_note_1': xx,
                        'report_note_2': xx,
                        'report_note_3': xx,
                        'report_note_4': xx,
                        'invoiced': xx,
                        'overcharge_startup': xx,
                        'overcharge_integrity': xx,
                        'purchase_order': xx,
                        'edit_notes': xx,
                        'audit_location_address_n': xx,

                        'name': f"Machine num: {row['factory_number']}",
                        'ipi_id': ipi_id,
                        'customer_id': customer_obj[0].parent_id if customer_obj[0].parent_id else customer[0],
                        'child_location_id': customer[0] if customer else False,
                        # 'serial_number': row['registration_number'],
                        'factory_number': row['factory_number'],
                        'city': city_name if city else False,
                        'state_id': province[0] if province else False,
                        'region_id': region[0] if region else False,
                        'first_check_date': row['first_audit_at'] if row['first_audit_at'] != "NULL" else False,
                        'previous_audit_date': row['last_audit_at'] if row['last_audit_at'] != "NULL" else False,
                        'audit_date': row['next_audit_at'],
                        # notified_organism_id: row['notified_organism_id'] >>> seems unused
                        'comment': row['note'] if row['note'] != "" else False,
                        # state?
                    })

                    # DM1104 SPECIFIC
                    if import_type == 'dm1104':
                        vals.update({
                            'zip': row['zipcode'],
                            'identification_code': row['customer_machine_code'],
                            'brand_maker': row['vendor'],
                            'street': row['address'],
                            'detail_id': detail[0] if detail else False,
                            'identification_id': identification[0] if identification else False,
                            'equipment_type': equipment_type if equipment_type else False,
                            'model': row['model'],
                            'built_year': row['construction_year'],
                            'registration_year': row['registration_year'],
                            'ce_marking': True if row['ce'] == 'SI' else False,
                            'ps_bar': row['ps_bar'] if row['ps_bar'] != "NULL" else False,
                            'fluid': row['fluid'] if row['fluid'] != 'NULL' else False,
                            # producibility?
                            'sector_of_use': usage.id,
                        })

                    # DPR162 SPECIFIC
                    if import_type == 'dpr162':
                        vals.update({
                            'type': 'LiftsDpr162',
                            'street': row['location_address '],
                            'zip': row['location_zipcode'],
                            # business_unit_id ?
                            # operator ?
                            'identification_code': row['name'],
                            # code ? , uguale a NAME con qualche campo in meno
                            # TODO: 'detail_id' : 'electrical_system' if row['plant_type'] == 1 else 'hydraulic_system',
                            'detail_id' : 20 if row['plant_type'] == 1 else 61,
                            # range??
                            # 'stop_number': row['stop_numb'],
                            'model': row['registration_number'],
                            'built_year': row['installation_year'],
                            'brand_maker': row['builder_name'],
                            'capacity': row['capacity'],
                        })

                    # DPR462 SPECIFIC
                    if import_type == 'dpr462':
                        measuring_points = int(row['measuring_points']) if \
                            (
                                row['measuring_points'] not in ['', 'MT', 'BT'],
                                # 10: messa a terra,
                                # 12: pericolo esplosione,
                                # 11: scarica atmosferiche,
                                # 12: passo e contatto,
                            ) else False
                        vals.update({
                            # type ? , maybe useles  all is 20
                            'street': row['location_address '],
                            'zip': row['location_zipcode'],
                            # business_unit_id ?
                            'measuring_points': measuring_points,
                            # energy_power
                            # surface_area
                            # structure_type
                            # man_hours
                            # contact_user_id
                            # operator ?
                            # code ? , uguale a NAME con qualche campo in meno
                            'identification_code': row['name'],
                            # periodicity?
                            # dangerous_gas >> not matching with selection field
                            # dangerous_dust >> not matching with selection
                            'step_points': row['step_points'],
                            # TODO: check selection options for fields below
                            'supply_type': row['supply_type'] if (row['supply_type'] in ['BT', 'MT', 'AT']) else False,
                            'distribution_type': row['distribution_type'] if (row['distribution_type'] in ['IT', 'TN', 'TT']) else False,
                            # contact_points
                            # plant_syte
                        })

                    rp_obj.create(vals)
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Line {file_line}: {e.faultCode}")
                    row['error'] = e.faultCode
                    error_writer.writerow(row)

    def format_date(self, date, type="date"):
        return date if date not in ['NULL', '0000-00-00'] else False

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
        print("\nMachine types have been mapped!")

    def map_identification(self):
        with open(MACH_IDENTIFICATION, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                di_obj = self.client.DetailIdentification
                description = row['description'].replace("   ", " ")
                mtype_id = di_obj.search([
                    ('name', "ilike", description),
                    ('ipi_id', "!=", True),
                ], limit=1)
                if not mtype_id:
                    # TODO: create or skipping? now it is creating new ones
                    print("Machine Indentification {} was not found!".format(row['description']))
                    detail = self.get_m2o_name('DetailConfig', int(row['machine_type_detail_id']))
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

    """INTEGRATION SCRIPTS """
    def integrate_data(self):
        import_type = ['dm1104', 'dpr162', 'dpr462'][1]
        import_file = self.select_asset_file(import_type)

        with open(import_file, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=self.file_delimiter, quotechar='"')
            file_line = 1
            for row in spam_reader:
                file_line += 1
                try:
                    # finding the partner
                    ad_obj = self.client.AssetDecrees
                    asset = ad_obj.search([('ipi_id', "=", row['id'])], limit=1)
                    if not asset:
                        print(f"Asset {row['factory_number']} not found!")
                        continue
                    asset = ad_obj.browse(asset[0])
                    detail = self.get_m2o_name('DetailConfig', row['machine_type_detail_id'])
                    identification = self.get_m2o_name('DetailIdentification', row['machine_tariffplan_id'])
                    equipment_type = self.client.DetailConfig.browse(detail[0]).equipment_type if detail else False
                    # preparing data to update
                    # serial_list = self.get_serial_number(row['serial_number'])
                    vals = {
                        'detail_id': detail[0] if detail else False,
                        'identification_id': identification[0] if identification else False,
                        'equipment_type': equipment_type if equipment_type else False,
                        # 'identification_code': row['customer_machine_code'],
                        # 'comment': row['note'] if row['note'] != "" else False,
                        # 'serial_number_1': serial_list[0],
                        # 'serial_number_2': serial_list[1],
                        # 'serial_number_3': serial_list[2],
                        # 'serial_number_4': serial_list[3],
                    }
                    # if asset.factory_number and asset.factory_number != row['factory_number']:
                        #  print("Wrong factory number ;(")
                    asset.write(vals)
                    # partner[0].type_company = partner_type
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Line {file_line}: {e}")

    def get_serial_number(self, serial):
        serial_list = serial.split("/")
        if len(serial_list) == 3:
            return ["0000"] + serial_list
        elif len(serial_list) == 4:
            return serial_list