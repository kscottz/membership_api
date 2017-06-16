from __future__ import absolute_import
from os import path
try:
    from dotenv import load_dotenv
    dotenv_path = path.join(path.dirname(__file__), '..', '.env')
    if path.exists(dotenv_path):
        load_dotenv(dotenv_path)
except ImportError:
    pass
