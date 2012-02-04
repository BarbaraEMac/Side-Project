#!/usr/bin/python

# The App Model

import hashlib, logging, random, urllib2, datetime

from decimal              import *
from django.utils         import simplejson as json
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from util.consts          import *
from util.helpers         import generate_uuid
from util.helpers         import url 
from util.model           import Model
from util.memcache_ref_prop import MemcacheReferenceProperty

NUM_SHARE_SHARDS = 15

class App(Model, polymodel.PolyModel):
    # Unique identifier for memcache and DB key
    uuid            = db.StringProperty( indexed = True )
    
    # Datetime when this model was put into the DB
    created         = db.DateTimeProperty( auto_now_add=True )
    
    # Person who created/installed this App
    store           = db.ReferenceProperty( db.Model, collection_name = 'apps' )
    
    # Defaults to None, only set if this App has been deleted
    old_client      = db.ReferenceProperty( db.Model, collection_name = 'deleted_apps' )
    
    store_url = db.StringProperty(indexed = True)
    
    # Shopify's token for this store
    store_token = db.StringProperty(indexed = True)

    # For Apps that use a click counter, this is the cached amount
    cached_clicks_count = db.IntegerProperty( default = 0 )
    
    def __init__(self, *args, **kwargs):
        self._memcache_key = kwargs['uuid'] if 'uuid' in kwargs else None 
        super(App, self).__init__(*args, **kwargs)
    
    @staticmethod
    def _get_from_datastore(uuid):
        """Datastore retrieval using memcache_key"""
        return App.all().filter('uuid =', uuid).get()

    @staticmethod
    def get_by_uuid(uuid):
        return App.all().filter('uuid =', uuid).get()

    @staticmethod
    def get_by_store( store ):
        return App.all().filter('store =', store).get()

    @staticmethod
    def get_by_url( store_url ):
        return App.all().filter('store_url =', store_url).get()

    def validateSelf( self ):
        # Subclasses should override this
        return

    def delete( self ):
        self.old_client = self.client
        self.client     = None
        self.put()
    
    @staticmethod
    def get_by_client( client ):
        return App.all().filter( 'client =', client )

    def count_clicks( self ):
        # Get an updated value by putting this on a queue
        taskqueue.add(
            queue_name = 'app-ClicksCounter', 
            url = '/a/appClicksCounter', 
            name = 'app_ClicksCounter_%s_%s' % (
                self.uuid,
                generate_uuid( 10 )),
            params = {
                'app_uuid' : self.uuid
            }
        )
        # Return an old cached value
        return self.cached_clicks_count
    
    def get_shares_count(self):
        """Count this apps sharded shares"""
        total = memcache.get(self.uuid+"ShareCounter")
        if total is None:
            total = 0
            for counter in ShareCounter.all().\
            filter('app_id =', self.uuid).fetch(15):
                total += counter.count
            memcache.add(key=self.uuid+"ShareCounter", value=total)
        return total
    
    def add_shares(self, num):
        """add num clicks to this app's share counter"""
        def txn():
            index = random.randint(0, NUM_SHARE_SHARDS-1)
            shard_name = self.uuid + str(index)
            counter = ShareCounter.get_by_key_name(shard_name)
            if counter is None:
                counter = ShareCounter(key_name=shard_name, 
                                       app_id=self.uuid)
            counter.count += num
            counter.put()

        db.run_in_transaction(txn)
        memcache.incr(self.uuid+"ShareCounter")

    def increment_shares(self):
        """Increment this link's click counter"""
        self.add_shares(1)



 # Shopify API Calls ------------------------------------------------------------
    def install_webhooks(self, product_hooks_too=True, webhooks=None):
        """ Install the webhooks into the Shopify store """
        # pass extra webhooks as a list
        if webhooks == None:
            webhooks = []

        logging.info("TOKEN %s" % self.store_token )
        url      = '%s/admin/webhooks.json' % self.store_url
        username = self.settings['api_key'] 
        password = hashlib.md5(self.settings['api_secret'] + self.store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        # See what we've already installed and flag it so we don't double install
        if product_hooks_too:
            # First fetch webhooks that already exist
            resp, content = h.request( url, "GET", headers = header)
            data = json.loads( content ) 
            #logging.info('%s %s' % (resp, content))

            product_create = product_delete = product_update = True
            for w in data['webhooks']:
                #logging.info("checking %s"% w['address'])
                if w['address'] == '%s/product/shopify/webhook/create' % URL or \
                   w['address'] == '%s/product/shopify/webhook/create/' % URL:
                    product_create = False
                if w['address'] == '%s/product/shopify/webhook/delete' % URL or \
                   w['address'] == '%s/product/shopify/webhook/delete/' % URL:
                    product_delete = False
                if w['address'] == '%s/product/shopify/webhook/update' % URL or \
                   w['address'] == '%s/product/shopify/webhook/update/' % URL:
                    product_update = False
        
        # If we don't want to install the product webhooks, 
        # flag all as "already installed"
        else:
            product_create = product_delete = product_update = False

        # Install the "App Uninstall" webhook
        data = {
            "webhook": {
                "address": "%s/a/shopify/webhook/uninstalled/%s/" % (
                    URL,
                    self.class_name()
                ),
                "format": "json",
                "topic": "app/uninstalled"
            }
        }
        webhooks.append(data)

        # Install the "Product Creation" webhook
        data = {
            "webhook": {
                "address": "%s/product/shopify/webhook/create" % ( URL ),
                "format" : "json",
                "topic"  : "products/create"
            }
        }
        if product_create:
            webhooks.append(data)
        
        # Install the "Product Update" webhook
        data = {
            "webhook": {
                "address": "%s/product/shopify/webhook/update" % ( URL ),
                "format" : "json",
                "topic"  : "products/update"
            }
        }
        if product_update:
            webhooks.append(data)

        # Install the "Product Delete" webhook
        data = {
            "webhook": {
                "address": "%s/product/shopify/webhook/delete" % ( URL ),
                "format" : "json",
                "topic"  : "products/delete"
            }
        }
        if product_delete:
            webhooks.append(data)

        for webhook in webhooks:
            logging.info('Installing extra hook %s' % webhook)
            logging.info("POSTING to %s %r " % (url, webhook))
            resp, content = h.request(
                url,
                "POST",
                body = json.dumps(webhook),
                headers = header
            )
            logging.info('%r %r' % (resp, content)) 
            if int(resp.status) == 401:
                Email.emailBarbara(
                    '%s WEBHOOK INSTALL FAILED\n%s\n%s\n%s' % (
                        self.class_name(),
                        resp,
                        self.store_url,
                        content
                    )        
                )
        logging.info('installed %d webhooks' % len(webhooks))
        
    def install_script_tags(self, script_tags=None):
        """ Install our script tags onto the Shopify store """
        if script_tags == None:
            script_tags = []

        url      = '%s/admin/script_tags.json' % self.store_url
        username = self.settings['api_key'] 
        password = hashlib.md5(self.settings['api_secret'] + self.store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        h.add_credentials(username, password)
        
        for script_tag in script_tags:
            logging.info("POSTING to %s %r " % (url, script_tag) )
            resp, content = h.request(
                url,
                "POST",
                body = json.dumps(script_tag),
                headers = header
            )
            logging.info('%r %r' % (resp, content))
            if int(resp.status) == 401:
                Email.emailBarbara(
                    '%s SCRIPT_TAGS INSTALL FAILED\n%s\n%s' % (
                        self.class_name(),
                        resp,
                        content
                    )        
                )
        logging.info('installed %d script_tags' % len(script_tags))

    def install_assets(self, assets=None):
        """Installs our assets on the client's store
            Must first get the `main` template in use"""
        username = self.settings['api_key'] 
        password = hashlib.md5(self.settings['api_secret'] + self.store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        h.add_credentials(username, password)
        
        main_id = None

        if assets == None:
            assets = []

        # get the theme ID
        theme_url = '%s/admin/themes.json' % self.store_url
        logging.info('Getting themes %s' % theme_url)
        resp, content = h.request(theme_url, 'GET', headers = header)

        if int(resp.status) == 200:
            # we are okay
            content = json.loads(content)
            for theme in content['themes']:
                if 'role' in theme and 'id' in theme:
                    if theme['role'] == 'main':
                        main_id = theme['id']
                        break
        else:
            logging.error('%s error getting themes: \n%s\n%s' % (
                self.class_name(),
                resp,
                content
            ))
            return

        # now post all the assets
        url = '%s/admin/themes/%d/assets.json' % (self.store_url, main_id)
        for asset in assets: 
            logging.info("POSTING to %s %r " % (url, asset) )
            resp, content = h.request(
                url,
                "PUT",
                body = json.dumps(asset),
                headers = header
            )
            logging.info('%r %r' % (resp, content))
            if int(resp.status) != 200: 
                Email.emailBarbara(
                    '%s SCRIPT_TAGS INSTALL FAILED\n%s\n%s' % (
                        self.class_name(),
                        resp,
                        content
                    )        
                )

        logging.info('installed %d assets' % len(assets))

def get_app_by_id( id ):
    return App.get(id)

## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
## -----------------------------------------------------------------------------
class ShareCounter(db.Model):
    """Sharded counter for link click-throughs"""

    app_id = db.StringProperty(indexed=True, required=True)
    count  = db.IntegerProperty(indexed=False, required=True, default=0)


