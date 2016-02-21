from google.appengine.api import users

def isUserAuth():
  user = users.get_current_user()
  if user and user.nickname() == 'pongiof':
    return True
  return False

def getErrorObject(errorMessage):
	obj = {'status': 'error', 'payload': 'Error: ' + errorMessage} 
   	return obj

def getResponseObject(payload, auth=None):
	obj = {'status': 'ok', 'payload': payload, 'auth': auth}
	return obj 