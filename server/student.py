
class Student(object):
    
    def __init__(self, profileid, name, year, email,
    major, zip, numMatch, spref = [1/3, 1/3, 1/3],
    careers = None, organizations = None):
        self._profileid = profileid
        self._name = name
        self._year = year
        self._email = email
        self._major = major
        self._zip = zip
        self._spref = spref
        self._numMatch = int(numMatch)
        self._careers = careers
        self._organizations = organizations

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)
    
