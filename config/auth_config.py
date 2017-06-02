import os

USE_AUTH = os.environ.get('USE_AUTH', 'TRUE') != 'FALSE'
JWT_SECRET = os.environ.get('JWT_SECRET', None)
JWT_CLIENT_ID = os.environ.get('JWT_CLIENT_ID', None)
ADMIN_CLIENT_ID = os.environ.get('ADMIN_CLIENT_ID', None)
ADMIN_CLIENT_SECRET = os.environ.get('ADMIN_CLIENT_SECRET', None)
AUTH_URL = os.environ.get('AUTH_URL', 'https://dsasf.auth0.com/')
AUTH_CONNECTION = os.environ.get('AUTH_CONNECTION', 'Username-Password-Authentication')