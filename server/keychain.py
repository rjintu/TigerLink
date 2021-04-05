from os import environ
from sys import stderr

class KeyChain:

    def __init__(self):
        self.CLIENT_ID = environ.get('GOOGLE_CLIENT_ID')
        self.CLIENT_SECRET = environ.get('GOOGLE_CLIENT_SECRET')
        self.FLASK_SECRET = environ.get('FLASK_SECRET')
        if self.CLIENT_ID is None:
            print('Could not load keys from environment variables')
            print('Loading keys through keys.py...')
            try:
                from . import keys
                self.CLIENT_ID = keys.GOOGLE_CLIENT_ID
                self.CLIENT_SECRET = keys.GOOGLE_CLIENT_SECRET
                self.FLASK_SECRET = keys.FLASK_SECRET
            except Exception as e:
                print("Error: could not load secret keys!", file=stderr)
                print("Do you have keys.py in the 'server' folder?", file=stderr)
                print("More info: " + str(e))
                exit(1)
