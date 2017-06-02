import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql://root@localhost:3306/dsa')
settings = {'name_or_url': DATABASE_URL, 'pool_size': 10, 'pool_recycle': 3600}