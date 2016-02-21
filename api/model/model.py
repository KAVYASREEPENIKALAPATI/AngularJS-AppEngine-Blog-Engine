from google.appengine.ext import ndb

class Tag(ndb.Model):
    """Model for representing a post tag."""
    tag = ndb.StringProperty(indexed=True)
    
class Post(ndb.Model):
    """Model for representing a blog post."""
    title = ndb.StringProperty(indexed=False, required=True)
    shortUrl = ndb.StringProperty(indexed=True, required=True)
    content = ndb.StringProperty(indexed=False, required=True)
    date = ndb.DateTimeProperty(indexed=True, auto_now_add=True, required=True)
    dateCompressed = ndb.ComputedProperty(lambda self: self.date.strftime('%Y/%m/%d'))
    tags = ndb.KeyProperty(kind=Tag, indexed=True, repeated=True)
    hidden = ndb.BooleanProperty(indexed=True, required=True)
