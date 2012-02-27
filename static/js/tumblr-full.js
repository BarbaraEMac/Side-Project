var AppsyDaisyTumblr_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyTumblr_waitForJquery, 100);
    } else {
        AppsyDaisyTumblr_run();
    }
}

var AppsyDaisyTumblr_run = function() {
    var btn           = document.getElementById( 'AppsyTumblr' );
    var children      = btn.childNodes;
    var tumblr_anchor = null;
    var inAnchor      = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName.toLowerCase() === "a" ) {
            tumblr_anchor = $(children[i]);
        }
    }

    tumblr_anchor
        .bind('mouseover', function(){
          inAnchor = true;
          setTimeout(function() { 
            if ( inAnchor ) { AppsyDaisyTumblr_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          inAnchor = false;
        });
};

var AppsyDaisyTumblr_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=tumblr&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyTumblr_waitForJquery();
