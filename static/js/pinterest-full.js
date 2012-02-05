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
        AppsyDaisy_run();
    } else {
        window.setTimeout(AppsyDaisy_waitForPinterest, 100);
    }
};

var AppsyDaisy_run = function() {
    var here = window.location.href;
    var btn  = document.getElementById( 'AppsyPinterest' );
    var children = btn.childNodes;
    var pinterest_iframe = null;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName === "IFRAME" ) {
            pinterest_iframe = children[i];
        }
    }

    var our_iframe = document.createElement( 'img' );
    our_iframe.id = 'AppsyDaisyPinterestImg';
    our_iframe.style.cursor = 'pointer';
    our_iframe.style.width  = '100%';
    our_iframe.style.height = '100%';
    our_iframe.style.position = 'absolute';
    our_iframe.style.top = '0px';
    our_iframe.style.left = '0px';
    our_iframe.style.zIndex = '2147483647';
    our_iframe.src = 'http://appsy-daisy.appspot.com/static/imgs/noimage.png';
    our_iframe.onclick = function() { AppsyDaisy_handleClick(); };
    our_iframe.onClick = function() { AppsyDaisy_handleClick(); };

    btn.appendChild( our_iframe );
};

var AppsyDaisy_handleClick = function(){
    var img  = document.getElementById( 'AppsyDaisyPinterestImg' );
    document.body.appendChild( img );

    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/p/click?url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisy_waitForPinterest();

