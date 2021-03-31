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
        cursor.execute('CREATE TABLE students ' +
                '(profileid TEXT, firstname TEXT, lastname TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT)')
        cursor.execute('DROP TABLE IF EXISTS alumni')
        cursor.execute('CREATE TABLE alumni ' +
                '(profileid TEXT, firstname TEXT, lastname TEXT, classyear TEXT, \
                    email TEXT, major TEXT, zip TEXT, numMatch TEXT)')
        cursor.execute('DROP TABLE IF EXISTS careers')
        cursor.execute('CREATE TABLE careers ' + 
                '(profileid TEXT, career TEXT)')
        cursor.execute('DROP TABLE IF EXISTS interests')
        cursor.execute('CREATE TABLE interests ' + 
                '(profileid TEXT, interest TEXT)')
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
    
    # TODO: separate careers
    def _add_student(self, cursor, student):
        student = [str(x) for x in student] # convert everything to strings
        student_elems = student[:-1]
        last_elem = student[-1]
        cursor.execute('INSERT INTO students(profileid, firstname, lastname, classyear, email, ' +
        'major, zip, numMatch) ' + 
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', student_elems)
        print('got here')
        for elem in last_elem:
            cursor.execute('INSERT INTO careers(profileid, career) ' + 'VALUES (%s, %s)', (student[0], elem))

    def _add_alum(self, cursor, alum):
        alum = [str(x) for x in alum] # convert everything to strings
        cursor.execute('INSERT INTO alumni(profileid, firstname, lastname, classyear, email, ' + 
        'major, zip, numMatch) ' + 
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', alum)
        for elem in alum[7]:
            cursor.execute('INSERT INTO careers(profileid, career) ' + 'VALUES (%s, %s)', alum[0], elem)

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
    
    def get_alumni(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT firstname, lastname, major, classyear FROM alumni')
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        cursor.close()
        return output

    # can search students or alumni
    # TODO: career in diff table (need to fix)
    def search(self, search_query, students=True, alumni=False):
        search_values = [str(x) for x in search_query] # convert everything to strings
        for i in range(0, len(search_values)):
            if (search_values[i] == ''):
                search_values[i] = '%%%%'
            
        print(search_values)
        firstname, lastname, email, major, zip, career = search_values
        output = []

        cursor = self._connection.cursor()

        if students:
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

        cursor.close()
        return output

    def disconnect(self):
        self._connection.close()
