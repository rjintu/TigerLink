
class Post(object):

    def __init__(self, postid, authorid, posttime, postcontent):
        self._postid = postid
        self._authorid = authorid
        self._posttime = posttime
        self._postcontent = postcontent

    def addField(fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(fieldName):
        return getattr(self, fieldName)