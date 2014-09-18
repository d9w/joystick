$(function() {

    namespace = '/console';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    var console_name = $('#console-name').text();

    socket.emit('join', {room:console_name});

    socket.on('log', function (data) {
            $('#output-'+data.id+'-text').text(data.lines);
            $('#output-'+data.id+'-text').addClass('running');
    });

    $(window).unload(function() {
        socket.emit('leave', {room:console_name});
    });

});
