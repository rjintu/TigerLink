
class Post(object):

    def __init__(self, postid, authorid, posttime, posttitle, postcontent, imgurl, privacy, communities, moderation):
        self._postid = postid
        self._authorid = authorid
        self._posttime = posttime
        self._posttitle = posttitle
        self._postcontent = postcontent
        self._imgurl = imgurl
        self._privacy = privacy
        self._communities = communities 
        self._moderation = moderation

    def addField(self, fieldName, fieldVal):
        setattr(self, fieldName, fieldVal)
    
    def getField(self, fieldName):
        return getattr(self, fieldName)