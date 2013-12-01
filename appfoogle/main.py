import webapp2
import controllers

app = webapp2.WSGIApplication([
    ('/putcomment', controllers.PutCommentHandler),
    ('/putmessage', controllers.PutMessageHandler),
    ('/search', controllers.GetFromAllHandler),
    ('/timestamp', controllers.DummyCreateTimestamps),
    ('/populate', controllers.PopulateHandler)
], debug=True)
