from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template
from flask_talisman import Talisman
import datetime
import json

from .database import Database
from .matching import Matching
from .cookiemonster import CookieMonster
from . import loginutil
from .keychain import KeyChain
from .admin import admin

keychain = KeyChain()
app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
app.secret_key = keychain.FLASK_SECRET
login_manager = loginutil.GoogleLogin(keychain)

# for forcing HTTPS and adding other security features
# CSP is disabled cause it messes with bootstrap
Talisman(app, content_security_policy=None)


# add other blueprints
app.register_blueprint(admin)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    if not loginutil.is_logged_in(session):
        # user is not logged in
        return redirect('/login')

    profileid = session['profileid']
    if user_exists(profileid):
        return redirect('/timeline')

    name = session['fullname']

    html = render_template('index.html', name=name)
    response = make_response(html)
    return response

# Note: when testing locally, must use port 8888 for Google SSO
# general welcome/login page


@app.route('/login', methods=['GET'])
def login():
    if loginutil.is_logged_in(session):
        # no need to be here
        return redirect('/index')

    html = render_template('login.html')
    response = make_response(html)
    return response

# Note: when testing locally, must use port 8888 for Google SSO


@app.route('/login/redirect', methods=['GET'])
def login_redirect():
    # redirect the user to Google's login page
    request_uri = login_manager.get_login_redirect(request)
    return redirect(request_uri)


def user_exists(profileid):
    db = Database()
    db.connect()
    does_user_exist = db.user_exists(profileid)
    db.disconnect()
    return does_user_exist

# for checking if user exists already, setting a session cookie,
# and redirecting to the next page


@app.route('/login/auth', methods=['GET'])
def login_auth():
    try:
        profileid, email, fullname, picture = login_manager.authorize(request)

        # set session!
        session['profileid'] = profileid
        session['email'] = email
        session['fullname'] = fullname
        session['picture'] = picture

        # check where to redirect user
        if user_exists(profileid):
            return redirect('/timeline')
        else:
            return redirect('/index')

    except Exception as e:
        return make_response('Failed to login: ' + str(e))


@app.route('/logout', methods=['GET'])
def logout():
    # simply clear the user's session
    session.pop('profileid', None)
    session.pop('email', None)
    session.pop('fullname', None)
    session.pop('picture', None)

    return redirect('/')


@app.route('/createuser', methods=['POST'])
def createuser():
    try:
        acct_info = request.form

        if session.get('profileid') is None:
            return redirect('/index')

        name = session['fullname']
        profileid = session['profileid']
        email = session['email']
        role = acct_info.get('role', '')
        major = acct_info.get('major', '')
        classyear = acct_info.get('classYear', '')
        nummatches = acct_info.get('numMatches', '')
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.getlist('industry')
        interests = acct_info.getlist('interests')
        user = [profileid, name, classyear, email, major,
                zipcode, nummatches, industry, interests]

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

    return redirect(url_for('timeline'))


@app.route('/loadpost', methods=['GET'])
def loadpost():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        db = Database()
        db.connect()
        role = db.get_role(profileid)

        info, careers, interests = None, None, None
        print(role)
        if role == 'student':
            info, careers, interests = db.get_student_by_id(profileid)
        elif role == 'alum':
            info, careers, interests = db.get_alum_by_id(profileid)
        db.disconnect()

        html = render_template(
            'createpost.html', picture=session['picture'], interests=interests)
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    return html


@app.route('/createpost', methods=['POST'])
def createpost():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        acct_info = request.form

        title = acct_info.get('title', '')
        content = acct_info.get('content', '')
        email = acct_info.get('email', '')
        private = acct_info.get('role', '')
        communities = acct_info.getlist(
            'communities')  # FIXME: verify this works
        imgurl = acct_info.get('imgurl', '')

        db = Database()
        db.connect()
        profileid = session['profileid']
        role = db.get_role(profileid)

        info, careers, interests = None, None, None
        print("role: " + str(role))
        if role == 'student':
            info, careers, interests = db.get_student_by_id(profileid)
        elif role == 'alum':
            info, careers, interests = db.get_alum_by_id(profileid)

        # info[0] is the author name
        name = info[0]
        currDate = str(datetime.datetime.now())

    # def create_post(self, authorId, authorName, time, title, content, image_url, private, communities):

        db.create_post(str(profileid), str(name), str(currDate), str(title),
                       str(content), str(imgurl), str(private), json.dumps(communities))
        db.disconnect()
        return redirect('/timeline')
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    return html

# TODO: remove this page (currently for debugging only)


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
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        # creates matches from matching.py file. returns a list of tuples.
        m = Matching()
        matches = m.match()
        html = render_template('displaymatches.html', matches=matches,
                               picture=session['picture'])
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response

# input (from get request): studentid, alumid


@app.route('/matchdetails', methods=['GET'])
def matchdetails():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        # retrieve information about matches
        db = Database()
        db.connect()
        student = request.args.get('student')
        alum = request.args.get('alum')
        student_info, student_careers, student_interests = db.get_student_by_id(
            student)

        # student_careers is being returned as a list of tuples
        # this block fixes that
        student_careers = fix_list_format(student_careers)

        alum_info, alum_careers, alum_interests = db.get_alum_by_id(alum)
        # alum_interests is being returned as a list of tuples
        # this block fixes that
        alum_interests = fix_list_format(alum_interests)

    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    html = "<table class='table'>"
    # print(student_careers)

    html += "<thead>"
    html += "<tr>\
                    <td style='width: 20%'><strong>MATCH INFO</strong></td>\
                    <td style='width: 40%'><strong>Student Info</strong></td>\
                    <td style='width: 40%'><strong>Alum Info</strong></td>\
                </tr>"
    html += "</thead>"
    html += "<tbody>"

    for i in range(len(student_info)+1):
        html += "<tr>"

        if i is 0:
            html += "<td ><strong>Name:</strong></td>"
        elif i is 1:
            html += "<td><strong>Class Year:</strong></td>"
        elif i is 2:
            html += "<td><strong>Email:</strong></td>"
        elif i is 3:
            html += "<td><strong>Major:</strong></td>"
        elif i is 4:
            html += "<td><strong>Zip Code:</strong></td>"
        elif i is 5:
            html += "<td><strong>Careers:</strong></td>"
        elif i is 6:
            html += "<td><strong>Groups:</strong></td>"

        if (i <= 4):
            html += '<td>' + student_info[i] + '</td>'
            html += '<td>' + alum_info[i] + '</td>'
        elif i is 5:
            stud_temp = ""
            alum_temp = ""

            for m in range(len(student_careers)-1):
                stud_temp += student_careers[m]
                stud_temp += ", "
            stud_temp += student_careers[-1]

            for n in range(len(alum_careers)-1):
                alum_temp += alum_careers[n]
                alum_temp += ", "
            alum_temp += alum_careers[-1]

            html += '<td>' + stud_temp + '</td>'
            html += '<td>' + alum_temp + '</td>'

        elif i is 6:
            stud_temp = ""
            alum_temp = ""

            for m in range(len(student_interests)-1):
                stud_temp += student_interests[m]
                stud_temp += ", "
            stud_temp += student_interests[-1]

            for n in range(len(alum_interests)-1):
                alum_temp += alum_interests[n]
                alum_temp += ", "
            alum_temp += alum_interests[-1]

            html += '<td>' + stud_temp + '</td>'
            html += '<td>' + alum_temp + '</td>'

        html += "</tr>"

    html += "</tbody>"
    html += "</table>"

    # html = render_template('displaymatches.html', student_info=student_info,
    #                      student_careers=student_careers, student_interests=student_interests,
    #                     alum_info=alum_info, alum_careers=alum_careers, alum_interests=alum_interests)
    # TODO: incorporate careers/interests
    response = make_response(html)
    return response


@app.route('/editprofile', methods=['GET'])
def getprofile():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        db = Database()
        db.connect()
        role = db.get_role(profileid)

        info, careers, interests = None, None, None
        print(role)
        if role == 'student':
            info, careers, interests = db.get_student_by_id(profileid)
            careers = fix_list_format(careers)
        elif role == 'alum':
            info, careers, interests = db.get_alum_by_id(profileid)
            interests = fix_list_format(interests)
        db.disconnect()
        print(info)
        print(careers)
        print(interests)
        html = render_template('editprofile.html', info=info,
                               careers=careers, interests=interests, picture=session['picture'], role=role)

    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response

# method to fix formatting of returned lists


def fix_list_format(thisList):
    for i in range(len(thisList)):
        thisList[i] = thisList[i][0]
    return thisList

# updates profile on save click


@app.route('/updateprofile', methods=['POST'])
def changeprofile():
    try:
        profileid = session['profileid']
        # first update the entry in the database
        # contents of array must be array of [name, classyear, email, major,
        # zip, nummatch, career]
        acct_info = request.form

        name = acct_info.get('name', '')
        classyear = acct_info.get('classYear', '')
        email = acct_info.get('email', '')
        major = acct_info.get('major', '')
        zipcode = acct_info.get('zipcode', '')
        nummatches = acct_info.get('numMatches', '')
        careers = acct_info.getlist('career')  # FIXME: verify this works
        interests = acct_info.getlist('interests')  # FIXME: verify this works

        new_info = [name, classyear,
                    email, major, zipcode, nummatches]

        db = Database()
        db.connect()
        role = db.get_role(profileid)
        if role == 'student':
            db.update_student(profileid, new_info, careers, interests)
        elif role == 'alum':
            db.update_alum(profileid, new_info, careers, interests)

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
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    search_query = None
    search_form = None
    try:
        name = request.args.get('namesearch', '%')
        email = request.args.get('email-address', '%')
        major = request.args.get('major', '%')
        zipcode = request.args.get('zipcode', '%')
        career = request.args.getlist('industry')
        search_req = request.args.get('student', '%')
        search_query = [name, email, major, zipcode, career, search_req]
        # database queries
        db = Database()
        db.connect()
        # FIXME: db.search() will take search_query and two booleans (student and alumni)
        results = db.search(search_query)
        db.disconnect()
        html = render_template(
            'search.html', results=results, picture=session['picture'])

    except Exception as e:
        html = str(search_query)
        print(e)

    response = make_response(html)
    return response


@app.route('/dosearch', methods=['GET'])
def dosearch():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    html = render_template('dosearch.html', picture=session['picture'])
    response = make_response(html)
    return response


@app.route('/timeline', methods=['GET'])
def timeline():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    db = Database()
    db.connect()

    role = str(db.get_role(profileid))
    info, careers, interests = None, None, None
    if role == 'student':
        info, careers, interests = db.get_student_by_id(profileid)
    elif role == 'alum':
        info, careers, interests = db.get_alum_by_id(profileid)

    posts = []
    output = db.get_posts()
    for i in output:
        if (role == i[7]):
            posts.append(i)
        elif (i[7] == 'private'):
            if not set(interests).isdisjoint(set(json.loads(i[8]))):
                posts.append(i)
        elif (i[7] == 'everyone'):
            posts.append(i)

    db.disconnect()
    html = render_template('timeline.html', posts=posts,
                           picture=session['picture'])
    response = make_response(html)
    return response


@app.route('/groups', methods=['GET'])
def groups():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    html = render_template('groups.html', picture=session['picture'])
    response = make_response(html)
    return response
