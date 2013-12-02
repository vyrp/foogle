from google.appengine.ext import ndb


class Comments(ndb.Model):
    uid = ndb.StringProperty()
    fbid = ndb.StringProperty()
    word = ndb.StringProperty()
    timestamp = ndb.IntegerProperty()


class Posts(ndb.Model):
    uid = ndb.StringProperty()
    fbid = ndb.StringProperty()
    word = ndb.StringProperty()
    timestamp = ndb.IntegerProperty()


class Messages(ndb.Model):
    uid = ndb.StringProperty()
    fbid = ndb.StringProperty()
    word = ndb.StringProperty()
    timestamp = ndb.IntegerProperty()


class User(ndb.Model):
    uid = ndb.StringProperty(required=True)
    access_token = ndb.StringProperty()
    msg_ts = ndb.IntegerProperty()
    pst_ts = ndb.IntegerProperty()
    cmt_ts = ndb.IntegerProperty()
    is_populating = ndb.BooleanProperty(default=False)

    @classmethod
    def find_or_create(cls, uid):
        user = cls.query(cls.uid == uid).get()
        if not user:
            user = User(uid=uid)
        return user
