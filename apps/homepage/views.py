#!/usr/bin/python

from google.appengine.api import memcache
from google.appengine.ext import webapp

from util.urihandler import URIHandler

class ShowLandingPage(URIHandler):
    def get(self, page):
        # TODO: TAKE OUT
        memcache.set('reload_uris', True)
        flushed = memcache.flush_all()

        template_values = { }
        
        self.response.out.write(self.render_page('landing.html', template_values))

class ShowMorePage(URIHandler):
    def get(self):
        template_values = { }
        
        self.response.out.write(self.render_page('more.html', template_values))

class ShowSelectPage(URIHandler):
    def get(self):
        template_values = { }
        
        self.response.out.write(self.render_page('select.html', template_values))

