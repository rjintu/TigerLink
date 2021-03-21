from flask import Flask, request, make_response, redirect
from flask import render_template

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
def index():
    html = "hello, world!"
    response = make_response(html)
    return response
