from flask import Flask, request, make_response, redirect, url_for
from flask import render_template
from os import environ
import json

from oauthlib.oauth2 import WebApplicationClient
import requests

from .database import Database
from .matching import Matching
from .cookiemonster import CookieMonster
from . import loginutil

app = Flask(__name__, template_folder="../templates", static_folder="../static")
oauth_cl= WebApplicationClient(loginutil.GOOGLE_CLIENT_ID)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response

# Note: when testing locally, must use port 8888 for Google SSO
@app.route('/login', methods=['GET'])
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = loginutil.get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = oauth_cl.prepare_request_uri(
        authorization_endpoint,
        redirect_uri= request.base_url + "/auth",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)
    

# for checking if user exists already, setting a session cookie,
# and redirecting to the next page
@app.route('/login/auth', methods=['GET'])
def login_auth():
    code = request.args.get('code')

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = loginutil.get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = oauth_cl.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(loginutil.GOOGLE_CLIENT_ID, loginutil.GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    oauth_cl.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_cl.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    return make_response(userinfo_response.json())

@app.route('/createstudent', methods=['POST'])
def createstudent():
    try:
        acct_info = request.form

        firstname, lastname = acct_info.get('name', 'test student').split()
        # We need this to pass. Throw an error otherwise
        profileid = acct_info['profileid']
        email = acct_info.get('email', '')
        role = acct_info.get('role', '') # FIXME 
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        matchbool = acct_info.get('matchBool', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.getlist('industry')
        student = [profileid, firstname, lastname, classyear, email, major, zipcode, nummatches, industry]
        print(student)
        db = Database()
        db.connect()
        db.create_students([student])
        db.disconnect()
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    # redirect to getstudents after the name is added, make sure to uncomment this
    return redirect(url_for('getstudents'))


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

@app.route('/editprofile', methods=['GET'])
def getprofile():
    try:
        temp_id = request.cookies.get('profileid')
        db = Database()
        db.connect()
        info = db.get_student_by_id(temp_id)
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
        temp_id = request.cookies.get('profileid')
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

        for i in new_info:
            print(i)

        db = Database()
        db.connect()
        db.update_student(temp_id, new_info)
        db.disconnect()

        # reload the editprofile page
        temp_id = request.cookies.get('profileid')
        db = Database()
        db.connect()
        info = db.get_student_by_id(temp_id)
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
        # search form
        # these are the form fields
        # cookie_handler = CookieMonster(request.form)
        # firstname = cookie_handler.getVar('firstname')
        # lastname = cookie_handler.getVar('lastname')
        # major = cookie_handler.getVar('major')
        # email = cookie_handler.getVar('email')
        # zipcode = cookie_handler.getVar('zipcode')
        # career = cookie_handler.getVar('career')
        # student = cookie_handler.getVar('student') # TODO: need to handle whether to search for students or alumni (checkbox?)
        firstname = request.args.get('firstname', '%')
        lastname = request.args.get('lastname', '%')
        email = request.args.get('email', '%')
        major = request.args.get('major', '%')
        zipcode = request.args.get('zipcode', '%')
        career = request.args.get('industry', '%')
        search_query = [firstname, lastname, major, email, zipcode, career]
        print(search_query)
        # database queries
        db = Database()
        db.connect()
        print('here')
        results = db.search(search_query) # FIXME: db.search() will take search_query and two booleans (student and alumni)
        print(results)
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

