#!/usr/bin/env python

import logging

from apps.feedback.models import Feedback
from util.urihandler      import URIHandler

# The "Shows" ------------------------------------------------------------------
class Feedback( URIHandler ):
    def get( self ):
        uuid = self.request.get( 's_u' )
        if uuid != "":
            store = ShopifyStore.get_by_uuid( uuid )
        else:
            store = None
        template_values = { "store" : store }

        self.response.out.write(self.render_page('feedback.html', template_values)) 
