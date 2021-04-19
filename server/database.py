from os import environ
from psycopg2 import connect
from .post import Post
import os

class Database:

    def __init__(self):
        # environment variable in Heroku
        self._url = environ.get('DATABASE_URL')

    def connect(self):
        if self._url is None:
            print('Using local database')
            self._connection = connect(host='localhost', port=5432,
                                       user='tigerlink', password='xxx', database='tldata')
        else:
            print('Using deployed database')
            self._connection = connect(self._url, sslmode='require')

    def init(self):
        cursor = self._connection.cursor()
        # Students table
        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('CREATE TABLE students ' +
                       '(profileid TEXT, name TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT, propic TEXT)')
        # Alumni table
        cursor.execute('DROP TABLE IF EXISTS alumni')
        cursor.execute('CREATE TABLE alumni ' +
                       '(profileid TEXT, name TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT, propic TEXT)')

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
        # Timeline posts tables (posts, postgraphics)
        cursor.execute('DROP TABLE IF EXISTS posts')
        cursor.execute('CREATE TABLE posts ' + 
                '(postid TEXT, authorname TEXT, authorid TEXT, posttime TEXT, posttitle TEXT, postcontent TEXT, imgurl TEXT, privacy TEXT, communities TEXT, profpic TEXT)')
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
        print('Database reset successfully')

    def reset_posts(self):
        cursor = self._connection.cursor()
        # Timeline posts tables (posts, postgraphics)
        cursor.execute('DROP TABLE IF EXISTS posts')
        cursor.execute('CREATE TABLE posts ' + 
                '(postid TEXT, authorname TEXT, authorid TEXT, posttime TEXT, posttitle TEXT, postcontent TEXT, imgurl TEXT, privacy TEXT, communities TEXT, profpic TEXT)')
        cursor.execute('DROP TABLE IF EXISTS comments')
        cursor.execute('CREATE TABLE comments ' +
                '(postid TEXT, author TEXT, comment TEXT)')
        cursor.execute('DROP TABLE IF EXISTS likes')
        cursor.execute('CREATE TABLE likes ' +
                '(postid TEXT, authorid TEXT)')

        self._connection.commit()
        cursor.close()

    def create_students(self, students):
        cursor = self._connection.cursor()
        for student in students:
            self._add_student(cursor, student)
        self._connection.commit()

        cursor.close()

    def create_alumni(self, alumni):
        cursor = self._connection.cursor()
        for alum in alumni:
            self._add_alum(cursor, alum)
        self._connection.commit()

        cursor.close()

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
                       'major, zip, numMatch, propic) ' +
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', student_elems)
        for elem in industry:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                           'VALUES (%s, %s)', [student[0], elem])

        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                           'VALUES (%s, %s)', [student[0], elem])

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
                       'major, zip, numMatch, propic) ' +
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', alum_elems)
        for elem in industry:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                           'VALUES (%s, %s)', (alum[0], elem))
        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                           'VALUES (%s, %s)', (alum[0], elem))

    def get_students(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid, name, classyear, email, \
        major, zip, numMatch, propic FROM students')
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

    def get_alumni(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid, name, classyear, email, \
        major, zip, numMatch, propic FROM alumni')
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

    def get_student_by_id(self, profileid):
        profileid = str(profileid)
        cursor = self._connection.cursor()
        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                       'nummatch, propic FROM students WHERE profileid=%s', [profileid])
        info = cursor.fetchone()

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

    # returns student, alumni, or admin. If not in database, returns None
    def get_role(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute(
            'SELECT role FROM roles WHERE profileid=%s', [profileid])
        role = cursor.fetchone()
        cursor.close()
        return None if role is None else role[0]

    # used for changing a user between student/alum
    # NOTE: this function is not safe yet! if you plan on using it, also
    # make sure to change the students/alum tables
    def set_role(self, profileid, newrole):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute('UPDATE roles SET role=%s WHERE profileid=%s', [newrole, profileid])
        cursor.close()
        self._connection.commit()

    def get_admin(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute('SELECT isadmin FROM roles WHERE profileid=%s', [profileid])
        isadmin = cursor.fetchone()
        cursor.close()
        return False if isadmin is None else isadmin[0] == 'true'

    def set_admin(self, profileid, is_admin):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        if is_admin:
            cursor.execute('UPDATE roles SET isadmin=%s WHERE profileid=%s', ['true', profileid])
        else:
            cursor.execute('UPDATE roles SET isadmin=%s WHERE profileid=%s', ['false', profileid])
        cursor.close()
        self._connection.commit()

    # returns True if user exists, False otherwise.
    def user_exists(self, profileid):
        return self.get_role(profileid) is not None

    # contents must be array of [name, classyear, email, major,
    # zip, nummatch, career]
    def update_student(self, profileid, contents, careers, interests):
        cursor = self._connection.cursor()
        args = contents.copy()  # dont modify list given to us
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

    # contents must be array of [name, classyear, email, major,
    # zip, nummatch, career]
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

    # can search students or alumni
    def search(self, search_query):
        # convert everything to strings
        search_values = [str(x) for x in search_query]
        for i in range(0, len(search_values)):
            if (search_values[i] == ''):
                search_values[i] = '%%%%'
        name, email, major, zipcode, _, _, typeofSearch = search_values
        career = search_query[-3]
        interest = search_query[-2]

        name = '%%' + name + '%%'
        name = name.lower()

        output = []
        cursor = self._connection.cursor()
        cursor2 = self._connection.cursor()
        cursor3 = self._connection.cursor()

        if typeofSearch in 'stud':
            stmtStr = "SELECT profileid, classyear, name, major, email FROM students WHERE lower(name) LIKE %s " + \
                "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()

            while row is not None:
                # look up all the careers for that person and filter out those which don't match.
                contains_career = False
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            contains_career = True
                        row2 = cursor2.fetchone()
                else:
                    contains_career = True

                # look up all the interests for that person and filter out those which don't match.
                contains_interest = False
                smtr = 'SELECT profileid, interest FROM interests WHERE profileid LIKE %s'
                cursor3.execute(smtr, [row[0]])
                row3 = cursor3.fetchone()
                if (len(interest) != 0):
                    while row3 is not None:
                        if (row3[1] in interest):
                            contains_interest = True
                        row3 = cursor3.fetchone()
                else:
                    contains_interest = True


                if contains_career and contains_interest:
                    output.append(row)
                row = cursor.fetchone()

        elif typeofSearch in 'alum':
            stmtStr = "SELECT profileid, classyear, name, major, email FROM alumni WHERE lower(name) LIKE %s " + \
                "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()

            while row is not None:
                # look up all the careers for that person and filter out those which don't match.
                contains_career = False
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            print(row2[1])
                            contains_career = True
                        row2 = cursor2.fetchone()
                else:
                    contains_career = True
                
                # look up all the interests for that person and filter out those which don't match.
                contains_interest = False
                smtr = 'SELECT profileid, interest FROM interests WHERE profileid LIKE %s'
                cursor3.execute(smtr, [row[0]])
                row3 = cursor3.fetchone()
                if (len(interest) != 0):
                    while row3 is not None:
                        if (row3[1] in interest):
                            contains_interest = True
                        row3 = cursor3.fetchone()
                else:
                    contains_interest = True

                if contains_career and contains_interest:
                    output.append(row)
                row = cursor.fetchone()

        # both student and alum
        else:
            stmtStr = "SELECT profileid, classyear, name, major, email FROM students WHERE lower(name) LIKE %s " + \
                "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()

            while row is not None:
                # look up all the careers for that person and filter out those which don't match.
                contains_career = False
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            contains_career = True
                        row2 = cursor2.fetchone()
                else:
                    contains_career = True
                
                # look up all the interests for that person and filter out those which don't match.
                contains_interest = False
                smtr = 'SELECT profileid, interest FROM interests WHERE profileid LIKE %s'
                cursor3.execute(smtr, [row[0]])
                row3 = cursor3.fetchone()
                if (len(interest) != 0):
                    while row3 is not None:
                        if (row3[1] in interest):
                            contains_interest = True
                        row3 = cursor3.fetchone()
                else:
                    contains_interest = True

                if contains_career and contains_interest:
                    output.append(row)
                row = cursor.fetchone()

            cursor = self._connection.cursor()
            cursor2 = self._connection.cursor()

            stmtStr = "SELECT profileid, classyear, name, major, email FROM alumni WHERE name LIKE %s " + \
                "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()

            while row is not None:
                # look up all the careers for that person and filter out those which don't match.
                contains_career = False
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            contains_career = True
                        row2 = cursor2.fetchone()
                else:
                    contains_career = True

                # look up all the interests for that person and filter out those which don't match.
                contains_interest = False
                smtr = 'SELECT profileid, interest FROM interests WHERE profileid LIKE %s'
                cursor3.execute(smtr, [row[0]])
                row3 = cursor3.fetchone()
                print(row3)
                if (len(interest) != 0):
                    while row3 is not None:
                        if (row3[1] in interest):
                            contains_interest = True
                        row3 = cursor3.fetchone()
                else:
                    contains_interest = True

                if contains_career and contains_interest:
                    output.append(row)
                row = cursor.fetchone()

        cursor.close()
        return output

    def get_posts(self):
        cursor = self._connection.cursor()

        stmtStr = "SELECT postid, authorid, authorname, posttime, posttitle, postcontent, " + \
                  "imgurl, privacy, communities, profpic FROM posts"
        cursor.execute(stmtStr)
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        output.reverse()
        cursor.close()
        return output

    def delete_post(self, postId):
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM posts WHERE postid=%s', [str(postId)])
        self._connection.commit()
        cursor.close()

        # postid TEXT, authorname, authorid TEXT, posttime TEXT, posttitle TEXT, postcontent TEXT, imgurl TEXT, privacy TEXT, communities TEXT

    def create_post(self, authorId, authorName, time, title, content, image_url, private, communities, profpic):
        cursor = self._connection.cursor()
        postid = str(os.getenv('numposts', 0))
        cursor.execute('INSERT INTO posts(postid, authorid, authorname, posttime, posttitle, postcontent, imgurl, privacy, communities, profpic) ' +
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                        [postid, authorId, authorName, time, title, content, image_url, private, communities, profpic])
        self._connection.commit()
        postid = int(postid) + 1
        environ['postid'] = str(postid +1)
        cursor.close()

    # reset all matches in the matches table
    def reset_matches(self):
        cursor = self._connection.cursor()
        # TODO: maybe there's a cleaner way to TRUNCATE the rows instead of dropping/creating table (performance issues?)
        cursor.execute('DROP TABLE IF EXISTS matches')
        cursor.execute('CREATE TABLE matches (studentid TEXT, alumid TEXT, similarity TEXT)')
        self._connection.commit()
        cursor.close()

    # add matches to the matches table
    # note: it is possible for duplicates to be added to the database, so make sure to reset first. 
    # potential TODO: check for duplicates?
    def add_matches(self, matches):
        cursor = self._connection.cursor()
        for match in matches:
            studentid = match[0]
            alumid = match[1]
            similarity = match[6]
            cursor.execute('INSERT INTO matches(studentid, alumid, similarity) VALUES (%s, %s, %s)', [studentid, alumid, similarity])
        self._connection.commit()
        cursor.close()
    
    # retrieve matches for a specific profileid
    # if display_all is set to True, then output all matches for all individuals
    def retrieve_matches(self, profileid, display_all=False):
        cursor = self._connection.cursor()
        role = self.get_role(profileid)
        stmtStr = ""
        if display_all:
            stmtStr = "SELECT studentid, alumid, similarity FROM matches"
            cursor.execute(stmtStr)
        
        else:
            if role == 'student':
                stmtStr = "SELECT studentid, alumid, similarity FROM matches WHERE studentid LIKE %s"
            elif role == 'alum':
                stmtStr = "SELECT studentid, alumid, similarity FROM matches WHERE alumid LIKE %s"
            cursor.execute(stmtStr, [profileid])

        row = cursor.fetchone()

        det_cursor = self._connection.cursor() # use this to fetch other info about each person
        output = [] # will store (studname, studyear, alumname, alumyear)
        while row is not None:
            curr_stud = row[0] # get the profileid of the student in the match
            curr_alum = row[1] # get the profileid of the alum in the match
            curr_sim = row[2] # get the similarity of the match itself

            det_cursor.execute('SELECT name, classyear FROM students WHERE profileid LIKE %s', [curr_stud])
            studname, studyear = det_cursor.fetchone()

            det_cursor.execute('SELECT name, classyear FROM alumni WHERE profileid LIKE %s', [curr_alum])
            alumname, alumyear = det_cursor.fetchone()

            # note: we currently need to return the profileids in the tuple because they are used for matchdetails JS
            output.append((curr_stud, curr_alum, studname, studyear, alumname, alumyear, curr_sim))

            row = cursor.fetchone()

        return output
            

    def disconnect(self):
        self._connection.close()
