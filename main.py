"""Import script for IPI projects

    In all imports we will import the externalID as "ipi_" + ipi DB.
    This will ease additional import that will be make for integration.

"""

from erppeek import Client
import logging
from export import Export
from model_imports.res_partner import ResPartner
from model_imports.geolocation import GeoLocation
from model_imports.asset_decree import AssetDecree

FILE_INPUT_PATH = 'account.invoice.csv'

ODOO_URL = 'http://localhost:8069'
ODOO_DB = '14c_demo_ipi'
ODOO_ACCOUNT = {'user': 'admin', 'pwd': 'admin'}
MAIN_PATH = "import_files/"

# setting erppeek
CLIENT = Client(ODOO_URL,
                db=ODOO_DB,
                user=ODOO_ACCOUNT['user'],
                password=ODOO_ACCOUNT['pwd'])

IPI_DEMO = Client(
            'https://ipi.odoo-demo.monksoftware.it/',
            db='odooipitest',
            user='admin',
            password="GRANDECampio'2019*")

print('Connected to {}. Start import\n'.format(ODOO_URL))

def check_modules():
    installed_mod = CLIENT.IrModuleModule.browse([('state', '=', 'installed')]).name
    required_mod = ['l10n_it_fatturapa', 'l10n_it_pec', 'l10n_it_fiscalcode',
                    'l10n_it_ipa']
    for module in required_mod:
        if module not in installed_mod:
            raise ImportError(f"Module {module} is  not installed!")

    print("\nYou're lucky..., all required moduled are installed ;)\n")

def import_data():
    company = CLIENT.ResCompany.browse([('name', '=', 'Ipi S.r.l.')], limit=1)
    # GeoLocation(CLIENT, company).map_cities()
    # GeoLocation(CLIENT, company).map_regions()
    # GeoLocation(CLIENT, company).map_provinces()
    # import utenti >> da Odoo
    # ResPartner(CLIENT, company).import_data()
    # ResPartner(CLIENT, company).setting_parent()

    # AssetDecree(CLIENT, company).map_machine_type()
    # AssetDecree(CLIENT, company).map_identification()
    # AssetDecree(CLIENT, company).import_data()


if __name__ == "__main__":
    print("Beginning import data...\n")
    # check_modules()
    Export(IPI_DEMO).export_data()
    # import_data()

    logging.info("\nFinito")
