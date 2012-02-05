#!/usr/bin/env python

import logging

from apps.store.models     import ShopifyStore
from apps.pinterest.models import Pinterest

from util.consts     import PINTEREST_APP
from util.helpers    import url
from util.shopify    import ShopifyAPI
from util.urihandler import URIHandler

# The "Shows" ------------------------------------------------------------------
class Pinterest( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('pinterest.html', template_values)) 

class PinterestBiller( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from Shopify
        shopify_url  = self.request.get( 'shop' )
        store_token  = self.request.get( 't' )

        # If we've already set up the app, redirect to welcome screen
        if Pinterest.get_by_url( shopify_url ):
            self.redirect( url( 'PinterestWelcome' ) )

        settings = {
            "recurring_application_charge": {
                "price": 0.99,
                "name": "Pinterest+",
                "return_url": "%s/p/billing_callback?app_uuid=%s" % (URL, self.uuid)
              }
        }  

        redirect_url = ShopifyAPI.recurring_billing( PINTEREST_APP, 
                                                     store_url, 
                                                     store_token )
        
        self.redirect( redirect_url )


class PinterestBillingCallback( URIHandler ):
    # Renders a app page
    def get(self):
        charge_id  = self.request.get( 'charge_id' )

        # Request varZ from Shopify
        shopify_url  = self.request.get( 'shop' )
        shopify_sig  = self.request.get( 'signature' )
        store_token  = self.request.get( 't' )

        # Get the store or create a new one
        store = ShopifyStore.get_or_create(shopify_url, store_token, self, app)
        
        # Fetch or create the app
        app    = Pinterest.get_or_create(store, token, charge_id)
        
        # Render the page
        template_values = {
            'app'        : app,
            'shop_owner' : store.full_name,
            'shop_name'  : store.name
        }


        self.redirect( url('PinterestWelcome') )


class PinterestWelcome( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('welcome.html', template_values)) 
