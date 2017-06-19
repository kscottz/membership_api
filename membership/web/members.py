from flask import Blueprint, jsonify, request
from membership.database.base import Session
from membership.database.models import Member, Committee, Role, Meeting, Attendee
from membership.web.auth import create_auth0_user, requires_auth
from membership.web.util import BadRequest
from membership.util.email import send_welcome_email
member_api = Blueprint('member_api', __name__)


@member_api.route('/member/list', methods=['GET'])
@requires_auth(admin=True)
def get_members(requester: Member, session: Session):
    results = []
    members = session.query(Member).all()
    for member in members:
        results.append({'id': member.id,
                        'name': member.name,
                        'email': member.email_address})
    return jsonify(results)


@member_api.route('/member', methods=['GET'])
@requires_auth(admin=False)
def get_member(requester: Member, session: Session):
    member = get_member_basics(requester)
    return jsonify(member)


def get_member_basics(member):
    return {'id': member.id,
            'info': {'first_name': member.first_name, 'last_name': member.last_name, 'biography': member.biography},
            'roles':
                [{'role': role.role, 'committee': role.committee.name
                    if role.committee else 'general'} for role in member.roles]
             }


def get_member_details_helper(member):
    member_dict = get_member_basics(member)
    member_dict['meetings'] = [attendee.meeting.name for attendee in member.meetings_attended]
    member_dict['votes'] = [{'election_id': eligible_vote.election_id,
                             'election_name': eligible_vote.election.name,
                             'election_status': eligible_vote.election.status,
                             'voted': eligible_vote.voted
                             } for eligible_vote in member.eligible_votes]
    return member_dict


@member_api.route('/member/details', methods=['GET'])
@requires_auth(admin=False)
def get_member_details(requester: Member, session: Session):
    member = get_member_details_helper(requester)
    return jsonify(member)


@member_api.route('/admin/member/details', methods=['GET'])
@requires_auth(admin=True)
def get_member_info(requester: Member, session: Session):
    other_member = session.query(Member).get(request.args['member_id'])
    return jsonify(get_member_details_helper(other_member))


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


@member_api.route('/meeting/list', methods=['GET'])
@requires_auth(admin=False)
def get_meeting(requester: Member, session: Session):
    meetings = session.query(Meeting).all()
    result = {m.id: m.name for m in meetings}
    return jsonify(result)


@member_api.route('/meeting/attend', methods=['POST'])
@requires_auth(admin=False)
def attend_meeting(requester: Member, session: Session):
    short_id = request.json['meeting_short_id']
    meeting = session.query(Meeting).filter_by(short_id=short_id).one_or_none()
    if not meeting:
        return BadRequest('Invalid meeting id')
    if len(session.query(Attendee).filter_by(meeting_id=meeting.id,
                                             member_id=requester.id).all()) > 0:
        return BadRequest('You have already logged into this meeting')
    a = Attendee()
    a.meeting = meeting
    a.member = requester
    session.add(a)
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


@member_api.route('/member/role', methods=['POST'])
@requires_auth(admin=True)
def add_role(requester: Member, session: Session):
    member_id = request.json.get('member_id', requester.id)
    committee_id = request.json['committee_id'] if request.json['committee_id'] != '0' else None
    role = Role(member_id=member_id, role=request.json['role'], committee_id=committee_id)
    session.add(role)
    session.commit()
    return jsonify({'status': 'success'})


@member_api.route('/member/attendee', methods=['POST'])
@requires_auth(admin=True)
def add_meeting(requester: Member, session: Session):
    member_id = request.json.get('member_id', requester.id)
    attend = Attendee(member_id=member_id, meeting_id=request.json['meeting_id'])
    session.add(attend)
    session.commit()
    return jsonify({'status': 'success'})
