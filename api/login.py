import logging

import webapp2

from google.appengine.api import users

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            text = ('Welcome, %s! (<a href="%s">sign out</a>)' %
                        (user.nickname(), users.create_logout_url('/')))
        else:
            text = ('<a href="%s">Sign in or register</a>.' %
                        users.create_login_url('/'))

        self.response.out.write("<html><body>%s</body></html>" % text)


app = webapp2.WSGIApplication([
    (r'/login', LoginHandler),
], debug=True)