from erppeek import Client

# setting erppeek
EXPORT_FIELDS = [
    'id', 'name', 'street', 'street2', 'city', 'zip', 'website', 'sdi_code',
    'phone', 'fax', 'email', 'pec_mail', 'iban', 'lang','company_type',
    'rating', 'target_audience', 'comment', 'is_competitor',
    'competitor_type', 'vat', 'fiscalcode', 'trust', 'split_payment',
    'type', 'sex', 'mobile', 'function', 'default_ipi_crm_password', 'customer',
    'is_apartment_building', 'is_customer_manager', 'supplier',
    'is_segnalatore_commerciale', 'is_company']


class Export:
    def __init__(self, CLIENT):
        self.client = CLIENT

    def export_data(self):
        print('Connected to {}'.format(self.client))
        query = """
        SELECT rp.id, rp.name, street, street2, city, zip, website, phone, fax, email, pec_mail, 
        lang, target_audience, comment, is_competitor, competitor_type, 
        vat, fiscalcode, type, mobile, rpjp.name, function, 
        rcs.name, rc.name, ct.name, --afp.name, aap.code, aar.code, 
         is_condominium,  is_company
        
        
        
        FROM res_partner AS rp
        LEFT JOIN res_partner_job_position rpjp ON rpjp.id = rp.job_position_id
        LEFT JOIN res_country_state rcs ON rcs.id = rp.state_id
        LEFT JOIN res_country rc ON rc.id = rp.country_id
        LEFT JOIN crm_team ct ON ct.id = rp.team_id
        --LEFT JOIN account_fiscal_position afp ON afp.id = rp.property_account_position_id
        --LEFT JOIN account_account aap ON aap.id = rp.property_account_payable_id
        --LEFT JOIN account_account aar ON aar.id = rp.property_account_receivable_id
        LIMIT 10"""
        self.client._cr.execute(query)
        partner_data = self.client.env.cr.fetchall()

        """
        MAPPING CAMPI
        sdi_code >> codice_destinatario
        company_type >> is_company
        
        user_id/name ???
        
        iban, rating, trust, split_payment, sex, default_ipi_crm_password,
        customer, is_apartment_building, is_customer_manager, supplier, is_segnalatore_commerciale,
        segment_id, campagna_id/display_name, default_ipi_crm_password, message_is_follower, customer, is_apartment_building,
        is_customer_manager, is_segnalatore_commerciale,
        """