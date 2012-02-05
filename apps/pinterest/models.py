#!/usr/bin/env python
import logging

from google.appengine.ext   import db

from apps.app.models        import App
from apps.email.models      import Email
from util.consts            import URL
from util.helpers           import generate_uuid

# ------------------------------------------------------------------------------
# Pinterest Class Definition ---------------------------------------------------
# ------------------------------------------------------------------------------
class Pinterest(App):
    def __init__(self, *args, **kwargs):
        """ Initialize this model """
        super(Pinterest, self).__init__(*args, **kwargs)
    
    def do_install( self ):
        # Define our script tag 
        pinterest_script = """
    <!-- START Pinterest Script -->
    <script type="text/javascript">
    (function() {
        window.PinIt = window.PinIt || { loaded:false };
        if (window.PinIt.loaded) return;
        window.PinIt.loaded = true;
        function async_load(){
            var s = document.createElement("script");
            s.type = "text/javascript";
            s.async = true;
            if (window.location.protocol == "https:")
                s.src = "https://assets.pinterest.com/js/pinit.js";
            else
                s.src = "http://assets.pinterest.com/js/pinit.js";
            var x = document.getElementsByTagName("script")[0];
            x.parentNode.insertBefore(s, x);
        }
        if (window.attachEvent)
            window.attachEvent("onload", async_load);
        else
            window.addEventListener("load", async_load, false);
    })();
    </script>
    <!-- END Pinterest Script -->
    """

        pinterest_button = """
    <a href="http://pinterest.com/pin/create/button/?url={{shop.url|escape}}{{product.url|escape}}&media={{product.featured_image|product_img_url:'large'}}&description=Found%20on%20url={{shop.url|escape}}!" class="pin-it-button" count-layout="horizontal">Pin It</a>
"""
        appsy_script = """
    <script>
        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script>""" % (URL, '/static/js/pinterest.js')

        snippet = pinterest_script + pinterest_button + appsy_script

        liquid_assets = [{
            'asset': {
                'value': snippet,
                'key': 'snippets/pinterest_plus.liquid'
            }
        }]

        # Install yourself in the Shopify store
        self.install_webhooks( webhooks = None )
        self.install_assets( assets = liquid_assets )
        
        self.activate_recurring_billing( )

        Email.welcomeClient( self.class_name(), 
                             self.store.email, 
                             self.store.full_name, 
                             self.store.name )
        
        # Email Barbara
        Email.emailBarbara(
            'Pinterest Install: %s %s %s' % (
                self.uuid,
                self.store.name,
                self.store_url
            )
        )

# Constructor --------------------------------------------------------------
def create_pinterest(store, charge_id):

    uuid = generate_uuid( 16 )
    app  = Pinterest( key_name    = uuid,
                      uuid        = uuid,
                      store       = store,
                      store_name  = store.name,  # Store name
                      store_url   = store.url,   # Store url
                      store_token = store.token, # Store token
                      charge_id   = charge_id ) 
    app.put()

    app.do_install()
        
    return app

# Accessors ----------------------------------------------------------------
def get_or_create_pinterest( store, token ):
    app = get_pinterest_by_url( store.url )
    
    if app is None:
        app = create_pinterest(store, token)
    
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

def get_pinterest_by_url( url ):
    return Pinterest.all().filter('store_url = ', url).get()

