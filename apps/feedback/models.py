#!/usr/bin/env python
from google.appengine.ext import db
from util.helpers         import generate_uuid
from util.model           import Model

# ------------------------------------------------------------------------------
# Feedback Class Definition ---------------------------------------------------
# ------------------------------------------------------------------------------
class Feedback(Model):
    # Datetime when this model was put into the DB
    created = db.DateTimeProperty(required=True, auto_now_add=True, indexed=False)
    email   = db.StringProperty  (required=False, indexed=False)
    text    = db.TextProperty    (required=False, indexed=False)

    def __init__(self, *args, **kwargs):
        """ Initialize this model """
        self._memcache_key = generate_uuid(16)
        super(Feedback, self).__init__(*args, **kwargs)

    @staticmethod
    def create( text, email ):
        feedback = Feedback( text = text, email = email )
        feedback.put()
