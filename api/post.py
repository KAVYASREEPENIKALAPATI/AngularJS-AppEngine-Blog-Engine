#!/usr/bin/env python
import logging
import re
import webapp2

from google.appengine.ext import ndb
from webapp2_extras import json

from api import common
from api import tag as tag_module
from api.model import model


def _processPosts(posts):
    processedPosts = []
    for post in posts:
      currentPost = {'id': post.key.urlsafe(),
                     'date': post.date.strftime('%x'), 
                     'title': post.title,
                     'tags': [tag.tag for tag in ndb.get_multi(post.tags)],
                     'content': post.content,
                     'shortUrl': post.shortUrl,
                     'year': post.date.strftime('%Y'),
                     'month': post.date.strftime('%m'),
                     'day': post.date.strftime('%d'),
                     'hidden': post.hidden,
                     'dateCompressed': post.dateCompressed,
                    };
      processedPosts.append(currentPost)
    return processedPosts

def _getPostsRange(limit=None, offset=0, postSelector=None, tag=None):
    if postSelector:
      postsQuery = model.Post.query(ndb.AND(
        model.Post.dateCompressed == postSelector[0],
        model.Post.shortUrl == postSelector[1]))
      return postsQuery.fetch(1), False
    if tag:
      postsQuery = model.Post.query(
        ndb.AND(model.Post.tags == tag.key,
          model.Post.hidden == False)).order(-model.Post.date)
      return postsQuery.fetch(), False
    
    postsQuery = model.Post.query(model.Post.hidden == False).order(-model.Post.date)
    postsCount = postsQuery.count()
    posts = postsQuery.fetch(limit, offset=offset)
    return posts, True if limit and (limit + offset) < postsCount else False


class PostHandler(webapp2.RequestHandler):
    def get(self):
      try:
        path = self.request.path.split('/');
        postDate = '/'.join(path[4:7])
        postShortUrl = path[7]
      except:
        self.response.write(json.encode(common.getErrorObject('wrong input, ' + self.request.path)))
        return
      post = _getPostsRange(postSelector=[postDate, postShortUrl])[0]
      if not post:
        self.response.write(json.encode(common.getErrorObject('post not available')))
        return
      postFields = _processPosts(post)
      self.response.write(json.encode(
        common.getResponseObject((postFields, False), auth=common.isUserAuth())
        )
      )


class PostListHandler(webapp2.RequestHandler):
    def get(self):
      try:
        path = self.request.path.split('/');
        postOffset = int(path[4])
        postLimit = int(path[5])
      except:
        self.response.write(json.encode(common.getErrorObject('wrong input, ' + self.request.path)))
        return
      postsData = _getPostsRange(postLimit, postOffset)
      posts = postsData[0]
      more = postsData[1]
      if not posts:
        self.response.write(json.encode(common.getErrorObject('no available posts')))
        return
      postsFields = _processPosts(posts)
      self.response.write(json.encode(common.getResponseObject((postsFields, more))))


class PostTagHandler(webapp2.RequestHandler):
    def get(self):
      try:
        path = self.request.path.split('/');
        tag = path[4]
      except:
        self.response.write(json.encode(common.getErrorObject('wrong input, ' + self.request.path)))
        return
      tag_obj = tag_module.getTags(tag=tag)[0]
      postsData = _getPostsRange(tag=tag_obj)
      posts = postsData[0]
      more = postsData[1]
      if not posts:
        self.response.write(json.encode(common.getErrorObject('no available posts')))
        return
      postsFields = _processPosts(posts)
      self.response.write(json.encode(common.getResponseObject((postsFields, more))))


class PostAddHandler(webapp2.RequestHandler):
    def post(self):
      if not common.isUserAuth():
        self.response.write('Sorry, you must login as admin first.')
        return
      formData = json.decode(self.request.body)
      if formData['edit']:
        post = _getPostsRange(postSelector=[formData['dateCompressed'], formData['short_url']])[0][0]
      else:
        post = model.Post()
      title = formData['title']
      post.title = title
      post.shortUrl = formData['short_url']
      if not post.shortUrl:
        post.shortUrl = re.sub('[^a-zA-Z0-9]', '-', title)
      post.content = formData['content']
      post.hidden = bool(int(formData['hidden']))
      
      post.tags = []
      logging.info(formData['tags'])
      all_tags_objs = tag_module.getTags()
      all_tags_text = set([tag.tag for tag in all_tags_objs])
      post_tags_text = set([text.strip() for text in formData['tags'].split(',')])
      
      new_tags_text = post_tags_text - all_tags_text
      for tag in new_tags_text:
        tag_obj = model.Tag(tag=tag)
        tag_obj.put()
        post.tags.append(tag_obj.key)
      for tag in all_tags_objs: 
        if tag.tag in post_tags_text:
          post.tags.append(tag.key)
      
      post.put()
      self.response.write('Post correctly added.');
      return


app = webapp2.WSGIApplication([
  (r'/api/posts/list/.+', PostListHandler),
	(r'/api/posts/tag/.+', PostTagHandler),
	(r'/api/posts/id/.+', PostHandler),
  (r'/api/posts/add.*', PostAddHandler)
], debug=True)
