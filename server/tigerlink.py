from flask import Flask, request, make_response, redirect, url_for, session, flash, abort
from flask import render_template
from flask_talisman import Talisman
from datetime import datetime, timezone, timedelta
import json
from sys import stderr

from .database import Database
from .matching import Matching
from . import loginutil
from .keychain import KeyChain
from .adminrouter import admin
from .loginrouter import login
from .action import emailUser, confirmDeletion
from .student import Student
from .alum import Alum

keychain = KeyChain()
app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
app.secret_key = keychain.FLASK_SECRET

# for forcing HTTPS and adding other security features
# CSP is disabled cause it messes with bootstrap
Talisman(app, content_security_policy=None)

# add other blueprints
app.register_blueprint(admin)
app.register_blueprint(login)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    if not loginutil.is_logged_in(session):
        # user is not logged in
        return redirect('/login')

    profileid = session['profileid']
    if user_exists(profileid):
        return redirect('/timeline')

    try:
        name = session['fullname']
        html = render_template('index.html', name=name)
        response = make_response(html)
        return response
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)

@app.route('/about', methods=['GET'])
def about():
    if loginutil.is_logged_in(session):
        # no need to be here
        return redirect('/index')
    try:
        html = render_template('about.html')
        response = make_response(html)
        return response
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)

# for checking if user exists already, setting a session cookie,
# and redirecting to the next page
def user_exists(profileid):
    db = Database()
    db.connect()
    does_user_exist = db.user_exists(profileid)
    db.disconnect()
    return does_user_exist

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
        year = acct_info.get('classYear', '')
        nummatches = acct_info.get('numMatches', '')
        propic = session['picture']
        zipcode = acct_info.get('zipcode', '')
        careers = acct_info.getlist('industry')
        communities = acct_info.getlist('interests')
        # user = [profileid, name, classyear, email, major, zipcode, nummatches, propic, industry, interests]
        user = None

        db = Database()
        db.connect()

        if role == 'student':
            user = Student(profileid, name, year, email, major, zipcode, nummatches, propic, careers=careers, communities=communities)
            db.create_students([user])
        else:
            user = Alum(profileid, name, year, email, major, zipcode, nummatches, propic, careers=careers, communities=communities)
            db.create_alumni([user])

        db.disconnect()

        emailUser(str(email), str(name), str(role), str(year))

    except Exception as e:
        print(e, file=stderr)
        abort(500)

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

        user = None
        if role == 'student':
            user = db.get_student_by_id(profileid)
        elif role == 'alum':
            user = db.get_alum_by_id(profileid)

        is_admin = db.get_admin(profileid)
        db.disconnect()

        html = render_template(
            'createpost.html', picture=session['picture'], communities=user._communities, is_admin=is_admin)
        response = make_response(html)
        return response
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)


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
        private = acct_info.get('role', '')
        communities = acct_info.getlist(
            'communities')
        imgurl = acct_info.get('imgurl', '')
        tags = acct_info.getlist('tags')
        print("tags: ")
        print(tags)
        db = Database()
        db.connect()
        profileid = session['profileid']
        role = db.get_role(profileid)

        user = None

        if role == 'student':
            user = db.get_student_by_id(profileid)
        elif role == 'alum':
            user = db.get_alum_by_id(profileid)

        name = user._name

        # store date and time in UTC (convert on client side)
        # store in UTC, convert on client side
        currDate = datetime.utcnow().isoformat()
        # currDate = str(datetime.now())

        db.create_post(str(profileid), str(name), str(currDate), str(title),
                    str(content), str(imgurl), str(private), json.dumps(communities), str(session['picture']), json.dumps(tags))
        db.disconnect()
        return redirect('/timeline')
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)

@app.route('/reportpost', methods=['POST'])
def reportpost():
    postid = request.form['postid']
    profileid = session['profileid']
    db = Database()
    db.connect()

    db.report_post(postid, profileid)
    db.disconnect()

    response = make_response('success!')
    return response

@app.route('/deletepost', methods=['POST'])
def deletepost():
    postid = request.form['postid']
    profileid = session['profileid']

    db = Database()
    db.connect()

    if db.verify_post_author(postid, profileid):
        db.delete_post(postid)
    db.disconnect()

    response = make_response('success!')
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
        # pull all of the matches that have been created so far (from database)
        db = Database()
        db.connect()
        matches = db.retrieve_matches(profileid)
        is_admin = db.get_admin(profileid)
        db.disconnect()
        html = render_template('displaymatches.html', matches=matches,
                            picture=session['picture'], is_admin=is_admin)   
        response = make_response(html)
        return response
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)

# modal component
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
        student = db.get_student_by_id(profileid)
        db.disconnect()

        html = render_template('studentdetails.html', student=student)
        return make_response(html)
    
    except Exception as e:
        print(e, file=stderr)
        return make_response("An error occurred. Please try again later.")

# modal component
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
        alum = db.get_alum_by_id(profileid)
        db.disconnect()

        html = render_template('alumdetails.html', alum=alum)
        return make_response(html)
    
    except Exception as e:
        print(e, file=stderr)
        return make_response("An error occurred. Please try again later.")

# modal component
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
            alum = db.get_alum_by_id(profileid)
            db.disconnect()

            html = render_template('alumdetails.html', alum=alum)
            return make_response(html)

        else:
            profileid = request.args.get('profileid')
            student = db.get_student_by_id(profileid)
            db.disconnect()

            html = render_template('studentdetails.html', student=student)
            return make_response(html)

    except Exception as e:
        print(e, file=stderr)
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
        role = db.get_role(profileid)
        is_admin = db.get_admin(profileid)
        student_match = request.args.get('student')
        alum_match = request.args.get('alum')
        student = db.get_student_by_id(student_match)
        alum = db.get_alum_by_id(alum_match)
        db.disconnect()

        joint_careers = [
            value for value in student._careers if value in alum._careers]
        joint_communities = [
            value for value in student._communities if value in alum._communities]

        majorSame = student._major == alum._major # TODO: check the style?

        html = "<table class='table'>"

        html += "<thead>"
        html += "<tr>\
                        <td style='width: 20%'><strong></strong></td>\
                        <td style='width: 40%'><strong>Student</strong></td>\
                        <td style='width: 40%'><strong>Alum</strong></td>\
                    </tr>"
        html += "</thead>"
        html += "<tbody>"

        # name
        html += '<tr>'
        html += '<td ><strong>Name:</strong></td>'
        html += '<td>' + student._name + '</td>'
        html += '<td>' + alum._name + '</td>'
        html += '</tr>'

        # class year
        html += '<tr>'
        html += '<td><strong>Class Year:</strong></td>'
        html += '<td>' + student._year + '</td>'
        html += '<td>' + alum._year + '</td>'
        html += '</tr>'

        # email
        html += '<tr>'
        html += '<td><strong>Email:</strong></td>'

        if not is_admin:
            if role == 'alum':
                html += '<td> <a href = \"mailto: ' + student._email + '\">' + student._email + '</a></td>' #hyperlink
                html += '<td>' + alum._email + '</td>'
            else:
                html += '<td>' + student._email + '</td>'
                html += '<td> <a href = \"mailto: ' + alum._email + '\">' + alum._email + '</a></td>' # hyperlink
        else:
            html += '<td>' + student._email + '</td>'
            html += '<td>' + student._email + '</td>'

        html += '</tr>'

        # major
        html += '<tr>'
        html += "<td><strong>Major:</strong></td>"
        if majorSame:
            html += '<td><strong>' + student._major + '</strong></td>'
            html += '<td><strong>' + alum._major + '</strong></td>'
        else:
            html += '<td>' + student._major + '</td>'
            html += '<td>' + alum._major + '</td>'
        html += '</tr>'

        # careers
        html += '<tr>'
        html += "<td><strong>Careers:</strong></td>"
        stud_temp, alum_temp = '', ''
        if student._careers:
            for m in range(len(student._careers) - 1):
                stud_temp += checkOverlap(student._careers[m], joint_careers)
                stud_temp += ', '
            stud_temp += checkOverlap(student._careers[-1], joint_careers)

        if alum._careers:
            for n in range(len(alum._careers) - 1):
                alum_temp += checkOverlap(alum._careers[n], joint_careers)
                alum_temp += ', '
            alum_temp += checkOverlap(alum._careers[-1], joint_careers)
        html += '<td>' + stud_temp + '</td>'
        html += '<td>' + alum_temp + '</td>'
        html += '</tr>'

        # communities
        html += '<tr>'
        html += '<td><strong>Communities:</strong></td>'
        stud_temp, alum_temp = '', ''
        if student._communities:
            for m in range(len(student._communities) - 1):
                stud_temp += checkOverlap(student._communities[m], joint_communities)
                stud_temp += ', '
            stud_temp += checkOverlap(student._communities[-1], joint_communities)

        if alum._communities:
            for n in range(len(alum._communities) - 1):
                alum_temp += checkOverlap(alum._communities[n], joint_communities)
                alum_temp += ', '
            alum_temp += checkOverlap(alum._communities[-1], joint_communities)

        html += '<td>' + stud_temp + '</td>'
        html += '<td>' + alum_temp + '</td>'
        html += '</tr>'

        html += '</tbody>'
        html += '</table>'

    except Exception as e:
        print(e, file=stderr)
        return make_response("An error occurred. Please try again later.")
    
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
        
        user = None # will be set to student or alum
        if role == 'student':
            user = db.get_student_by_id(profileid)

        elif role == 'alum':
            user = db.get_alum_by_id(profileid)
        is_admin = db.get_admin(profileid)
        db.disconnect()
        html = render_template('editprofile.html', user=user, picture=session['picture'], role=role, is_admin=is_admin)
        response = make_response(html)
        return response

    except Exception as e:
        print(e, file=stderr)
        abort(500)

# updates profile on save click
@app.route('/updateprofile', methods=['POST'])
def updateprofile():
    try:
        profileid = session['profileid']
        # first update the entry in the database
        # contents of array must be array of [name, classyear, email, major,
        # zip, nummatch, career]
        acct_info = request.form

        name = acct_info.get('name', '')
        year = acct_info.get('classYear', '')
        email = acct_info.get('email', '')
        major = acct_info.get('major', '')
        zipcode = acct_info.get('zipcode', '')
        nummatches = acct_info.get('numMatches', '')
        careers = acct_info.getlist('career')
        communities = acct_info.getlist('interests')

        db = Database()
        db.connect()
        role = db.get_role(profileid)

        if role == 'student':
            student = db.get_student_by_id(profileid)
            student._name = name
            student._year = year
            student._email = email
            student._major = major
            student._zipcode = zipcode
            student._numMatch = nummatches
            student._careers = careers
            student._communities = communities
            db.update_student(student) # use the profileid already in Student object
        elif role == 'alum':
            alum = db.get_alum_by_id(profileid)
            alum._name = name
            alum._year = year
            alum._email = email
            alum._major = major
            alum._zipcode = zipcode
            alum._numMatch = nummatches
            alum._careers = careers
            alum._communities = communities
            db.update_alum(alum) # use the profileid already in Alum object

        db.disconnect()
        flash("Your profile has been updated successfully.", "success")

    except Exception as e:
        print(e, file=stderr)
        flash("There was an issue updating your profile. Please try again later.", "danger")

    return redirect('editprofile')

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

        response = make_response(html)
        return response

    except Exception as e:
        print(e, file=stderr)
        abort(500)

@app.route('/dosearch', methods=['GET'])
def dosearch():
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
        is_admin = db.get_admin(profileid)
        db.disconnect()

        html = render_template('dosearch.html', picture=session['picture'],
                            is_admin=is_admin)
    
        response = make_response(html)
        return response

    except Exception as e:
        print(e, file=stderr)
        abort(500)

@app.route('/timeline', methods=['GET'])
def timeline():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    profileid = session['profileid']
    if not user_exists(profileid):
        # profile has not been created
        return redirect('/index')

    try:
        POSTS_PER_PAGE = 5  # set this to the number of posts to display at any point
        db = Database()
        db.connect()

        role = str(db.get_role(profileid))
        is_admin = db.get_admin(profileid)
        user = None

        if role == 'student':
            user = db.get_student_by_id(profileid)
        elif role == 'alum':
            user = db.get_alum_by_id(profileid)
            # TODO: do I need this part?
            for i in range(0, len(user._communities)):
                user._communities[i] = user._communities[i][0]

        offset = int(request.args.get('offset', 0))

        # don't allow negative offsets
        if offset < 0:
            return redirect('/timeline')

        # ensure offsets always start at set intervals
        if offset % POSTS_PER_PAGE != 0:
            offset = offset // POSTS_PER_PAGE * POSTS_PER_PAGE
            return redirect(f'/timeline?offset={offset}')
        
        # ensure we don't start too high with the offsets
        max_posts = db.get_num_posts()
        # handle case where timeline is empty
        if max_posts is None:
            max_posts = 0

        if offset > int(max_posts):
            return redirect(f'/timeline?offset={max_posts}')

        posts = []
        output = db.get_posts()
        reported_posts = db.get_reports_byprofileid(profileid)

        time_offset = int(request.args.get('time_offset', 240)) # FIXME: need to pass in user time zone from JS (right now offset doesn't exist)
        for i in output:
            curr_time = datetime.fromisoformat(i[3])
            # local_tz = get_localzone()
            curr_time = curr_time - timedelta(minutes=time_offset)
            # curr_time = curr_time.replace(tzinfo=timezone.utc).astimezone(tz=local_tz)
            formatted_time = curr_time.strftime("%A, %B %d at %I:%M %p")

            copy = i[:3] + (formatted_time,) + i[4:8] + (', '.join(json.loads(i[8])),) + i[9:11] + (', '.join(json.loads(i[11])),)
            print(copy)
            if str(copy[0]) in reported_posts:
                continue
            elif copy[1] == profileid or role == i[7]:
                posts.append(copy)
            elif (i[7] == 'private'):
                if not set(user._communities).isdisjoint(set(json.loads(i[8]))):
                    posts.append(copy)
            elif (i[7] == 'everyone'):
                posts.append(copy)            

        # if empty list, means there are no more posts. more_posts is True iff more posts to show.
        more_posts = (posts[offset + POSTS_PER_PAGE:] != [])
        posts = posts[offset:offset+POSTS_PER_PAGE]

        if (len(posts) == 0) and (offset != 0):
            return redirect(f'/timeline?offset={0}')

        db.disconnect()
        html = render_template('timeline.html', posts=posts,
                            picture=session['picture'], profileid=profileid, more_posts=more_posts, is_admin=is_admin)
        response = make_response(html)
        return response

    except Exception as e:
        print(e, file=stderr)
        abort(500)

@app.route('/delete', methods=['POST'])
def deleteProfile():
    if not loginutil.is_logged_in(session):
        # user not logged in
        return redirect('/login')

    try:
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
    
    except Exception as e:
        print(e, file=stderr)
        abort(500)
    
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

@app.errorhandler(500)
def server_error(err):
    html = render_template('servererror.html')
    return make_response(html)
