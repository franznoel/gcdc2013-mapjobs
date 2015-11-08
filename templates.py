import webapp2, jinja2, os, const, json, datetime

from google.appengine.api import users, mail
from model import Jobs, Resumes, Profile

j = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),os.path.join(const.TEMPLATES,'mapjobs_v1'))),
  extensions=['jinja2.ext.autoescape']
)

class BaseHandler(webapp2.RequestHandler):
  def render_html(self,template,values=''):
    t = j.get_template(template)
    self.response.content_type = 'text/html'
    self.response.write(t.render(values))
    
class StaticJobHandler(BaseHandler):
  def get(self,html):
    self.render_html(html)
    
app = webapp2.WSGIApplication([
  ('/templates/(.*)',StaticJobHandler),
], debug=True)