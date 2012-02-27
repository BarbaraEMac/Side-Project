#!/usr/bin/python

import hashlib
import logging

from django.utils         import simplejson as json
from google.appengine.api   import memcache
from google.appengine.ext   import db

from util                   import httplib2
from util.consts            import *
from util.model             import Model
from util.helpers           import generate_uuid
from util.shopify_helpers import get_shopify_url
from util.shopify import ShopifyAPI

# ------------------------------------------------------------------------------
# ShopifyStore Class Definition ------------------------------------------------
# ------------------------------------------------------------------------------
class ShopifyStore( Model ):
    """A ShopifyStore or the website"""
    uuid    = db.StringProperty(indexed = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
    # Owner Properties
    full_name = db.StringProperty( indexed = False )
    email     = db.StringProperty( indexed = True )

    # Store properties
    name    = db.StringProperty( indexed = False )
    url     = db.LinkProperty  ( indexed = True )
    domain  = db.LinkProperty  ( indexed = True )
    token   = db.StringProperty( indexed = False )

    # Shopify's billing charge id
    charge_id = db.StringProperty( indexed = True )

    # Apps
    pinterest_enabled = db.BooleanProperty( indexed=False, default=False )
    facebook_enabled  = db.BooleanProperty( indexed=False, default=False )
    twitter_enabled   = db.BooleanProperty( indexed=False, default=False )
    fancy_enabled     = db.BooleanProperty( indexed=False, default=False )
    gplus_enabled     = db.BooleanProperty( indexed=False, default=False )
    tumblr_enabled    = db.BooleanProperty( indexed=False, default=False )
    
    # Uninstalled flag
    uninstalled       = db.BooleanProperty( indexed=True, default=False )

    def __init__(self, *args, **kwargs):
        self._memcache_key = kwargs['uuid'] if 'uuid' in kwargs else None 
        super(ShopifyStore, self).__init__(*args, **kwargs)
    
    @staticmethod
    def _get_from_datastore( uuid ):
        """Datastore retrieval using memcache_key"""
        return db.Query(ShopifyStore).filter('uuid =', uuid).get()
    
    def delete( self ):
        self.uninstalled = True
        self.put()

    # Accessors
    @staticmethod
    def get_by_email( email ):
        return ShopifyStore.all().filter( 'email =', email ).get()

    @staticmethod
    def get_by_uuid( uuid ):
        return ShopifyStore.all().filter( 'uuid =', uuid ).get()

    def validateSelf( self ):
        self.url = get_shopify_url( self.url )

    # Constructor
    @staticmethod
    def create( url_ ):
        url_ = get_shopify_url( url_ )
        logging.info('url :%s ' % url_)

        uuid = generate_uuid( 16 )

        store = ShopifyStore( key_name = uuid,
                              uuid     = uuid,
                              url      = url_ )
        return store
    
    def updateButtons( self, p, fb, tw, g, f, t ):
        self.pinterest_enabled = p
        self.facebook_enabled  = fb
        self.twitter_enabled   = tw
        self.gplus_enabled     = g
        self.fancy_enabled     = f
        self.tumblr_enabled    = t

        self.put()

    # Accessors 
    @staticmethod
    def get_by_url(store_url):
        store_url = get_shopify_url( store_url )

        store = ShopifyStore.all().filter( 'url =', store_url ).get()
        return store

    @staticmethod
    def get_or_create( store_url ):
        store = ShopifyStore.get_by_url( store_url )

        if not store:
            store = ShopifyStore.create( store_url ) 
        
        return store

    def get_clicks_count(self, app):
        """Count this apps sharded clicks"""
        total = memcache.get(self.uuid+app+"ClickCounter")
        if total is None:
            total = 0
            for counter in ClickCounter.all().\
            filter('app_uuid =', self.uuid).fetch(NUM_CLICK_SHARDS):
                total += counter.count
            memcache.add(key=self.uuid+app+"ClickCounter", value=total)
        return total

    def get_weekly_count(self, app):
        clicks = self.get_clicks_count(app)
        self.clear_clicks(app)

        return clicks
    
    def add_clicks(self, app, num):
        """add num clicks to this App's click counter"""
        def txn():
            index = random.randint(0, NUM_CLICK_SHARDS-1)
            shard_name = self.uuid + app + str(index)
            counter = ClickCounter.get_by_key_name(shard_name)
            if counter is None:
                counter = ClickCounter(key_name=shard_name, 
                                       app_uuid=self.uuid)
            counter.count += num
            counter.put()

        db.run_in_transaction(txn)
        memcache.incr(self.uuid+app+"ClickCounter")

    def increment_clicks(self, app):
        """Increment this link's click counter"""
        self.add_clicks(app, 1)

    def clear_clicks( self, app ):
        memcache.add(key=self.uuid+app+"ClickCounter", value=0)

        for i in range( 0, NUM_CLICK_SHARDS ):
            shard_name = self.uuid + app + str(i)
            counter = ClickCounter.get_by_key_name(shard_name)
            if counter:
                counter.count = 0
                counter.put()

    # Shopify API Calls  -------------------------------------------------------
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

        ShopifyAPI.install_webhooks( self.store_url, 
                                     self.store_token,
                                     webhooks )
    
    def install_script_tags(self, script_tags=None):
        """ Install our script tags onto the Shopify store """
        if script_tags == None:
            script_tags = []
        
        ShopifyAPI.install_script_tags( self.store_url, 
                                        self.store_token,
                                        script_tags )
        
    def install_assets(self, assets=None):
        if assets == None:
            assets = []

        ShopifyAPI.install_assets( self.store_url, 
                                   self.store_token,
                                   assets )

    def activate_recurring_billing(self):
        ShopifyAPI.activate_recurring_charge( self.store_url, 
                                              self.store_token,
                                              self.charge_id )

    def fetch_store_info(self, token):
        data = ShopifyAPI.fetch_store_info( self.url, token )
        
        domain = get_shopify_url( data['domain'] ) 
        if domain == '':
            domain = url_

        self.token     = token
        self.email     = data['email']
        self.name      = data['name']
        self.domain    = domain
        self.full_name = data['shop_owner']
    
        self.put()

    def get_cost( self ):
        cost = 0
        if self.pinterest_enabled:
            cost += 1
        if self.fancy_enabled:
            cost += 1
        if self.facebook_enabled:
            cost += 1
        if self.twitter_enabled:
            cost += 1
        if self.tumblr_enabled:
            cost += 1
        if self.gplus_enabled:
            cost += 1

        if cost == 0:
            return 0
        if cost == 1:
            return 0.99
        elif cost > 1:
            return 0.99 + (cost-1)*0.5

## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
class ClickCounter(db.Model):
    """Sharded counter for clicks"""

    app_uuid = db.StringProperty (indexed=True, required=True)
    count    = db.IntegerProperty(indexed=False, required=True, default=0)
