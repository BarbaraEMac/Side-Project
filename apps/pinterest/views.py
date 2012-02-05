#!/usr/bin/env python

import logging
from urlparse              import urlparse


from apps.store.models     import ShopifyStore
from apps.pinterest.models import get_pinterest_by_url
from apps.pinterest.models import get_or_create_pinterest
from apps.pinterest.models import create_pinterest

from util.consts     import PINTEREST_APP
from util.consts     import SHOPIFY_APPS
from util.consts     import URL
from util.helpers    import url
from util.shopify    import ShopifyAPI
from util.shopify_helpers import get_shopify_url
from util.urihandler import URIHandler

# The "Shows" ------------------------------------------------------------------
class Pinterest( URIHandler ):
    def get( self ):
        template_values = { 'API_KEY' : SHOPIFY_APPS[PINTEREST_APP]['api_key'] }

        self.response.out.write(self.render_page('pinterest.html', template_values)) 

class PinterestBiller( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from Shopify
        store_url   = get_shopify_url( self.request.get( 'shop' ) )
        shopify_sig = self.request.get( 'signature' )
        store_token = self.request.get( 't' )

        # If we've already set up the app, redirect to welcome screen
        if get_pinterest_by_url( store_url ) != None:
            self.redirect( url( 'PinterestWelcome' ) )
            return

        # Get the store or create a new one
        store = ShopifyStore.get_or_create(store_url, store_token, PINTEREST_APP)
        
        settings = {
            "recurring_application_charge": {
                "price": 0.99,
                "name": "Pinterest+",
                'test' : True,
                "return_url": "%s/p/billing_callback?s_u=%s" % (URL, store.uuid)
              }
        }  

        redirect_url = ShopifyAPI.recurring_billing( PINTEREST_APP, 
                                                     store_url, 
                                                     store_token,
                                                     settings )
        
        self.redirect( redirect_url )


class PinterestBillingCallback( URIHandler ):
    # Renders a app page
    def get(self):
        # Request varZ from Shopify
        charge_id = self.request.get( 'charge_id' )
        store     = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        if ShopifyAPI.verify_recurring_charge( PINTEREST_APP, store.url, store.token, charge_id ):
            # Fetch or create the app
            app    = get_or_create_pinterest(store, charge_id)
            
            # Render the page
            template_values = {
                'app'        : app,
                'shop_owner' : store.full_name,
                'shop_name'  : store.name
            }


            self.redirect( url('PinterestWelcome') )
        else:
            self.redirect( url('PinterestBillingCancelled') )


class PinterestBillingCancelled( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('cancelled.html', template_values)) 

class PinterestWelcome( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('welcome.html', template_values)) 

class PinterestClick( URIHandler ):
    def get( self ):
        page_url  = urlparse( self.request.get( 'url' ) )
        domain    = "%s://%s" % (page_url.scheme, page_url.netloc)
        store_url = get_shopify_url( domain )

        app = get_pinterest_by_url( store_url )
        app.increment_clicks()
