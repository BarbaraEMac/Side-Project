var waitForPinterest = function() {
    var btn = document.getElementById( 'PinItButton' );

    if ( !btn ) {
        window.setTimeout(waitForPinterest,100);
    } else {
        run();
    }
};

var run = function() {
    alert('running');
    var here = window.location.href;


};
