#!/usr/bin/python

import hashlib
import logging

from django.utils           import simplejson as json
from google.appengine.api   import memcache
from google.appengine.ext   import db

from apps.email.models      import Email
from apps.store.scripts     import *

from util                   import httplib2
from util.consts            import *
from util.helpers           import generate_uuid
from util.model             import Model
from util.shopify_helpers   import get_shopify_url
from util.shopify           import ShopifyAPI

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

    # Shopify API Calls  -------------------------------------------------------
    def do_install( self ):
        # Define our asset 
        scripts = buttons = appsy_scripts = ""
        
        if self.pinterest_enabled:
            scripts += pinterest_script 
            buttons += '\n%s' % pinterest_button
            appsy_scripts += appsy_pinterest_script
        
        if self.fancy_enabled:
            scripts += fancy_script 
            buttons += '\n%s' % fancy_button
            appsy_scripts += appsy_fancy_script
        
        if self.facebook_enabled:
            scripts += facebook_script 
            buttons += '\n%s' % facebook_button
            appsy_scripts += appsy_facebook_script
        
        if self.tumblr_enabled:
            scripts += tumblr_script 
            buttons += '\n%s' %  tumblr_button
            appsy_scripts += appsy_tumblr_script
        
        if self.gplus_enabled:
            scripts += gplus_script 
            buttons += '\n%s' % gplus_button
            appsy_scripts += appsy_gplus_script
        
        if self.twitter_enabled:
            scripts += twitter_script 
            buttons += '\n%s' % twitter_button
            appsy_scripts += appsy_twitter_script
        
        div = "\n\n<div id='AppsyDaisy' style='float: left;'>%s\n</div>\n" % buttons

        liquid_assets = [{
            'asset': {
                'value': "%s %s %s" % (div, scripts, appsy_scripts),
                'key': 'snippets/social_plus.liquid'
            }
        }]

        # Install yourself in the Shopify store
        self.install_webhooks( webhooks = None )
        self.install_assets( assets = liquid_assets )
        
        self.activate_recurring_billing( )

        Email.welcomeClient( self.email, 
                             self.full_name, 
                             self.name )
        
        # Email Barbara
        Email.emailBarbara(
            'Pinterest Install: %s %s %s' % (
                self.uuid,
                self.name,
                self.url
            )
        )

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

        ShopifyAPI.install_webhooks( self.url, 
                                     self.token,
                                     webhooks )
    
    def install_script_tags(self, script_tags=None):
        """ Install our script tags onto the Shopify store """
        if script_tags == None:
            script_tags = []
        
        ShopifyAPI.install_script_tags( self.url, 
                                        self.token,
                                        script_tags )
        
    def install_assets(self, assets=None):
        if assets == None:
            assets = []

        ShopifyAPI.install_assets( self.url, 
                                   self.token,
                                   assets )

    def activate_recurring_billing(self):
        ShopifyAPI.activate_recurring_charge( self.url, 
                                              self.token,
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

