from config.email_config import EMAIL_API_KEY, EMAIL_DOMAIN, USE_EMAIL
import json
import logging
import membership
from membership.database.models import Email
import pkg_resources
import requests


def send_emails(sender, subject, email_template, recipient_variables):
    url = 'https://api.mailgun.net/v3/' + EMAIL_DOMAIN + '/messages'
    payload = [
        ('from', sender),
        ('recipient-variables', json.dumps(recipient_variables)),
        ('subject', subject),
        ('html', email_template)
    ]
    payload.extend([('to', email) for email in recipient_variables.keys()])
    if USE_EMAIL:
        r = requests.post(url, data=payload, auth=('api', EMAIL_API_KEY))
        if r.status_code > 299:
            logging.error(r.text)


def send_welcome_email(email, name, verify_url):
    # now send email with this link
    sender = 'New Member Outreach <members@' + EMAIL_DOMAIN + '>'
    template = pkg_resources.resource_string(membership.__name__, 'templates/welcome_email.html')
    recipient_variables = {email: {'name': name, 'link': verify_url}}
    send_emails(sender, 'Welcome %recipient.name%', template, recipient_variables)


def update_email(email: Email) -> str:
    url = 'https://api.mailgun.net/v3/routes'
    payload = [
        ('priority', 0),
        ('description', 'Forwarding rule for {address}'.format(address=email.email_address)),
        ('expression', 'match_recipient("{address}")'.format(address=email.email_address)),
    ]
    payload.extend([('action', 'forward("{address}")'.format(address=forward.forward_to))
                    for forward in email.forwarding_addresses])
    if email.external_id:
        r = requests.put(url + '/' + email.external_id, data=payload, auth=('api', EMAIL_API_KEY))
        if r.status_code > 299:
            logging.error(r.text)
            raise Exception('Update failed')
        return email.external_id
    else:
        r = requests.post(url, data=payload, auth=('api', EMAIL_API_KEY))
        if r.status_code > 299:
            logging.error(r.text)
            raise Exception('Update failed')
        return r.json().get('route').get('id')