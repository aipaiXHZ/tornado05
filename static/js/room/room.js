var ws=new WebSocket('ws://'+location.host+'/ws');//建立连接
ws.onopen=function(){//建立连接触发函数
    // ws.send('Hello world');//向后台发送消息，会被后台的on_message接收
};
ws.onmessage=function (e){// 后台发射过来的内容
    data=JSON.parse(e.data);
    console.log(data);
    var existing=$('#m'+data.id);
    if (existing.length>0) return;
    var node=$(data.html);
    node.hide();
    $('#box').append(node);
    node.slideDown();
};
//其它方法还有onerror
function sendInp() {
    var $inp=$('#inp').val();
    ws.send($inp);// 发射给后台
}