"""Manages image upload and serving."""

import logging
import api.cloudstorage as gcs
import webapp2

from api import config
from api import common
from google.appengine.api import images
from google.appengine.ext import blobstore


def _create_file(file_type, filename, data):
    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(filename, 'w',
                        content_type=file_type,
                        options={
                            'x-goog-meta-foo': 'foo',
                            'x-goog-meta-bar': 'bar'},
                        retry_params=write_retry_params)
    gcs_file.write(data)
    gcs_file.close()
    logging.info('File created.')


class ImageUploadHandler(webapp2.RequestHandler):
    """Handles image upload requests."""

    def post(self): # pylint: disable=C0111
        if not common.is_user_auth():
            self.response.write('Sorry, you must login as admin first.')
            return
        file_data = self.request.POST['file']
        _create_file(file_data.type, config.BUCKET + '/' + file_data.filename,
                     file_data.value)
        self.response.write('File uploaded successfully.')


class ImageReadHandler(webapp2.RequestHandler):
    """Handles image read requests."""
    def get(self): # pylint: disable=C0111
        try:
            path = self.request.path.split('/')
            filename = path[4]
        except Exception:
            logging.info('invalid filename.')
            self.error(404)
            return
        blob_key = blobstore.create_gs_key('/gs' + config.BUCKET + '/' +
                                           filename)
        img_url = images.get_serving_url(blob_key=blob_key)
        logging.info('redirect to image address %s', img_url)
        self.redirect(img_url)


APP = webapp2.WSGIApplication([
    (r'/api/image/upload', ImageUploadHandler),
    (r'/api/image/read.*', ImageReadHandler)
], debug=True)
