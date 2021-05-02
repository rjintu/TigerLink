
class Student(object):
    
    def __init__(self, profileid, name, year, email,
    major, zipp, numMatch, propic, spref = [1/3, 1/3, 1/3], 
    careers = None, communities = None):
        self._profileid = profileid
        self._name = name
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._spref = spref
        self._numMatch = int(numMatch)
        self._propic = propic
        self._careers = careers
        self._communities = communities

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)
    
