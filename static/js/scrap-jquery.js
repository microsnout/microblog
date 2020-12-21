$(document).ready(function() {

    // Visitor name changed handler
    $('#id_visitor-name, #id_visitor-pin').on('keyup change', function() {

        $.post('/blog/visitor_query/', {
                name: $('#id_visitor-name').val(),
                pin: $('#id_visitor-pin').val()
            },
            function(data) {
                var status = data['status'];
                if (status == 'Null') {
                    // No name or less than minimum length
                    $('#id_visitor-name').css('color', 'grey');
                    $('#id_visitor-pin').css('color', 'grey');
                    $('#id_visitor-pin').prop('disabled', true);
                    $('#visitor_name_help').html('- Enter name or userid -')
                    $('#visitor_pin_help').html('- Enter 1 to 6 digit pin -')
                    $('#id_comment-button').prop('disabled', true);
                    $('#id_visitor-name').focus();
                } else if (status == 'Match') {
                    // Name in db, pin match
                    $('#id_visitor-name').css('color', 'green');
                    $('#id_visitor-pin').css('color', 'green');
                    $('#id_visitor-pin').prop('disabled', false);
                    $('#visitor_name_help').html('- Name is validated -')
                    $('#visitor_pin_help').html('- Pin is valid -')
                    $('#id_comment-button').prop('disabled', false);
                } else if (status == 'Found') {
                    // Name in db, invalid pin
                    $('#id_visitor-name').css('color', 'red');
                    $('#id_visitor-pin').css('color', 'grey');
                    $('#id_visitor-pin').prop('disabled', false);
                    $('#visitor_name_help').html('- Name is recognized -')
                    $('#visitor_pin_help').html('- Enter matching pin-')
                    $('#id_comment-button').prop('disabled', true);
                } else if (status == 'Avail') {
                    // Name is unrecognized but available
                    $('#id_visitor-name').css('color', 'grey');
                    $('#id_visitor-pin').css('color', 'grey');
                    $('#id_visitor-pin').prop('disabled', false);
                    $('#visitor_name_help').html('- New name is available -')
                    $('#visitor_pin_help').html('- Enter 1 to 6 digit pin -')
                    $('#id_comment-button').prop('disabled', false);
                }
            }
        )
    })

    $('#id_visitor-name').on('keypress', function(event) {
        var regex = new RegExp("^[a-zA-Z0-9. _]+$");
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    });

    $('#id_visitor-pin').on('keypress', function(event) {
        var regex = new RegExp("^[0-9]+$");
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
            event.preventDefault();
            return false;
        }
    });

    $('#id_visitor-name').trigger('change');
});