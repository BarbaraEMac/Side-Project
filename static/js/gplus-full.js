var AppsyDaisyGplus_waitForGplus = function() {
    var btn      = document.getElementById( 'AppsyGplus' );
    var children = btn.childNodes;
    var runFlag  = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName != undefined && children[i].tagName.toLowerCase() === "div" ) {
            runFlag = true;
        }
    }
    
    if ( runFlag ) {
        AppsyDaisyGplus_waitForJquery();
    } else {
        window.setTimeout(AppsyDaisyGplus_waitForGplus, 100);
    }
};

var AppsyDaisyGplus_waitForJquery = function() {
    if ( typeof jQuery != 'function' ) {
        window.setTimeout(AppsyDaisyGplus_waitForJquery, 100);
    } else {
        AppsyDaisyGplus_run();
    }
}

var AppsyDaisyGplus_run = function() {
    var btn       = document.getElementById( 'AppsyGplus' );
    var children  = btn.childNodes;
    var gplus_div = null;
    var inDiv     = false;

    for ( var i = 0; i < children.length; i ++ ) {
        if( children[i].tagName.toLowerCase() === "div" ) {
            gplus_div = $(children[i]);
        }
    }

    gplus_div
        .bind('mouseover', function(){
          //console.log('entered iframe');
          inDiv = true;
          setTimeout(function() { 
            if ( inDiv ) { AppsyDaisyGplus_handleClick(); }
          }, 900);
        })
        .bind('mouseout', function(){
          //console.log('left iframe');
          inDiv = false;
        });
};

var AppsyDaisyGplus_handleClick = function(){
    var iframe = document.createElement( 'iframe' );
    iframe.style.display = 'none';
    iframe.src = "http://appsy-daisy.appspot.com/store/click?app=gplus&url=" + encodeURIComponent( window.location.href );
    document.body.appendChild( iframe );
};

AppsyDaisyGplus_waitForGplus();

