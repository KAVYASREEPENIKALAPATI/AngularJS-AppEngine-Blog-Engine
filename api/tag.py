import logging

import webapp2

from webapp2_extras import json

from api.model import model
from api import common

def getTags(tag=None):
    if not tag:
        tagsQuery = model.Tag.query().order(model.Tag.tag)
    else:
        tagsQuery = model.Tag.query(model.Tag.tag == tag)
    return tagsQuery.fetch()

class TagListHandler(webapp2.RequestHandler):
    def get(self):
        tags = getTags()
        tagsDict = []
        for tag in tags:
            currentTag = {'tag': tag.tag}
            tagsDict.append(currentTag)
        self.response.write(json.encode(common.getResponseObject(tagsDict)))


app = webapp2.WSGIApplication([
    (r'/api/tags/list', TagListHandler),
], debug=True)