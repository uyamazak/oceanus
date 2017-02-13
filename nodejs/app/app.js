// This program is free software. It comes without any warranty, to
// the extent permitted by applicable law. You can redistribute it
// and/or modify it under the terms of the Do What The Fuck You Want
// To Public License, Version 2, as published by Sam Hocevar. See
// http://sam.zoy.org/wtfpl/COPYING for more details.

var util        = require('util')
  , opts       = require('opts')
  , redis      = require('redis')
  , subscriber = redis.createClient(6379, '192.168.2.70')


opts.parse([
    {
        'short':       'p',
        'long':        'port',
        'description': 'WebSocket Port',
        'value':       true,
        'required':    true
    }
]);

subscriber.on("error", function(err) {
    util.debug(err);
});


subscriber.subscribe("bizocean");
subscriber.on("message", function(channel, message) {
    //util.puts(message);
    wsServer.broadcast(message);
});


var WebSocketServer = require('websocket').server;
var http = require('http');

var server = http.createServer(function(request, response) {
    console.log((new Date()) + ' Received request for ' + request.url);
    response.writeHead(404);
    response.end();
});
server.listen(8889, function() {
    console.log((new Date()) + ' Server is listening on port 8889');
});

wsServer = new WebSocketServer({
    httpServer: server,
    // You should not use autoAcceptConnections for production
    // applications, as it defeats all standard cross-origin protection
    // facilities built into the protocol and the browser.  You should
    // *always* verify the connection's origin and decide whether or not
    // to accept it.
    autoAcceptConnections: false
});

function originIsAllowed(origin) {
  // put logic here to detect whether the specified origin is allowed.
  return true;
}

var connects = [];

wsServer.on('connection', function(ws){
    console.log('on connection');
    console.log(ws);
    connects.push(ws);
    ws.on('close', function(){
        console.log("on close");
        connects = connects.filter(function (conn, i) {
            return (conn === ws) ? false : true;
        });
    });
});


wsServer.on('request', function(request) {
    if (!originIsAllowed(request.origin)) {
      // Make sure we only accept requests from an allowed origin
      request.reject();
      console.log((new Date()) + ' Connection from origin ' + request.origin + ' rejected.');
      return;
    }

    var connection = request.accept('echo-protocol', request.origin);
    console.log((new Date()) + ' Connection accepted.');
    console.log(request);
    connection.on('message', function(message) {
        if (message.type === 'utf8') {
            console.log('Received Message: ' + message.utf8Data);
            connection.sendUTF(message.utf8Data);
        }
        else if (message.type === 'binary') {
            console.log('Received Binary Message of ' + message.binaryData.length + ' bytes');
            connection.sendBytes(message.binaryData);
        }
    });
    connection.on('close', function(reasonCode, description) {
        console.log((new Date()) + ' Peer ' + connection.remoteAddress + ' disconnected.');
    });
});




wsServer.broadcast = function broadcast(data) {
  console.log(connects);
  connects.forEach(function each(conn) {
    console.log(conn);
  });
};


