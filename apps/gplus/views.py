#!/usr/bin/env python

import logging

from util.urihandler import URIHandler

# The "Shows" ------------------------------------------------------------------
class Gplus( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('coming_soon.html', template_values)) 
