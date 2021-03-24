from flask import Flask, request, make_response, redirect
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

@app.route('/createstudent', methods=['GET'])
def index():
    try:
        userid = request.args.get('userid', '')
        firstname = request.args.get('firstname', '')
        lastname = request.args.get('lastname', '')
        db = Database()
        db.connect()
        db.create_student()
        db.disconnect()
        html = f"user {firstname} {lastname} created successfully!"
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
    
    response = make_response(html)
    return response

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
