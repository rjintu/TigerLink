from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

from database import Database
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

# for checking if user exists already, setting a session cookie,
# and redirecting to the next page


@app.route('/login/auth', methods=['POST'])
def login_auth():
    profileid = request.form['profileid']

    db = Database()
    db.connect()
    student_profile = db.get_student_by_id(
        profileid)  # TODO: do same for alums
    if student_profile is None:
        return redirect(url_for('index'))
    else:
        # set the cookie!
        response = redirect(url_for('getstudents'))
        response.set_cookie('profileid', profileid)
        return response


@app.route('/createstudent', methods=['POST'])
def createstudent():
    try:
        acct_info = request.form

        firstname, lastname = acct_info.get('name', 'test student').split()
        # We need this to pass. Throw an error otherwise
        profileid = acct_info['profileid']
        email = acct_info.get('email', '')
        role = acct_info.get('role', '')
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        matchbool = acct_info.get('matchBool', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.get('industry', '')

        # TODO: verify this step
        student = [profileid, firstname, lastname, classyear,
                   email, major, zipcode, nummatches, industry]

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
    try:
        # these are the form fields
        cookie_handler = CookieMonster()
        firstname = cookie_handler.getVar('firstname')
        lastname = cookie_handler.getVar('lastname')
        major = cookie_handler.getVar('major')
        email = cookie_handler.getVar('email')
        zipcode = cookie_handler.getVar('zipcode')
        career = cookie_handler.getVar('career')
        # TODO: need to handle whether to search for students or alumni (checkbox?)
        student = cookie_handler.getVar('student')

        search_query = [firstname, lastname, major, email, zipcode, career]

        # database queries
        db = Database()
        db.connect()
        # FIXME: db.search() will take search_query and two booleans (student and alumni)
        results = db.search(search_query)
        db.disconnect()
        html = render_template('search.html', search_query=search_query)

    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response
