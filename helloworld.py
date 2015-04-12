import cgi
from google.appengine.api import users
import webapp2

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/bookdate" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Reserve Date"></div>
    </form>
  </body>
</html>
"""

class MainPage(webapp2.RequestHandler):
  def get(self):
    # Checks for active Google account session
    user = users.get_current_user()

    if user:
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('Hello, ' + user.nickname())
    else:
      self.redirect(users.create_login_url(self.request.uri))
        
class BookDate(webapp2.RequestHandler):
  def post(self):
    self.response.write('<html><body>Your comment:<pre>')
    self.response.write(cgi.escape(self.request.get('content')))
    self.response.write('</pre></body></html>')

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/bookdate', BookDate),
], debug=True)
