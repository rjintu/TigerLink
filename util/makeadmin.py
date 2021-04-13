# run this script to make a specific user an admin
# usage: python util/makeadmin.py email
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from server.database import Database

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('Incorrect number of arguments: must list user email')
    email = sys.argv[1]
    db = Database()
    db.connect()
    profileid = db.get_profileid_by_email(email)
    if profileid is None:
        print('No profile with email ' + email + ' exists.')
        exit(0)
    db.set_role(profileid, 'admin')
    print('Set ' + email + ' to admin role.')
    db.disconnect()
