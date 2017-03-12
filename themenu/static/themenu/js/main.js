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

    // Api call for the tags for autocomplete
    // https://select2.github.io/examples.html
    // var selectDropDowns = $('.select-multiple');
    // if (selectDropDowns) {
    //     // console.log(selectDropDowns);
    //     for (var i = 0; i < selectDropDowns.length; i++) {
    //         model = $(selectDropDowns[i]).data('model');
    //         $(selectDropDowns[i]).select2({
    //             placeholder: 'Start typing for ' + model + ' ...',
    //             // To include data here, the elements need a "text" field,
    //             //      as well as the id field
    //             // data: data
    //         });
    //         fetchDataAndAppend('/api/' + model, {}, $(selectDropDowns[i]));
    //     }

    // }

    $('.grocery-checkbox').change(function() {
        var groceryId = $(this).data('grocery-id');
        var groceryType = $(this).data('grocery-type');
        var checked = this.checked;
        console.log('clicked', groceryId, checked);
        postGroceryUpdate(groceryId, groceryType, checked)
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

function postGroceryUpdate(groceryId, groceryType, checked) {
    var $posting = $.ajax({
            type: 'POST',
            url: '/groceryupdate/',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                groceryId: groceryId,
                groceryType: groceryType,
                checked: checked
            })
    });
    $posting.done(function(data) {
        console.log('Finished grocery ID', groceryId);
        // window.location.reload();
    });
}


function fetchDataAndAppend(url, data, jqueryElement) {
    var $get = $.ajax({
        type: 'GET',
        url: url,
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify(data),
        success: function(data) {
            console.log("Success getting", url);
            appendApiData(data, jqueryElement);
        }
    });
}

function appendApiData(data, jqueryElement) {
    for (var i = 0; i < data.length; i++) {
        jqueryElement.append('<option value="' + data[i].id + '">' + data[i].name + '</option>');
    }
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
