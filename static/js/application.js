
$(document).ready(function () {
    //connect to the socket server.
    var socket = io.connect("http://" + document.domain + ":" + location.port);
    console.log(socket)
    var messages_received = [];

    //receive details from server
    socket.on("newMessage", function (msg) {
        console.log("Received Message" + msg.message);
        messages_received.push(msg.message);
        messages = "";
        for (var i = 0; i < messages_received.length; i++) {
            messages = messages + "<p style='display: block'>" + messages_received[i].toString() + "</p>";
        }
        $("#msgs").html(messages);
    });

    $("#submit").click(function (msg) {
        socket.emit("MESSAGE", $("#content").val())
    })

    socket.on('err', function (err) {
        console.log(err)
    })

});