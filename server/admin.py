from flask import Blueprint, make_response, redirect, render_template, session, abort

from . import loginutil
from .database import Database

admin = Blueprint('admin', __name__, template_folder="../templates",
        static_folder="../static")

@admin.route('/admin', methods=['GET'])
@admin.route('/admin/', methods=['GET'])
@admin.route('/admin/index', methods=['GET'])
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

@admin.route('/admin/permissions', methods=['GET'])
def permissions():
    if not loginutil.is_logged_in(session):
        return redirect('/login')
    profileid = session['profileid']

    db = Database()
    db.connect()
    role = db.get_role(profileid)
    db.disconnect()

    if role != "admin":
        abort(403)

    html = render_template('permissions.html')
    return make_response(html)
