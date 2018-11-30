$(document).ready(function () {

    $('form').on('submit', function (event) {

        $.ajax({
            data: {
                name: $('#nameInput').val(),
                pass: $('#pass').val()
            },
            type: 'POST',
            url: '/login'
        })
            .done(function (data) {

                if (data.error) {
                    $('#errorAlert').text(data.error).show();
                    $('#successAlert').hide();
                }
                else {
                    $('#successAlert').text(data.name).show();
                    $('#errorAlert').hide();
                }

            });

        event.preventDefault();


    });

});