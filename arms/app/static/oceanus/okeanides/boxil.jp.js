var oceanus_c=function(evt,jsn){
 var oid=1000;
 var oceanus_external_url="https://www.bizocean.jp/oceanus/external.html";
 var evt=evt||"boxil-pageview";
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
 ifm.id=ifm_id;
 ifm.width=0;
 ifm.height=0;
 ifm.border=0;
 ifm.style="border:0";
 ifm.frameBorder=0;
 var en=encodeURIComponent;
 var ref=en(d.referrer);
 var url=en(d.URL);
 var tit=en(d.title);
 var enc=en(d.charset);
 if(jsn&&window.JSON){jsn=en(window.JSON.stringify(jsn));}
 ifm.src=oceanus_external_url+"?oid="+oid+"&evt="+evt+"&ref="+ref+'&url='+url+'&tit='+tit+'&enc='+enc+'&jsn='+jsn;
 if(!ifm_exsisted){d.body.appendChild(ifm);}
};
oceanus_c();
((function(){
 var buttons=document.getElementsByTagName("button");
 var b_length=buttons.length;
 var click_send=function(b,e){oceanus_c("buttonclick",{"btntext":b.innerText,"class":b.className,"clientXY":e.clientX+'.'+e.clientY});};
 for(var i=0;i<b_length;i++){
  var b=buttons[i];
  if(b.addEventListener){
   b.addEventListener("click",function(e){click_send(this,e);},false);
  }else{
   b.attachEvent("onclick",function(e){click_send(this,e);});
  }
}
}))();