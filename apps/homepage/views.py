#!/usr/bin/python

from google.appengine.ext import webapp

from google.appengine.api.datastore_errors import BadValueError

from util.urihandler import URIHandler

class ShowLandingPage(URIHandler):
    # Renders the main template
    def get(self, page):
        template_values = { }
        
        self.response.out.write(self.render_page('landing.html', template_values))

