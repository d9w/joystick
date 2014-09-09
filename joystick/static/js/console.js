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
            } else {
                $('#expand-'+command_id).html('[+]');
            }
        });
    };

    $('.expand').each(function() {
        var text = $(this).attr('id').split('-')[1];
        if ($(this).is(":visible")) {
            socket.emit('open log', {'id': text});
        }
        $(this).click(function() {
            toggle_output(text);
        });
    });

    //TODO: use ajax instead of a full page load for forms
    var form = $('#push-button');

      form.find('select:first').change( function() {
        $.ajax( {
          type: "POST",
          url: form.attr( 'action' ),
          data: form.serialize(),
          success: function( response ) {
            console.log( response );
          }
        } );
      } );
});
