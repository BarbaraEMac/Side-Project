function gp_e(){for(var a=document.getElementById("AppsyGplus").childNodes,c=!1,b=0;b<a.length;b++)void 0!=a[b].tagName&&"div"===a[b].tagName.toLowerCase()&&(c=!0);c?f():window.setTimeout(gp_e,100)}function f(){"function"!=typeof jQuery?window.setTimeout(f,100):gp_g()} 
function gp_g(){for(var a=document.getElementById("AppsyGplus").childNodes,c=null,b=!1,d=0;d<a.length;d++)"div"===a[d].tagName.toLowerCase()&&(c=$(a[d]));c.bind("mouseover",function(){b=!0;setTimeout(function(){if(b){var a=document.createElement("iframe");a.style.display="none";a.src="http://appsy-daisy.appspot.com/store/click?app=gplus&url="+encodeURIComponent(window.location.href);document.body.appendChild(a)}},900)}).bind("mouseout",function(){b=!1})}gp_e();