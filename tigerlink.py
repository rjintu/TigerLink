from os import environ
from flask import Flask, request, make_response, redirect
from flask import render_template

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
def index():
    html = "hello, world! <br>"
    html += environ.get('DATABASE_URL')
    response = make_response(html)
    return response
