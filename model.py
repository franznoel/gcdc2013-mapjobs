from google.appengine.ext import ndb

class ModelUtils(object):
  def to_dict(self):
    result = super(ModelUtils,self).to_dict()
    result['urlsafe'] = self.key.urlsafe()
    #result['key'] = self.key
    result['id'] = self.key.id()
    return result

class Jobs(ModelUtils,ndb.Model):
  company = ndb.StringProperty(indexed=True)
  position = ndb.StringProperty(indexed=True)
  address = ndb.TextProperty()
  description = ndb.TextProperty()
  link = ndb.TextProperty()
  geopoint = ndb.GeoPtProperty()
  organization = ndb.JsonProperty()
  dateCreated = ndb.DateTimeProperty(auto_now_add=True)
  dateUpdated = ndb.DateTimeProperty(auto_now=True)
  
class Resumes(ModelUtils,ndb.Model):
  position = ndb.StringProperty(indexed=True)
  link = ndb.TextProperty()
  address = ndb.TextProperty()
  description = ndb.TextProperty()
  geopoint = ndb.GeoPtProperty()
  organization = ndb.JsonProperty()
  dateCreated = ndb.DateTimeProperty(auto_now_add=True)
  dateUpdated = ndb.DateTimeProperty(auto_now=True)
  

class ResumeOrganizations(ModelUtils,ndb.Model):
  startDate = ndb.StringProperty()
  endDate = ndb.StringProperty()
  description = ndb.StringProperty()
  name = ndb.StringProperty(indexed=True) #organizationName
  title = ndb.StringProperty(indexed=True)
  primary = ndb.BooleanProperty()
  location = ndb.StringProperty()
  department = ndb.StringProperty()
  type = ndb.StringProperty()
  dateCreated = ndb.DateTimeProperty(auto_now_add=True)
  dateUpdated = ndb.DateTimeProperty(auto_now=True)

class Profile(ModelUtils,ndb.Model):
  user_id = ndb.StringProperty(indexed=True)
  lastname = ndb.StringProperty(indexed=True)
  firstname = ndb.StringProperty(indexed=True)
  email = ndb.TextProperty()
  address = ndb.TextProperty()
  geopoint = ndb.GeoPtProperty()
  link = ndb.StringProperty()
  dateCreated = ndb.DateTimeProperty(auto_now_add=True)
  dateUpdated = ndb.DateTimeProperty(auto_now=True)
  
  