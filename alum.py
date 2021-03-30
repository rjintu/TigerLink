
class Alum(object):

    def __init__(self, gauth, netid, fname, lname, year, email,
    major, zipp, numMatch, career = None, organizations = None):
        self._gauth = gauth
        self._netid = netid
        self._fname = fname
        self._lname = lname
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._numMatch = numMatch
        self._career = career

    def addField(fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(fieldName):
        return getattr(self, fieldName)