function fb_e(){for(var a=document.getElementById("AppsyFacebook").childNodes,c=!1,b=0;b<a.length;b++)void 0!=a[b].tagName&&"div"===a[b].tagName.toLowerCase()&&(c=!0);c?f():window.setTimeout(fb_e,100)}function f(){"function"!=typeof jQuery?window.setTimeout(f,100):fb_g()}
function fb_g(){for(var a=document.getElementById("AppsyFacebook").childNodes,c=null,b=!1,d=0;d<a.length;d++)void 0!=a[d].tagName&&"div"===a[d].tagName.toLowerCase()&&(c=$(a[d]));c.bind("mouseover",function(){b=!0;setTimeout(function(){if(b){var a=document.createElement("iframe");a.style.display="none";a.src="http://appsy-daisy.appspot.com/store/click?app=facebook&url="+encodeURIComponent(window.location.href);document.body.appendChild(a)}},900)}).bind("mouseout",function(){b=!1})}fb_e();