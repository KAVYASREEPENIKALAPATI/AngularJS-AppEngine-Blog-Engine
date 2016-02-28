"""Common methods used by most of the classes."""
from google.appengine.api import users
from api import config

def is_user_auth():
    """Checks if the user is authorize to perfom admin functions."""
    user = users.get_current_user()
    if user and user.nickname() == config.ADMIN_USERNAME:
        return True
    return False

def get_error_object(error_message):
    """Formats an error object to be returned in JSON."""
    obj = {'status': 'error', 'payload': 'Error: ' + error_message}
    return obj

def get_response_object(payload, auth=None):
    """Formats a valid object to be returned in JSON."""
    obj = {'status': 'ok', 'payload': payload, 'auth': auth}
    return obj
