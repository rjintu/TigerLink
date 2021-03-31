
class Alum(object):

    def __init__(self, profid, fname, lname, year, email,
    major, zipp, numMatch, careers = None, organizations = None):
        self._profid = profid
        self._fname = fname
        self._lname = lname
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._numMatch = numMatch
        self._careers = careers
        self._organizations = organizations

    def addField(fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(fieldName):
        return getattr(self, fieldName)