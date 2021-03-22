from flask import Flask, request, make_response, redirect
from flask import render_template

from database import Database

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
def index():
    try:
        db = Database()
        db.connect()
        db.create_students()
        db.disconnect()
        html = "database ran successfully!"
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

        html = ""
        for row in students:
            html += str(row) + "<br>"
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response
