# run this script to reset your local database
# usage: python util/resetdb.py
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from server.database import Database

db = Database()
db.connect()
db.init()
db.disconnect()
