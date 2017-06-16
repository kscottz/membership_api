from config import dotenv
from membership.web.base_app import app


# For running as script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
