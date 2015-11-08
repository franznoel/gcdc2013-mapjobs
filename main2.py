import webapp2, jinja2, os, const, json, datetime, cgi, urllib
from google.appengine.ext import ndb
from google.appengine.api import users, mail, urlfetch, oauth
from model import Jobs, Resumes, ResumeOrganizations, Profile
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets
from apiclient.discovery import build

j = jinja2.Environment(
  loader=jinja2.FileSystemLoader(
    os.path.join(os.path.dirname(__file__),os.path.join(const.TEMPLATES,'mapjobs_v1'))
  ),
  extensions=['jinja2.ext.autoescape']
)

decorator = OAuth2DecoratorFromClientSecrets(
  os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
  'https://www.googleapis.com/auth/plus.me')
  
service = build('plus', 'v1')

def get_geo(address):
  address = address.replace(" ","+")
  browser_key = "AIzaSyDuPf4TU5-JFoFly269wIVnM1nvcWNsX5Y"
  sensor = "true"
  url = "http://maps.googleapis.com/maps/api/geocode/json?api_key="+ browser_key +"&address=" + address + "&sensor="+ sensor
  result = urlfetch.fetch(url)
  data = json.loads(result.content)
  lat = data['results'][0]['geometry']['location']['lat']
  long = data['results'][0]['geometry']['location']['lng']
  return ndb.GeoPt(str(lat) +","+ str(long))

  
class BaseHandler(webapp2.RequestHandler):
  def render_html(self,template,values=''):
    t = j.get_template(template)
    self.response.content_type = 'text/html'
    self.response.write(t.render(values))
  
  def render_json(self,queries):
    queries_list = []
    for query in queries:
      queries_list.append(query.to_dict())
    for value in queries_list:
      value['dateCreated'] = value['dateCreated'].strftime('%b %d, %Y')
      value['dateUpdated'] = value['dateUpdated'].strftime('%b %d, %Y')
      value['geopoint'] = str(value['geopoint'])
    self.response.content_type = 'text/json'
    self.response.write(json.dumps(queries_list))
  
  def render_normal_json(self,queries):
    queries_list = []
    for query in queries:
      queries_list.append(query.to_dict())
    for value in queries_list:
      value['dateCreated'] = value['dateCreated'].strftime('%b %d, %Y')
      value['dateUpdated'] = value['dateUpdated'].strftime('%b %d, %Y')
    self.response.content_type = 'text/json'
    self.response.write(json.dumps(queries_list))
  
  def render_multi_json(self,**kwargs):
    queries_list = []
    queries_dict = {}
    for kw_query, queries in kwargs.items():
      queries_dict[kw_query] = []
      for query in queries:
        queries_dict[kw_query].append(query.to_dict())
      for value in queries_dict[kw_query]:
        value['dateCreated'] = value['dateCreated'].strftime('%b %d, %Y')
        value['dateUpdated'] = value['dateUpdated'].strftime('%b %d, %Y')
        value['geopoint'] = str(value['geopoint'])
    self.response.content_type = 'text/json'
    self.response.write(json.dumps(queries_dict))
    

class SearchHandler(BaseHandler):
  def post(self):
    s = self.request.get('s')
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    profiles = Profile.query(ndb.OR(Profile.firstname==s,Profile.lastname==s))
    resumes = Resumes.query(Resumes.position==s)
    jobs = Jobs.query(ndb.OR(Jobs.position==s,Jobs.company==s))
    self.render_multi_json(resumes=resumes,profiles=profiles,jobs=jobs)
    '''
    if user:
      current_user = 'Hello, '+ user.nickname()
      user_url = logout_url
      title = "Click to logout from Google."
    values = {
      'current_user' : current_user,
      'user_url' : user_url,
      'profiles' : profiles,
      'resumes' : resumes,
      'jobs' : jobs,
      's' : self.request.get('s'),
    }
    self.render_html('search.html',values)
    '''
    

class ProfileViewHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      profile = Profile.query(Profile.user_id==user.user_id()).get()
      values = {
        'user' : user,
        'logout_url' : logout_url,
        'user_id': user.user_id(),
        'profile' : profile,
      }
      self.render_html('profile.html',values)
    else:
      self.redirect(login_url)

class ProfileUpdateViewHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      profile = Profile.query(Profile.user_id==user.user_id()).get()
      values = {
        'user' : user,
        'profile' : profile,
        'logout_url' : logout_url,
        'user_id' : user.user_id(),
      }
      self.render_html('profile-update.html',values)
    else:
      self.redirect(login_url)
  
class ResumesViewHandler(BaseHandler):
  @decorator.oauth_aware
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      url = service.tasks().list(tasklist='@default').execute(decorator.http()) if decorator.has_credentials() else decorator.authorize_url()
      profile_key = ndb.Key("Profile",user.email())
      resumes = Resumes.query(ancestor=profile_key)
      values = {
        'url' : url,
        'resumes' : resumes,
        'oauth_user' : oauth.get_current_user() or "Hello",
        'logout_url' : logout_url,
        'user' : user,
      }
      self.render_html('resumes.html',values)
    else:
      self.redirect(login_url)

class ResumeDetailViewHandler(BaseHandler):
  def get(self,urlString):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      resume_key = ndb.Key(urlsafe=urlString)
      resume = resume_key.get()
      resumeorgs = ResumeOrganizations.query(ancestor = resume_key).fetch()
      values = {
        'resumeorgs' : resumeorgs,
        'resume' : resume,
        'logout_url' : logout_url,
        'user' : user,
      }
      self.render_html('resume-detail.html',values)
    else:
      self.redirect(login_url)
      
      
class ResumeCreateViewHandler(BaseHandler):
  @decorator.oauth_aware
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      profile_key = ndb.Key("Profile",user.user_id())
      resumes = Resumes.query(ancestor=profile_key)
      if decorator.has_credentials():
        response = service.tasks().list(tasklist='@default').execute(decorator.http())
        http = decorator.http()
        values = {
          'decorator' : http,
          #'access_token' : credentials.access_token,
          #'refresh_token' : credentials.refresh_token,
          'params' : self.request.params,
          'resumes' : resumes,
          'logout_url' : logout_url,
          'user' : user,
        }
      else:
        url = decorator.authorize_url()
        values = {
          'params' : self.request.params,
          'url' : decorator.authorize_url(),
          'resumes' : resumes,
          'logout_url' : logout_url,
          'user' : user,
          'secrets' : SECRETS,
        }
      credentials = True if decorator.has_credentials() else False
      #self.response.write(credentials)
      self.render_html('resume-create.html',values)
    else:
      self.redirect(login_url)

      
class ResumeUpdateViewHandler(BaseHandler):
  def get(self,resume_id):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      resume_key = ndb.Key(urlsafe=resume_id)
      resume = resume_key.get()
      values = {
        'resume' : resume,
        'logout_url' : logout_url,
        'user' : user,
      }
      self.render_html('resume-update.html',values)
    else:
      self.redirect(login_url)

class ResumeOrganizationCreateHandler(BaseHandler):
  def post(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user: 
      resume_key = ndb.Key(urlsafe = self.request.get('resume_urlString'))
      resume_org = ResumeOrganizations(parent = resume_key)
      resume_org.name = self.request.get('name')
      resume_org.title = self.request.get('title')
      resume_org.startDate = self.request.get('startDate')
      resume_org.endDate = self.request.get('endDate')
      resume_org.location = self.request.get('location')
      resume_org.department = self.request.get('department')
      resume_org.primary = True if self.request.get('primary') == "true" else False
      resume_org.type = self.request.get('type')
      resume_org.description = self.request.get('description')
      resume_org.put()
    else:
      self.redirect(login_url)
  def get(self):
    self.redirect('/resumes/');

class ResumeOrganizationsHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      resume_orgs = ResumeOrganizations.query().fetch()
      self.render_normal_json(resume_orgs)
    else:
      self.redirect(login_url)

class JobsViewHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      profile_key = ndb.Key('Profile',user.email())
      jobs = Jobs.query(ancestor=profile_key)
      values = {
        'jobs' : jobs,
        'user' : user,
        'logout_url' : logout_url,
        'login_url' : login_url,
      }
      self.render_html('jobs.html',values)
    else:
      self.redirect(login_url)
    
class JobCreateViewHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      values = {
        'user' : user,
        'logout_url' : logout_url,
      }
      self.render_html('jobs-create.html',values)
    else:
      self.redirect(login_url)

class JobDetailViewHandler(BaseHandler):
  def get(self,job_id):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      job_key = ndb.Key(urlsafe=job_id)
      job = job_key.get()
      values = {
        'job' : job,
        'logout_url' : logout_url,
        'user' : user,
      }
      self.render_html('job-detail.html',values)
    else:
      self.redirect(login_url)
      

class JobUpdateViewHandler(BaseHandler):
  def get(self,job_id):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      job_key = ndb.Key(urlsafe=job_id)
      job = job_key.get()
      values = {
        'job' : job,
        'logout_url' : logout_url,
        'user' : user,
      }
      self.render_html('job-update.html',values)
    else:
      self.redirect(login_url)
      
class MainHandler(BaseHandler):
  def post(self):
    s = self.request.get('s')
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    profiles = Profile.query(ndb.OR(Profile.firstname==s,Profile.lastname==s))
    resumes = Resumes.query(Resumes.position==s)
    jobs = Jobs.query(ndb.OR(Jobs.position==s,Jobs.company==s))
    if user:
      current_user = 'Hello, '+ user.nickname()
      user_url = logout_url
      title = "Click to logout from Google."
    values = {
      'current_user' : current_user,
      'user_url' : user_url,
      'profiles' : profiles,
      'resumes' : resumes,
      'jobs' : jobs,
      's' : self.request.get('s'),
    }
    self.render_html('search.html',values)
    
  def get(self):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri) # raise NotAllowedError
    profile=''
    if user:
      profile = Profile.query(Profile.user_id==user.user_id())
      if profile.count() <= 0:
        profile = Profile()
        profile.user_id = user.user_id()
        profile.email = user.email()
        profile.firstname = user.nickname()
        profile_key = profile.put()
      else:
        profile_key = Profile.query(Profile.user_id==user.user_id())
      profile = profile_key.get()
      current_user = 'Hello, '+ user.nickname()
      user_url = logout_url
      title = "Click to logout from Google."
    else:
      current_user = 'Google Sign in'
      user_url = login_url 
      title = "Click to sign in with your Google Account."
    values = {
      'current_user' : current_user,
      'user_url' : user_url,
      'profile' : profile,
    }
    self.render_html('index.html',values)

# Jobs
class JobsHandler(BaseHandler):
  def get(self):
    jobs = Jobs.query().fetch()
    self.render_json(jobs)
    
class JobHandler(BaseHandler):
  def get(self,job_id):
    job = ndb.Key(urlsafe=job_id).get()
    job_dict = job.to_dict()
    job_dict['dateCreated'] = job_dict['dateCreated'].strftime('%b %d, %Y')
    job_dict['dateUpdated'] = job_dict['dateUpdated'].strftime('%b %d, %Y')
    value['geopoint'] = str(value['geopoint'])
    self.render_json(job_dict)

class JobCreateHandler(BaseHandler):
  def post(self):
    user = users.get_current_user()
    if user:
      profile_key = ndb.Key('Profile',user.email())
      job = Jobs(parent=profile_key)
      job.company = self.request.get('company')
      job.address = self.request.get('address')
      job.geopoint = get_geo(self.request.get('address'))
      job.description = self.request.get('description')
      job.position = self.request.get('position')
      job.link = self.request.get('link')
      job.put()
      self.redirect('/jobs/')
  def get(self):
    self.redirect('/')

class JobUpdateHandler(BaseHandler):
  def post(self,job_id):
    user = users.get_current_user()
    if user:
      job = ndb.Key(urlsafe=job_id).get()
      job.company = self.request.get('company')
      job.address = self.request.get('address')
      job.geopoint = get_geo(self.request.get('address'))
      job.description = self.request.get('description')
      job.position = self.request.get('position')
      job.link = self.request.get('link')
      job.put()
      self.redirect('/jobs/')

    
class JobDeleteHandler(BaseHandler):
  def get(self,job_id):
    user = users.get_current_user()
    if user:
      job_key = ndb.Key(urlsafe=job_id)
      job = job_key.get()
      job.key.delete()
    self.redirect('/jobs/')    
  def delete(self,job_id):
    user = users.get_current_user()
    if user:
      job_key = ndb.Key(urlsafe=job_id)
      job = job.get()
      job.key.delete()

# Resumes
class ResumesHandler(BaseHandler):
  def get(self):
    resumes = Resumes.query().fetch()
    self.render_json(resumes)

class ResumeHandler(BaseHandler):
  def get(self,urlString):
    resume = ndb.Key(urlsafe=urlString).get()
    resume_dict = resume.to_dict()
    resume_dict['dateCreated'] = resume_dict['dateCreated'].strftime('%b %d, %Y')
    resume_dict['dateUpdated'] = resume_dict['dateUpdated'].strftime('%b %d, %Y')
    resume_dict['geopoint'] = str(resume_dict['geopoint'])
    self.render_json(resume_dict)
    
class ResumeCreateHandler(BaseHandler):
  def get(self):
    self.redirect('/')
  def post(self):
    user = users.get_current_user()
    if user:
      resume = Resumes(parent = ndb.Key('Profile',user.email()))
      resume.position = self.request.get('position')
      resume.address = self.request.get('address')
      resume.description = self.request.get('description')
      resume.geopoint = get_geo(self.request.get('address'))
      resume.link = self.request.get('link')
      resume.put()
      self.redirect('/resumes/')
    else:
      self.redirect('/')
    
class ResumeUpdateHandler(BaseHandler):
  def get(self):
    self.redirect('/')
  def post(self,resume_id):
    user = users.get_current_user()
    if user:
      resume_key = ndb.Key(urlsafe=resume_id)
      resume = resume_key.get()
      resume.position = self.request.get('position')
      resume.address = self.request.get('address')
      resume.description = self.request.get('description')
      resume.geopoint = get_geo(self.request.get('address'))
      resume.link = self.request.get('link')
      resume.put()
      self.redirect('/resumes/')
    
class ResumeDeleteHandler(BaseHandler):
  def get(self,resume_id):
    user = users.get_current_user()
    logout_url = users.create_logout_url(self.request.uri)
    login_url = users.create_login_url(self.request.uri)
    if user:
      resume_key = ndb.Key(urlsafe=resume_id)
      resume = resume_key.get()
      resume.key.delete()
      self.redirect('/resumes/')
    else:
      self.redirect('/')
      
  def delete(self,resume_id):
    user = users.get_current_user()
    if user:
      resume_key = ndb.Key(urlsafe=resume_id)
      resume = resume_key.get()
      resume.key.delete()
      self.redirect('/resumes/')
    else:
      self.redirect('/')
  
# Profiles
class ProfileHandler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    login_url = users.create_login_url()
    if user:
      profiles = Profile.query(Profile.user_id==user.user_id()).fetch()
      self.render_json(profiles)
    else:
      self.redirect('/')


class ProfileUpdateHandler(BaseHandler):
  def get(self):
    self.redirect('/profile/')
  def post(self,profile_id):
    user = users.get_current_user()
    if user:
      profile_key = ndb.Key(urlsafe=profile_id)
      profile = profile_key.get()
      profile.lastname = self.request.get('lastname')
      profile.firstname = self.request.get('firstname')
      profile.address = self.request.get('address')
      profile.geopoint = get_geo(self.request.get('address'))
      profile.link = self.request.get('link')
      profile_key = profile.put()
      self.redirect('/profile/')
    else:
      self.redirect('/')
      
class GeoHandler(BaseHandler):
  def get(self):
    geo = get_geo(self.request.get('address'))
    self.response.write(geo)


class Oauth2Handler(BaseHandler):
  def get(self):
    user = users.get_current_user()
    user_oauth = oauth.get_current_user()
    self.response.write(user_oauth)
    if user:
      client_id = "676481030478-0fi923mg6rbe1tqbvffr8n5ih56p63gg.apps.googleusercontent.com"
      client_secret = "AXSaN3iaVse0lL_GCRp7ioPQ"
      scope = urllib.unquote(self.request.get("scope")).decode("utf-8")
      redirect_uri = urllib.unquote(self.request.get("redirect_uri")).decode("utf-8")
      flow = Oauth2WebServerFlow(client_id, client_secret, scope,redirect_uri=redirect_uri)
      code = self.request.get("code")
      redirect_uri = "http://localhost:19080/oauth"
      grant_type = "authorization_code"
      form_fields = {
        "code" : code,
        "client_id" : client_id,
        "client_secret" : client_secret,
        "redirect_uri" : redirect_uri,
        "grant_type" : grant_type,
      }
      form_data = urllib.urlencode(form_fields)
      url_validator = "https://www.googleapis.com/oauth2/v1/tokeninfo"
      #url_validator = "https://www.googleapis.com/o/oauth2/token?access_token=" + code
      result = urlfetch.fetch(
        headers = {'Content-Type': 'application/x-www-form-urlencoded'},
        url = url_validator,
        payload = form_data,
        method = urlfetch.POST,
      )
      self.response.write(result.content)


app = webapp2.WSGIApplication([
  ('/', MainHandler),
  ('/geo',GeoHandler),
  ('/oauth2callback',Oauth2Handler),
  ('/job/create/', JobCreateViewHandler),
  ('/job/create', JobCreateHandler),
  ('/job/(.*)/update/', JobUpdateViewHandler),
  ('/job/(.*)/update', JobUpdateHandler),
  ('/job/(.*)/', JobDetailViewHandler),
  ('/job/(.*)/delete', JobDeleteHandler),
  ('/job/(.*)',JobHandler),
  ('/jobs/',JobsViewHandler),
  ('/jobs',JobsHandler),
  ('/resume/organization/create',ResumeOrganizationCreateHandler),
  ('/resume/organizations',ResumeOrganizationsHandler),
  ('/resume/create/', ResumeCreateViewHandler),
  ('/resume/create', ResumeCreateHandler),
  ('/resume/(.*)/update/', ResumeUpdateViewHandler),
  ('/resume/(.*)/update', ResumeUpdateHandler),
  ('/resume/(.*)/',ResumeDetailViewHandler),
  ('/resume/(.*)/delete', ResumeDeleteHandler),
  ('/resume/(.*)',ResumeHandler),
  ('/resumes/',ResumesViewHandler),
  ('/resumes',ResumesHandler),
  ('/profile/(.*)/update', ProfileUpdateHandler),
  ('/profile',ProfileHandler),
  ('/profile/',ProfileViewHandler),
  ('/search',SearchHandler),
  ('/profile/update/',ProfileUpdateViewHandler),
  (decorator.callback_path, decorator.callback_handler()),
], debug=True)





