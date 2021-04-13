from flask import Blueprint, make_response, redirect, render_template, session, abort

from . import loginutil
from .database import Database

admin = Blueprint('admin', __name__, 
        template_folder="../templates",
        static_folder="../static",
        url_prefix="/admin")

@admin.route('/', methods=['GET'])
@admin.route('/index', methods=['GET'])
def index():
    if not loginutil.is_logged_in(session):
        return redirect('/login')
    profileid = session['profileid']

    db = Database()
    db.connect()
    role = db.get_role(profileid)
    db.disconnect()
        
    if role != "admin":
        abort(403)

    html = render_template('admin.html')
    return make_response(html)

@admin.errorhandler(403)
def permissions(err):
    html = render_template('permissions.html')
    return make_response(html)
