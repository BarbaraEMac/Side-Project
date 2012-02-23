#!/usr/bin/env python

import logging
from urlparse              import urlparse

from apps.pinterest.models import get_pinterest_by_url
from apps.store.models     import ShopifyStore
from util.shopify_helpers  import get_shopify_url

from util.urihandler import URIHandler

class StoreClick( URIHandler ):
    def post( self ):
        page_url  = urlparse( self.request.get( 'url' ) )
        domain    = "%s://%s" % (page_url.scheme, page_url.netloc)
        store_url = get_shopify_url( domain )

        app = get_pinterest_by_url( store_url )

        # Increment the total number of social shares
        app.increment_clicks()

class StoreSetup( URIHandler ):
    def post( self ):
        store_url = get_shopify_url( self.request.get('url') )

        store = ShopifyStore.get_by_url(store_url)

        if not store:
            store = ShopifyStore.create( store_url )
        
        logging.error(self.request.get('pinterest') )

        store.updateButtons( self.request.get('pinterest') == 'true',
                             self.request.get('facebook') == 'true',
                             self.request.get('twitter') == 'true',
                             self.request.get('tumblr') == 'true',
                             self.request.get('fancy') == 'true',
                             self.request.get('gplus') == 'true' )

        return store

