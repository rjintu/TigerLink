from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template

from .database import Database
from .matching import Matching
from .cookiemonster import CookieMonster
from . import loginutil
from .keychain import KeyChain

keychain = KeyChain()
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = keychain.FLASK_SECRET
login_manager = loginutil.GoogleLogin(keychain)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    profileid = session['profileid']
    if profileid is None:
        # user is not logged in
        return redirect('/login')

    db = Database()
    db.connect()
    user = db.get_student_by_id(profileid)
    db.disconnect()
    if user is not None:
        # profile is already created
        return redirect('/getstudents')

    html = render_template('index.html')
    response = make_response(html)
    return response

# Note: when testing locally, must use port 8888 for Google SSO
@app.route('/login', methods=['GET'])
def login():
    # redirect the user to Google's login page
    request_uri = login_manager.get_login_redirect(request)
    return redirect(request_uri)

# for checking if user exists already, setting a session cookie,
# and redirecting to the next page
@app.route('/login/auth', methods=['GET'])
def login_auth():
    try:
        profileid, email, fullname = login_manager.authorize(request)

        # set session!
        session['profileid'] = profileid
        session['email'] = email
        session['fullname'] = fullname
        
        # check where to redirect user
        db = Database()
        db.connect()
        user = db.get_student_by_id(profileid)
        db.disconnect()
        if user is None:
            return redirect('/index')
        else:
            return redirect('/getstudents')

    except Exception as e:
        return make_response('Failed to login: ' + str(e))

@app.route('/createuser', methods=['POST'])
def createuser():
    try:
        acct_info = request.form

        if session['profileid'] is None:
            return redirect('/index')

        firstname, lastname = session['fullname'].split()
        # We need this to pass. Throw an error otherwise
        profileid = session['profileid']
        email = session['email']
        role = acct_info.get('role', '')
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        matchbool = acct_info.get('matchBool', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.getlist('industry')
        interests = acct_info.getlist('interests')
        user = [profileid, firstname, lastname, classyear, email, major, zipcode, nummatches, industry, interests]

        db = Database()
        db.connect()

        if role == 'student':
            db.create_students([user])

        else:
            db.create_alumni([user])

        db.disconnect()
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    # redirect to getstudents after the name is added, make sure to uncomment this
    return redirect(url_for('timeline')) # TODO: change the redirect to the right page


@app.route('/getstudents', methods=['GET'])
def getstudents():
    try:
        db = Database()
        db.connect()
        students = db.get_students()
        db.disconnect()
        html = render_template('getstudents.html', students=students)
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response

@app.route('/displaymatches', methods=['GET'])
def getmatches():
    try:
        # creates matches from matching.py file. returns a list of tuples.
        m = Matching()
        matches = m.match()
        html = render_template('displaymatches.html', matches=matches)
    
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
    
    response = make_response(html)
    return response

@app.route('/editprofile', methods=['GET'])
def getprofile():
    try:
        profileid = session['profileid']
        db = Database()
        db.connect()
        info = db.get_student_by_id(profileid)
        db.disconnect()
        html = render_template('editprofile.html', info=info)
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response

  # updates profile on save click
@app.route('/updateprofile', methods=['POST'])
def changeprofile():
    info = []
    try:
        profileid = session['profileid']
        # first update the entry in the database
        # contents of array must be array of [firstname, lastname, classyear, email, major,
        # zip, nummatch, career]
        acct_info = request.form

        firstname = acct_info.get('firstname', '')
        lastname = acct_info.get('lastname', '')
        classyear = acct_info.get('classYear', '')
        email = acct_info.get('email', '')
        major = acct_info.get('major', '')
        zipcode = acct_info.get('zipcode', '')
        nummatches = acct_info.get('numMatches', '')
        career = acct_info.get('career', '')

        new_info = [firstname, lastname, classyear,
                    email, major, zipcode, nummatches, career]

        db = Database()
        db.connect()
        db.update_student(profileid, new_info)
        db.disconnect()

        # reload the editprofile page
        db = Database()
        db.connect()
        info = db.get_student_by_id(profileid)
        db.disconnect()
        # return redirect(url_for('editprofile', info=info))
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    return redirect('editprofile')

# Note: search will automatically query both students and alumni
# TODO: implement this page in the frontend
@app.route('/search', methods=['GET'])
def search():
    search_query = None
    search_form = None
    try:
        firstname = request.args.get('firstname', '%')
        email = request.args.get('email', '%')
        major = request.args.get('major', '%')
        zipcode = request.args.get('zipcode', '%')
        career = request.args.get('industry', '%')
        search_query = [firstname, major, email, zipcode, career]
        print(search_query)
        # database queries
        db = Database()
        db.connect()
        results = db.search(search_query) # FIXME: db.search() will take search_query and two booleans (student and alumni)
        db.disconnect()
        html = render_template('search.html', results=results)

    except Exception as e:
        html = str(search_query) 
        print(e)

    response = make_response(html)
    return response


@app.route('/dosearch', methods=['GET'])
def dosearch():
    html = render_template('dosearch.html')
    response = make_response(html)
    return response

@app.route('/timeline', methods=['GET'])
def timeline():
    html = render_template('timeline.html')
    response = make_response(html)
    return response

@app.route('/groups', methods=['GET'])
def groups():
    html = render_template('groups.html')
    response = make_response(html)
    return response

