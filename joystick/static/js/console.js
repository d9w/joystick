$(function() {

    namespace = '/test';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.emit('join', {room:'testroom'});

    socket.on('log', function (data) {
            $('#output-'+data.id+'-text').text(data.lines);
    });

    $(window).unload(function() {
        socket.emit('leave', {room:'testroom'});
    });
});
