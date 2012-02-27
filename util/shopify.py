#!/usr/bin/python

import hashlib, logging, random, urllib2, datetime

from django.utils         import simplejson as json
from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.ext import db
from google.appengine.ext.db import polymodel

from apps.email.models      import Email
from util                 import httplib2
from util.consts          import *
from util.helpers         import generate_uuid
from util.helpers         import url 
from util.model           import Model
from util.memcache_ref_prop import MemcacheReferenceProperty

NUM_SHARE_SHARDS = 15

class ShopifyAPI():

    # Shopify API Calls --------------------------------------------------------
    @staticmethod
    def install_webhooks( store_url, store_token, webhooks = [] ):
        """ Install the webhooks into the Shopify store """
        url      = '%s/admin/webhooks.json' % store_url
        
        username = PLUS_API_KEY
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
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
                    '%s WEBHOOK INSTALL FAILED\n%s\n%s' % (
                        resp,
                        store_url,
                        content
                    )        
                )
        logging.info('installed %d webhooks' % len(webhooks))
        
    @staticmethod
    def install_script_tags( store_url, store_token, script_tags = [] ):
        """ Install our script tags onto the Shopify store """

        url      = '%s/admin/script_tags.json' % store_url
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
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
            if int(resp.status) > 400:
                Email.emailBarbara(
                    '%s SCRIPT_TAGS INSTALL FAILED\n%s' % (
                        resp,
                        content
                    )        
                )
        logging.info('installed %d script_tags' % len(script_tags))

    @staticmethod
    def install_assets( store_url, store_token, assets = [] ):
        """Must first get the `main` template in use"""
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        h.add_credentials(username, password)
        
        main_id = None

        if assets == None:
            assets = []

        # get the theme ID
        theme_url = '%s/admin/themes.json' % store_url
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
            logging.error('%s error getting themes: \n%s' % (resp, content))
            return

        # now post all the assets
        url = '%s/admin/themes/%d/assets.json' % (store_url, main_id)
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
                    '%s SCRIPT_TAGS INSTALL FAILED\n%s' % (
                        resp,
                        content
                    )        
                )

        logging.info('installed %d assets' % len(assets))

    @staticmethod
    def recurring_billing( store_url, store_token, settings ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges.json' % store_url
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        logging.info('url %s' % url)
        resp, content = h.request(
                url,
                "POST",
                body    = json.dumps(settings),
                headers = header
            )

        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201:
            data = json.loads ( content )['recurring_application_charge']
            return data['confirmation_url']

        return ''

    @staticmethod
    def verify_recurring_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges/%s.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)

        logging.info("BARBAR %s" % url)
        
        resp, content = h.request(url, "GET", headers=header)
        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            data = json.loads ( content )['recurring_application_charge']
            return data['status'] == 'accepted' or data['status'] == 'active'


        return False

    @staticmethod
    def activate_recurring_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges/%s/activate.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        settings = { "recurring_application_charge": { "id": charge_id } }

        resp, content = h.request(url, "POST", body=json.dumps(settings), headers=header)
        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            return True #success

        return False #failure

    @staticmethod
    def delete_recurring_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges/%s.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        resp, content = h.request(url, "DELETE", headers=header)
        logging.info('Uninstall: %r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            return True #success

        return False #failure

    @staticmethod
    def fetch_store_info(store_url, store_token):
        # Constuct the API URL
        url      = '%s/admin/shop.json' % ( store_url )
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
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


    @staticmethod
    def onetime_charge( store_url, store_token, settings ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/application_charges.json' % store_url
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        logging.info('url %s' % url)
        resp, content = h.request(
                url,
                "POST",
                body    = json.dumps(settings),
                headers = header
            )

        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201:
            data = json.loads ( content )['application_charge']
            return data['confirmation_url']

        return ''

    @staticmethod
    def verify_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/application_charges/%s.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)

        logging.info("BARBAR %s" % url)
        
        resp, content = h.request(url, "GET", headers=header)
        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            data = json.loads ( content )['application_charge']
            return data['status'] == 'accepted' or data['status'] == 'active'

        return False

    @staticmethod
    def activate_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/application_charges/%s/activate.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        settings = { "application_charge": { "id": charge_id } }

        resp, content = h.request(url, "POST", body=json.dumps(settings), headers=header)
        logging.info('%r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            return True #success

        return False #failure

    @staticmethod
    def delete_charge( store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/application_charges/%s.json' % (store_url, charge_id)
        
        username = PLUS_API_KEY 
        password = hashlib.md5(PLUS_API_SECRET + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        resp, content = h.request(url, "DELETE", headers=header)
        logging.info('Uninstall: %r %r' % (resp, content)) 
        if int(resp.status) == 201 or int(resp.status) == 200:
            return True #success

        return False #failure
