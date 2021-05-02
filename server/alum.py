
class Alum(object):

    def __init__(self, profid, name, year, email,
    major, zipp, numMatch, propic, careers = None, communities = None):
        self._profileid = profid
        self._name = name
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._numMatch = int(numMatch)
        self._propic = propic
        self._careers = careers
        self._communities = communities

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)
