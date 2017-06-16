from config.email_config import EMAIL_API_KEY, EMAIL_DOMAIN, USE_EMAIL
import json
import logging
import membership
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
