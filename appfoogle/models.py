from google.appengine.ext import ndb


class Comments(ndb.Model):
    uid_word = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    timestamp = ndb.IntegerProperty(required=True, indexed=False)


class Posts(ndb.Model):
    uid_word = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    timestamp = ndb.IntegerProperty(required=True, indexed=False)


class Messages(ndb.Model):
    uid_word = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    timestamp = ndb.IntegerProperty(required=True, indexed=False)


class User(ndb.Model):
    uid = ndb.StringProperty(required=True)
    last_timestamp = ndb.IntegerProperty(default=0, indexed=False)
    is_populating = ndb.BooleanProperty(default=False, indexed=False)

    @classmethod
    def find_or_create(cls, uid):
        return cls.query(cls.uid == uid).get() or User(uid=uid)
