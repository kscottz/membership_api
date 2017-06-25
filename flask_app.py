from config.portal_config import APP_PORT
from membership.web.base_app import app

# For running as script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT)
