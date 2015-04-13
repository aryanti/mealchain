import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/bookdate" method="post">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Reserve Date"></div>
    </form>
    <hr>
    <form>Contributor's name:
      <input value="%s" name="helper_name">
      <input type="submit" value="switch">
    </form>
    <a href="%s">%s</a>
  </body>
</html>
"""

DEFAULT_HELPER_NAME = 'anonymous contributor'

def booking_key(helper_name=DEFAULT_HELPER_NAME):
  return ndb.Key('Meal', helper_name)
  
class Helper(ndb.Model):
  identity = ndb.StringProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)
  
class Booking(ndb.Model):
  author = ndb.StructuredProperty(Helper)
  content = ndb.StringProperty(indexed=False)
  date = ndb.DateTimeProperty(auto_now_add=True)
  booked_date = ndb.DateTimeProperty(indexed=False)

class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.write('<html><body>')
    helper_name = self.request.get('helper_name',
                                   DEFAULT_HELPER_NAME)
    
    bookings_query = Booking.query(
      ancestor=booking_key(helper_name)).order(-Booking.date)
    bookings = bookings_query.fetch(10)
    
    user = users.get_current_user()
    for booking in bookings:
      if booking.author:
        author = booking.author.email
        self.response.write('<b>%s</b> wrote:' % author)
      else:
        self.response.write('An anonymous person wrote:')
      self.response.write('<blockquote>%s</blockquote>' %
                          cgi.escape(booking.content))

    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
    
    sign_query_params = urllib.urlencode({'helper_name':
                                          helper_name})
    self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %
                        (sign_query_params, cgi.escape(helper_name),
                         url, url_linktext))
        
class BookDate(webapp2.RequestHandler):
  def post(self):
    helper_name = self.request.get('helper_name',
                                    DEFAULT_HELPER_NAME)
    booking = Greeting(parent=helper_key(helper_name))

    if users.get_current_user():
      booking.author = Helper(
        identity=users.get_current_user().user_id(),
        email=users.get_current_user().email())

    booking.content = self.request.get('content')
    booking.put()

    query_params = {'helper_name': helper_name}
    self.redirect('/?' + urllib.urlencode(query_params))

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/bookdate', BookDate),
], debug=True)
