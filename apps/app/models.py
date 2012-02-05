#!/usr/bin/python

import logging
import random

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from util.consts          import *
from util.model           import Model
from util.shopify         import ShopifyAPI

NUM_CLICK_SHARDS = 15

class App(Model, polymodel.PolyModel):
    # Unique identifier for memcache and DB key
    uuid        = db.StringProperty( required=True, indexed=True )
    
    # Datetime when this model was put into the DB
    created     = db.DateTimeProperty( required= True, auto_now_add=True, indexed=False )
    
    # Person who created/installed this App
    store       = db.ReferenceProperty( db.Model, required=False, collection_name='apps' )
    
    # Defaults to None, only set if this App has been deleted
    old_store   = db.ReferenceProperty( db.Model, required=False, collection_name='deleted_apps' )
    
    # Cached here so we don't need to fetch the 'store' Model
    store_url   = db.StringProperty(required=True, indexed = True)
    store_token = db.StringProperty(required=True, indexed = False)
    
    # Shopify's billing charge id
    charge_id   = db.StringProperty(required=True, indexed = True)

    # For Apps that use a click counter, this is the cached amount
    cached_clicks_count = db.IntegerProperty( default = 0, indexed=False )
    
    def __init__(self, *args, **kwargs):
        self._memcache_key = kwargs['uuid'] if 'uuid' in kwargs else None 
        super(App, self).__init__(*args, **kwargs)
    
    @staticmethod
    def _get_from_datastore(uuid):
        """Datastore retrieval using memcache_key"""
        return App.all().filter('uuid =', uuid).get()

    @staticmethod
    def get_by_uuid( uuid ):
        return App.all().filter('uuid =', uuid).get()

    def validateSelf( self ):
        # Subclasses should override this
        return

    def get_clicks_count(self):
        """Count this apps sharded clicks"""
        total = memcache.get(self.uuid+"AppClickCounter")
        if total is None:
            total = 0
            for counter in AppClickCounter.all().\
            filter('app_uuid =', self.uuid).fetch(NUM_CLICK_SHARDS):
                total += counter.count
            memcache.add(key=self.uuid+"AppClickCounter", value=total)
        return total
    
    def add_clicks(self, num):
        """add num clicks to this App's click counter"""
        def txn():
            index = random.randint(0, NUM_CLICK_SHARDS-1)
            shard_name = self.uuid + str(index)
            counter = AppClickCounter.get_by_key_name(shard_name)
            if counter is None:
                counter = AppClickCounter(key_name=shard_name, 
                                       app_uuid=self.uuid)
            counter.count += num
            counter.put()

        db.run_in_transaction(txn)
        memcache.incr(self.uuid+"AppClickCounter")

    def increment_clicks(self):
        """Increment this link's click counter"""
        self.add_clicks(1)

    # Shopify API Calls --------------------------------------------------------
    def install_webhooks(self, webhooks=None):
        """ Install the webhooks into the Shopify store """
        # pass extra webhooks as a list
        if webhooks == None:
            webhooks = []

        # Install the "App Uninstall" webhook
        data = {
            "webhook": {
                "address": "%s/a/webhook/uninstall?u=%s" % (
                    URL,
                    self.uuid
                ),
                "format": "json",
                "topic": "app/uninstalled"
            }
        }
        webhooks.append(data)

        ShopifyAPI.install_webhooks( self.class_name(), 
                                     self.store_url, 
                                     self.store_token,
                                     webhooks )
    
    def install_script_tags(self, script_tags=None):
        """ Install our script tags onto the Shopify store """
        if script_tags == None:
            script_tags = []
        
        ShopifyAPI.install_script_tags( self.class_name(), 
                                        self.store_url, 
                                        self.store_token,
                                        script_tags )
        
    def install_assets(self, assets=None):
        if assets == None:
            assets = []

        ShopifyAPI.install_script_tags( self.class_name(), 
                                        self.store_url, 
                                        self.store_token,
                                        assets )

    def activate_recurring_billing(self):
        ShopifyAPI.activate_recurring_charge( self.class_name(), 
                                              self.store_url, 
                                              self.store_token,
                                              charge_id )
    
    def delete( self ):
        # Turn off billing
        ShopifyAPI.delete_recurring_charge( self.class_name(),
                                            self.store_url,
                                            self.store_token,
                                            self.charge_id )
        # Mark App as 'deleted'
        self.old_store = self.store
        self.store     = None
        self.put()

## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
class AppClickCounter(db.Model):
    """Sharded counter for clicks"""

    app_uuid = db.StringProperty (indexed=True, required=True)
    count    = db.IntegerProperty(indexed=False, required=True, default=0)


