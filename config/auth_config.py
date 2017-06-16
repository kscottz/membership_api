import os

USE_AUTH = os.environ.get('USE_AUTH', 'TRUE') != 'FALSE'

# the user to authenticate as if external auth is off (for testing only)
NO_AUTH_EMAIL = os.environ.get('NO_AUTH_EMAIL', 'joe.schmoe@example.com')

# the client id and secret for verifying users token
JWT_SECRET = os.environ.get('JWT_SECRET', None)
JWT_CLIENT_ID = os.environ.get('JWT_CLIENT_ID', None)
AUTH_URL = os.environ.get('AUTH_URL', 'https://dsasf.auth0.com/')
AUTH_CONNECTION = os.environ.get('AUTH_CONNECTION', 'Username-Password-Authentication')

# the client ID and secret for the non-interactive auth client (for creating users in auth0)
ADMIN_CLIENT_ID = os.environ.get('ADMIN_CLIENT_ID', None)
ADMIN_CLIENT_SECRET = os.environ.get('ADMIN_CLIENT_SECRET', None)

