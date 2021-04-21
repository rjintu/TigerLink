from flask import Blueprint, request, make_response, redirect, render_template, session, abort

from . import loginutil
from .database import Database
from .matching import Matching

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
    db.disconnect()
    html = render_template('matches.html', matches=matches)
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
    db.disconnect()

    html = render_template('users.html', students=students, alumni=alumni)
    return make_response(html)

@admin.errorhandler(403)
def permissions(err):
    html = render_template('permissions.html')
    return make_response(html)
