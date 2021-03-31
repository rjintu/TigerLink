from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

from database import Database
from matching import Matching

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

        firstname, lastname = acct_info.get('name', 'test student').split()
        email = acct_info.get('email', '')
        role = acct_info.get('role', '') # FIXME 
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        matchbool = acct_info.get('matchBool', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.get('industry', '')

        # TODO: verify this step
        student = [profileid, firstname, lastname, classyear, email, major, zipcode, nummatches, industry]
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
