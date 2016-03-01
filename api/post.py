"""Manages all the posts-related actions, i.e. add/edit/view/list."""
import re
import webapp2

from google.appengine.ext import ndb
from webapp2_extras import json

from api import common
from api import tag as tag_module
from api.model import model


def process_posts(posts):
    """Processes POST objects and returns a dict for each post."""
    processed_posts = []
    for post in posts:
        current_post = {'id': post.key.urlsafe(),
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
                       }
        processed_posts.append(current_post)
    return processed_posts


def get_posts_range(limit=None, offset=0, post_selector=None, tag=None):
    """Returns POSTS according to the parameters."""
    if post_selector:
        posts_query = model.Post.query(ndb.AND(
            model.Post.dateCompressed == post_selector[0],
            model.Post.shortUrl == post_selector[1]))
        return posts_query.fetch(1), False
    if tag:
        posts_query = model.Post.query(ndb.AND(
            model.Post.tags == tag.key,
            model.Post.hidden == False)).order(-model.Post.date)
        return posts_query.fetch(), False
    posts_query = model.Post.query(
        model.Post.hidden == False).order(-model.Post.date)
    posts_count = posts_query.count()
    if limit:
        posts = posts_query.fetch(limit, offset=offset)
    else:
        posts = posts_query.fetch(offset=offset)
    return posts, True if limit and (limit + offset) < posts_count else False


class PostHandler(webapp2.RequestHandler):
    """Handles single post view."""
    def get(self, date, short_url): # pylint: disable=C0111
        if not (date and short_url):
            self.response.write(json.encode(common.get_error_object(
                'wrong input, ' + self.request.path)))
            return
        post = get_posts_range(post_selector=[date, short_url])[0]
        if not post:
            self.response.write(json.encode(common.get_error_object(
                'post not available')))
            return
        post_fields = process_posts(post)
        self.response.write(json.encode(common.get_response_object(
            (post_fields, False), auth=common.is_user_auth())))
        return


class PostListHandler(webapp2.RequestHandler):
    """Handles list all posts."""
    def get(self, offset, limit): # pylint: disable=C0111
        if not (offset and limit):
            self.response.write(json.encode(common.get_error_object(
                'wrong input, ' + self.request.path)))
            return
        posts_data = get_posts_range(int(limit), int(offset))
        posts = posts_data[0]
        more = posts_data[1]
        if not posts:
            self.response.write(json.encode(common.get_error_object(
                'no available posts')))
            return
        posts_fields = process_posts(posts)
        self.response.write(json.encode(common.get_response_object((
            posts_fields, more))))
        return


class PostTagHandler(webapp2.RequestHandler):
    """Handles list all posts for a tag."""
    def get(self, tag): # pylint: disable=C0111
        if not tag:
            self.response.write(json.encode(common.get_error_object(
                'wrong input, ' + self.request.path)))
            return
        try:
            tag_obj = tag_module.get_tags(tag=tag)[0]
        except Exception:
            self.response.write(json.encode(common.get_error_object(
                'Tag not available')))
            return
        posts_data = get_posts_range(tag=tag_obj)
        posts = posts_data[0]
        more = posts_data[1]
        if not posts:
            self.response.write(json.encode(common.get_error_object(
                'no available posts')))
            return
        posts_fields = process_posts(posts)
        self.response.write(json.encode(common.get_response_object((
            posts_fields, more))))
        return


class PostAddHandler(webapp2.RequestHandler):
    """Handles add/edit posts."""
    def post(self): # pylint: disable=C0111
        if not common.is_user_auth():
            self.response.write('Sorry, you must login as admin first.')
            return

        form_data = json.decode(self.request.body)
        if form_data['edit']:
            post = get_posts_range(post_selector=
                                   [form_data['dateCompressed'],
                                    form_data['short_url']])[0][0]
        else:
            post = model.Post()

        title = form_data['title']
        post.title = title
        post.shortUrl = form_data['short_url']
        if not post.shortUrl:
            post.shortUrl = re.sub('[^a-zA-Z0-9]', '-', title)
        post.content = form_data['content']
        post.hidden = bool(int(form_data['hidden']))

        post.tags = []
        all_tags_objs = tag_module.get_tags()
        all_tags_text = set([tag.tag for tag in all_tags_objs])
        post_tags_text = set(
            [text.strip() for text in form_data['tags'].split(',')])
        new_tags_text = post_tags_text - all_tags_text
        for tag in new_tags_text:
            tag_obj = model.Tag(tag=tag)
            tag_obj.put()
            post.tags.append(tag_obj.key)
        for tag in all_tags_objs:
            if tag.tag in post_tags_text:
                post.tags.append(tag.key)

        post.put()
        self.response.write('Post correctly added.')
        return

ROUTES = [webapp2.Route(r'/api/posts/tag/<tag:.+>', handler=PostTagHandler),
          webapp2.Route(r'/api/posts/list/<offset:\d+>/<limit:\d+>',
                        handler=PostListHandler),
          webapp2.Route(
              r'/api/posts/id/<date:\d{4}/\d{2}/\d{2}>/<short_url:.+>',
              handler=PostHandler),
          webapp2.Route(r'/api/posts/add', handler=PostAddHandler),
         ]
APP = webapp2.WSGIApplication(routes=ROUTES, debug=True)
