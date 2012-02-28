#!/usr/bin/env python

import logging

from urlparse               import urlparse

from apps.analytics.models  import Analytics_ThisWeek
from apps.store.models      import ShopifyStore
from util.consts            import *
from util.shopify           import ShopifyAPI
from util.shopify_helpers   import get_shopify_url
from util.urihandler        import URIHandler

class StoreClick( URIHandler ):
    def get( self ):
        app      = self.request.get( 'app' )
        url      = self.request.get( 'url' )
        page_url = urlparse( url )
        domain   = "%s://%s" % (page_url.scheme, page_url.netloc)
        store    = ShopifyStore.get_by_url( domain )

        # Increment the total number of social shares
        Analytics_ThisWeek.add_new( store, app, url )

class StoreSetup( URIHandler ):
    def post( self ):

        store = ShopifyStore.get_by_url( self.request.get('url') )

        if not store:
            logging.info("making a new store")
            store = ShopifyStore.create( store_url )
        
        store.update_buttons( self.request.get('pinterest') == 'true',
                             self.request.get('facebook') == 'true',
                             self.request.get('twitter') == 'true',
                             self.request.get('tumblr') == 'true',
                             self.request.get('fancy') == 'true',
                             self.request.get('gplus') == 'true' )

        logging.info('TOKEN: %s'% store.token)

class StoreBiller( URIHandler ):
    def post( self ):

        store = ShopifyStore.get_by_url( self.request.get('url') )
        settings = {
            "recurring_application_charge": {
                "price": store.get_cost(),
                "name": "Social ++ Shopify App",
                'test' : True,
                "return_url": "%s/store/billing_callback?s_u=%s" % (URL, store.uuid)
              }
        }  

        redirect_url = ShopifyAPI.recurring_billing( store.url, 
                                                     store.token,
                                                     settings )
        self.response.out.write( redirect_url )

class StoreOneTime( URIHandler ):
    def post( self ):

        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )

        settings = {
            "application_charge": {
                "price": 5.00,
                "name": "Customization & Support",
                'test' : True,
                "return_url": "%s/store/onetime_callback?s_u=%s" % (URL, store.uuid)
              }
        }  

        redirect_url = ShopifyAPI.onetime_charge( store.url, 
                                                  store.token,
                                                  settings )
        self.response.out.write( redirect_url )

class StoreUninstall( URIHandler ):
    def get(self):
        return self.post()

    def post( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )

        store.delete()
        
        Email.emailBarbara(
            'Unistall: %s %s %s' % (
                self.uuid,
                self.name,
                self.url
            )
        )

