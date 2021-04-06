
class Alum(object):

    def __init__(self, profid, name, year, email,
    major, zipp, numMatch, careers = None, organizations = None):
        self._profid = profid
        self._name = name
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