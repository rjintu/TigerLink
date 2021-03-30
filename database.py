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
                '(userid INTEGER, firstname TEXT, lastname TEXT, classyear TEXT, \
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
    
    def _add_student(self, cursor, student):
        student = [str(x) for x in student] # convert everything to strings
        cursor.execute('INSERT INTO students(userid, firstname, lastname, classyear, email, ' +
        'major, zip, numMatch, career) ' + 
        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', student)

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

    def disconnect(self):
        self._connection.close()
