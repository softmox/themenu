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
  //   // console.log(selectDropDowns);
  //   for (var i = 0; i < selectDropDowns.length; i++) {
  //     model = $(selectDropDowns[i]).data('model');
  //     $(selectDropDowns[i]).select2({
  //       placeholder: 'Start typing for ' + model + ' ...',
  //       // To include data here, the elements need a "text" field,
  //       //    as well as the id field
  //       // data: data
  //     });
  //     fetchDataAndAppend('/api/' + model, {}, $(selectDropDowns[i]));
  //   }

  // }


  // Search bar: pass to the /dishes/search url
  $('#dish-search-form').submit(function(event) {
    event.preventDefault();
    let dishSearchText = $('#dish-search-input').val();
    if (dishSearchText) {
      urlParams = $.param({ text: dishSearchText });
      newUrl = '/dishes/search?' + urlParams;
      console.log(newUrl);
      window.location.href = newUrl;
    }
  })

  $('.grocery-checkbox').on('click touch', function() {
    var groceryId = $(this).data('grocery-id');
    var groceryType = $(this).data('grocery-type');
    var checked = this.checked;
    console.log('clicked', groceryId, checked);
    postGroceryUpdate(groceryId, groceryType, checked)
  });

  $('.course-checkbox').on('click touch', function() {
    var dishId = $(this).data('dish-id');
    var mealId = $(this).data('meal-id');
    var attribute = $(this).data('attribute');
    var checked = this.checked;
    console.log('clicked', dishId, mealId, attribute, checked);
    postCourseUpdate(dishId, mealId, attribute, checked)
  });

  $('#add-ingredient').on('click touch', function(event) {
    event.preventDefault();
    //cloneDiv('#ingredient-div');
    cloneDiv();
  });


		$('.list-group.checked-list-box .list-group-item').each(function () {

    // Settings
    var $widget = $(this),
      $checkbox = $('<input type="checkbox" class="hidden" />'),
      // If we want different colors, add a "data-danger"
      // color = ($widget.data('color') ? $widget.data('color') : "success"),
      color = "success",
      style = "list-group-item-",
      settings = {
        on: {
          icon: 'glyphicon glyphicon-check'
        },
        off: {
          icon: 'glyphicon glyphicon-unchecked'
        }
      };

    $widget.css('cursor', 'pointer')
    $widget.append($checkbox);

    // Event Handlers
    $widget.on('click', function (event) {
      // Ignore the click if it was on the dropdown button (checking meals)
      if (event.target.type != 'button' && !dropdownsOpen()) {
        // First handle change in style to set checked
        $checkbox.prop('checked', !$checkbox.is(':checked'));
        $checkbox.triggerHandler('change');
        updateDisplay();

        // Now handle data posting actions
        var groceryId = $widget.data('grocery-id');
        var groceryType = $widget.data('grocery-type');
        var checked = $checkbox.prop('checked');
        console.log('clicked', groceryId, checked);
        postGroceryUpdate(groceryId, groceryType, checked)
      }
    });
    $checkbox.on('change', function () {
      updateDisplay();
    });


    // Actions
    function updateDisplay() {
      var isChecked = $checkbox.is(':checked');

      // Set the button's state
      $widget.data('state', (isChecked) ? "on" : "off");

      // Set the button's icon
      $widget.find('.state-icon')
        .removeClass()
        .addClass('state-icon ' + settings[$widget.data('state')].icon);

      // Update the button's color
      if (isChecked) {
        $widget.addClass(style + color);
      } else {
        $widget.removeClass(style + color);
      }
    }

    // Initialization
    function init() {

      if ($widget.data('checked') == true) {
        $checkbox.prop('checked', !$checkbox.is(':checked'));
      }

      updateDisplay();

      // Inject the icon if applicable
      if ($widget.find('.state-icon').length == 0) {
        $widget.prepend('<span class="state-icon ' + settings[$widget.data('state')].icon + '"></span>');
      }
    }
    init();
  });


});

function cloneDiv(selector) {
  //var d2 = $(selector).clone();

  //var $el = $('#id_ingredient');

  //var $el = $('.ingredient-div');
  var curCount = $('.ingredient-container').length - 1;  // Dont count the dummy
  curCount++;
  //var $inContainer = $('.ingredient-container:last');
  var $inContainer = $('#ingredient-container-0');

  var d2 = $inContainer.clone().prop('id', 'ingredient-container-' + curCount).show();
  //$('#ingredient-div').append(d2);
  // $inContainer.after(d2);
  $('.ingredient-container:last').after(d2)
  // $el.remove();
  // $('.ingredient-div .select2-container').each(function() {
    // $(this).prop('id', 'testing-' + curCount);
  // });

  function initSelect2() {
    var $d2s = $('.ingredient-div .django-select2');
    // $d2s.empty();
    // $d2s.removeData();
    // Calling the method below reinitializes the dropdowns, but duplicates
    $d2s.djangoSelect2();
    // I have 0 idea why there's just one last one that breaks and duplicates... :(
    var $elsToRemove = $('.ingredient-div .select2-container');
    $elsToRemove[$elsToRemove.length - 1].remove();
  }
  initSelect2();
}

function resetSelect2() {
  var $d2s = $('.django-select2');
  $d2s.empty();
  $d2s.removeData();
  $d2s.djangoSelect2();
}

function dropdownsOpen() {
  var dropIsOpen = false;
	$(".list-group-item").each(function(idx, li) {
    if ($(li).hasClass('open')) {
      dropIsOpen = true;
    }
  })
  return dropIsOpen;
}


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


function imgError(image) {
  $(image).hide();
}
