#!/usr/bin/env python

import logging

from apps.store.models      import ShopifyStore

from util.consts            import URL
from util.helpers           import url
from util.shopify           import ShopifyAPI
from util.shopify_helpers   import get_shopify_url
from util.urihandler        import URIHandler

# The "Shows" ------------------------------------------------------------------
class StoreAppSelect( URIHandler ):
    def get( self ):
        # Request varZ from Shopify
        store_url   = get_shopify_url( self.request.get( 'shop' ) )
        shopify_sig = self.request.get( 'signature' )
        store_token = self.request.get( 't' )

        # Get the store or create a new one
        store = ShopifyStore.get_or_create(store_url, store_token)
        
        """
        # If we've already set up the app, redirect to welcome screen
        if store.charge_id != None:
            self.redirect( "%s?s_u=%s" % (url('StoreWelcome'), store.uuid) )
            return
        """
        
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('select.html', template_values)) 

class StoreRecurringCallback( URIHandler ):
    def get(self):
        # Request varZ from Shopify
        charge_id = self.request.get( 'charge_id' )
        store     = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        if ShopifyAPI.verify_recurring_charge( store.url, 
                                               store.token, 
                                               charge_id ):
            store.do_install()
            
            store.charge_id = charge_id
            store.put()
            
            self.redirect("%s?s_u=%s" % (url('StoreWelcome'), store.uuid) )
        
        else:
            self.redirect( "%s?s_u=%s" % (url('StoreRecurringCancelled'), store.uuid) )

class StoreRecurringCancelled( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('cancelled.html', template_values)) 

class StoreOneTimeCallback( URIHandler ):
    def get(self):
        # Request varZ from Shopify
        charge_id = self.request.get( 'charge_id' )
        store     = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        if ShopifyAPI.verify_charge( store.url, 
                                     store.token, 
                                     charge_id ):
            store.onetime_charge_id = charge_id
            store.put()
            
            self.redirect("%s?s_u=%s&thx=true" % (url('StoreSupport'), store.uuid) )
        
        else:
            self.redirect( "%s?s_u=%s" % (url('StoreOneTimeCancelled'), store.uuid) )

class StoreOneTimeCancelled( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('cancelled.html', template_values)) 

class StoreSupport( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        
        just_paid = self.request.get('thx') != ""
        if just_paid:
            ShopifyAPI.activate_charge( store.url, store.token, store.onetime_charge_id )

        template_values = { 'store'  : store,
                            'paid'   : store.onetime_charge_id != None,
                            'thanks' : just_paid }

        self.response.out.write(self.render_page('support.html', template_values)) 

class StoreWelcome( URIHandler ):
    def get( self ):
        store = ShopifyStore.get_by_uuid( self.request.get('s_u') )
        template_values = { 'store' : store }

        self.response.out.write(self.render_page('welcome.html', template_values)) 

