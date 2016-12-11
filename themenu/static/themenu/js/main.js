$(document).ready(function() {
    // CSRF setup for ajax calls
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $('.course-checkbox').change(function() {
        var dishId = $(this).data('dish-id');
        var mealId = $(this).data('meal-id');
        var attribute = $(this).data('attribute');
        var checked = this.checked;
        console.log('clicked', dishId, mealId, attribute, checked);
        postCourseUpdate(dishId, mealId, attribute, checked)
    });
});


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function postCourseUpdate(dishId, mealId, attribute, checked) {
    var $posting = $.ajax({
            type: 'POST',
            url: '/courseupdate/',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                dishId: dishId,
                mealId: mealId,
                attribute: attribute,
                checked: checked
            })
    });
    $posting.done(function(data) {
        console.log('Finished posting dish ID', dishId, 'mealId', mealId);
        // window.location.reload();
    });
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
