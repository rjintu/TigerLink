
class Alum(object):

    def __init__(self, profid, name, year, email,
    major, zipp, numMatch, careers = None, organizations = None):
        self._profileid = profid
        self._name = name
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._numMatch = int(numMatch)
        self._careers = careers
        self._organizations = organizations

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)