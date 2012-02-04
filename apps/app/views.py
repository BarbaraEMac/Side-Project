#!/usr/bin/env python

from apps.app.models            import * 
from apps.client.shopify.models import ClientShopify

from util.helpers               import *
from util.urihandler            import URIHandler
from util.consts                import *

# The "Dos" --------------------------------------------------------------------
class DoDeleteApp( URIHandler ):
    def post( self ):
        client   = self.get_client()
        app_uuid = self.request.get( 'app_uuid' )
        
        logging.info('app id: %s' % app_uuid)
        app = get_app_by_id( app_uuid )
        if app.client.key() == client.key():
            logging.info('deelting')
            app.delete()
        
        self.redirect( '/client/account' )

# The "Shows" ------------------------------------------------------------------
class ShopifyRedirect( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from us
        app          = self.request.get( 'app' )
        
        # Request varZ from Shopify
        shopify_url  = self.request.get( 'shop' )
        shopify_sig  = self.request.get( 'signature' )
        store_token  = self.request.get( 't' )
        shopify_timestamp = self.request.get( 'timestamp' )

        # Get the store or create a new one
        client = ClientShopify.get_or_create(shopify_url, store_token, self, app)
        
        # Cache the client!
        self.db_client = client

        # TODO: apps on shopify have to direct properly
        # the app name has to corespond to AppnameWelcome view
        redirect_url = url('%sWelcome' % app)

        if redirect_url != None:
            redirect_url = '%s?%s' % (redirect_url, self.request.query_string)
        else:
            redirect_url = '/'
        logging.info("redirecting app %s to %s" % (app, redirect_url))
        
        self.redirect(redirect_url)

