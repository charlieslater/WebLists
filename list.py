import webapp2
import cgi 
import urllib

from google.appengine.ext import ndb
from google.appengine.api import users

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/write?%s" method="post">
      <div><textarea name="content" rows="1" cols"60"></textarea></div>
      <div><input type="submit" value="Add to List"></div>
    </form>
    <hr>
    <form> List name:
      <input value"%s" name="list_name">
      <input type="submit" value="switch">
    </form>
    <a href="%s">%s</a>
  </body>
</html>
"""

DEFAULT_LIST_NAME = 'default_list'

def list_key(list_name=DEFAULT_LIST_NAME):
    return ndb.Key('List', list_name)

class ListContent(ndb.Model):
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler): 
    def get(self):
        self.response.write('<html><body>')
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        ListContent_query = ListContent.query(
            ancestor=list_key(list_name)).order(-ListContent.date)
        ListContents = ListContent_query.fetch(10)
        for c in ListContents:
            if c.author:
                self.response.write(
                       '<b>%s</b> wrote:' % ListContents.author.nickname())
            else:
                self.response.write('Anonymous added:')
            self.response.write('<blockquote>%s</blockquote>' % 
                                cgi.escape(c.content))

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Login' 
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        sign_query_params = urllib.urlencode({'list_name': list_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % 
                           (sign_query_params, cgi.escape(list_name), 
                           url, url_linktext))
        
class List(webapp2.RequestHandler):
    def post(self):
        list_name = self.request.get('list_name', 
                                     DEFAULT_LIST_NAME)
        listcontent = ListContent(parent=list_key(list_name))
        if users.get_current_user():
            listcontent.author = users.get_current_user()

        listcontent.content = self.request.get('content')
        listcontent.put()
        
        query_params = {'list_name' : list_name}
        self.redirect('/?' + urllib.urlencode(query_params))

application = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/write', List), 
], debug=True)

