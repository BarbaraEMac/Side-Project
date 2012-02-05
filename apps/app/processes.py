#!/usr/bin/env python

import logging, re, hashlib, urllib

from apps.app.models        import App
from apps.email.models      import Email

from util.helpers           import *
from util.urihandler        import URIHandler
from util.consts            import *

class DoUninstallApp( URIHandler ):
    def post(self, app_name):
        # Grab the ShopifyApp
        store_url = self.request.headers['X-Shopify-Shop-Domain']
        logging.info("store: %s " % store_url)
        app = App.get_by_uuid( self.request.get('u') )
        
        Email.emailBarbara("UNinstall app: %s\n%r %s" % (
                app.class_name(),
                self.request, 
                self.request.headers
            )
        )

        app.delete()
