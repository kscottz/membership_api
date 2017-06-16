import os

USE_EMAIL = os.environ.get('USE_EMAIL', 'TRUE') != 'FALSE'
EMAIL_DOMAIN = os.environ.get('EMAIL_DOMAIN', 'dsasf.org')
EMAIL_API_KEY = os.environ.get('EMAIL_API_KEY', None)
