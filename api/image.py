import logging
import os
import api.cloudstorage as gcs
import webapp2

from webapp2_extras import json

from api.model import model
from api import common
from google.appengine.api import images
from google.appengine.ext import blobstore

_BUCKET = '/francesco_uploads'


class ImageUploadHandler(webapp2.RequestHandler):
    def _createFile(self, file_type, filename, data):
        logging.info('Creating file %s.\n' % filename)

        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open(filename,
            'w',
            content_type=file_type,
            options={'x-goog-meta-foo': 'foo', 'x-goog-meta-bar': 'bar'},
            retry_params=write_retry_params)
        gcs_file.write(data)
        gcs_file.close()
        logging.info('File created.')

    def post(self):
        if not common.isUserAuth():
            self.response.write('Sorry, you must login as admin first.')
            return
        file = self.request.POST['file']
        self._createFile(file.type, _BUCKET + '/' + file.filename, file.value)
        self.response.write('File uploaded successfully.')


class ImageListHandler(webapp2.RequestHandler):
    def get(self):
        if not common.isUserAuth():
            self.response.write('Sorry, you must login as admin first.')
            return
        self.response.write('Listbucket directory mode result:\n')
        for stat in gcs.listbucket(_BUCKET, delimiter='/'):
            self.response.write('%r' % stat)
            self.response.write('\n')
            if stat.is_dir:
                for subdir_file in gcs.listbucket(stat.filename, delimiter='/'):
                    self.response.write('  %r' % subdir_file)
                    self.response.write('\n')


class ImageReadHandler(webapp2.RequestHandler):
    def get(self):
        try:
            path = self.request.path.split('/');
            filename = path[4]
        except:
            logging.info('invalid filename.')
            self.error(404)
            return
        blob_key = blobstore.create_gs_key('/gs' + _BUCKET + '/' + filename)
        img_url = images.get_serving_url(blob_key=blob_key)
        logging.info('redirect to image address %s', img_url)
        self.redirect(img_url)


app = webapp2.WSGIApplication([
    (r'/api/image/upload', ImageUploadHandler),
    (r'/api/image/list', ImageListHandler),
    (r'/api/image/read.*', ImageReadHandler)
], debug=True)