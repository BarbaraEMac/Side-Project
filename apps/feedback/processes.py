#!/usr/bin/env python

import logging
import os

from apps.email.models    import Email
from apps.feedback.models import Feedback
from util.urihandler      import URIHandler

# The "Dos" ------------------------------------------------------------------
class FeedbackPost( URIHandler ):
    def post( self ):
        text  = self.request.get('text')
        email = self.request.get('email')
        
        # Make the feedback obj.
        Feedback.create( text, email )

        url = ''
        # Try to get url:
        try:
            url = urlparse(self.request.headers.get('referer'))
        except:
            pass

        if url == '':
            url = os.environ['HTTP_REFERER']

        # Email Barbara
        Email.emailBarbara( 'Feedback: %s\n%s\n%s' % (email, text, url) )

        self.response.out.write("Thanks!") 
