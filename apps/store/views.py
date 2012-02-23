#!/usr/bin/env python

import logging

from apps.store.models import ShopifyStore

from util.consts     import URL
from util.helpers    import url
from util.shopify    import ShopifyAPI
from util.shopify_helpers import get_shopify_url
from util.urihandler import URIHandler

# The "Shows" ------------------------------------------------------------------
class Biller( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from Shopify
        store_url   = get_shopify_url( self.request.get( 'shop' ) )
        shopify_sig = self.request.get( 'signature' )
        store_token = self.request.get( 't' )

        # If we've already set up the app, redirect to welcome screen
        store = get_pinterest_by_url( store_url )
        if store != None:
            self.redirect( "%s?s_u=%s" % (url('Welcome'), store.uuid) )
            return

        # Get the store or create a new one
        store = ShopifyStore.get_or_create(store_url, store_token)
        
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


class BillingCallback( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from Shopify
        charge_id = self.request.get( 'charge_id' )
        store     = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        if ShopifyAPI.verify_recurring_charge( store.url, 
                                               store.token, 
                                               charge_id ):
            # Fetch or create the app
            app    = get_or_create_pinterest(store, charge_id)
            
            # Render the page
            template_values = {
                'app'        : app,
                'shop_owner' : store.full_name,
                'shop_name'  : store.name
            }

            self.redirect("%s?s_u=%s" % (url('Welcome'), store.uuid) )
        else:
            self.redirect( "%s?s_u=%s" % (url('BillingCancelled'), store.uuid) )


class BillingCancelled( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('cancelled.html', template_values)) 

class Welcome( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('welcome.html', template_values)) 



