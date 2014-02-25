import webapp2
import jinja2
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def user_key(id):
    return ndb.Key('GroceryList',id)


class GroceryItem(ndb.Model):
    name = ndb.StringProperty()
    cost = ndb.FloatProperty()
    quantity = ndb.IntegerProperty()
    total = ndb.FloatProperty()
    picture = ndb.BlobProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)


class MainHandler(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        items_query = GroceryItem.query(
            ancestor=user_key(users.get_current_user().user_id())).order(-GroceryItem.time)
        items = items_query.fetch(10)
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user':users.get_current_user(),
            'items':items,
            'url':url,
            'url_linktext':url_linktext,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class GroceryList(webapp2.RequestHandler):

    def post(self):
        user = users.get_current_user();
        item = GroceryItem(parent=user_key(user.user_id()))
        item.name = self.request.get('name')
        item.cost = self.request.get('cost')
        item.quantity = self.request.get('quantity')
        item.picture = self.request.get('img')
        item.total = item.cost * item.quantity
        item.put()

        query_params = {'user': user_key(user.user_id())}
        self.redirect('/?' + urllib.urlencode(query_params))


app = webapp2.WSGIApplication([
    ('/', MainHandler)
    ('/add', GroceryList)
], debug=True)
