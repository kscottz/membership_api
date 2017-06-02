from config.email_config import EMAIL_API_KEY, EMAIL_DOMAIN
import json
import logging
import requests


def send_emails(subject, email_template, recipient_variables):
    url = 'https://api.mailgun.net/v3/' + EMAIL_DOMAIN + '/messages'
    payload = [
        ('from', 'DSA SF <members@dsasf.org>'),
        ('recipient-variables', json.dumps(recipient_variables)),
        ('subject', subject),
        ('html', email_template)
    ]
    payload.extend([('to', email) for email in recipient_variables.keys()])
    r = requests.post(url, data=payload, auth=('api', EMAIL_API_KEY))
    if r.status_code > 299:
        logging.error(r.text)
