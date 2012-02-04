#!/usr/bin/python

import logging

from google.appengine.api   import memcache
from google.appengine.ext   import db
from google.appengine.ext.db import polymodel

from util.consts            import *
from util.model             import Model
from util.helpers           import generate_uuid

# ------------------------------------------------------------------------------
# ShopifyStore Class Definition ------------------------------------------------
# ------------------------------------------------------------------------------
class ShopifyStore(Model, polymodel.PolyModel):
    """A ShopifyStore or the website"""
    uuid    = db.StringProperty(indexed = True)
    created = db.DateTimeProperty(auto_now_add = True)
    email   = db.StringProperty(indexed=True)

    # Store properties
    name    = db.StringProperty( indexed = False )
    url     = db.LinkProperty  ( indexed = True )
    domain  = db.LinkProperty  ( indexed = True )
    token   = db.StringProperty( default = '' )
    id      = db.StringProperty( indexed = True )

    # Owner Properties
    full_name = db.StringProperty( default = '', indexed = False )

    def __init__(self, *args, **kwargs):
        self._memcache_key = kwargs['uuid'] if 'uuid' in kwargs else None 
        super(ShopifyStore, self).__init__(*args, **kwargs)
    
    @staticmethod
    def _get_from_datastore( uuid ):
        """Datastore retrieval using memcache_key"""
        return db.Query(ShopifyStore).filter('uuid =', uuid).get()

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
    def create( url_, token, app_type ):
        url_ = get_shopify_url( url_ )
        
        # Query the Shopify API to learn more about this store
        data = get_store_info( url_, token, app_type )
        
        # Make the Merchant 
        # Now, make the store
        uuid  = generate_uuid( 16 )
        domain = get_shopify_url( data['domain'] )
        if domain == '':
            domain = url_

        store = ShopifyStore( key_name = uuid,
                               uuid     = uuid,
                               email    = data['email'],
                               passphrase = '',
                               name     = data['name'],
                               url      = url_,
                               domain   = domain,
                               token    = token,
                               id       = str(data['id']),
                               full_name = data['shop_owner'])
        store.put()

        # Query the Shopify API to dl all Products
        taskqueue.add(
                url = build_url('FetchShopifyProducts'),
                params = {
                    'client_uuid': uuid,
                    'app_type'   : app_type
                }
            )

        return store

    # Accessors 
    @staticmethod
    def get_by_url(store_url):
        store_url = get_shopify_url( store_url )

        store = ShopifyStore.all().filter( 'url =', store_url ).get()
        return store

    @staticmethod
    def get_or_create( store_url, store_token='', app_type="" ):
        store = ShopifyStore.get_by_url(store_url)

        if not store:
            store = ShopifyStore.create( store_url, 
                                         store_token, 
                                         app_type )
        return store

    def get_products( self, app_type ):
        """ Fetch images for all the products in this store """

        # Construct the API URL
        url      = '%s/admin/products.json' % (self.url)
        
        # Fix inputs ( legacy )
        if app_type == "pinterest":
            app_type = 'PinterestApp'
        
        # Grab Shopify API settings
        settings = SHOPIFY_APPS[app_type]

        username = settings['api_key'] 
        password = hashlib.md5(settings['api_secret'] + self.token).hexdigest()

        # this creates a password manager
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        # for which `url` is a super-url
        passman.add_password(None, url, username, password)

        # create the AuthHandler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)

        opener = urllib2.build_opener(authhandler)

        # All calls to urllib2.urlopen will now use our handler
        # Make sure not to include the protocol in with the URL, or
        # HTTPPasswordMgrWithDefaultRealm will be very confused.
        # You must (of course) use it when fetching the page though.
        urllib2.install_opener(opener)

        # authentication is now handled automatically for us
        logging.info("Querying %s" % url )
        result = urllib2.urlopen(url)

        # Grab the data about the order from Shopify
        details  = json.loads( result.read() ) 
        products = details['products']

        for p in products:
            ProductShopify.create_from_json( self, p ) 

# Shopify API Calls  -----------------------------------------------------------
def get_store_info(store_url, store_token, app_type):
    
    # Fix inputs ( legacy )
    if app_type == "referral":
        app_type = 'ReferralShopify'
    elif app_type == "sibt": 
        app_type = 'SIBTShopify'
    elif app_type == "buttons": 
        app_type = 'ButtonsShopify'
    
    # Grab Shopify API settings
    settings = SHOPIFY_APPS[app_type]

    # Constuct the API URL
    url      = '%s/admin/shop.json' % ( store_url )
    username = settings['api_key'] 
    password = hashlib.md5(settings['api_secret'] + store_token).hexdigest()
    header   = {'content-type':'application/json'}
    h        = httplib2.Http()
    
    # Auth the http lib
    h.add_credentials(username, password)
    
    logging.info("Querying %s" % url )
    resp, content = h.request( url, "GET", headers = header)
    
    details = json.loads( content ) 
    logging.info( details )
    shop    = details['shop']
    logging.info('shop: %s' % (shop))
    
    return shop

