import csv
from .parameters import ACTOR_IMPORT_FILE_DICT, USERS_PATH, ID_MAP_PATH, \
    ACTORS_ERR_FILE, ID_FIELD_DICT,AUDITS_IMPORT_FILE_DICT, AUDITS_STATE_DICT

AUDIT_TYPE_DICT = {
    'FUN_BIEN': 5,
    'FUN_BIEN_INT_DEC':  5,
    'FUN_QUADR':  7,
    'FUN_QUADR_INT_DEC':  7,
    'FUN_QUIN':  8,
    'FUN_QUIN_INT_DEC':  8,
    'FUN_TRIEN':  4,
    'FUN_TRIEN_INT_DEC':  4,
    'INT_DEC':  1,
    'NULL':  12,
    'PRIMA_PERIOD':  2,
    'QUIN':  1,
    'SUCC':  1,
    'SUCC_ANNUALE':  2,
    'SUCC_BIENNALE':  3,
    'SUCC_TRIENNALE':  4,
    'VIS_INT_BIEN':  1,
    }


class DynamicAudit:
    def __init__(self, client, company, import_type):
        self.client = client
        self.company = company
        self.import_type = import_type
        self.file_delimiter = ","

    def get_client(self, ipi_id):
        client = self.client.ResPartner.search([
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
                    ipi_id = f"__{ipi_field}{row['id']}"
                    if da_obj.search([('ipi_id', "=", ipi_id)]):
                        print('Audit ' + ipi_id + " already exists!")
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
                    asset = self.get_m2o_name('AssetDecrees', row['machine_id'], 'ipi_id')
                    if not asset:
                        print(f"Asset {row['machine_id']} not found!")
                        continue
                    # set audit result
                    result_id = False
                    if row['state'] in ['5']:
                        result_id = 1
                    else:
                        result_id = 2
                    asset_id = self.client.AssetDecrees.browse(asset)
                    xx = False

                    vals = ({
                        'ipi_id': ipi_id,
                        'equipment_record_id': asset_id.id,
                        'audit_record_ref': '%s,%s' % ('asset.decrees', asset_id.id),
                        'audit_type_id': AUDIT_TYPE_DICT[row['type_audit_code']],
                        # 'holder_id': xx,
                        'customer_id': asset_id.customer_id.id,
                        # 'supplier_id': xx,
                        # 'engeener_id': xx,
                        'audit_date': self.format_date(row['audit_planned_start']),
                        # 'audit_planned_end': xx,
                        # 'audit_date': self.format_date(row['audit_deadline_at']),
                        # 'audit_started_at': xx,
                        # 'audit_ended_at': xx,
                        # 'report_file_signed_dt': xx,
                        # 'report_file_signed': xx,
                        # 'street': row['audit_location_address'],
                        # 'audit_location_zipcode': xx,
                        # 'audit_location_region': xx,
                        # 'audit_location_province': xx,
                        # 'audit_location_city': xx,
                        # 'audit_location_company': xx,
                        # 'audit_regime': xx,
                        'audit_sequence': row['audit_protocol'],
                        # 'audit_protocol_date': xx,
                        # 'type_audit_code': xx,
                        # 'customer_user_id': xx,
                        # 'supplier_inspection_user_id': xx,
                        'description': row['notes'],
                        # 'audit_request_file': xx,
                        # 'holder_nomination_file': xx,
                        # 'comunication_file': xx,
                        # 'report_file': xx,  TODO: attachment
                        # 'report_number': xx,
                        # 'supplier_rate': xx,
                        # 'holder_rate': xx,
                        # 'invoice_date': xx,
                        # 'invoice_number': xx,
                        # 'invoice_amount': xx,
                        # 'gross_margin_percentage': xx,
                        # 'report_maintenance_status': xx,
                        # 'report_principal_organs_status': xx,
                        # 'report_behavior_in_test': xx,
                        # 'report_configurations_in_test': xx,
                        # 'report_is_available': xx,
                        # 'report_is_not_available_causes': xx,
                        # 'report_note_5': xx,
                        # 'machine_type_id': xx,
                        # 'machine_type_detail_id': xx,
                        # 'machine_tariffplan_id': xx,
                        'state': AUDITS_STATE_DICT[row['state']],
                        'result_id': result_id,
                        # 'contract_id': xx,
                        # 'manager_id': xx,
                        # 'bu_id': xx,
                        # 'previous_audit_id_suspended': xx,
                        # 'previous_audit_id_rejected': xx,
                        # 'previous_audit_id_break': xx,
                        # 'price_first_audit': xx,
                        # 'price_next_audit': xx,
                        # 'report_note_1': xx,
                        # 'report_note_2': xx,
                        # 'report_note_3': xx,
                        # 'report_note_4': xx,
                        # 'invoiced': xx,
                        # 'overcharge_startup': xx,
                        # 'overcharge_integrity': xx,
                        # 'purchase_order': xx,
                        # 'edit_notes': xx,
                        # 'audit_location_address_n': xx,
                    })

                    da_obj.create(vals)
                    print(f"{file_line}")
                except Exception as e:
                    print(f"Error line {file_line}: {e.faultCode}")
                    row['error'] = e.faultCode
                    # error_writer.writerow(row)

    def format_date(self, date, type="date"):
        return date if date not in ['NULL', '0000-00-00'] else False
