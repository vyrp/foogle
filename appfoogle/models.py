from google.appengine.ext import ndb


class Comments(ndb.Model):
    uid = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    word = ndb.StringProperty(required=True)
    timestamp = ndb.IntegerProperty(required=True)


class Posts(ndb.Model):
    uid = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    word = ndb.StringProperty(required=True)
    timestamp = ndb.IntegerProperty(required=True)


class Messages(ndb.Model):
    uid = ndb.StringProperty(required=True)
    fbid = ndb.StringProperty(required=True, indexed=False)
    word = ndb.StringProperty(required=True)
    timestamp = ndb.IntegerProperty(required=True)


class User(ndb.Model):
    uid = ndb.StringProperty(required=True)
    access_token = ndb.StringProperty(indexed=False)
    msg_timestamp = ndb.IntegerProperty(default=0, indexed=False)
    pst_timestamp = ndb.IntegerProperty(default=0, indexed=False)
    cmt_timestamp = ndb.IntegerProperty(default=0, indexed=False)
    is_populating = ndb.BooleanProperty(default=False, indexed=False)

    @classmethod
    def find_or_create(cls, uid):
        return cls.query(cls.uid == uid).get() or User(uid=uid)
