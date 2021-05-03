from flask import Blueprint, request, make_response, redirect, render_template, session, abort

from .database import Database
from . import loginutil
from .keychain import KeyChain

login = Blueprint('login', __name__, 
        template_folder="../templates",
        static_folder="../static",
        url_prefix="/login")

keychain = KeyChain()
login_manager = loginutil.GoogleLogin(keychain)

# Note: when testing locally, must use port 8888 for Google SSO
# general welcome/login page
@login.route('/', methods=['GET'])
def login_route():
    if loginutil.is_logged_in(session):
        # no need to be here
        return redirect('/index')

    html = render_template('login.html')
    response = make_response(html)
    return response

@login.route('/redirect', methods=['GET'])
def login_redirect():
    # redirect the user to Google's login page
    request_uri = login_manager.get_login_redirect(request)
    return redirect(request_uri)

@login.route('/auth', methods=['GET'])
def login_auth():
    try:
        profileid, email, fullname, picture = login_manager.authorize(request)

        # set session!
        session['profileid'] = profileid
        session['email'] = email
        session['fullname'] = fullname
        session['picture'] = picture

        # check where to redirect user
        db = Database()
        db.connect()
        user_exists = db.user_exists(profileid)
        db.disconnect()
        
        if user_exists:
            return redirect('/timeline')
        else:
            return redirect('/index')

    except Exception as e:
        return make_response('Failed to login: ' + str(e))

@login.route('/logout', methods=['GET'])
def logout():
    # simply clear the user's session
    session.pop('profileid', None)
    session.pop('email', None)
    session.pop('fullname', None)
    session.pop('picture', None)

    return redirect('/')
