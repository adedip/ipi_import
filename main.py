"""Import script for IPI projects

    In all imports we will import the externalID as "ipi_" + ipi DB.
    This will ease additional import that will be make for integration.

"""

from erppeek import Client
import logging
from model_imports.res_partner import ResPartner
from model_imports.geolocation import GeoLocation
from model_imports.asset_decree import AssetDecree

# setting erppeek

CLIENT = Client('http://localhost:8069',
                db='14c_demo_ipi',
                user='admin',
                password='admin')

# CLIENT = Client(
#             'https://ipi14.odoo-svil.monksoftware.it',
#             db='odooipi14svil',
#             user='admin',
#             password="kingcrimson*14")


print('Connected to Client. Start import\n')


def check_modules():
    installed_mod = CLIENT.IrModuleModule.browse([('state', '=', 'installed')]).name
    required_mod = ['l10n_it_fatturapa', 'l10n_it_pec', 'l10n_it_fiscalcode',
                    'l10n_it_ipa']
    for module in required_mod:
        if module not in installed_mod:
            raise ImportError(f"Module {module} is  not installed!")

    print("\nYou're lucky..., all required moduled are installed ;)\n")


def import_data(import_type):
    company = CLIENT.ResCompany.browse([('name', '=', 'Ipi S.r.l.')], limit=1)
    # mapping geolocation
    # GeoLocation(CLIENT, company, import_type).map_cities()
    # GeoLocation(CLIENT, company, import_type).map_regions()
    # GeoLocation(CLIENT, company, import_type).map_provinces()

    # ResPartner(CLIENT, company, import_type).import_data()
    # ResPartner(CLIENT, company, import_type).map_ids()
    # ResPartner(CLIENT, company, import_type).setting_parent()
    # ResPartner(CLIENT, company, import_type).import_users()

    # AssetDecree(CLIENT, company, import_type).map_machine_type()
    # AssetDecree(CLIENT, company, import_type).map_identification()
    # AssetDecree(CLIENT, company, import_type).import_data()

    # INTEGRATIONS ######
    ResPartner(CLIENT, company, import_type).integrate_data()
    # ResPartner(CLIENT, company, import_type).clean_data()

    # AssetDecree(CLIENT, company, import_type).integrate_data()


if __name__ == "__main__":
    print("Beginning import data...\n")
    # check_modules()
    import_type = ['all', 'dm1104', 'dpr162', 'dpr462'][0]
    import_data(import_type)
    logging.info("\nFinito ;)")
