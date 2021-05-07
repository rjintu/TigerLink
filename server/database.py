from os import environ
from psycopg2 import connect
from .post import Post
from .action import emailUser, confirmDeletion, emailAlumMatch, emailStudentMatch
import os
from sys import stderr

class Database:

    def __init__(self):
        # environment variable in Heroku
        self._url = environ.get('DATABASE_URL')

    # connect to the database
    def connect(self):
        if self._url is None:
            print('Using local database')
            self._connection = connect(host='localhost', port=5432,
                                    user='tigerlink', password='xxx', database='tldata')
        else:
            print('Using deployed database')
            self._connection = connect(self._url, sslmode='require')

    # reset all existing tables
    def init(self):
        cursor = self._connection.cursor()
        # Students table
        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('CREATE TABLE students ' +
                    '(profileid TEXT, name TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, nummatch TEXT, propic TEXT)')
        # Alumni table
        cursor.execute('DROP TABLE IF EXISTS alumni')
        cursor.execute('CREATE TABLE alumni ' +
                    '(profileid TEXT, name TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, nummatch TEXT, propic TEXT)')
        # Roles table
        cursor.execute('DROP TABLE IF EXISTS roles')
        cursor.execute('CREATE TABLE roles ' +
                    '(profileid TEXT, role TEXT, isadmin TEXT)')
        # Careers table
        cursor.execute('DROP TABLE IF EXISTS careers')
        cursor.execute('CREATE TABLE careers ' +
                    '(profileid TEXT, career TEXT)')
        # Interests table
        cursor.execute('DROP TABLE IF EXISTS interests')
        cursor.execute('CREATE TABLE interests ' +
                    '(profileid TEXT, interest TEXT)')
        # Timeline posts tables
        cursor.execute('DROP TABLE IF EXISTS posts')
        cursor.execute('CREATE TABLE posts ' + 
                '(postid SERIAL, authorname TEXT, authorid TEXT, posttime TEXT, posttitle TEXT, postcontent TEXT, imgurl TEXT, privacy TEXT, communities TEXT, propic TEXT)')
        cursor.execute('DROP TABLE IF EXISTS comments')
        cursor.execute('CREATE TABLE comments ' +
                '(postid TEXT, author TEXT, comment TEXT)')
        cursor.execute('DROP TABLE IF EXISTS likes')
        cursor.execute('CREATE TABLE likes ' +
                '(postid TEXT, authorid TEXT)')
        # Matches table
        cursor.execute('DROP TABLE IF EXISTS matches')
        cursor.execute('CREATE TABLE matches ' +
                    '(studentid TEXT, alumid TEXT, similarity TEXT)')

        self._connection.commit()
        cursor.close()
        print('Database reset and initialized successfully')

    # reset all tables holding posts 
    def reset_posts(self):
        cursor = self._connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS posts')
        cursor.execute('CREATE TABLE posts ' + 
                '(postid SERIAL, authorname TEXT, authorid TEXT, posttime TEXT, posttitle TEXT, postcontent TEXT, imgurl TEXT, privacy TEXT, communities TEXT, propic TEXT)')
        cursor.execute('DROP TABLE IF EXISTS comments')
        cursor.execute('CREATE TABLE comments ' +
                '(postid TEXT, author TEXT, comment TEXT)')
        cursor.execute('DROP TABLE IF EXISTS likes')
        cursor.execute('CREATE TABLE likes ' +
                '(postid TEXT, authorid TEXT)')

        self._connection.commit()
        cursor.close()

    # add students to database
    # :param students: [profileid, name, classyear, email, major, zipcode, nummatches, propic, industry, interests]
    def create_students(self, students):
        cursor = self._connection.cursor()
        for student in students:
            self._add_student(cursor, student)
        self._connection.commit()

        cursor.close()

    # add alumni to database
    # :param alumni: [profileid, name, classyear, email, major, zipcode, nummatches, propic, industry, interests]
    def create_alumni(self, alumni):
        cursor = self._connection.cursor()
        for alum in alumni:
            self._add_alum(cursor, alum)
        self._connection.commit()

        cursor.close()

    # helper method to add individual student to database
    def _add_student(self, cursor, student):
        student_elems = student[:-2]
        # convert everything to strings
        student_elems = [str(x) for x in student_elems]
        profileid = student_elems[0]
        industry = student[-2]
        interests = student[-1]
        cursor.execute('INSERT INTO roles(profileid, role, isadmin) ' +
                    'VALUES (%s, %s, %s)', [profileid, 'student', 'false'])
        cursor.execute('INSERT INTO students(profileid, name, classyear, email, ' +
                    'major, zip, nummatch, propic) ' +
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', student_elems)
        for elem in industry:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                        'VALUES (%s, %s)', [student[0], elem])

        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                        'VALUES (%s, %s)', [student[0], elem])

    # helper method to add individual alum to database
    def _add_alum(self, cursor, alum):
        alum_elems = alum[:-2]
        # convert everything to strings
        alum_elems = [str(x) for x in alum_elems]
        profileid = alum_elems[0]
        industry = alum[-2]
        interests = alum[-1]
        cursor.execute('INSERT INTO roles(profileid, role, isadmin) ' +
                    'VALUES (%s, %s, %s)', [profileid, 'alum', 'false'])
        cursor.execute('INSERT INTO alumni(profileid, name, classyear, email, ' +
                    'major, zip, nummatch, propic) ' +
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', alum_elems)
        for elem in industry:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                        'VALUES (%s, %s)', (alum[0], elem))
        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                        'VALUES (%s, %s)', (alum[0], elem))

    # delete student from database
    # :param profileid: unique id of user
    def delete_student(self, profileid):
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM students WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM roles WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM careers WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM interests WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM matches WHERE studentid=%s', [profileid])
        cursor.execute('DELETE FROM posts WHERE authorid=%s', [profileid])
        self._connection.commit()
        cursor.close()

    # delete alum from database
    # :param profileid: unique id of user
    def delete_alum(self, profileid):
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM alumni WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM roles WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM careers WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM interests WHERE profileid=%s', [profileid])
        cursor.execute('DELETE FROM matches WHERE alumid=%s', [profileid])
        cursor.execute('DELETE FROM posts WHERE authorid=%s', [profileid])
        self._connection.commit()
        cursor.close()

    # get all students from the database
    def get_students(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid, name, classyear, email, \
        major, zip, nummatch, propic FROM students')
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        cursor.execute('SELECT profileid, career FROM careers')
        row = cursor.fetchone()
        careers = []
        while row is not None:
            careers.append(row)
            row = cursor.fetchone()

        cursor.execute('SELECT profileid, interest FROM interests')
        row = cursor.fetchone()
        interests = []
        while row is not None:
            interests.append(row)
            row = cursor.fetchone()

        cursor.close()
        return output, careers, interests

    # get all alumni from the database
    def get_alumni(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid, name, classyear, email, \
        major, zip, nummatch, propic FROM alumni')
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        cursor.execute('SELECT profileid, career FROM careers')
        row = cursor.fetchone()
        careers = []
        while row is not None:
            careers.append(row)
            row = cursor.fetchone()

        cursor.execute('SELECT profileid, interest FROM interests')
        row = cursor.fetchone()
        interests = []
        while row is not None:
            interests.append(row)
            row = cursor.fetchone()

        cursor.close()
        return output, careers, interests

    # gets information about a specific student
    # :param profileid: unique user id
    # outputs info (list), careers (list), interests (list)
    def get_student_by_id(self, profileid):
        profileid = str(profileid)
        cursor = self._connection.cursor()
        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                    'nummatch, propic FROM students WHERE profileid=%s', [profileid])
        info = cursor.fetchone() # info = [name, classyear, email, major zip, nummatch, propic]

        # getting this user's career interests
        cursor.execute(
            'SELECT career FROM careers WHERE profileid=%s', [profileid])
        temp = cursor.fetchone()
        careers = []
        while temp is not None:
            careers.append(temp)
            temp = cursor.fetchone()

        # getting this user's groups
        cursor.execute(
            'SELECT interest FROM interests WHERE profileid=%s', [profileid])
        temp = cursor.fetchone()
        interests = []
        while temp is not None:
            interests.append(temp[0])
            temp = cursor.fetchone()

        cursor.close()
        return info, careers, interests

    # gets information about a specific alum
    # :param profileid: unique user id
    # outputs info (list), careers (list), interests (list)
    def get_alum_by_id(self, profileid):
        profileid = str(profileid)
        cursor = self._connection.cursor()
        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                    'nummatch, propic FROM alumni WHERE profileid=%s', [profileid])
        info = cursor.fetchone()

        # getting this user's career interests
        cursor.execute(
            'SELECT career FROM careers WHERE profileid=%s', [profileid])
        temp = cursor.fetchone()
        careers = []
        while temp is not None:
            careers.append(temp[0])
            temp = cursor.fetchone()

        # getting this user's groups
        cursor.execute(
            'SELECT interest FROM interests WHERE profileid=%s', [profileid])
        temp = cursor.fetchone()
        interests = []
        while temp is not None:
            interests.append(temp)
            temp = cursor.fetchone()

        cursor.close()
        return info, careers, interests

    # utility function for looking up a user by their email
    # :param email: email address of user
    # outputs profileid of user
    def get_profileid_by_email(self, email):
        email = str(email)

        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid FROM students WHERE email=%s', [email])
        profileid = cursor.fetchone()
        if profileid is None:
            cursor.execute('SELECT profileid FROM alumni WHERE email=%s', [email])
            profileid = cursor.fetchone()
            if profileid is None:
                return None
        return profileid[0]

    # gets the role of the user
    # :param profileid: unique id of user
    # outputs student or alum, or None if the user is not in the database
    def get_role(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute(
            'SELECT role FROM roles WHERE profileid=%s', [profileid])
        role = cursor.fetchone()
        cursor.close()
        return None if role is None else role[0]

    # change a user between student and alum
    # warning: using this function will also eliminate all matches associated with the user
    # TODO: verify this is fully operational!
    def set_role(self, profileid, newrole):
        profileid = str(profileid)

        oldrole = self.get_role(profileid)

        # new role and old role are the same
        if newrole == oldrole:
            return

        # catch issues where client passes an invalid role
        if newrole != 'student' and newrole != 'alum':
            print('Invalid role', file=stderr)
            return 
        
        cursor = self._connection.cursor()
        # if student, delete from students and matches
        if oldrole == 'student' and newrole == 'alum':
            # fetch information
            cursor.execute('SELECT profileid, name, classyear, email, major, zip, ' +
                            'nummatch, propic FROM students WHERE profileid=%s', [profileid])
            info = cursor.fetchone()

            # delete from students and matches
            cursor.execute('DELETE FROM students WHERE profileid=%s', [profileid])
            cursor.execute('DELETE FROM matches WHERE studentid=%s', [profileid])

            # add to alumni
            cursor.execute('INSERT INTO alumni(profileid, name, classyear, email, ' +
                        'major, zip, nummatch, propic) ' +
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', info)

        # if alum, delete from students and alum
        elif oldrole == 'alum' and newrole == 'student':
            # fetch information
            cursor.execute('SELECT profileid, name, classyear, email, major, zip, ' +
                        'nummatch, propic FROM students WHERE profileid=%s', [profileid])
            info = cursor.fetchone()

            # delete from alumni and matches
            cursor.execute('DELETE FROM alumni WHERE profileid=%s', [profileid])
            cursor.execute('DELETE FROM matches WHERE alumid=%s', [profileid])

            # add to students
            cursor.execute('INSERT INTO students(profileid, name, classyear, email, ' +
                        'major, zip, nummatch, propic) ' +
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', info)

        # update the role
        cursor.execute('UPDATE roles SET role=%s WHERE profileid=%s', [newrole, profileid])
        cursor.close()
        self._connection.commit()

    # returns whether the user is an admin or not
    # :param profileid: unique id of user
    # outputs a boolean value
    def get_admin(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute('SELECT isadmin FROM roles WHERE profileid=%s', [profileid])
        isadmin = cursor.fetchone()
        cursor.close()
        return False if isadmin is None else isadmin[0] == 'true'

    # promotes/demotes a user to be an admin/non-admin
    # :param profileid: unique id of user
    # :param is_admin: boolean flag for whether the user should be set as an admin or not
    def set_admin(self, profileid, is_admin):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        if is_admin:
            cursor.execute('UPDATE roles SET isadmin=%s WHERE profileid=%s', ['true', profileid])
        else:
            cursor.execute('UPDATE roles SET isadmin=%s WHERE profileid=%s', ['false', profileid])
        cursor.close()
        self._connection.commit()

    # returns True if user exists, False otherwise
    # :param profileid: unique id of user
    def user_exists(self, profileid):
        return self.get_role(profileid) is not None

    
    # updates a student entry in the database
    # :param profileid: unique id of user
    # :param info: [name, classyear, email, major, zip, nummatch]
    # :param careers: [[profileid, career1], [profileid, career2]]
    # :param interests: [[profileid, interest1], [profileid, interest2]]
    def update_student(self, profileid, info, careers, interests):
        cursor = self._connection.cursor()
        args = info.copy()  # dont modify list given to us
        args.append(profileid)
        args = [str(x) for x in args]  # just convert everything to strings
        cursor.execute('UPDATE students SET name=%s, ' +
                    'classyear=%s, email=%s, major=%s, zip=%s, nummatch=%s ' +
                    'WHERE profileid=%s', args)

        # delete previous career entires from database and insert new ones
        cursor.execute('DELETE FROM careers WHERE profileid=%s', [profileid])
        for elem in careers:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                        'VALUES (%s, %s)', [profileid, elem])

        # delete previous interest entires from database and insert new ones
        cursor.execute('DELETE FROM interests WHERE profileid=%s', [profileid])
        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                        'VALUES (%s, %s)', [profileid, elem])

        self._connection.commit()
        cursor.close()

    # updates alum entry in database
    # :param profileid: unique id of user
    # :param info: [name, classyear, email, major, zip, nummatch]
    # :param careers: [[profileid, career1], [profileid, career2]]
    # :param interests: [[profileid, interest1], [profileid, interest2]]
    def update_alum(self, profileid, contents, careers, interests):
        cursor = self._connection.cursor()
        args = contents.copy()  # dont modify list given to us
        args.append(profileid)
        args = [str(x) for x in args]  # just convert everything to strings
        cursor.execute('UPDATE alumni SET name=%s, ' +
                    'classyear=%s, email=%s, major=%s, zip=%s, nummatch=%s ' +
                    'WHERE profileid=%s', args)

        # delete previous career entires from database and insert new ones
        cursor.execute('DELETE FROM careers WHERE profileid=%s', [profileid])
        for elem in careers:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                        'VALUES (%s, %s)', [profileid, elem])

        # delete previous interest entires from database and insert new ones
        cursor.execute('DELETE FROM interests WHERE profileid=%s', [profileid])
        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                        'VALUES (%s, %s)', [profileid, elem])

        self._connection.commit()
        cursor.close()

    def fix_list_format(self, thisList):
        for i in range(len(thisList)):
            thisList[i] = thisList[i][0]
        return thisList


    # helper method to determine if a user's list of careers has any overlap with search query careers
    # if no careers specified (i.e. empty list) or there is overlap, returns True. Otherwise returns False
    # :param cursor: database cursor
    # :param profileid: unique id of user
    # :param careers: list of careers (from search query)
    def _contains_career(self, profileid, careers):
        cursor = self._connection.cursor()
        overlap = False
        stmtStr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
        cursor.execute(stmtStr, [profileid])
        row = cursor.fetchone()
        if (len(careers) != 0):
            while row is not None:
                if (row[1] in careers):
                    overlap = True
                row = cursor.fetchone()
        else:
            overlap = True
        
        return overlap

    # helper method to determine if a user's list of interests has any overlap with search query interests
    # if no interests specified (i.e. empty list) or there is overlap, returns True. Otherwise returns False
    # :param cursor: database cursor
    # :param profileid: unique id of user
    # :param interests: list of interests (from search query)
    def _contains_interest(self, profileid, interests):
        cursor = self._connection.cursor()
        overlap = False
        stmtStr = 'SELECT profileid, interest FROM interests WHERE profileid LIKE %s'
        cursor.execute(stmtStr, [profileid])
        row = cursor.fetchone()
        if (len(interests) != 0):
            while row is not None:
                if (row[1] in interests):
                    overlap = True
                row = cursor.fetchone()
        else:
            overlap = True

        return overlap

    # helper method to search students table
    # returns a cursor pointing to the results from query of students table
    # :param name: search query name
    # :param email: search query email
    # :param major: search query major
    # :param zipcode: search query zipcode
    def _search_students(self, name, email, major, zipcode):
        cursor = self._connection.cursor()
        stmtStr = "SELECT profileid, classyear, name, major, email FROM students WHERE lower(name) LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
        cursor.execute(stmtStr, [name, email, major, zipcode])
        return cursor

    # helper method to search alumni table
    # returns a cursor pointing to the results from query of alumni table
    # :param name: search query name
    # :param email: search query email
    # :param major: search query major
    # :param zipcode: search query zipcode
    def _search_alumni(self, name, email, major, zipcode):
        cursor = self._connection.cursor()
        stmtStr = "SELECT profileid, classyear, name, major, email FROM alumni WHERE lower(name) LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
        cursor.execute(stmtStr, [name, email, major, zipcode])
        return cursor

    # search users based on given queries
    # returns list of users in form [profileid, classyear, name, major, email]
    # :param search_query: list in form [name, email, major, zipcode, career, interest, typeofSearch]
    def search(self, search_query):
        # convert everything to strings
        search_values = [str(x) for x in search_query]
        for i in range(0, len(search_values)):
            if (search_values[i] == ''):
                search_values[i] = '%%%%'
        name, email, major, zipcode, _, _, typeofSearch = search_values
        careers = search_query[-3]
        interests = search_query[-2]
        name = '%%' + name.lower() + '%%'

        output = []
        search_students = typeofSearch in 'stud'
        search_alumni = typeofSearch in 'alum'

        # determine whether to search both student and alumni tables 
        if (typeofSearch not in 'stud' and typeofSearch not in 'alum') or typeofSearch in 'both':
            search_students = True
            search_alumni = True

        if search_students:
            cursor = self._search_students(name, email, major, zipcode)
            row = cursor.fetchone()

            # filter users based on career and interest
            while row is not None:
                profileid = row[0]
                if self._contains_career(profileid, careers) and self._contains_interest(profileid, interests):
                    output.append(row)
                row = cursor.fetchone()

        if search_alumni:
            cursor = self._search_alumni(name, email, major, zipcode)
            row = cursor.fetchone()

            # filter users based on career and interest
            while row is not None:
                profileid = row[0]
                if self._contains_career(profileid, careers) and self._contains_interest(profileid, interests):
                    output.append(row)
                row = cursor.fetchone()

        cursor.close()
        return output

    # returns approximate number of posts in database (based on postid max)
    def get_num_posts(self):
        cursor = self._connection.cursor()

        stmtStr = "SELECT MAX(postid) FROM posts "
        cursor.execute(stmtStr)
        num_posts = cursor.fetchone()[0]

        return num_posts

    # verify that the post author matches the given profileid. Return True if this is the case, False otherwise.
    # :param postid: unique id of post
    # :param profileid: unique id of user
    def verify_post_author(self, postid, profileid):
        cursor = self._connection.cursor()

        stmtStr = "SELECT authorid from posts WHERE postid = %s"
        cursor.execute(stmtStr, [str(postid)])

        row = cursor.fetchone()
        return row[0] == profileid

    # get all posts from the database
    # :param limit: maximum number of posts to query, defaults to None
    # :param offset: offset for posts, defaults to 0
    def get_posts(self, limit=None, offset=0):
        cursor = self._connection.cursor()

        stmtStr = "SELECT postid, authorid, authorname, posttime, posttitle, postcontent, " + \
                  "imgurl, privacy, communities, propic FROM posts "

        if limit:
            stmtStr += "ORDER BY postid DESC OFFSET %s LIMIT %s"
            cursor.execute(stmtStr, [str(offset), str(limit)])
        else:
            cursor.execute(stmtStr)

        row = cursor.fetchone()
        output = []
        while row is not None:
            print(row)
            output.append(row)
            row = cursor.fetchone()

        # output.reverse()
        cursor.close()
        return output

    # delete post from database
    # :param postid: unique id of post
    def delete_post(self, postid):
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM posts WHERE postid=%s', [str(postid)])
        self._connection.commit()
        cursor.close()

    # create a new post, add to database
    # :param profileid: unique id of user
    # :param authorName: name of user
    # :param time: current time (should be stored in UTC format)
    # :param title: post title
    # :param content: post content
    # :param image_url: url of image (currently Cloudinary)
    # :param privacy: # TODO: clarify
    # :param communities: list of communities to which the post should be displayed
    # :param propic: user's profile picture
    def create_post(self, profileid, authorName, time, title, content, image_url, privacy, communities, propic):
        cursor = self._connection.cursor()
        cursor.execute('INSERT INTO posts(authorid, authorname, posttime, posttitle, postcontent, imgurl, privacy, communities, propic) ' +
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        [profileid, authorName, time, title, content, image_url, privacy, communities, propic])
        self._connection.commit()
        cursor.close()

    # reset all matches in the matches table
    def reset_matches(self):
        cursor = self._connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS matches')
        cursor.execute('CREATE TABLE matches (studentid TEXT, alumid TEXT, similarity TEXT)')
        self._connection.commit()
        cursor.close()

    # add matches to the matches table
    # :param matches: list objects as created by Match class in matching.py
    # note: it is possible for duplicates to be added to the database, so make sure to reset first. 
    def add_matches(self, matches):
        cursor = self._connection.cursor()
        for match in matches:
            studentid = match[0]
            alumid = match[1]
            similarity = match[6]
            cursor.execute('INSERT INTO matches(studentid, alumid, similarity) VALUES (%s, %s, %s)', [studentid, alumid, similarity])
            # student_address, student_name, alum_address, alum_name, student_class_year, student_interests, student_career_interests
            # student_address, student_name, alum_address, alum_name, alum_classyear, alum_interests, alum_career_interests
            alum, alum_careers, alum_interests = self.get_alum_by_id(alumid)
            stud, stud_careers, stud_interests = self.get_student_by_id(studentid)

            # alum_careers = self.fix_list_format(alum_careers)
            stud_careers = self.fix_list_format(stud_careers)

            # print(alum_interests)
            # print(stud_interests)

            # info = [name, classyear, email, major zip, nummatch, propic]
            emailAlumMatch(stud[2], stud[0], alum[2], alum[0], stud[1], stud_interests, stud_careers)
            emailStudentMatch(stud[2], stud[0], alum[2], alum[0], alum[1], alum_interests, alum_careers)
        self._connection.commit()
        cursor.close()

    # delete a specific match
    # :param studentid: unique id of user (student)
    # :param alumid: unique id of user (alum)
    def delete_match(self, studentid, alumid):
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM matches WHERE studentid=%s AND alumid=%s',
                [studentid, alumid])
        self._connection.commit()
        cursor.close()

    def all_matches(self):
        cursor = self._connection.cursor()
        stmtStr = "SELECT studentid, alumid, similarity FROM matches"
        cursor.execute(stmtStr)
        row = cursor.fetchone()

        output = [] # will store (studname, studyear, alumname, alumyear)
        while row is not None:
            curr_stud = row[0] # profileid of the student in the match
            curr_alum = row[1] # profileid of the alum in the match
            curr_sim = row[2] # similarity score
        
            det_cursor.execute('SELECT name, classyear FROM students WHERE profileid LIKE %s', [curr_stud])
            studname, studyear = det_cursor.fetchone()

            det_cursor.execute('SELECT name, classyear FROM alumni WHERE profileid LIKE %s', [curr_alum])
            alumname, alumyear = det_cursor.fetchone()

            # note: we need to return the profileids in the tuple because they are used for matchdetails JS
            output.append((curr_stud, curr_alum, studname, studyear, alumname, alumyear, curr_sim))

            row = cursor.fetchone()
        
        cursor.close()
        return output

    
    # retrieve matches for a specific profileid
    # if display_all is set to True, then output all matches for all individuals
    def retrieve_matches(self, profileid, display_all=False):
        cursor = self._connection.cursor()
        stmtStr = ""
        if display_all:
            stmtStr = "SELECT studentid, alumid, similarity FROM matches"
            cursor.execute(stmtStr)
        
        else:
            role = self.get_role(profileid)
            if role == 'student':
                stmtStr = "SELECT studentid, alumid, similarity FROM matches WHERE studentid LIKE %s"
            elif role == 'alum':
                stmtStr = "SELECT studentid, alumid, similarity FROM matches WHERE alumid LIKE %s"
            cursor.execute(stmtStr, [profileid])

        row = cursor.fetchone()

        det_cursor = self._connection.cursor() # use this to fetch other info about each person
        output = [] # will store (studname, studyear, alumname, alumyear)
        while row is not None:
            curr_stud = row[0] # profileid of the student in the match
            curr_alum = row[1] # profileid of the alum in the match
            curr_sim = row[2] # similarity of the match itself

            det_cursor.execute('SELECT name, classyear FROM students WHERE profileid LIKE %s', [curr_stud])
            studname, studyear = det_cursor.fetchone()

            det_cursor.execute('SELECT name, classyear FROM alumni WHERE profileid LIKE %s', [curr_alum])
            alumname, alumyear = det_cursor.fetchone()

            # note: we need to return the profileids in the tuple because they are used for matchdetails JS
            output.append((curr_stud, curr_alum, studname, studyear, alumname, alumyear, curr_sim))

            row = cursor.fetchone()

        return output
            
    # disconnect from the database
    def disconnect(self):
        self._connection.close()
