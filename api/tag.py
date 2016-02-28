"""Manages tags."""
import webapp2

from webapp2_extras import json

from api.model import model
from api import common

def get_tags(tag=None):
    """Returns a list of available tags."""
    if not tag:
        tags_query = model.Tag.query().order(model.Tag.tag)
    else:
        tags_query = model.Tag.query(model.Tag.tag == tag)
    return tags_query.fetch()


class TagListHandler(webapp2.RequestHandler):
    """Handles tag list requests."""
    def get(self): # pylint: disable=C0111
        tags = get_tags()
        tags_dict = []
        for tag in tags:
            current_tag = {'tag': tag.tag}
            tags_dict.append(current_tag)
        self.response.write(json.encode(common.get_response_object(tags_dict)))


APP = webapp2.WSGIApplication([
    (r'/api/tags/list', TagListHandler),
], debug=True)
