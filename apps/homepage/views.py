#!/usr/bin/python

from google.appengine.api import memcache
from google.appengine.ext import webapp

from util.urihandler import URIHandler

class ShowLandingPage(URIHandler):
    # Renders the main template
    def get(self, page):
        memcache.set('reload_uris', True)
        flushed = memcache.flush_all()

        template_values = { }
        
        self.response.out.write(self.render_page('landing.html', template_values))

