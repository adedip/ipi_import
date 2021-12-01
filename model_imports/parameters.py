"""Main parameters for different imports"""
IMPORT_PATH = "import_files/"
ERROR_PATH = "error_files/"

# GEOLOCATION

# PARTNERS
# ACTORS_PATH = "import_files/all_actors.csv"

ACTOR_IMPORT_FILE_DICT = {
    'dm1104': IMPORT_PATH + "pi_10_partner_exp_short.csv",
    'dpr162': IMPORT_PATH + "dpr162_actors.csv",
    # 'dpr462': IMPORT_PATH + "dpr_462_machines_short.csv",
}

ACTORS_ERR_FILE = ERROR_PATH + "actors_error.csv"

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