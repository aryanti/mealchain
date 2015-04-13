import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DEFAULT_HELPER_NAME = 'anon'

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
    helper_name = self.request.get('helper_name',
                                   DEFAULT_HELPER_NAME)
    
    bookings_query = Booking.query(
      ancestor=booking_key(helper_name)).order(-Booking.date)
    bookings = bookings_query.fetch(10)
    
    user = users.get_current_user()
    if user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
    template_values = {
      'user': user,
      'bookings': bookings,
      'helper_name': urllib.quote_plus(helper_name),
      'url': url,
      'url_linktext': url_linktext,
    }
    
    template = JINJA_ENVIRONMENT.get_template('index.html')
    self.response.write(template.render(template_values))
        
class BookDate(webapp2.RequestHandler):
  def post(self):
    helper_name = self.request.get('helper_name',
                                    DEFAULT_HELPER_NAME)
    booking = Booking(parent=booking_key(helper_name))

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
