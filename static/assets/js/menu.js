$(document).ready(function() {

    $(document).on('click', '#close-btn', function() {
        req = $.ajax({
            url : '/close_window',
            type : 'POST'
        });

        req.done(function(data) {
            console.log("closed window")

        });
    });

    $(document).on('click', '#min-btn', function() {
        req = $.ajax({
            url : '/minimize_window',
            type : 'POST'
        });

        req.done(function(data) {
            console.log("minimized_window")

        });
    });

    $(document).on('click', '#max-btn', function() {
        req = $.ajax({
            url : '/maximize_window',
            type : 'POST'
        });

        req.done(function(data) {
            console.log("maximized_window")

        });
    });


});