from config.auth_config import JWT_SECRET, JWT_CLIENT_ID, ADMIN_CLIENT_ID, ADMIN_CLIENT_SECRET, \
    AUTH_CONNECTION, AUTH_URL, USE_AUTH, NO_AUTH_EMAIL
from config.portal_config import PORTAL_URL
from datetime import datetime, timedelta
from functools import wraps
from flask import request, Response, jsonify
import jwt
import logging
from membership.database.base import Session
from membership.database.models import Member
import pkg_resources
import random
import requests
import string

PASSWORD_CHARS = string.ascii_letters + string.digits


def deny(reason: str= '') -> Response:
    """Sends a 401 response that enables basic auth"""
    response = jsonify({
        'status': 'error',
        'err': 'Could not verify your access level for that URL.\n'
               'You have to login with proper credentials and' + reason
    })
    response.status_code = 401
    return response


def requires_auth(admin=False):
    """ This defines a decorator which when added to a route function in flask requires authorization to
    view the route.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if USE_AUTH:
                auth = request.headers.get('authorization')
                if not auth:
                    return deny('Authorization not found.')
                token = auth.split()[1]
                try:
                    token = jwt.decode(token, JWT_SECRET, audience=JWT_CLIENT_ID)
                except Exception as e:
                    return deny(str(e))
                email = token.get('email')
            else:
                email = NO_AUTH_EMAIL
            session = Session()
            try:
                member = session.query(Member).filter_by(email_address=email).one()
                authenticated = False
                if admin:
                    for role in member.roles:
                        if role.committee_id is None and role.role == 'admin':
                            authenticated = True
                else:
                    authenticated = True
                if authenticated:
                    kwargs['requester'] = member
                    kwargs['session'] = session
                    return f(*args, **kwargs)
                return deny('not enough access')
            finally:
                session.close()

        return decorated
    return decorator


current_token = {}


def get_auth0_token():
    if not current_token or datetime.now() > current_token['expiry']:
        current_token.update(generate_auth0_token())
    return current_token['token']


def generate_auth0_token():
    payload = {'grant_type': "client_credentials",
               'client_id': ADMIN_CLIENT_ID,
               'client_secret': ADMIN_CLIENT_SECRET,
               'audience': AUTH_URL + 'api/v2/'}
    response = requests.post(AUTH_URL + 'oauth/token', json=payload).json()
    return {'token': response['access_token'],
            'expiry': datetime.now() + timedelta(seconds=response['expires_in'])}


def create_auth0_user(email):
    if not USE_AUTH:
        return PORTAL_URL
    # create the user
    payload = {
        'connection': AUTH_CONNECTION,
        'email': email,
        'password': ''.join(random.SystemRandom().choice(PASSWORD_CHARS) for _ in range(12)),
        'user_metadata': {},
        'email_verified': False,
        'verify_email': False
    }
    headers = {'Authorization': 'Bearer ' + get_auth0_token()}
    r = requests.post(AUTH_URL + 'api/v2/users', json=payload, headers=headers)
    if r.status_code > 299:
        logging.error(r.json())
        raise Exception('Failed to create user')
    user_id = r.json()['user_id']

    # get a password change URL
    payload = {
        'result_url': PORTAL_URL,
        'user_id': user_id
    }
    r = requests.post(AUTH_URL + 'api/v2/tickets/password-change', json=payload, headers=headers)
    if r.status_code > 299:
        logging.error(r.json())
        raise Exception('Failed to get password url')
    reset_url = r.json()['ticket']

    # get email verification link
    payload = {
        'result_url': reset_url,
        'user_id': user_id
    }
    r = requests.post(AUTH_URL + 'api/v2/tickets/email-verification', json=payload, headers=headers)
    if r.status_code > 299:
        logging.error(r.json())
        raise Exception('Failed to get verify url')
    validate_url = r.json()['ticket']
    return validate_url

