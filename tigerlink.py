from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

from database import Database

app = Flask(__name__, template_folder='.')

@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    try:
        db = Database()
        db.connect()
        db.init()

        u1 = [1, 'Devon', 'Ulrich', 2023, 'dulrich@princton.edu', 'COS',
              'USA', '93981', '2', 'SWE']
        u2 = [2, 'Ayush', 'Alag', 1998, 'aalag@princton.edu', 'COS',
              'USA', '95050', '5', 'Finance']
        u3 = [3, 'Rohan', 'Jinturkar', 2023, 'rjintu@microsoft.org', 'ECE',
              'USA', '99999', '1', 'PM']

        db.create_students([u1, u2, u3])
        db.disconnect()
    except Exception as e:
        print(e)

    html = render_template('index.html')
    response = make_response(html)
    return response


@app.route('/login', methods=['GET'])
def login():
    html = render_template('login.html')
    response = make_response(html)
    return response

@app.route('/createstudent', methods=['POST'])
def createstudent():
    print('here')
    try:
        acct_info = request.form

        # TODO: how to retrieve the name, email of the person from Google?
        # TODO: tokenize the name into first and last
        role = acct_info.get('role')
        classyear = acct_info.get('classYear')
        matchbool = acct_info.get('matchBool')
        nummatches = acct_info.get('numMatches')
        zipcode = acct_info.get('zipcode')
        industry = acct_info.get('industry')

        # TODO: verify this step
        student = ['1', 'firstname', 'lastname', classyear, 'email', 'major', zipcode, nummatches, industry]

        # db = Database()
        # db.connect()
        # db.create_student(student)
        # db.disconnect()
        html = f"fields: {role} {classyear} {matchbool} {nummatches} {zipcode} {industry}"
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
    
    # redirect to getstudents after the name is added
    return redirect(url_for('getstudents'))
    # response = make_response(html)
    # return response

@app.route('/getstudents', methods=['GET'])
def getstudents():
    try:
        db = Database()
        db.connect()
        students = db.get_students()
        db.disconnect()
        html = render_template('getstudents.html', students=students)

        # html = ""
        # for row in students:
        #     html += str(row) + "<br>"
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response
