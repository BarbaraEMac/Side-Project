function e(){for(var a=document.getElementById("AppsyPinterest").childNodes,c=!1,b=0;b<a.length;b++)"IFRAME"===a[b].tagName&&(c=!0);c?f():window.setTimeout(e,100)}function f(){"function"!=typeof jQuery?window.setTimeout(f,100):g()}
function g(){for(var a=document.getElementById("AppsyPinterest").childNodes,c=null,b=!1,d=0;d<a.length;d++)"IFRAME"===a[d].tagName&&(c=$(a[d]));c.bind("mouseover",function(){b=!0;setTimeout(function(){if(b){var a=document.createElement("iframe");a.style.display="none";a.src="http://appsy-daisy.appspot.com/p/click?url="+encodeURIComponent(window.location.href);document.body.appendChild(a)}},900)}).bind("mouseout",function(){b=!1})}e();
