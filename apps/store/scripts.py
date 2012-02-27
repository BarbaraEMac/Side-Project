#!/usr/bin/python

from util.consts            import *

### Pinterest ------------------------------------------------------------------
pinterest_script = """<!-- START Pinterest Script -->
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
</script>"""

pinterest_button = """<div id="AppsyPinterest" style="float: left; width: 90px;"><a href="http://pinterest.com/pin/create/button/?url={{shop.url|escape}}{{product.url|escape}}&media={{product.featured_image|product_img_url:'large'}}&description=Found%20on%20{{shop.domain|escape}}!" class="pin-it-button" count-layout="horizontal">Pin It</a></div>"""
        
appsy_pinterest_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script> """ % (URL, '/static/js/pinterest.js')

### Facebook ------------------------------------------------------------------
facebook_script = """
<!-- START Facebook Script -->
    <div id="fb-root"></div>
    <script>(function(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=166070566811816";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'facebook-jssdk'));
</script>"""

facebook_button = """<div id="AppsyFacebook" style="float: left; width: 90px;"> <div class="fb-like" data-href="http://appsy-daisy.appspot.com" data-send="false" data-layout="button_count" data-width="450" data-show-faces="false"></div></div>"""
        
appsy_facebook_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script>""" % (URL, '/static/js/facebook.js')

### Twitter ------------------------------------------------------------------
twitter_script = """
<!-- START Twitter Script -->
    <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0];if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src="//platform.twitter.com/widgets.js";fjs.parentNode.insertBefore(js,fjs);}}(document,"script","twitter-wjs");
</script>"""

twitter_button = """<div id="AppsyTwitter" style="float: left; width: 90px;"><a href="https://twitter.com/share" class="twitter-share-button" data-via="BarbaraEMac">Tweet</a> </div>"""
        
appsy_twitter_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script>""" % (URL, '/static/js/twitter.js')

### Tumblr ------------------------------------------------------------------
tumblr_script = """ """

tumblr_button = """<div id="AppsyTumblr" style="float: left; width: 90px;"><a href="http://www.tumblr.com/share" title="Share on Tumblr" style="display:inline-block; text-indent:-9999px; overflow:hidden; width:61px; height:20px; background:url('http://platform.tumblr.com/v1/share_2.png') top left no-repeat transparent;">Share on Tumblr</a></div>"""
        
appsy_tumblr_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script>""" % (URL, '/static/js/tumblr.js')

### Fancy ------------------------------------------------------------------
fancy_script = """
<!-- START Fancy Script -->
    <script src="http://www.thefancy.com/fancyit.js" type="text/javascript">
</script>"""

fancy_button = """<div id="AppsyFancy" style="float: left; width: 90px;"><a id="FancyButton" href="http://www.thefancy.com/fancyit?ItemURL={{shop.url|escape}}{{product.url|escape}}&Title={{product.title|escape}}&Category=Other&ImageURL={{product.featured_image|product_img_url:'large'}}">Fancy</a></div>"""
        
appsy_fancy_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script> """ % (URL, '/static/js/fancy.js')

### Gplus ------------------------------------------------------------------
gplus_script = """
<!-- START Gplus Script -->
    <script type="text/javascript">
      (function() {
        var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
        po.src = 'https://apis.google.com/js/plusone.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
      })();
</script>"""

gplus_button = """<div id="AppsyGplus" style="float: left; width: 90px; margin-top: -2px;"><g:plusone annotation="inline" width="120"></g:plusone></div>"""
        
appsy_gplus_script = """
    <script>
        if ( typeof jQuery != 'function' ) {
            var script = window.document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js";
            window.document.getElementsByTagName("head")[0].appendChild(script);
        }

        var script = window.document.createElement("script");
        script.type = "text/javascript";
        script.src = "%s%s";
        window.document.getElementsByTagName("head")[0].appendChild(script);
    </script> """ % (URL, '/static/js/gplus.js')
