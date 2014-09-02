function hide_flash_message_container() {
    //$('#flash_message_container').slideUp('medium');
}

$(document).ready(function() {
    $('#flash_message_container').slideDown(400, function() {
        setTimeout(hide_flash_message_container, 5000);
    });
})
