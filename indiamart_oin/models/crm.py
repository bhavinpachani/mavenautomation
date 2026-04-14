from odoo import api, fields, models
import requests
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

TIMEOUT = 20


class Leads(models.Model):
    _inherit = 'crm.lead'

    indiamart_name = fields.Char()
    lead_type = fields.Selection(
        [('phone_calls', 'Phone Calls'),
         ('buy_enquiry', 'Buy Enquiry'),
         ('buy_leads', 'Buy Leads')],
        string='Type of Lead',
    )
    indiamart_id = fields.Many2one('indiamart.enquiry', string='IndiaMart A/c')
    indiamart_query_id = fields.Char("Indiamart Query#")

    @api.model
    def _cron_enquiry_indiamart_leads(self):
        """Cron for reading leads from IndiaMart periodically."""

        partner_obj = self.env['res.partner'].sudo()
        country_obj = self.env['res.country'].sudo()
        state_obj = self.env['res.country.state'].sudo()
        lead_obj = self.env['crm.lead'].sudo()

        for indiamart_conf in self.env['indiamart.enquiry'].search([]):
            cur_time = datetime.now() + timedelta(hours=5, minutes=30)
            end_date = datetime.strftime(cur_time, '%d-%m-%Y %H:%M')

            start_time = cur_time - timedelta(days=6)
            start_date = datetime.strftime(start_time, '%d-%m-%Y %H:%M')

            url = (
                'https://mapi.indiamart.com/wservce/crm/crmListing/v2/'
                '?glusr_crm_key=' + str(indiamart_conf.key)
                + '&start_time=' + start_date + ':00'
                + '&end_time=' + end_date + ':00'
            )
            _logger.info('IndiaMart Lead Request URL: %s.', url)

            try:
                response = requests.post(url, timeout=TIMEOUT)
                data = response.json()
                print("Data resposne = \n \n",data)
                for lead in data.get('RESPONSE', []):
                    indiamart_query_id = str(
                        lead.get('UNIQUE_QUERY_ID', '') or ''
                    ).strip().replace(" ", "")

                    country_rec = False
                    if lead.get('SENDER_COUNTRY_ISO', ''):
                        country_rec = country_obj.search(
                            [('code', '=', lead['SENDER_COUNTRY_ISO'].strip().upper())],
                            limit=1,
                        )

                    lead_type = False
                    query_type = lead.get('QUERY_TYPE', '')
                    if query_type in ('P', 'p'):
                        lead_type = 'phone_calls'
                    elif query_type in ('W', 'w'):
                        lead_type = 'buy_enquiry'
                    elif query_type in ('B', 'b'):
                        lead_type = 'buy_leads'

                    partner_id = partner_obj.search([
                        ('email', '=', str(lead.get('SENDER_EMAIL', '') or '').strip().replace(" ", "")),
                        ('phone', '=', str(lead.get('SENDER_MOBILE', '') or '').strip()),
                    ], limit=1)

                    state = False
                    if lead.get('SENDER_STATE', ''):
                        state = state_obj.search(
                            [('name', '=', lead['SENDER_STATE'].strip())],
                            limit=1,
                        )

                    address = (
                        lead.get('SENDER_ADDRESS', '')
                        and lead['SENDER_ADDRESS'].split(',')
                        or ''
                    )
                    phone = lead.get('SENDER_MOBILE', '')
                    print("Phone === \n \n",phone)
                    clean_number = phone.replace('+91-', '')
                    print("Clean number => \n \n",clean_number)

                    domain = ['|', ('active', '=', True), ('active', '=', False)]
                    if lead.get('SUBJECT', ''):
                        domain.append('|')
                        domain.append(('name', '=', str(lead.get('SUBJECT', '') or '').strip()))
                        domain.append(('indiamart_name', '=', str(lead.get('SUBJECT', '') or '').strip()))
                    if lead.get('SENDER_NAME', ''):
                        domain.append(('contact_name', '=', str(lead.get('SENDER_NAME', '') or '').strip()))
                    if lead.get('SENDER_MOBILE', ''):
                        domain.append(('phone', '=', str(clean_number or '').strip()))
                    if lead.get('SENDER_EMAIL', ''):
                        domain.append(('email_from', '=', str(lead.get('SENDER_EMAIL', '') or '').strip().replace(" ", "")))

                    lead_rec = lead_obj.search(domain)
                    if not lead_rec and indiamart_query_id:
                        lead_rec = lead_obj.search(
                            [('indiamart_query_id', '=', indiamart_query_id)]
                        )

                    if not lead_rec:
                        lead_rec = lead_obj.create({
                            'type': 'lead',
                            'name': str(lead.get('SUBJECT', '') or '').strip(),
                            'indiamart_name': str(lead.get('SUBJECT', '') or '').strip(),
                            'partner_id': partner_id.id if partner_id else False,
                            'contact_name': str(lead.get('SENDER_NAME', '') or '').strip(),
                            'partner_name': str(lead.get('SENDER_COMPANY') or '').strip(),
                            'lead_type': lead_type,
                            'street': lead.get('SENDER_ADDRESS', '') or '',
                            'city': str(lead.get('SENDER_CITY', '') or '').strip(),
                            'state_id': state.id if state else False,
                            'country_id': country_rec.id if country_rec else False,
                            'phone': str(clean_number or '').strip(),
                            'description': lead.get('QUERY_MESSAGE', ''),
                            'email_from': str(lead.get('SENDER_EMAIL', '') or '').strip().replace(" ", ""),
                            'zip': (
                                address[-1].strip()
                                if address and address[-1].strip().isdigit()
                                else ''
                            ),
                            'company_id': indiamart_conf.company_id.id if indiamart_conf.company_id else False,
                            'priority': '3',
                            'indiamart_id': indiamart_conf.id,
                            'indiamart_query_id': indiamart_query_id or False,
                        })
                        lead_rec.write({'user_id': False})
            except Exception as e:
                _logger.error('IndiaMart Lead Sync Error: %s', e)
