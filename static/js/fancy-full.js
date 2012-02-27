var AppsyDaisyFancy_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyFancy_waitForJquery, 100);
    } else {
        AppsyDaisyFancy_run();
    }
}

var AppsyDaisyFancy_run = function() {
    var btn          = document.getElementById( 'AppsyFancy' );
    var children     = btn.childNodes;
    var fancy_anchor = null;
    var inAnchor     = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName.toLowerCase() === "a" ) {
            fancy_anchor = $(children[i]);
        }
    }

    fancy_anchor
        .bind('mouseover', function(){
          // console.log('entered anchor');
          inAnchor = true;
          setTimeout(function() { 
            if ( inAnchor ) { AppsyDaisyFancy_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          // console.log('left anchor');
          inAnchor = false;
        });
};

var AppsyDaisyFancy_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=fancy&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyFancy_waitForJquery();
