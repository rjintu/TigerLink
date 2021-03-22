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

    def create_students(self):
        cursor = self._connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS students')
        cursor.execute('CREATE TABLE students ' +
                '(userid INTEGER, firstname TEXT, lastname TEXT)')
        cursor.execute('INSERT INTO students (userid, firstname, lastname) ' +
                'VALUES (1, \'Devon\', \'Ulrich\')')
        self._connection.commit()

        cursor.close()

    def disconnect(self):
        self._connection.close()
