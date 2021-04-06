from os import environ
from psycopg2 import connect
from .post import Post


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
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT)')
        # Alumni table
        cursor.execute('DROP TABLE IF EXISTS alumni')
        cursor.execute('CREATE TABLE alumni ' +
                       '(profileid TEXT, name TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT)')

        # Roles table
        cursor.execute('DROP TABLE IF EXISTS roles')
        cursor.execute('CREATE TABLE roles ' + 
                '(profileid TEXT, role TEXT)')
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
                '(postid TEXT, authorid TEXT, posttime TEXT, postcontent TEXT)')
        cursor.execute('DROP TABLE IF EXISTS postgraphics')
        cursor.execute('CREATE TABLE postgraphics ' +
                '(postid TEXT, postgraphic TEXT)')

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
        cursor.execute('INSERT INTO roles(profileid, role) ' +
                       'VALUES (%s, %s)', [profileid, 'student'])
        cursor.execute('INSERT INTO students(profileid, name, classyear, email, ' +
                       'major, zip, numMatch) ' +
                       'VALUES (%s, %s, %s, %s, %s, %s, %s)', student_elems)
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
        cursor.execute('INSERT INTO roles(profileid, role) ' +
                       'VALUES (%s, %s)', [profileid, 'alum'])
        cursor.execute('INSERT INTO alumni(profileid, name, classyear, email, ' +
                       'major, zip, numMatch) ' +
                       'VALUES (%s, %s, %s, %s, %s, %s, %s)', alum_elems)
        for elem in industry:
            cursor.execute('INSERT INTO careers(profileid, career) ' +
                           'VALUES (%s, %s)', (alum[0], elem))
        for elem in interests:
            cursor.execute('INSERT INTO interests(profileid, interest) ' +
                           'VALUES (%s, %s)', (alum[0], elem))

    def get_students(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT profileid, name, classyear, email, \
        major, zip, numMatch FROM students')
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
        major, zip, numMatch FROM alumni')
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
                       'nummatch FROM students WHERE profileid=%s', [profileid])
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
            interests.append(temp)
            temp = cursor.fetchone()

        cursor.close()
        return info, careers, interests

    def get_alum_by_id(self, profileid):
        profileid = str(profileid)
        cursor = self._connection.cursor()
        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                       'nummatch FROM alumni WHERE profileid=%s', [profileid])
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
            interests.append(temp)
            temp = cursor.fetchone()

        cursor.close()
        return info, careers, interests

    # returns student, alumni, or admin. If not in database, returns None
    def get_role(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute('SELECT role FROM roles WHERE profileid=%s', [profileid])
        role = cursor.fetchone()
        return role[0]

    # returns True if user exists, False otherwise.
    # TODO: refactor to use roles table
    def user_exists(self, profileid):
        profileid = str(profileid)

        cursor = self._connection.cursor()
        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                       'nummatch FROM students WHERE profileid=%s', [profileid])
        info = cursor.fetchone()
        if info is not None:
            cursor.close()
            return True

        cursor.execute('SELECT name, classyear, email, major, zip, ' +
                       'nummatch FROM alumni WHERE profileid=%s', [profileid])
        info = cursor.fetchone()
        if info is not None:
            cursor.close()
            return True

        cursor.close()
        return False

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
        name, email, major, zipcode, career, typeofSearch = search_values
        career = search_query[-2]

        output = []
        cursor = self._connection.cursor()
        cursor2 = self._connection.cursor()
        if typeofSearch in 'stud':
            stmtStr = "SELECT profileid, classyear, name, major, zip FROM students WHERE name LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()

            while row is not None:
                # look up all the careers for that person and filter out those who aren't valid.
                contains = False 
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            print(row2[1])
                            contains=True
                        row2 = cursor2.fetchone()
                else:
                    contains=True

                if contains:
                    output.append(row)
                row = cursor.fetchone()
        
        elif typeofSearch in 'alum':
            stmtStr = "SELECT profileid, classyear, name, major, zip FROM alumni WHERE name LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()
            
            while row is not None:
                # look up all the careers for that person and filter out those who aren't valid.
                contains = False 
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            print(row2[1])
                            contains=True
                        row2 = cursor2.fetchone()
                else:
                    contains=True

                if contains:
                    output.append(row)
                row = cursor.fetchone()

        else:
            stmtStr = "SELECT profileid, classyear, name, major, zip FROM students WHERE name LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()
            
            while row is not None:
                # look up all the careers for that person and filter out those who aren't valid.
                contains = False 
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            print(row2[1])
                            contains=True
                        row2 = cursor2.fetchone()
                else:
                    contains=True

                if contains:
                    output.append(row)
                row = cursor.fetchone()

            cursor = self._connection.cursor()
            cursor2 = self._connection.cursor()

            stmtStr = "SELECT profileid, classyear, name, major, zip FROM alumni WHERE name LIKE %s " + \
            "AND email LIKE %s AND major LIKE %s AND zip LIKE %s"
            cursor.execute(stmtStr, [name, email, major, zipcode])
            row = cursor.fetchone()
            
            while row is not None:
                # look up all the careers for that person and filter out those who aren't valid.
                contains = False 
                smtr = 'SELECT profileid, career FROM careers WHERE profileid LIKE %s'
                cursor2.execute(smtr, [row[0]])
                row2 = cursor2.fetchone()
                print("career:")
                print(career)
                print(career[0])
                print(len(career))
                if (len(career) != 0):
                    while row2 is not None:
                        if (row2[1] in career):
                            print(row2[1])
                            contains=True
                        row2 = cursor2.fetchone()
                else:
                    contains=True

                if contains:
                    output.append(row)
                row = cursor.fetchone()


        cursor.close()
        return output


    def create_timeline(self):
        cursor = self._connection.cursor()
        cursor.execute('INSERT INTO posts(postid, authorid, posttime, postcontent) ' +
                           'VALUES (%s, %s, %s, %s)', ['1', '123', 'April 6th, 12:51am', 'This is a sample timeline post that was put into the database.'])
        cursor.close()
        cursor = self._connection.cursor()

        stmtStr = "SELECT postid, authorid, posttime, postcontent FROM posts"
        cursor.execute(stmtStr)
        row = cursor.fetchone()
        output = []
        while (row is not None):
            output.append(row)
            row = cursor.fetchone()

        print(output)
        return output

    def disconnect(self):
        self._connection.close()
