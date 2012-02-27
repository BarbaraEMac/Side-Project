var AppsyDaisyPinterest_waitForPinterest = function() {
    var btn      = document.getElementById( 'AppsyPinterest' );
    var children = btn.childNodes;
    var runFlag  = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "iframe" ) {
            runFlag = true;
        }
    }
    
    if ( runFlag ) {
        AppsyDaisyPinterest_waitForJquery();
    } else {
        window.setTimeout(AppsyDaisyPinterest_waitForPinterest, 100);
    }
};

var AppsyDaisyPinterest_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyPinterest_waitForJquery, 100);
    } else {
        AppsyDaisyPinterest_run();
    }
}

var AppsyDaisyPinterest_run = function() {
    var btn              = document.getElementById( 'AppsyPinterest' );
    var children         = btn.childNodes;
    var pinterest_iframe = null;
    var inIframe         = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "iframe" ) {
            console.log('running pinterest');
            pinterest_iframe = $(children[i]);
        }
    }

    pinterest_iframe
        .bind('mouseover', function(){
          //console.log('entered iframe');
          inIframe = true;
          setTimeout(function() { 
            if ( inIframe ) { AppsyDaisyPinterest_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          //console.log('left iframe');
          inIframe = false;
        });
};

var AppsyDaisyPinterest_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=pinterest&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyPinterest_waitForPinterest();

