from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

from database import Database
from matching import Matching
from cookiemonster import CookieMonster

app = Flask(__name__)

@app.route('/index', methods=['GET'])
def index():
    html = render_template('index.html')
    response = make_response(html)
    return response

# Note: when testing locally, must use port 8888 for Google SSO
@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
def login():
    html = render_template('login.html')
    response = make_response(html)
    return response

@app.route('/createstudent', methods=['POST'])
def createstudent():
    try:
        acct_info = request.form

        firstname, lastname = acct_info.get('name', 'test user').split()
        profileid = acct_info['profileid'] # We need this to pass. Throw an error otherwise
        email = acct_info.get('email', '')
        role = acct_info.get('role', '') # FIXME 
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        matchbool = acct_info.get('matchBool', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.get('industry', '')

        print(role)
        # TODO: verify this step
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

    response = make_response(html)
    return response
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

