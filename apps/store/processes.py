#!/usr/bin/env python

import logging
from urlparse              import urlparse

from apps.pinterest.models import get_pinterest_by_url
from util.shopify_helpers  import get_shopify_url

from util.urihandler import URIHandler

class Click( URIHandler ):
    def get( self ):
        page_url  = urlparse( self.request.get( 'url' ) )
        domain    = "%s://%s" % (page_url.scheme, page_url.netloc)
        store_url = get_shopify_url( domain )

        app = get_pinterest_by_url( store_url )

        # Increment the total number of social shares
        app.increment_clicks()

