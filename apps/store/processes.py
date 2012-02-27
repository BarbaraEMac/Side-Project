#!/usr/bin/env python

import logging
from urlparse               import urlparse

from apps.store.models      import ShopifyStore
from util.consts            import *
from util.shopify           import ShopifyAPI
from util.shopify_helpers   import get_shopify_url
from util.urihandler        import URIHandler

class StoreClick( URIHandler ):
    def get( self ):
        page_url  = urlparse( self.request.get( 'url' ) )
        domain    = "%s://%s" % (page_url.scheme, page_url.netloc)
        store = ShopifyStore.get_by_url( domain )
        app = self.request.get( 'app' )

        # Increment the total number of social shares
        store.increment_clicks( app )

class StoreSetup( URIHandler ):
    def post( self ):
        store_url = get_shopify_url( self.request.get('url') )

        store = ShopifyStore.get_by_url(store_url)

        if not store:
            store = ShopifyStore.create( store_url )
        
        store.updateButtons( self.request.get('pinterest') == 'true',
                             self.request.get('facebook') == 'true',
                             self.request.get('twitter') == 'true',
                             self.request.get('tumblr') == 'true',
                             self.request.get('fancy') == 'true',
                             self.request.get('gplus') == 'true' )

class StoreBiller( URIHandler ):
    def post( self ):

        store_url = get_shopify_url( self.request.get('url') )

        store = ShopifyStore.get_by_url(store_url)
        settings = {
            "recurring_application_charge": {
                "price": store.get_cost(),
                "name": "SocialPlus",
                'test' : True,
                "return_url": "%s/store/billing_callback?s_u=%s" % (URL, store.uuid)
              }
        }  

        redirect_url = ShopifyAPI.recurring_billing( store.url, 
                                                     store.token,
                                                     settings )
        self.response.out.write( redirect_url )

