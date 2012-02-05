var AppsyDaisy_waitForPinterest = function() {
    var btn      = document.getElementById( 'AppsyPinterest' );
    var children = btn.childNodes;
    var runFlag  = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName === "IFRAME" ) {
            runFlag = true;
        }
    }
    
    if ( runFlag ) {
        AppsyDaisy_waitForJquery();
    } else {
        window.setTimeout(AppsyDaisy_waitForPinterest, 100);
    }
};

var AppsyDaisy_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisy_waitForJquery, 100);
    } else {
        AppsyDaisy_run();
    }
}

var AppsyDaisy_run = function() {
    var btn  = document.getElementById( 'AppsyPinterest' );
    var children = btn.childNodes;
    var pinterest_iframe = null;
    var inIframe = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName === "IFRAME" ) {
            pinterest_iframe = $(children[i]);
        }
    }

    pinterest_iframe
        .bind('mouseover', function(){
          //console.log('entered iframe');
          inIframe = true;
          setTimeout(function() { 
            if ( inIframe ) { AppsyDaisy_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          //console.log('left iframe');
          inIframe = false;
        });
};

var AppsyDaisy_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/p/click?url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisy_waitForPinterest();

