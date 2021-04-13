from flask import Blueprint, make_response, redirect, render_template, session, abort

from . import loginutil
from .database import Database

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
    role = db.get_role(profileid)
    db.disconnect()

    if role != "admin":
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

    html = render_template('matches.html')
    return make_response(html)

@admin.errorhandler(403)
def permissions(err):
    html = render_template('permissions.html')
    return make_response(html)
