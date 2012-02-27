var AppsyDaisyFacebook_waitForFacebook = function() {
    var btn      = document.getElementById( 'AppsyFacebook' );
    var children = btn.childNodes;
    var runFlag  = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "div" ) {
            runFlag = true;
        }
    }
    
    if ( runFlag ) {
        AppsyDaisyFacebook_waitForJquery();
    } else {
        window.setTimeout(AppsyDaisyFacebook_waitForFacebook, 100);
    }
};

var AppsyDaisyFacebook_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyFacebook_waitForJquery, 100);
    } else {
        AppsyDaisyFacebook_run();
    }
}

var AppsyDaisyFacebook_run = function() {
    var btn             = document.getElementById( 'AppsyFacebook' );
    var children        = btn.childNodes;
    var facebook_iframe = null;
    var inIframe        = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "div" ) {
            facebook_iframe = $(children[i]);
        }
    }

    facebook_iframe
        .bind('mouseover', function(){
          //console.log('entered iframe');
          inIframe = true;
          setTimeout(function() { 
            if ( inIframe ) { AppsyDaisyFacebook_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          //console.log('left iframe');
          inIframe = false;
        });
};

var AppsyDaisyFacebook_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=facebook&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyFacebook_waitForFacebook();

