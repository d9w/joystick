$(function() {

    namespace = '/console';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    var console_name = $('#console-name').text();

    socket.emit('join', {room:console_name});

    socket.on('log', function (data) {
            $('#output-'+data.id+'-text').text(data.lines);
    });

    $(window).unload(function() {
        socket.emit('leave', {room:console_name});
    });
});
