function tu_d(){"function"!=typeof jQuery?window.setTimeout(tu_d,100):tu_f()} function tu_f(){for(var b=document.getElementById("AppsyTumblr").childNodes,e=null,c=!1,a=0;a<b.length;a++)"a"===b[a].tagName.toLowerCase()&&(e=$(b[a]));e.bind("mouseover",function(){c=!0;setTimeout(function(){if(c){var a=document.createElement("iframe");a.style.display="none";a.src="http://appsy-daisy.appspot.com/store/click?app=tumblr&url="+encodeURIComponent(window.location.href);document.body.appendChild(a)}},900)}).bind("mouseout",function(){c=!1})}tu_d();
