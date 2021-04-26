from flask import Flask, request, make_response, redirect, url_for, session, flash
from flask import render_template
from flask_talisman import Talisman
from datetime import datetime, timezone, timedelta
# from tzlocal import get_localzone
# import pytz
import json

from .database import Database
from .matching import Matching
from . import loginutil
from .keychain import KeyChain
from .admin import admin
from .action import emailUser, confirmDeletion

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
        propic = session['picture']
        zipcode = acct_info.get('zipcode', '')
        industry = acct_info.getlist('industry')
        interests = acct_info.getlist('interests')
        user = [profileid, name, classyear, email, major,
                zipcode, nummatches, propic, industry, interests]

        db = Database()
        db.connect()

        if role == 'student':
            db.create_students([user])
        else:
            db.create_alumni([user])

        db.disconnect()

        emailUser(str(email), str(name), str(role), str(classyear))

    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    return redirect(url_for('timeline', firstLogin='True'))


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
            for i in range(0, len(interests)):
                interests[i] = interests[i][0]
        is_admin = db.get_admin(profileid)
        db.disconnect()

        html = render_template(
            'createpost.html', picture=session['picture'], interests=interests, is_admin=is_admin)
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

        # store date and time in UTC (convert on client side)
        # store in UTC, convert on client side
        currDate = datetime.utcnow().isoformat()
        # currDate = str(datetime.now())

        db.create_post(str(profileid), str(name), str(currDate), str(title),
                       str(content), str(imgurl), str(private), json.dumps(communities), str(session['picture']))
        db.disconnect()
        return redirect('/timeline')
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        return make_response(html)

    return html


@app.route('/displaymatches', methods=['GET'])
def getmatches():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        # pull all of the matches that have been created so far (from database)
        db = Database()
        db.connect()
        matches = db.retrieve_matches(profileid)
        is_admin = db.get_admin(profileid)
        db.disconnect()
        html = render_template('displaymatches.html', matches=matches,
                               picture=session['picture'], is_admin=is_admin)
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)

    response = make_response(html)
    return response


@app.route('/studentdetails', methods=['GET'])
def studentdetails():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        db = Database()
        db.connect()
        profileid = request.args.get('profileid')
        student, careers, interests = db.get_student_by_id(profileid)
        db.disconnect()

        careers = fix_list_format(careers)
        html = render_template('studentdetails.html', student=student,
                               careers=careers, interests=interests)
        return make_response(html)
    except Exception as e:
        return make_response("An error occurred. Please try again later.")


@app.route('/alumdetails', methods=['GET'])
def alumdetails():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        db = Database()
        db.connect()
        profileid = request.args.get('profileid')
        alum, careers, interests = db.get_alum_by_id(profileid)
        db.disconnect()

        interests = fix_list_format(interests)
        html = render_template('alumdetails.html', alum=alum,
                               careers=careers, interests=interests)
        return make_response(html)
    except Exception as e:
        return make_response("An error occurred. Please try again later.")


@app.route('/genericdetails', methods=['GET'])
def genericdetails():
    if not loginutil.is_logged_in(session):
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    profileid = request.args.get('profileid')

    db = Database()
    db.connect()
    role = db.get_role(profileid)
    db.disconnect()

    try:
        db = Database()
        db.connect()

        if role == 'alum':
            profileid = request.args.get('profileid')
            alum, careers, interests = db.get_alum_by_id(profileid)
            db.disconnect()

            interests = fix_list_format(interests)
            html = render_template('alumdetails.html', alum=alum,
                                   careers=careers, interests=interests)
            return make_response(html)

        else:
            profileid = request.args.get('profileid')
            student, careers, interests = db.get_student_by_id(profileid)
            db.disconnect()

            careers = fix_list_format(careers)
            html = render_template('studentdetails.html', student=student,
                                   careers=careers, interests=interests)
            return make_response(html)

    except Exception as e:
        return make_response("An error occurred. Please try again later.")


def checkOverlap(element, list):
    if element in list:
        return "<strong>" + str(element) + "</strong>"
    return str(element)

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

        joint_careers = [
            value for value in student_careers if value in alum_careers]
        joint_interests = [
            value for value in student_interests if value in alum_interests]

        majorSame = False
        if student_info[3] == alum_info[3]:
            majorSame = True

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

        if i == 0:
            html += "<td ><strong>Name:</strong></td>"
        elif i == 1:
            html += "<td><strong>Class Year:</strong></td>"
        elif i == 2:
            html += "<td><strong>Email:</strong></td>"
        elif i == 3:
            html += "<td><strong>Major:</strong></td>"
        elif i == 4:
            html += "<td><strong>Zip Code:</strong></td>"
        elif i == 5:
            html += "<td><strong>Careers:</strong></td>"
        elif i == 6:
            html += "<td><strong>Groups:</strong></td>"

        if (i <= 4):
            if i == 3 and majorSame:
                html += '<td><strong>' + student_info[i] + '</strong></td>'
                html += '<td><strong>' + alum_info[i] + '</strong></td>'
            else:
                html += '<td>' + student_info[i] + '</td>'
                html += '<td>' + alum_info[i] + '</td>'
        elif i == 5:
            stud_temp = ""
            alum_temp = ""

            for m in range(len(student_careers)-1):
                stud_temp += checkOverlap(student_careers[m], joint_careers)
                stud_temp += ", "
            stud_temp += checkOverlap(student_careers[-1], joint_careers)

            for n in range(len(alum_careers)-1):
                alum_temp += checkOverlap(alum_careers[n], joint_careers)
                alum_temp += ", "
            alum_temp += checkOverlap(alum_careers[-1], joint_careers)

            html += '<td>' + stud_temp + '</td>'
            html += '<td>' + alum_temp + '</td>'

        elif i == 6:
            stud_temp = ""
            alum_temp = ""

            if student_interests:
                for m in range(len(student_interests)-1):
                    stud_temp += checkOverlap(
                        student_interests[m], joint_interests)
                    stud_temp += ", "
                stud_temp += checkOverlap(
                    student_interests[-1], joint_interests)

            if alum_interests:
                for n in range(len(alum_interests)-1):
                    alum_temp += checkOverlap(
                        alum_interests[n], joint_interests)
                    alum_temp += ", "
                alum_temp += checkOverlap(alum_interests[-1], joint_interests)

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
        is_admin = db.get_admin(profileid)
        db.disconnect()
        print(info)
        print(careers)
        print(interests)
        html = render_template('editprofile.html', info=info,
                               careers=careers, interests=interests, picture=session['picture'], role=role, is_admin=is_admin)

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
        careers = acct_info.getlist('career')
        interests = acct_info.getlist('interests')

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
        flash("Your profile has been updated successfully.")
        # reload the editprofile page
        # db = Database()
        # db.connect()
        # info = db.get_student_by_id(profileid)
        # db.disconnect()
        # return redirect(url_for('editprofile', info=info))
    except Exception as e:
        html = "error occurred: " + str(e)
        print(e)
        response = make_response(html)
        return response

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
    try:
        name = request.args.get('namesearch', '%')
        email = request.args.get('email-address', '%')
        major = request.args.get('major', '%')
        zipcode = request.args.get('zipcode', '%')
        career = request.args.getlist('industry')
        interest = request.args.getlist('interest')
        search_req = request.args.get('searchreq', '%')
        search_query = [name, email, major,
                        zipcode, career, interest, search_req]
        # database queries
        db = Database()
        db.connect()
        results = db.search(search_query)
        is_admin = db.get_admin(session['profileid'])
        db.disconnect()
        html = render_template(
            'search.html', results=results, picture=session['picture'],
            is_admin=is_admin)

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

    db = Database()
    db.connect()
    is_admin = db.get_admin(profileid)
    db.disconnect()

    html = render_template('dosearch.html', picture=session['picture'],
                           is_admin=is_admin)
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
    is_admin = db.get_admin(profileid)
    info, careers, interests = None, None, None
    if role == 'student':
        info, careers, interests = db.get_student_by_id(profileid)
    elif role == 'alum':
        info, careers, interests = db.get_alum_by_id(profileid)
        for i in range(0, len(interests)):
            interests[i] = interests[i][0]

    posts = []
    output = db.get_posts()

    # FIXME: need to pass in user time zone from JS (right now offset doesn't exist)
    offset = int(request.args.get('offset', 240))
    for i in output:
        curr_time = datetime.fromisoformat(i[3])
        # local_tz = get_localzone()
        curr_time = curr_time - timedelta(minutes=offset)
        # curr_time = curr_time.replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
        formatted_time = curr_time.strftime("%A, %B %d at %I:%M %p")

        copy = i[:3] + (formatted_time,) + i[4:]
        if (role == i[7]):
            posts.append(copy)
        elif (i[7] == 'private'):
            if not set(interests).isdisjoint(set(json.loads(i[8]))):
                posts.append(copy)
        elif (i[7] == 'everyone'):
            posts.append(copy)

    db.disconnect()
    html = render_template('timeline.html', posts=posts,
                           picture=session['picture'], is_admin=is_admin)
    response = make_response(html)
    return response


@app.route('/delete', methods=['GET'])
def deleteProfile():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    email = session['email']

    db = Database()
    db.connect()
    role = db.get_role(profileid)

    if role == 'student':
        db.delete_student(profileid)
    else:
        db.delete_alum(profileid)

    db.disconnect()

    confirmDeletion(str(email))

    html = render_template('delete.html')
    response = make_response(html)
    return response
    
@app.errorhandler(404)
def page_not_found(err):
    if not loginutil.is_logged_in(session):
        # user is not logged in
        return redirect('/login')
    
    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')
        
    html = render_template('404.html', picture=session['picture'])
    return make_response(html)
