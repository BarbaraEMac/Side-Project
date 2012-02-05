#!/usr/bin/python

import logging, os
import inspect

from google.appengine.ext        import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from apps.store.models  import ShopifyStore

from util.consts        import *
from util.templates     import render 

class URIHandler( webapp.RequestHandler ):

    def __init__(self):
        # For simple caching purposes. Do not directly access this. Use self.get_store() instead.
        try:
            self.response.headers.add_header('P3P', P3P_HEADER)
        except:
            pass
        self.db_store = None

    # Return None if not authenticated.
    # Otherwise return db instance of store.
    def get_store(self):
        if self.db_store:
            return self.db_store

        return self.db_store
    
    def render_page(self, template_file_name, content_template_values, template_path=None):
        """This re-renders the full page with the specified template."""
        store = self.get_store()

        template_values = {
            'URL'   : URL,
            'store' : store
        }
        merged_values = dict(template_values)
        merged_values.update(content_template_values)
        
        path = os.path.join('templates/', template_file_name)
        
        app_path = self.get_app_path()

        if template_path != None:
            logging.info('got template_path: %s' % template_path)
            path = os.path.join(template_path, path)
        elif app_path != None:
            path = os.path.join(app_path, path)

        logging.info("Rendering %s" % path )
        self.response.headers.add_header('P3P', P3P_HEADER)
        return render(path, merged_values)

    def get_app_path(self):
        module = inspect.getmodule(self).__name__
        parts = module.split('.')
        app_path = None 
        
        if len(parts) > 2:
            if parts[0] == 'apps':
                # we have an app
                app_path = '/'.join(parts[:-1])

        return app_path

