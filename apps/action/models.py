#!/usr/bin/env/python

# The Action Model

import datetime, logging
import random

from google.appengine.api    import memcache
from google.appengine.api    import datastore_errors 
from google.appengine.datastore import entity_pb
from google.appengine.ext    import db
from google.appengine.ext.db import polymodel

from util.consts             import *
from util.helpers            import generate_uuid
from util.model              import Model

## -----------------------------------------------------------------------------
## Action SuperClass -----------------------------------------------------------
## -----------------------------------------------------------------------------
class Action(Model, polymodel.PolyModel):
    
    # Unique identifier for memcache and DB key
    uuid            = db.StringProperty( indexed = True )
    
    # Datetime when this model was put into the DB
    created         = db.DateTimeProperty( auto_now_add=True )
    
    # The App that this Action is for
    app_            = db.ReferenceProperty( db.Model, collection_name = 'app_actions' )
    
    def __init__(self, *args, **kwargs):
        self._memcache_key = kwargs['uuid'] if 'uuid' in kwargs else None 
        super(Action, self).__init__(*args, **kwargs)
    
    @classmethod
    def _get_from_datastore(cls, uuid):
        """Datastore retrieval using memcache_key"""
        return Action.all().filter('uuid =', uuid).get()

    @staticmethod
    def get_by_uuid( uuid ):
        return Action.get(uuid)

    @staticmethod
    def get_by_app( app, admins_too = False ):
        if admins_too:
            return Action.all().filter( 'app_ =', app ).get()
        else:
            return Action.all().filter( 'app_ =', app ).filter('is_admin =', False).get()

