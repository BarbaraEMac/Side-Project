#!/usr/bin/env python

from google.appengine.ext import db

from apps.app.models      import App

# ------------------------------------------------------------------------------
# Pinterest Class Definition ---------------------------------------------------
# ------------------------------------------------------------------------------
class Pinterest(App):
    """ShopifyStores install the Pinterest App"""  

    def __init__(self, *args, **kwargs):
        """ Initialize this model """
        super(Pinterest, self).__init__(*args, **kwargs)

    # Constructor ------------------------------------------------------------------
    @staticmethod
    def create(store, app_token):

        uuid = generate_uuid( 16 )
        app = ButtonsShopify( key_name    = uuid,
                              uuid        = uuid,
                              store       = store,
                              store_name  = store.name, # Store name
                              store_url   = store.url, # Store url
                              store_token = app_token ) 
        app.put()

        app.do_install()
            
        return app


    def do_install( self ):
        # Define our script tag 
        tags = [{
            "script_tag": {
                "src": "%s/b/shopify/load/buttons.js?app_uuid=%s" % (
                    URL,
                    self.uuid
                ),
                "event": "onload"
            }
        }]

        # Install yourself in the Shopify store
        self.install_webhooks( product_hooks_too = False )
        self.install_script_tags( script_tags = tags )

        # Fire off "personal" email from Fraser
        Email.welcomeClient( "Pinterest+", 
                             self.store.merchant.get_attr('email'), 
                             self.store.merchant.get_full_name(), 
                             self.store.name )
        
        # Email Barbara
        Email.emailBarbara(
            'ButtonsShopify Install: %s %s %s' % (
                self.uuid,
                self.store.name,
                self.store.url
            )
        )

    # Accessors ----------------------------------------------------------------
    @staticmethod
    def get_or_create( store, token ):
        app = Pinterest.get_by_url( store.url )
        
        if app is None:
            app = Pinterest.create(store, token)
        
        elif token != None and token != '':
            if app.store_token != token:
                # TOKEN mis match, this might be a re-install
                logging.warn(
                    'We are going to reinstall this app because the stored token does not match the request token\n%s vs %s' % (
                        app.store_token,
                        token
                    )
                ) 
                try:
                    app.store_token = token
                    app.store       = store
                    app.old_store   = None
                    app.put()
                    
                    app.do_install()
                except:
                    logging.error('encountered error with reinstall', exc_info=True)
        return app


