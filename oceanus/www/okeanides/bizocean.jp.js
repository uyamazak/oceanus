Object.keys||(Object.keys=function(){var e=Object.prototype.hasOwnProperty,d=!{toString:null}.propertyIsEnumerable("toString"),g="toString toLocaleString valueOf hasOwnProperty isPrototypeOf propertyIsEnumerable constructor".split(" "),b=g.length;return function(c){if("object"!==typeof c&&"function"!==typeof c||null===c)throw new TypeError("Object.keys called on non-object");var a=[],h;for(h in c)e.call(c,h)&&a.push(h);if(d)for(h=0;h<b;h++)e.call(c,g[h])&&a.push(g[h]);return a}}());
var oceanus = oceanus || [];
oceanus.a = ((function(opt){
  var docCookies={getItem:function(a){if(!a||!this.hasItem(a)){return null}return unescape(document.cookie.replace(new RegExp("(?:^|.*;\\s*)"+escape(a).replace(/[\-\.\+\*]/g,"\\$&")+"\\s*\\=\\s*((?:[^;](?!;))*[^;]?).*"),"$1"))},setItem:function(d,g,c,b,a,e){if(!d||/^(?:expires|max\-age|path|domain|secure)$/i.test(d)){return}var f="";if(c){switch(c.constructor){case Number:f=c===Infinity?"; expires=Tue, 19 Jan 2038 03:14:07 GMT":"; max-age="+c;break;case String:f="; expires="+c;break;case Date:f="; expires="+c.toGMTString();break}}document.cookie=escape(d)+"="+escape(g)+f+(a?"; domain="+a:"")+(b?"; path="+b:"")+(e?"; secure":"")},removeItem:function(b,a){if(!b||!this.hasItem(b)){return}document.cookie=escape(b)+"=; expires=Thu, 01 Jan 1970 00:00:00 GMT"+(a?"; path="+a:"")},hasItem:function(a){return(new RegExp("(?:^|;\\s*)"+escape(a).replace(/[\-\.\+\*]/g,"\\$&")+"\\s*\\=")).test(document.cookie)},keys:function(){var a=document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g,"").split(/\s*(?:\=[^;]*)?;\s*/);for(var b=0;b<a.length;b++){a[b]=unescape(a[b])}return a}};
  var getParameterByName=function(b,a){if(!a){a=window.location.href}b=b.replace(/[\[\]]/g,"\\$&");var c=new RegExp("[?&]"+b+"(=([^&#]*)|&|#|$)");results=c.exec(a);if(!results){return null}if(!results[2]){return""}return decodeURIComponent(results[2].replace(/\+/g," "))};
  var d = document;
  var args = [];
  var opt = opt || [];
  args.oid = opt.oid||2;
  args.evt = opt.evt||null;
  args.uid = opt.uid||null;
  args.ref = opt.ref||d.referrer.substr(0,1024);
  args.tit = opt.tit||d.title.substr(0, 256);
  args.evt = opt.evt||'pageview';
  args.url = opt.url||d.URL.substr(0,1024);
  args.enc = d.charset;
  args.scr = screen.width+'x'+screen.height;
  args.vie = d.documentElement.clientWidth+'x'+d.documentElement.clientHeight;
  args.jsn = opt.jsn||null;
  args.debug = opt.debug||null;
  var w = window;
  var s_key = 'oceanus_sid';
  // session
  var sid = docCookies.getItem(s_key);
  if( ! sid){
    var c = "abcdef0123456789".split("");
    var sid = "";
    for(var i=0; i<16; i++){
      sid += c[Math.floor(Math.random() * c.length)];
    }
  }
  docCookies.setItem(s_key, sid, 94608000, "/");
  args.sid = sid;
  // bizocean variables
  var jsn = opt.jsn || {};
  var kw_match = getParameterByName("keyword");
  if(kw_match) {
    jsn.kwd = kw_match;
    var cat_match = location.pathname.match(/\/search\/([0-9]+)/);
    if(cat_match){
      jsn.cat = decodeURIComponent(cat_match[1]);
    }
  }
  if(w.JSON && Object.keys(jsn).length){
    args.jsn = w.JSON.stringify(jsn);
  }
  // bizocean id
  if(!args.uid){
    var biz_id = getParameterByName('member_state[id]', docCookies.getItem("auth_state"));
    if(biz_id){
      args.uid = biz_id;
    }else if(typeof(w.memberInfo) != 'undefined' &&
      typeof(w.memberInfo.member_state) != 'undefined' &&
      typeof(w.memberInfo.member_state.id) != 'undefined') {
      args.uid = w.memberInfo.member_state.id || null;
    }
  }
  return args;
}));
oceanus.f = oceanus.f || ((function(args){
  args = this.a(args);
  var d = document;
  var en = encodeURIComponent;
  var swallow_url= this.swallow_url || "https://oceanus.bizocean.co.jp/swallow";
  var aArray = [];
  var aKeys = Object.keys(args);
  for(var i=0, len= aKeys.length; i<len; i++){
    if(args[aKeys[i]]){
      aArray.push(en(aKeys[i]) + '=' + en(args[aKeys[i]]));
    }
  }
  var qs = aArray.join('&');
  var b = new Image();
  b.src = swallow_url + '?' + qs;
  b.onerror = function(e){};
}));
((function(){
  var q = oceanus_q || null;
  if(!q) return;
  var qKeys = Object.keys(q);
  for(var i=0, len= qKeys.length; i<len; i++){
    if(typeof q[qKeys[i]] == "object"){
      oceanus.f(q[qKeys[i]]);
    }
  }
}))();
var oceanus_q = [];
oceanus_q.push = ((function(arg){
  oceanus.f(arg);
}));
if(typeof oceanus.autosend != "undefined"){
  oceanus.autosend = oceanus.autosend;
}else{
  oceanus.autosend = true;
}
if(oceanus.autosend) oceanus.f();