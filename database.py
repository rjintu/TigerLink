from os import environ
from psycopg2 import connect

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

        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('DROP TABLE IF EXISTS alumni')
        cursor.execute('CREATE TABLE students ' +
                '(profileid TEXT, firstname TEXT, lastname TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip INTEGER, numMatch INTEGER, \
                    career TEXT)')
        cursor.execute('CREATE TABLE alumni ' +
                '(profileid TEXT, firstname TEXT, lastname TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip INTEGER, numMatch INTEGER, \
                    career TEXT)')
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
    
    # TODO: add google ID
    # TODO: separate careers
    def _add_student(self, cursor, student):
        student = [str(x) for x in student] # convert everything to strings
        cursor.execute('INSERT INTO students(profileid, firstname, lastname, classyear, email, ' +
        'major, zip, numMatch, career) ' + 
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', student)

    # TODO: add google ID
    def _add_alum(self, cursor, alum):
        alum = [str(x) for x in alum] # convert everything to strings
        cursor.execute('INSERT INTO alumni(profileid, firstname, lastname, classyear, email, ' + 
        'major, zip, numMatch, career) ' + 
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', alum)

    def get_students(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT firstname, lastname, major, classyear FROM students')
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        cursor.close()
        return output

    def get_student_by_id(self, profileid):
        profileid = str(profileid)
        cursor = self._connection.cursor()
        cursor.execute('SELECT firstname, lastname, classyear, email, major, zip, ' +
                'nummatch, career FROM students WHERE profileid=%s', [profileid])
        return cursor.fetchone()

    # contents must be array of [firstname, lastname, classyear, email, major,
    # zip, nummatch, career]
    # FIXME: handle the career table updates
    def update_student(self, profileid, contents):
        cursor = self._connection.cursor()
        args = contents.copy() # dont modify list given to us
        career = args[-1]
        args = args[:-1] # drop career arg at the end, handle separate
        args.append(profileid)
        args = [str(x) for x in args] # just convert everything to strings
        cursor.execute('UPDATE students SET firstname=%s, lastname=%s, ' +
                'classyear=%s, email=%s, major=%s, zip=%s, nummatch=%s ' +
                'WHERE profileid=%s', args)
        self._connection.commit()
        cursor.close()


    # can search students or alumni
    # TODO: career in diff table
    def search(self, search_query, students=True, alumni=False):
        search_values = [str(x) for x in search_query] # convert everything to strings
        for i in range(0, len(search_values)):
            if (search_values[i] == ''):
                search_values[i] = '%%%%'
            
        print(search_values)
        firstname, lastname, email, major, zipcode, career = search_values
        output = []

        cursor = self._connection.cursor()

        if students:
            # stmtStr = 'SELECT * from students'
            # cursor.execute(stmtStr)
            # FIXME: broken sql statement
            # stmtStr = "SELECT firstname, lastname FROM students WHERE firstname LIKE %s AND " + \
            # "lastname LIKE %s AND email LIKE %s AND major LIKE %s"
            stmtStr = "SELECT firstname, lastname, major, career FROM students WHERE firstname LIKE %s " + \
            "AND lastname LIKE %s AND email LIKE %s AND major LIKE %s"
            cursor.execute(stmtStr, [firstname, lastname, email, major])
            row = cursor.fetchone()
            
            while row is not None:
                output.append(row)
                row = cursor.fetchone()
        
        if alumni:
            cursor.execute('SELECT firstname, lastname, major, email, zip, career FROM alumni' +
            'VALUES (%s, %s, %s, %s, %s, %s)', search_values)
            row = cursor.fetchone()

            while row is not None:
                output.append(row)
                row = cursor.fetchone()

        print('hi')
        cursor.close()
        return output

    def disconnect(self):
        self._connection.close()
