var AppsyDaisyTwitter_waitForTwitter = function() {
    var btn      = document.getElementById( 'AppsyTwitter' );
    var children = btn.childNodes;
    var runFlag  = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "iframe" ) {
            runFlag = true;
        }
    }
    
    if ( runFlag ) {
        AppsyDaisyTwitter_waitForJquery();
    } else {
        window.setTimeout(AppsyDaisyTwitter_waitForTwitter, 100);
    }
};

var AppsyDaisyTwitter_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyTwitter_waitForJquery, 100);
    } else {
        AppsyDaisyTwitter_run();
    }
}

var AppsyDaisyTwitter_run = function() {
    var btn  = document.getElementById( 'AppsyTwitter' );
    var children = btn.childNodes;
    var twitter_iframe = null;
    var inIframe = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "iframe" ) {
            twitter_iframe = $(children[i]);
        }
    }

    twitter_iframe
        .bind('mouseover', function(){
          //console.log('entered iframe');
          inIframe = true;
          setTimeout(function() { 
            if ( inIframe ) { AppsyDaisyTwitter_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          //console.log('left iframe');
          inIframe = false;
        });
};

var AppsyDaisyTwitter_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=twitter&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyTwitter_waitForTwitter();

