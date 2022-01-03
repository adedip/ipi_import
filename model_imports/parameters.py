"""Main parameters for different imports"""
IMPORT_PATH = "import_files/"
ERROR_PATH = "error_files/"

# AUDITS
AUDITS_IMPORT_FILE_DICT = {
    'all': "***",
    'dm1104': IMPORT_PATH + "dm1104_audits_short.csv",
    'dpr162': IMPORT_PATH + "***",
    'dpr462': IMPORT_PATH + "***.csv",
}

AUDITS_STATE_DICT = {
    '-2': 1,  # 'In attesa ratifica contratto',
    '-1': 1,  # 'Verifica senza contratto',
    '0': 1,  # 'FROZEN',
    '1': 1,  # 'Verifica creata',
    '2': 1,  # 'Upload doc tit. funzione e del',
    '3': 2,  # 'Verificatore associato',
    '4': 20,  # 'Verbale di verifica inserito',
    '5': 6,  # 'Verifica chiusa',
    '6': 2,  # 'Verifica sospesa',
    '7': 6,  # 'Verifica negativa',
}

# PARTNERS
# ACTORS_PATH = "import_files/all_actors.csv"

ACTOR_IMPORT_FILE_DICT = {
    'all': IMPORT_PATH + "ipi_10_partner_set_parent.csv",
    'dm1104': IMPORT_PATH + "**.csv",
    'dpr162': IMPORT_PATH + "dpr162_actors.csv",
    'dpr462': IMPORT_PATH + "**.csv",
}

ACTOR_FIELD_DICT =  {
    'all': 'name',
    'dm1104': 'company_name',
    'dpr162': 'company_name',
    'dpr462': 'company_name',
}

ACTORS_ERR_FILE = ERROR_PATH + "actors_error.csv"
# PARTNER_MAP_FILE = MAPPING_PATH + "ipi_odoo_id_mapping_DEF.csv"

USERS_PATH = "import_files/res_users.csv"
ID_MAP_PATH = "import_files/ipi_odoo_id_mapping_short.csv"

# ASSETS

MACH_ERR_FILE = ERROR_PATH + "machines_error.csv"
MACH_TYPE_FILE = IMPORT_PATH + "machine_types.csv"
MACH_IDENTIFICATION = IMPORT_PATH + "machines_specific_details.csv"
IMPORT_FILE_DICT = {
    'dm1104': IMPORT_PATH + "customer_machines_medium.csv",
    'dpr162': IMPORT_PATH + "dpr_162_machines_short.csv",
    'dpr462': IMPORT_PATH + "dpr_462_machines_short.csv",
    'odoo': IMPORT_PATH + "odoo10_macchine_export.csv",
}

ID_FIELD_DICT = {
    'dm1104': 'ipi_id',
    'dpr162': 'ipi162_id',
    'dpr462': 'ipi462_id',
}