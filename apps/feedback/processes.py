#!/usr/bin/env python

import logging
import os

from apps.email.models    import Email
from apps.feedback.models import Feedback
from util.urihandler      import URIHandler

# The "Dos" ------------------------------------------------------------------
class FeedbackPost( URIHandler ):
    def post( self ):
        title = self.request.get('title')
        text  = self.request.get('text')
        email = self.request.get('email')
        owner = self.request.get('owner')
        store_name = self.request.get('store_name')
        store_url  = self.request.get('store_url')
        
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
        Email.emailBarbara( '<p>[%s]:</p> <p>%s: %s</p> <p>%s</p> <p>%s</p> <p>%s</p><p>%s</p><p>%s</p>' % (title, owner, email, text, store_name, store_url, url) )

        self.response.out.write("Thanks!") 
