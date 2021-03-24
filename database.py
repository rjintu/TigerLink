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
                    email TEXT, major TEXT, country TEXT, zip INTEGER, numMatch INTEGER, \
                    career TEXT)')

    def create_students(self, students):
        for student in students:
            create_student(student)
        self._connection.commit()

        cursor.close()
    
    def create_student(student):
        cursor.execute('INSERT INTO students(userid, firstname, lastname, classyear, email ' +
        'major, zip, numMatch, career) ' + 
        'VALUES (' + student[0] + ", " + student[1] + ", " + student[2] + ", " +  student[3]+ ", " + 
        student[4] + ", " + student[5] + ", " + student[6] + ", " + student[7] + ", " + 
        student[8] + ')')

    def get_students(self):
        cursor = self._connection.cursor()
        cursor.execute('SELECT userid, firstname, lastname FROM students')
        row = cursor.fetchone()
        output = []
        while row is not None:
            output.append(row)
            row = cursor.fetchone()

        cursor.close()
        return output

    def disconnect(self):
        self._connection.close()
