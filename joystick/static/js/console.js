$(function() {

    namespace = '/test';

    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });

    socket.on('log', function (data) {
            $('#output-'+data.id+'-text').text(data.lines);
    });

    function toggle_output(command_id){
        $('#output-'+command_id).slideToggle(400, function() {
            if ($('#output-'+command_id).is(":visible")) {
                $('#expand-'+command_id).html('[-]');
                socket.emit('open log', {'id':command_id});
            } else {
                $('#expand-'+command_id).html('[+]');
            }
        });
    };

    $('.expand').each(function() {
        var text = $(this).attr('id').split('-')[1];
        $(this).click(function() {
            toggle_output(text);
        });
    });
    //toggle_output(3);

});
