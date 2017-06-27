from flask import Blueprint, jsonify, request, Response
from membership.database.base import Session
from membership.database.models import Email, ForwardingAddress, Member
from membership.web.auth import requires_auth
from membership.util.email import update_email


email_api = Blueprint('email_api', __name__)


@email_api.route('/emails', methods=['POST'])
@requires_auth(admin=True)
def get_elections(requester: Member, session: Session):
    email = Email()
    email.email_address = request.json['email_address']
    for forwarding_email in request.json['forwarding_addresses']:
        forwarding_address = ForwardingAddress()
        forwarding_address.incoming_email = email
        forwarding_address.forward_to = forwarding_email
    email.external_id = update_email(email)
    session.add(email)
    session.commit()
    return jsonify({'status': 'success'})