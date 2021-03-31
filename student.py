
class Student(object):
    
    # grad is a boolean whether its a grad student or not
    def __init__(self, profid, fname, lname, year, email,
    major, zipp, numMatch, spref = [1/3, 1/3, 1/3],
    careers = None, organizations = None):
        self._profid = profid
        self._fname = fname
        self._lname = lname
        self._year = year
        self._email = email
        self._major = major
        self._zip = zipp
        self._spref = spref
        self._numMatch = numMatch
        self._careers = careers
        self._organizations = organizations

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)
    
