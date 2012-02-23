#!/usr/bin/env python

import logging

from apps.store.models      import ShopifyStore

from util.consts            import URL
from util.helpers           import url
from util.shopify           import ShopifyAPI
from util.shopify_helpers   import get_shopify_url
from util.urihandler        import URIHandler

# The "Shows" ------------------------------------------------------------------
class StoreBiller( URIHandler ):
    def get(self):
        # Request varZ from Shopify
        store_url   = get_shopify_url( self.request.get( 'shop' ) )
        shopify_sig = self.request.get( 'signature' )
        store_token = self.request.get( 't' )

        # Get the store or create a new one
        store = ShopifyStore.get_or_create(store_url, store_token)
        
        # If we've already set up the app, redirect to welcome screen
        if store.charge_id != None:
            self.redirect( "%s?s_u=%s" % (url('Welcome'), store.uuid) )
            return
        
        # Fetch store info
        store.fetch_store_info( token ) 
        
        settings = {
            "recurring_application_charge": {
                "price": 0.99,
                "name": "+",
                'test' : True,
                "return_url": "%s/p/billing_callback?s_u=%s" % (URL, store.uuid)
              }
        }  

        redirect_url = ShopifyAPI.recurring_billing( store_url, 
                                                     store_token,
                                                     settings )
        
        self.db_client = store
        self.redirect( redirect_url )

class StoreBillingCallback( URIHandler ):
    def get(self):
        # Request varZ from Shopify
        charge_id = self.request.get( 'charge_id' )
        store     = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        if ShopifyAPI.verify_recurring_charge( store.url, 
                                               store.token, 
                                               charge_id ):
            store.charge_id = charge_id
            store.put()
            
            self.redirect("%s?s_u=%s" % (url('Welcome'), store.uuid) )
        
        else:
            self.redirect( "%s?s_u=%s" % (url('BillingCancelled'), store.uuid) )

class StoreBillingCancelled( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('cancelled.html', template_values)) 

class StoreWelcome( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('welcome.html', template_values)) 



