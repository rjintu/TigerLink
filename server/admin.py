from flask import Blueprint, request, make_response, redirect, render_template, session, abort

from . import loginutil
from .database import Database
from .matching import Matching
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__, 
        template_folder="../templates",
        static_folder="../static",
        url_prefix="/admin")

# ensure user is logged in & is an admin
def verify_access(session):
    if not loginutil.is_logged_in(session):
        return redirect('/login')
    profileid = session['profileid']

    db = Database()
    db.connect()
    is_admin = db.get_admin(profileid)
    db.disconnect()

    if not is_admin:
        abort(403)

@admin.route('/', methods=['GET'])
@admin.route('/index', methods=['GET'])
def index():
    action = verify_access(session)
    if action is not None:
        return action
        
    return redirect('/admin/matches')

@admin.route('/matches', methods=['GET'])
def matches():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    matches = db.retrieve_matches(session['profileid'], display_all=True)
    # count num matches currently in db for each user
    studCnt = {}
    alumCnt = {}
    for match in matches:
        if studCnt.get(match[0]):
            studCnt[match[0]] += 1
        else:
            studCnt[match[0]] = 1
        if alumCnt.get(match[1]):
            alumCnt[match[1]] += 1
        else:
            alumCnt[match[1]] = 1

    students, _, _ = db.get_students()
    for i in range(len(students)):
        students[i] = list(students[i])
        students[i].append(studCnt.get(students[i][0], 0))

    alumni, _, _ = db.get_alumni()
    for i in range(len(alumni)):
        alumni[i] = list(alumni[i])
        alumni[i].append(alumCnt.get(alumni[i][0], 0))
    db.disconnect()
    html = render_template('matches.html', matches=matches, students=students, alumni=alumni)
    return make_response(html)

@admin.route('/creatematches', methods=['POST'])
def creatematches():
    action = verify_access(session)
    if action is not None:
        return action

    m = Matching()
    matches = m.match()

    db = Database()
    db.connect()
    db.reset_matches()
    db.add_matches(matches)
    db.disconnect()

    # todo: add error handling
    response = make_response('success!')
    return response

@admin.route('/deletematches', methods=['POST'])
def deletematches():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.reset_matches()
    db.disconnect()

    # todo: add error handling
    response = make_response('success!')
    return response

@admin.route('/manualmatch', methods=['POST'])
def manualmatch():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.add_matches([[request.form['studentid'], request.form['alumid'],
                'i', 'want', 'to', 'die', 55.0]])
    db.disconnect()

    response = make_response('success!')
    return response

@admin.route('/deletematch', methods=['POST'])
def deletematch():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.delete_match(request.form['studentid'], request.form['alumid']) 
    db.disconnect()

    response = make_response('success!')
    return response

@admin.route('/users', methods=['GET'])
def users():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    students, _, _ = db.get_students()
    alumni, _, _ = db.get_alumni()
    admin_dict = db.get_admin_dict()
    db.disconnect()

    html = render_template('users.html', students=students, alumni=alumni, admins=admin_dict)
    return make_response(html)

@admin.route('/deletestudent', methods=['POST'])
def deletestudent():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.delete_student(request.form['profileid'])
    db.disconnect()

    response = make_response('success!')
    return response

@admin.route('/deletealum', methods=['POST'])
def deletealum():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.delete_alum(request.form['profileid'])
    db.disconnect()

    response = make_response('success!')
    return response

@admin.route('/timeline', methods=['GET'])
def timeline():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    output = db.get_posts()
    posts = []
        
    offset = 240 # FIXME: change to user's time zone? 
    for post in output:
        curr_time = datetime.fromisoformat(post[3])
        curr_time = curr_time - timedelta(minutes=offset)
        formatted_time = curr_time.strftime("%A, %B %d at %I:%M %p")
        copy = post[:3] + (formatted_time,) + post[4:]
        posts.append(copy)

    db.disconnect()
    html = render_template('admin-timeline.html', posts=posts)
    response = make_response(html)
    return response

@admin.route('/deletepost', methods=['POST'])
def deletepost():
    action = verify_access(session)
    if action is not None:
        return action

    db = Database()
    db.connect()
    db.delete_post(request.form['postid'])
    db.disconnect()

    response = make_response('success!')
    return response

@admin.errorhandler(403)
def permissions(err):
    html = render_template('permissions.html')
    return make_response(html)
