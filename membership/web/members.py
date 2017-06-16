from flask import Blueprint, jsonify, request
from membership.database.base import Session
from membership.database.models import Member, Committee, Role
from membership.web.auth import create_auth0_user, requires_auth
from membership.util.email import send_welcome_email
member_api = Blueprint('member_api', __name__)


@member_api.route('/member/list', methods=['GET'])
@requires_auth(admin=True)
def get_members(requester: Member, session: Session):
    results = []
    members = session.query(Member).all()
    for member in members:
        results.append({'name': member.first_name + ' ' + member.last_name,
                       'email': member.email_address})
    return jsonify(results)


@member_api.route('/member', methods=['GET'])
@requires_auth(admin=False)
def get_member_info(requester: Member, session: Session):
    member = {'info': {'first_name': requester.first_name, 'last_name': requester.last_name},
              'roles':
                  [{'role': role.role, 'committee': role.committee.name
                  if role.committee else 'general'} for role in requester.roles]
              }
    return jsonify(member)


@member_api.route('/member', methods=['POST'])
@requires_auth(admin=True)
def add_member(requester: Member, session: Session):
    member = Member(**request.json)
    verify_url = create_auth0_user(member.email_address)
    send_welcome_email(member.email_address, member.first_name, verify_url)
    session.add(member)
    session.commit()
    return jsonify({'status': 'success'})


@member_api.route('/committee/list', methods=['GET'])
@requires_auth(admin=False)
def get_committees(requester: Member, session: Session):
    committees = session.query(Committee).all()
    result = {c.id: c.name for c in committees}
    return jsonify(result)


@member_api.route('/committee', methods=['POST'])
@requires_auth(admin=True)
def add_committee(requester: Member, session: Session):
    committee = Committee(name=request.json['name'])
    session.add(committee)
    admins = request.json['admin_list'].split(',')
    members = session.query(Member).filter(Member.email_address.in_(admins)).all()
    for member in members:
        role = Role(role='admin')
        role.committee = committee
        role.member = member
        session.add(role)
    session.commit()
    return jsonify({'status': 'success'})


@member_api.route('/admin', methods=['POST'])
@requires_auth(admin=True)
def make_admin(requester: Member, session: Session):
    member = session.query(Member).filter_by(email_address=request.json['email_address']).one()
    committee_id = request.json['committee'] if request.json['committee'] != '0' else None
    role = Role(member_id= member.id, role='admin', committee_id=committee_id)
    session.add(role)
    session.commit()
    return jsonify({'status': 'success'})
