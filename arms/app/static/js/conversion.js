var oceanus_conversion=function(oid,evt,jsn){
 var oid=oid||"notset";
 var oceanus_external_url="https://www.bizocean.jp/oceanus/external.html";
 var evt=evt||"conversion";
 var jsn=jsn||"";
 var d=document;
 var ifm_id="oceanus-external-ifm"
 var ifm=document.getElementById(ifm_id);
 var ifm_exsisted=null;
 if(ifm){
  ifm_exsisted=true;
 }else{
  ifm_exsisted=false;
  ifm=d.createElement("iframe");
 }
 ifm.id=ifm_id;ifm.width=0;ifm.height=0;ifm.border=0;ifm.style="border:0";ifm.frameBorder=0;
 var en=encodeURIComponent;
 var ref=en(d.referrer);
 var url=en(d.URL);
 var tit=en(d.title);
 var enc=en(d.charset);
 var vie=d.documentElement.clientWidth+'x'+d.documentElement.clientHeight;
 if(jsn&&window.JSON){jsn=en(window.JSON.stringify(jsn));}
 ifm.src=oceanus_external_url+"?oid="+oid+"&evt="+evt+"&ref="+ref+'&url='+url+'&tit='+tit+'&enc='+enc+'&jsn='+jsn+'&vie='+vie;
 if(!ifm_exsisted){d.body.appendChild(ifm);}
}
var oceanus_oid=oceanus_oid||null;
var oceanus_evt=oceanus_evt||null;
var oceanus_jsn=oceanus_jsn||null;
oceanus_conversion(oceanus_oid,oceanus_evt,oceanus_jsn);