import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://root@localhost:3306/dsa')
settings = {'name_or_url': DATABASE_URL, 'pool_size': 10, 'pool_recycle': 3600}
SUPER_USER_FIRST_NAME = os.environ.get('SUPER_USER_FIRST_NAME', 'Joe')
SUPER_USER_LAST_NAME = os.environ.get('SUPER_USER_LAST_NAME', 'Schmoe')
SUPER_USER_EMAIL = os.environ.get('SUPER_USER_EMAIL', 'joe.schmoe@example.com')
