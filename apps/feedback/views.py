#!/usr/bin/env python

import logging

from apps.feedback.models import Feedback
from util.urihandler      import URIHandler

# The "Shows" ------------------------------------------------------------------
class Feedback( URIHandler ):
    def get( self ):
        template_values = { }

        self.response.out.write(self.render_page('feedback.html', template_values)) 
