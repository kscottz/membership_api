import config  # noqa: F401
from flask import request, Response, jsonify
from flask import Flask
from flask_cors import CORS
from membership.database.base import Session
from membership.database.models import Member
from membership.web.auth import create_auth0_user, requires_auth

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=["GET"])
def health_check():
    return jsonify({'health': True})


@app.route('/members', methods=["GET"])
@requires_auth(admin=True)
def get_members():
    session = Session()
    try:
        results = []
        members = session.query(Member).all()
        for member in members:
            results.append({'name': member.first_name + ' ' + member.last_name,
                           'email': member.email_address})
        return jsonify(results)
    finally:
        session.close()


@app.route('/member', methods=["POST"])
@requires_auth(admin=True)
def add_member():
    session = Session()
    try:
        member = Member(**request.json)
        create_auth0_user(member.email_address, member.first_name)
        session.add(member)
        session.commit()
        return jsonify({'status': 'success'})
    finally:
        session.close()
