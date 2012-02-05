#!/usr/bin/python

import hashlib, logging, random, urllib2, datetime

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

class ShopifyAPI():

    # Shopify API Calls --------------------------------------------------------
    @staticmethod
    def install_webhooks( app, store_url, store_token, webhooks = [] ):
        """ Install the webhooks into the Shopify store """
        url      = '%s/admin/webhooks.json' % store_url
        
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
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
                    '%s WEBHOOK INSTALL FAILED\n%s\n%s\n%s' % (
                        app,
                        resp,
                        app.store_url,
                        content
                    )        
                )
        logging.info('installed %d webhooks' % len(webhooks))
        
    @staticmethod
    def install_script_tags( app, store_url, store_token, script_tags = [] ):
        """ Install our script tags onto the Shopify store """

        url      = '%s/admin/script_tags.json' % store_url
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
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
                        app,
                        resp,
                        content
                    )        
                )
        logging.info('installed %d script_tags' % len(script_tags))

    @staticmethod
    def install_assets( app, store_url, store_token, assets = [] ):
        """Must first get the `main` template in use"""
        
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
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
            logging.error('%s error getting themes: \n%s\n%s' % (app, resp, content))
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
                    '%s SCRIPT_TAGS INSTALL FAILED\n%s\n%s' % (
                        app,
                        resp,
                        content
                    )        
                )

        logging.info('installed %d assets' % len(assets))

    @staticmethod
    def recurring_billing( app, store_url, store_token, settings ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges.json' % store_url
        
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        resp, content = h.request(
                url,
                "POST",
                body    = json.dumps(settings),
                headers = header
            )

        return ''

    @staticmethod
    def activate_recurring_charge( app, store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges/#%s/activate.json' % (store_url, charge_id)
        
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        resp, content = h.request(url, "POST", body=json.dumps(settings), headers=header)

        return ''

    @staticmethod
    def delete_recurring_charge( app, store_url, store_token, charge_id ):
        """ Setup store with a recurring blling charge for htis app."""
        url      = '%s/admin/recurring_application_charges/#%s.json' % (store_url, charge_id)
        
        username = SHOPIFY_APPS[app]['api_key'] 
        password = hashlib.md5(SHOPIFY_APPS[app]['api_secret'] + store_token).hexdigest()
        header   = {'content-type':'application/json'}
        h        = httplib2.Http()
        
        # Auth the http lib
        h.add_credentials(username, password)
        
        resp, content = h.request(url, "DELETE", body=json.dumps(settings), headers=header)

        return ''


    
