import csv

MAIN_PATH = "/home/ubuntu/Development/Odoo/14/parts/others/monk/ipi_import/import_files/"
CITIES_FILE = MAIN_PATH + "cities.csv"
PROVINCES_FILE = MAIN_PATH + "provinces.csv"
REGIONS_FILE = MAIN_PATH + "regions.csv"


class GeoLocation:
    def __init__(self, client, company, import_type):
        self.encoding = "utf8"
        self.client = client
        self.company = company
        self.import_type = import_type

    def map_regions(self):
        with open(REGIONS_FILE, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                rcr_obj = self.client.ResCountryRegion
                region_id = rcr_obj.search([('name', "=", row['name'])], limit=1)
                if region_id:
                    rcr_obj.browse(region_id[0]).ipi_id = int(row['id'])
                else:
                    print("Region {} was not found!".format(row['name']))

        print("\n Regions have been mapped!")

    def map_provinces(self):
        with open(PROVINCES_FILE, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                rcs_obj = self.client.ResCountryState
                province_id = rcs_obj.search([('name', "=", row['name'])], limit=1)
                if province_id:
                    rcs_obj.browse(province_id[0]).ipi_id = int(row['id'])
                else:
                    print("Province {} was not found!".format(row['name']))

        print("\n Regions have been mapped!")

    def map_cities(self):
        with open(CITIES_FILE, 'r', encoding='utf8') as csvfile:
            spam_reader = csv.DictReader(
                csvfile, delimiter=",", quotechar='"')
            for row in spam_reader:
                rc_obj = self.client.ResCity
                name = row['name'].title()
                city_id = rc_obj.search([('name', "=", name)], limit=1)
                if city_id:
                    rc_obj.browse(city_id[0]).ipi_id = int(row['id'])
                else:
                    print("city {} was not found!".format(name))
                    # TODO: 40 cities not found, create them?
        print("\n Cities have been mapped!")
