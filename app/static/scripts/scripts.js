var QUESTION_LIST = {};

//jQuery Custom plugins
(function($) {
    $.fn.my_required = function(message = "") {
        return this.each(function() {

            var elem = $(this);

            if (!message) {
                message = 'This is required';
            }
            var msg_elem = '<p class="text-danger">' + message + '</p>';

            elem.on('blur', function() {
                if (elem.val() === "") {
                    show_input_error(elem, message);
                }
            });

            elem.on('focus', function() {
                elem.css({
                    border: '1px solid #ccc'
                }).siblings('.text-danger').remove();
            });
        });
    };

}(jQuery));


var show_input_error = function(elem, message = "") {

    if (!message) {
        message = 'This is required';
    }

    var msg_elem = '<p class="text-danger">' + message + '</p>';

    elem.css({
        border: '1px solid red'
    }).after(msg_elem);
};

var checks = function() {
    if ($('#upvote').hasClass('btn-success')) {
        $('#downvote').attr('disabled', true);
    }

    var downvote = $('#downvote');
    if (downvote.hasClass('btn-success')) {
        $('#upvote').attr('disabled', true);
    }
};

var showAlert = function(message, category = "success") {
    /*
    It shows a bootstrap-styled alert box for notifications.
    */
    var alert = '<div class="alert alert-' + category + ' alert-dismissible" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button>' + message + '</div>';
    $('#alert').append(alert);
};

var UpdateMath = function(TeX, elementID) {
    //set the MathOutput HTML
    //document.getElementById("MathOutput").innerHTML = TeX;
    $('#' + elementID).text(TeX);
    //reprocess the MathOutput Element
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, elementID]);
    return $('#' + elementID);
};

var UpdateText = function(text, elementID) {
    $(elementID).text(text);
    return (elementID);
};

var preview = function(inputElem, previewElem) {
    var elem = $(inputElem);
    if (elem.val() != "") {
        UpdateMath(elem.val(), previewElem);
    }
    elem.on('keyup', function() {
        var text = $(this).val();
        UpdateMath(text, previewElem);
    });
};

var error = function(jqxhr) {
    var json = jqxhr.responseJSON;

    if (json) {
        showAlert(json.message, 'danger');
    } else {
        showAlert(jqxhr.statusText, 'danger');
    }
};

var add_success_class = function(elem) {
    elem.removeClass('btn-default').addClass('btn-success');
};

var add_default_class = function(elem) {
    elem.removeClass('btn-success').addClass('btn-default');
};

var toggle_two_classes = function(elem, class1, class2) {
    if (elem.hasClass(class1)) {
        elem.removeClass(class1).addClass(class2);
    } else {
        elem.removeClass(class2).addClass(class1);
    }
};

//Kepresses bindings for options 
$(function(){
    $(document).on('keyup', function(event){
        var key = String.fromCharCode(event.which);
        var options = $('.options .btn');

        if (key === "1" || key === "A" || key === "a") {
            if ($(options[0]).hasClass('btn-danger')) {
                toggle_two_classes($(options[0]), 'btn-danger', 'btn-default');
            } else {
                toggle_two_classes($(options[0]), 'btn-default', 'btn-info');
            }
        } else if (key === "2" || key === "B" || key === "b") {
            if ($(options[1]).hasClass('btn-danger')) {
                toggle_two_classes($(options[1]), 'btn-danger', 'btn-default');
            } else {
                toggle_two_classes($(options[1]), 'btn-default', 'btn-info');
            }
        } else if (key === "3" || key === "C" || key === "c") {
            if ($(options[2]).hasClass('btn-danger')) {
                toggle_two_classes($(options[2]), 'btn-danger', 'btn-default');
            } else {
                toggle_two_classes($(options[2]), 'btn-default', 'btn-info');
            }

        } else if (key === "4" || key === "D" || key === "d") {
            if ($(options[3]).hasClass('btn-danger')) {
                toggle_two_classes($(options[3]), 'btn-danger', 'btn-default');
            } else {
                toggle_two_classes($(options[3]), 'btn-default', 'btn-info');
            }
        } else if (event.which === 13) {
            $('.option-form').trigger('submit');
        }
    });
});

//Solutions 
$(function(){
    $(document).on('click', '.sol-controls button:not("#edit-sol")', function(){
        var self = $(this);

        data = {
            id: self.data('id'),
            is_upvote: 1
        };

        if (self.hasClass('downvote-sol')) {
            data.is_upvote = 0;
        }

        $.ajax({
            url: '/vote-solution',
            data: data,
            type: 'POST',
            success: function(){
                toggle_two_classes(self, 'btn-default', 'btn-success');

                if (data.is_upvote) {
                    if (self.hasClass('btn-success')) {
                        self.next().attr('disabled', true);
                    } else {
                        self.next().attr('disabled', false);
                    }
                } else {
                    if (self.hasClass('btn-success')) {
                        self.prev().attr('disabled', true);
                    } else {
                        self.prev().attr('disabled', false);
                    }
                }
            },
            error: function(jqxhr){
                error(jqxhr);
            }
        });
    });
});

//Post Solutions
$(function(){
    $(document).on('click', '#edit-sol', function(){
        var sol_form = $('#solution-form');
        var val = $('#to-edit').text();
        if (sol_form.css('display') === "none") {
            sol_form.css('display', 'block');
            $('#solution-form #body').val(val);
            $('#sol-preview').text(val);
        } else {
            sol_form.css('display', 'none');
        }
    });
});

$(function() {
    $(document).on('submit', '#solution-form', function(event) {
        event.preventDefault();
        var validate = true;
        var sol_id = $(this).children('input[type="hidden"]');

        if (validate) {
            $.ajax({
                url: '/post-solution',
                type: 'POST',
                data: $('#solution-form, input[name="question-id"]').serialize(),
                success: function() {
                    // Reload the question.
                    var ques_id = $('input[name="question-id"]').val();
                    get_questions(ques_id);
                    //Show the appropriate message;
                    if ($.isEmptyObject(sol_is)) {
                        showAlert('Solution Posted Successfully.', 'success')
                    } else {
                        showAlert('Solution Edited successfully.', 'success');
                    }
                    
                },
                error: function(jqxhr) {
                    error(jqxhr);
                }
            });
        }
    });
});

// Modify Questions Validations 
var validate_modify_questions = function() {

    var elem_to_check = [
        $('#body'),
        $('#option1'),
        $('#option2')
    ]

    options = $('textarea[id^="option"]');
    checked_options = $('input[id^="check_option"]:checked');
    elem_msg = '<p class="text-danger">At least one options should be correct.</p>';
    has_error = false;

    for (var i = 0; i < elem_to_check.length; i++) {
        if (elem_to_check[i].val() === "") {
            show_input_error(elem_to_check[i]);
            has_error = true;
        }
    }

    if (!validate_tags()) {
        has_error = true;
    }

    if ($.isEmptyObject(checked_options)) {
        options.each(function() {
            if ($(this).val() !== "") {
                $(this).after(elem_msg);
            }
        });
        has_error = true;
    }

    return has_error;
}

$(function() {

    // Set Up validation checks
    $('#body').my_required();
    $('#modify-ques-form #option1').my_required();
    $('#modify-ques-form #option2').my_required();

    $('#modify-ques-form').on('submit', function(event) {
        var has_error = validate_modify_questions();
        console.log(has_error);
        if (has_error) {
            event.preventDefault();
            return;
        }
    });
});


var keep_solved_ques = function() {
    if ($('#keep-solved-ques').hasClass('btn-success')) {
        return true
    }
    return false
}


// Set User settings 
$(function() {
    $('.dropdown-settings li>button').on('click', function(event) {
        var self = $(this);
        var data = {
            name: self.data('type')
        };
        var original_text;

        $.ajax({
            url: '/user-setting',
            type: 'POST',
            data: data,
            beforeSend: function() {
                original_text = self.text();
                self.text('setting ...').attr('disabled', true);

            },
            success: function(){
                toggle_two_classes(self, 'btn-default', 'btn-success');

                if (self.data('type') === "KSQ" && self.hasClass('btn-success')) {
                    QUESTION_LIST = {};
                }

                self.text(original_text).attr('disabled', false);
            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });

        event.stopPropagation();
    });
});


// Tag-it settings
$(function() {
    $('#tags').tagit({
        allowSpaces: true,
        autocomplete: {
            source: function(request, response) {
                $.ajax({
                    url: '/get-tags',
                    dataType: 'json',
                    data: {
                        query: request.term
                    },
                    success: function(data) {
                        response($.map(data, function(item) {
                            return {
                                label: item,
                                value: item
                            }
                        }));
                        return data
                    }
                });
            },
            minLength: 3
        }
    });
});

// Button Hover Settings
var button_hover_effects = function(elemID) {
    var child_html;

    $(document).on('mouseenter', elemID, function() {
        var self = $(this);
        child_html = self.html();
        var count = self.data('count');
        var new_html = '<b>' + count + '</b>';
        self.html(new_html);
    }).on('mouseout', elemID, function() {
        var self = $(this);
        self.html(child_html);
    });
}

//Favourite AJAX Call
$(function() {

    button_hover_effects('#favourite');

    $('.question-box').on('click', '#favourite', function() {

        var fav = $('#favourite');

        $.ajax({
            url: '/favourite-question',
            type: 'POST',
            data: $('input[name="question-id"]').serialize(),
            success: function() {
                var fav_star = fav.children('.glyphicon');

                toggle_two_classes(fav, 'btn-default', 'btn-success')
                toggle_two_classes(fav_star, 'glyphicon-star-empty', 'glyphicon-star')

                // if (fav_star.hasClass('glyphicon-star-empty')) {

                //     fav_star.removeClass('glyphicon-star-empty')
                //         .addClass('glyphicon-star');

                //     fav.removeClass('btn-default')
                //         .addClass('btn-success');
                // } else {

                //     fav_star.removeClass('glyphicon-star')
                //         .addClass('glyphicon-star-empty');

                //     fav.removeClass('btn-success')
                //         .addClass('btn-default');
                // }

            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });
    });
});

//Upvote Ajax
$(function() {

    button_hover_effects('#upvote');

    $(document).on('click', '#upvote', function() {

        var upvote = $('#upvote');

        $.ajax({
            url: '/upvote',
            type: 'POST',
            data: $('input[name="question-id"]').serialize(),
            success: function() {
                var upvote_count = $('.upvote-count');
                var currentUpvote = parseInt(upvote_count.text(), 10);

                if (upvote.hasClass('btn-default')) {

                    upvote.removeClass('btn-default')
                        .addClass('btn-success');

                    upvote_count.text(currentUpvote + 1);

                    $('#downvote').attr('disabled', true);
                } else {
                    upvote.removeClass('btn-success')
                        .addClass('btn-default');

                    upvote_count.text(currentUpvote - 1);

                    $('#downvote').attr('disabled', false);
                }
            },
            error: function(jqxhr, textStatus, errorThrown) {
                var json = jqxhr.responseJSON;
                showAlert(json.message, 'danger');
            }
        });
    });
});

/*Add or remove downvote*/
$(function() {

    button_hover_effects('#downvote');

    $('.question-box').on('click', '#downvote', function() {

        var downvote = $(this);

        $.ajax({
            url: '/downvote',
            type: 'POST',
            data: $('input[name="question-id"]').serialize(),
            success: function() {
                var upvote_count = $('.upvote-count');
                var currentUpvote = parseInt(upvote_count.text(), 10);

                if (downvote.hasClass('btn-default')) {
                    downvote.removeClass('btn-default')
                        .addClass('btn-success');

                    upvote_count.text(currentUpvote - 1);

                    $('#upvote').attr('disabled', true);
                } else {
                    downvote.removeClass('btn-success')
                        .addClass('btn-default');

                    upvote_count.text(currentUpvote + 1);

                    $('#upvote').attr('disabled', false);
                }
            },
            error: function(jqxhr, textStatus, errorThrown) {
                error(jqxhr);
            }
        });
    });
});

var validate_tags = function() {

    if ($('#tags').val() === "") {
        $('.tagit').css({
                border: '1px solid red'
            })
            .after('<p class="text-danger">Please fill this element.</p>');
        return false;
    }
    return true;
}

//Tags to user
$(function() {
    /*
    For adding tags to a User. 
    */

    $('#tags-form').on('submit', function(event) {
        event.preventDefault();

        if (validate_tags()) {

            var submit = $(this).children('input[type="submit"]');
            $.ajax({
                url: '/add-user-tags',
                type: 'POST',
                data: $(this).serialize(),
                beforeSend: function() {
                    submit.attr('value', 'Adding ... ')
                        .attr('disabled', true);
                },
                complete: function() {
                    $('#tags').attr('value', '');
                    submit.attr('value', 'Add')
                        .attr('disabled', false);
                },
                success: function(data, textStatus, jqxhr) {
                    var list = $('.list-group');
                    var alt_msg = list.next();

                    if (!$.isEmptyObject(alt_msg)) {
                        alt_msg.remove();
                    }

                    list.children().remove();
                    $.each(data, function(key, value) {
                        var firstHalf = '<a href="#" data-id="';
                        var secondHalf = '" class="close" type="button">';
                        var link = firstHalf + value + secondHalf + 'x</a>';
                        list.append('<li class="list-group-item">' + key + link);
                    });

                    $('.tagit-choice').remove();
                },
                error: function(jqxhr, textStatus, errorThrown) {
                    if (jqxhr.status === 406) {
                        showAlert('At least one tag is required.', 'info');
                    } else {
                        showAlert('Error while adding tags', 'danger');
                    }
                }
            });

        }
    });
});

// Removing tags
$(function() {
    /*
    For removing tags from the User.
    */
    $('.list-group').on('click', 'a[type="button"]', function() {
        var self = $(this);
        var id = self.data('id');
        $.ajax({
            url: '/remove-user-tags',
            type: 'POST',
            data: {
                'id': id
            },
            success: function(data) {
                self.parent().remove()
            },
            error: function(jqxhr, textStatus, errorThrown) {
                var json = jqxhr.responseJSON;
                showAlert(json.message, 'danger');
            }
        });
    });
});

// Event on Selecting Options
$(function() {
    /*
    This sets up an event where each option is checked for the selected
    class. If it has that class, the selected class is removed.
    HACK - Serialize() do not include fields which do not have names.
    Hence, we remove the name attribute if the option is not selected
    to stop it from showing in the form.
    */
    $('.question-box').on('click', '.options > .btn', function() {
        var btn = $(this);
        if (btn.hasClass('btn-info') || btn.hasClass('btn-danger')) {
            btn.removeClass('btn-info').addClass('btn-default');
            btn.removeClass('btn-danger').addClass('btn-default');
            btn.next().removeAttr('name');
        } else {
            btn.removeClass('btn-default').addClass('btn-info');
            btn.next().attr('name', 'opt');
        }
    });
});

var get_questions = function(id = 0) {
    data = {};

    if (id) {
        data.question_id = id;
    }

    if (keep_solved_ques() || id) { // Don't remove solved on specific question too.
        data.remove_solved = 0; // don't remove solved
    }

    $.ajax({
        url: '/get-questions',
        data: data, // To show solved or not
        success: function(data, textStatus, jqxhr) {
            QUESTION_LIST = data;
            load_next_question();
        },
        error: function(jqxhr, textStatus, errorThrown) {
            error(jqxhr);
        }
    });

}

var load_next_question = function() {

    if ($.isEmptyObject(QUESTION_LIST)) {
        get_questions();
        return;
    }

    for (var key in QUESTION_LIST) {
        console.log(key);
        var data = QUESTION_LIST[key];
        $('.question-box .row').replaceWith(data); // Replaces all the descendants

        delete QUESTION_LIST[key];
        break;
    }

    checks();

    return;
}

var validate_options_check = function() {
    if (!$('.options > .btn').hasClass('btn-info')) {
        showAlert('Choose at least one option.', 'info');
        return false;
    }
    return true;
}

var auto_load = function() {
    if ($('#auto-load').hasClass('btn-success')) {
        return true;
    }
    return false;
}

// Loading questions of Sidebar
$(function() {
    $('.sidebar').on('click', 'p > a', function(event) {
        event.preventDefault();
        id = $(this).data('id');
        get_questions(id);
    });
});

// Submitting Questions for User
$(function() {
    $('.question-box').on('submit', '.option-form', function(event) {
        event.preventDefault();
        var submit = $('.option-form input[type="submit"]');

        if (submit.val() === "Next Question") {
            location.reload();
            return;
        }

        if (validate_options_check()) {

            var is_correct = false;

            $.ajax({
                url: '/check-answer',
                type: 'POST',
                data: $(this).serialize(),
                beforeSend: function() {
                    submit.attr('value', 'Checking...')
                        .prop('disabled', true);
                },
                complete: function() {

                    if (is_correct) {
                        submit.attr('disabled', true);

                        if (auto_load()) {
                            var counter = 3;
                            var interval = setInterval(function() {
                                counter--;
                                submit.attr('value', 'Loading ' + counter)

                                if (counter === 0) {
                                    submit.attr('value', 'Loading..')
                                    load_next_question();
                                    console.log('returned before query complete')
                                    clearInterval(interval);
                                }
                            }, 1000);

                        } else {
                            submit.attr('value', 'Next Question')
                                .attr('disabled', false);
                        }

                    } else {
                        submit.attr('value', 'Recheck')
                            .attr('disabled', false);
                    }

                },
                success: function(data, textStatus, jqxhr) {

                    var options = $('.options .btn-info');

                    $.each(data, function(key, value) {
                        if (value) {
                            is_correct = true;
                        } else {
                            is_correct = false;
                            return false; // To exit the loop
                        }
                    });

                    if (is_correct) {
                        options.removeClass('btn-info')
                            .addClass('btn-success');
                    } else {
                        options.removeClass('btn-info')
                            .addClass('btn-danger');
                    }
                },
                error: function(jqxhr, textStatus, errorThrown) {
                    if (jqxhr.status === 406) {
                        showAlert('Choose at least one Option', 'info');
                    } else {
                        showAlert('Something went wrong.', 'danger');
                    }
                    submit.attr('value', 'Check')
                        .prop('disabled', false);
                }
            }).done();
        }

    });
});

$(function() {
    /*
    For adding the disabled button on downvote if upvoted 
    and vice versa
    */
    checks();

    // For setting the height of Sidebar 
    // and user tags
    var height = parseInt($('.question-box').css('height'));
    if (height > 564) {
        var obj = {
            height: height
        }
        $('.user-tags-col').css(obj);
        $('.sidebar').css(obj);

    }
});

// close boxes using data dismiss
$(function() {
    $('.close').on('click', function() {
        var id = $(this).data('dismiss');
        $('#' + id).hide(20).attr('style', '');
    });
});

// For showing the MathJax Preview
$(function() {
    var elem = $('#modify-ques-form #body');
    if (elem.val() !== "") {
        UpdateMath(elem.val(), "MathQues").addClass('lead')
            .removeClass('placeholder-text');
    }
    elem.on('keyup', function() {
        var text = $(this).val();
        UpdateMath(text, "MathQues").addClass('lead')
            .removeClass('placeholder-text');
    });
});

// For shwing the description preview
$(function() {
    var elem = $('#modify-ques-form #description');
    if (elem.val() != "") {
        UpdateText(elem.val(), "#desc-preview");
    }
    $('#modify-ques-form #description').on('keyup', function() {
        var text = $(this).val();
        UpdateText(text, "#desc-preview");
    });
});

$(function() {
    preview('#solution-form #body', 'sol-preview');
});

$(function() {
    preview('form #option1', 'option_preview_1');
});

$(function() {
    preview('form #option2', 'option_preview_2');
});

$(function() {
    preview('form #option3', 'option_preview_3');
});

$(function() {
    preview('form #option4', 'option_preview_4');
});

/*MATHJax Configurations*/
MathJax.Hub.Config({
    extensions: ["tex2jax.js", "mml2jax.js", "asciimath2jax.js"],
    tex2jax: {
        inlineMath: [
            ['$', '$'],
            ['\\(', '\\)']
        ]
    },
    asciimath2jax: {
        delimiters: [
            ['`', '`'],
            ['$', '$']
        ]
    }
});
