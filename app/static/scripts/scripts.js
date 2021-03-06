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
                }).next('.text-danger').remove();
            });
        });
    };

    $.fn.just_text_node = function(text) {
        return this.contents()
            .filter(function() {
                return this.nodeType == 3;
            })
            .replaceWith(text)
    };

}(jQuery));

function escapeHTML(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

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

    // $('.upvote-btn').each(function(){
    //     var obj = $(this);

    //     if (obj.hasClass('btn-success')) {
    //         obj.siblings('.downvote-btn')
    //            .attr('disabled', true);
    //     }
    // });

    // $('.downvote-btn').each(function(){
    //     var obj = $(this);

    //     if (obj.hasClass('btn-success')) {
    //         obj.siblings('.upvote-btn')
    //            .attr('disabled', true);
    //     }
    // });
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
    return $(elementID);
};

var preview = function(inputElem, previewElem) {

    var css = {
        color: '#000',
        'font-style': 'normal'
    };
    var elem = $(inputElem);

    if (elem.val() !== "") {
        UpdateMath(elem.val(), previewElem).css(css);
    }

    $(document).on('keyup', inputElem, function() {
        var self = $(this);
        var text = self.val();


        UpdateMath(text, previewElem).css(css);

    });
};

var error = function(jqxhr) {
    var json = jqxhr.responseJSON;

    if (json) {
        showAlert(json.message, json.category);
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


var hide_options = function() {
    var options = $('.options');
    options.css('visibility', 'hidden');
    $('.hide-option-layer').show('fast');

};

var toggle_difficulty = function() {
    var difficulty = $('.difficulty');
    var difficulty_btn = $('#hide-difficulty');

    if (difficulty_btn.hasClass('btn-success')) {
        difficulty.hide('fast');
    } else {
        difficulty.show('fast');
    }
};

var show_options = function() {
    var options = $('.options');
    $('.hide-option-layer').hide('fast');
    options.css('visibility', '');
};

var report_questions = function(self, _data) {
    var report_btn = $('#report-question');
    var data = {
        "question-id": $('input[name="question-id"]').val()
    };

    $.extend(data, _data);

    $.ajax({
        url: '/report-question',
        type: 'POST',
        data: data,
        beforeSend: function() {
            self.prop('disabled', true);
        },
        success: function() {
            toggle_two_classes(report_btn, 'btn-default', 'btn-success');

            self.prop('disabled', false);
            // Hide the modal
            $('#report-ques-modal').modal('hide');
        },
        error: function(jqxhr) {
            error(jqxhr);
        }
    });
};

// Contact Us FORM
$(function() {
    $("#contact-form").on('submit', function(e) {
        e.preventDefault();

        var self = $(this);

        var btn = self.children('#submit');

        $.ajax({
            url: '/contact-us',
            type: 'POST',
            data: self.serialize(),
            beforeSend: function() {
                btn.attr('disabled', true);
            },
            complete: function() {
                btn.attr('disabled', false);
            },
            success: function(data) {
                showAlert(data.message, 'success');
            },
            error: function(jqxhr) {
                error(jqxhr)
            }
        });
    });
});

// Skip Questions
$(function() {
    $('#skip-question-btn').on('click', function() {
        window.location.reload();
    });
});

// Report Questions
$(function() {
    $('.question-box').on('click', '#report-question', function(e) {
        var self = $(this);

        if (self.hasClass('btn-default')) {
            $('#report-ques-modal').modal();
        } else {
            report_questions(self);
        }
    });

    $('.modal').on('click', '#report-ques-btn', function(e) {
        var data = {
            message: $('#report-message').val()
        };
        var self = $(this);

        if (data.message) {
            report_questions(self, data);
        } else {
            report_questions(self);
        }
    })
});

// Updating description.
$(function() {
    $(document).on('click', '#edit-desc-btn', function(e) {
        var markup = '<textarea id="desc-text" class="form-control" rows="3"></textarea>';
        var save_btn = '<button type="submit" id="save-desc-btn" class="btn btn-default">Update</button>'
        var form = '<form id="user-desc-form" action="post">';
        var end_form = '</form>';
        var user_desc = $('#user-desc');

        var self = $(this);
        // For taking only the text value of the elem and not the child
        var text = $.trim(user_desc.contents()[0].nodeValue);

        user_desc.replaceWith(form + markup + save_btn + end_form);
        $('#desc-text').val(text).my_required();

        $('#user-desc-form').on('submit', function(e) {
            e.preventDefault();
            var new_desc = $('#desc-text').val();
            var self = $(this);
            $.ajax({
                url: '/user/info',
                type: 'POST',
                data: {
                    description: new_desc
                },
                beforeSend: function() {
                    self.attr('disabled', true);
                },
                success: function(data) {
                    var p = '<p id="user-desc">' + escapeHTML(new_desc);
                    var edit_icon = '<span class="glyphicon glyphicon-edit"></span>';
                    var end_p = '<button id="edit-desc-btn" class="btn btn-link btn-xs">' +
                        edit_icon +
                        ' Edit</button></p>';

                    $('#user-desc-form').replaceWith(p + end_p);

                    showAlert(data.message, 'success');
                },
                error: function(jqxhr) {
                    error(jqxhr)
                }
            });
        });

    });
});

//Updating username 
$(function() {
    $(document).on('click', '#edit-username-btn', function() {

        var username = $('#username');
        var user_val = $(username.contents()[0]);

        var form = '<form method="post" action="/user/info" id="edit-username-form" class="form-inline">' +
            '<div class="form-group">' +
            '<input type="text" name="username" class="form-control" placeholder="Jane Doe">' +
            '</div>' +
            '<button type="submit" class="btn btn-default">Save</button>' +
            '</form>';

        username.replaceWith(form);
        $('#edit-username-form input').val(user_val.text());

    });


});
// Hide options 
$(function() {
    var hide_opts = $('#hide-options');

    if (hide_opts.hasClass('btn-success')) {
        hide_options();
    }

    $(".question-box").on('click', '#show-options-btn', function(e) {
        show_options();
        e.preventDefault();
    });
});

// pagination 
$(function() {
    $(document).on('click', '.previous, .next', function(event) {
        event.preventDefault();

        var self = $(this);
        var user_id = $('input[name="user-id"]').val();
        var question_id = $('input[name="question-id"]').val();
        var type = self.parent().attr('class').split(' ')[0];

        var url = '/user/' + user_id + '/' + type;
        var data = {
            page: self.data('page')
        };

        if (type === 'view-solutions') {
            url = '/question/' + question_id + '/' + type;
        } else if (type === 'tag-ques') {
            url = $(location).attr('pathname');
        }

        if (self.hasClass('previous')) {
            data.page -= 1;
        } else {
            data.page += 1;
        }

        $.ajax({
            url: url,
            data: data,
            beforeSend: function() {
                self.addClass('disabled');
            },
            complete: function() {
                self.removeClass('disabled');
            },
            success: function(data, textStatus, jqxhr) {
                var html = data['content'];
                var elem = '#' + type;

                if (html) {
                    $(elem).html(html);
                }

                // For rendering the Math again.
                MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
            },
            error: function(jqxhr) {
                error(jqxhr)
            }
        });
    });
});

//Solutions 
$(function() {
    $(document).on('click', '.sol-upvote-btn, .sol-downvote-btn', function() {
        var self = $(this);

        data = {
            id: self.data('id'), // Solution ID
            is_upvote: 1
        };

        if (self.hasClass('sol-downvote-btn')) {
            data.is_upvote = 0;
        }

        $.ajax({
            url: '/vote-solution',
            data: data,
            type: 'POST',
            beforeSend: function() {
                self.attr('disabled', true);
            },
            success: function() {
                toggle_two_classes(self, 'btn-default', 'btn-success');

                if (data.is_upvote) {
                    if (self.hasClass('btn-success')) {
                        self.siblings('.sol-downvote-btn:first')
                            .attr('disabled', true);
                    } else {
                        self.siblings('.sol-downvote-btn:first')
                            .attr('disabled', false);
                    }
                } else {
                    if (self.hasClass('btn-success')) {
                        self.siblings('.sol-upvote-btn:first').attr('disabled', true);
                    } else {
                        self.siblings('.sol-upvote-btn:first').attr('disabled', false);
                    }
                }

                self.attr('disabled', false);
            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });
    });
});

//Post Solutions
$(function() {
    $(document).on('click', '#edit-sol', function() {
        var self = $(this);
        var sol_form = $('#solution-form');
        //var val = $.trim($('#to-edit').text());

        var ques_id = $('input[name="question-id"]').val();

        $.ajax({
            url: '/question/' + ques_id + '/solution',
            beforeSend: function() {
                self.attr('disabled', true);
            },
            success: function(data) {
                var val = '';

                val = data.solution;

                var css = {
                    display: 'none',
                };

                if (sol_form.css('display') === "none") {
                    css.display = 'block';

                    sol_form.css(css);
                    $('#solution-form #body').val(val);
                    $('#sol-preview').text(val).css({
                        height: '130px'
                    });
                } else {
                    sol_form.css(css);
                }

                preview('#solution-form #body', 'sol-preview');

            }
        });

        // var css = {
        //         display: 'none',
        //     };

        // if (sol_form.css('display') === "none") {
        //     css.display = 'block';

        //     sol_form.css(css);
        //     $('#solution-form #body').val(val);
        //     $('#sol-preview').text(val).css({
        //         height: '130px'
        //     });
        // } else {
        //     sol_form.css(css);
        // }
    });
});

// Submit solution
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
                success: function(data) {
                    // Reload the question.
                    var ques_id = $('input[name="question-id"]').val();
                    get_questions(ques_id);
                    //Show the appropriate message;
                    if (sol_id.length === 0) {
                        showAlert(data.message, 'success')
                    } else {
                        showAlert(data.message, 'success');
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
    var check_option_names = [
        '#check_option1',
        '#check_option2',
        '#check_option3',
        '#check_option4'
    ]

    options = $('textarea[id^="option"]');
    checked_options = $('input[id^="check_option"]:checked');
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

    if (checked_options.length === 0) {
        showAlert('At least one option should be selected as correct.', 'danger');
        has_error = true;
    } else {
        options.each(function(index) {

            var checked = false;
            var self = $(this);

            if (self.val() === '' &&
                $(check_option_names[index]).is(':checked')) {
                showAlert('A correct option should contain text.', 'danger');
            }
        });
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
                self.just_text_node('setting ...').attr('disabled', true);

            },
            success: function() {
                toggle_two_classes(self, 'btn-default', 'btn-success');
                // keep Solved Questions
                if (self.data('type') === "KSQ" && self.hasClass('btn-success')) {
                    QUESTION_LIST = {};
                }
                // Hide Options
                if (self.data('type') === "HO" && self.hasClass('btn-success')) {
                    hide_options();
                }

                // Hide Difficulty
                if (self.data('type') === 'HD') {
                    toggle_difficulty();
                }

                self.just_text_node(original_text).attr('disabled', false);
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
        onTagLimitExceeded: function(event, ui) {
            showAlert('You cannot add more than 5 tags.', 'warning');
        },
        tagLimit: 5,
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
        var new_html = '<span class="button-hover"><strong>' + count + '</strong></span>';
        self.html(new_html);
    }).on('mouseout', elemID, function() {
        var self = $(this);
        self.html(child_html);
    });
}

//UnSolved Questions
$(function() {
    $(document).on('click', '.unsolve-btn', function(e) {

        var self = $(this);
        var data = {
            'question-id': self.data('id')
        }

        $.ajax({
            url: '/unsolve',
            data: data,
            type: 'POST',
            beforeSend: function() {
                self.attr('disabled', true);
            },
            success: function(data, textStatus, jqxhr) {
                self.attr('disabled', false);
                if (self.has('span').length === 0) {
                    self.parents('.panel').remove();
                } else {
                    self.remove();
                }

                showAlert(jqxhr.responseJSON.message, 'success');
            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });
        e.stopPropagation();
    });
});

//Favourite Upvote and downvote Ajax
$(function() {

    button_hover_effects('.upvote-btn');
    button_hover_effects('.downvote-btn');
    button_hover_effects('.favourite-btn');

    $(document).on('click', '.upvote-btn, .downvote-btn, .favourite-btn', function() {

        var btn = $(this);
        var data = {
            "question-id": btn.data('id')
        };

        var url = '/upvote';
        if (btn.hasClass('downvote-btn')) {
            url = '/downvote';
        } else if (btn.hasClass('favourite-btn')) {
            url = '/favourite-question';
        }

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            beforeSend: function() {
                btn.attr('disabled', true);
            },
            complete: function() {
                btn.attr('disabled', false);
            },
            success: function() {
                var vote_count = $('.upvote-count');
                var currentvote = parseInt(vote_count.text(), 10);

                if (btn.hasClass('upvote-btn')) {
                    if (btn.hasClass('btn-default')) {
                        add_success_class(btn);
                        vote_count.text(currentvote + 1);
                        btn.siblings('.downvote-btn:first').attr('disabled', true);
                    } else {
                        add_default_class(btn);
                        vote_count.text(currentvote - 1);
                        btn.siblings('.downvote-btn:first').attr('disabled', false);
                    }
                } else if (btn.hasClass('favourite-btn')) {
                    var fav_star = btn.children('.glyphicon');
                    toggle_two_classes(btn, 'btn-default', 'btn-success')
                    toggle_two_classes(fav_star, 'glyphicon-star-empty', 'glyphicon-star')
                } else {
                    if (btn.hasClass('btn-default')) {
                        add_success_class(btn);
                        vote_count.text(currentvote - 1);
                        btn.siblings('.upvote-btn:first').attr('disabled', true);
                    } else {
                        add_default_class(btn);
                        vote_count.text(currentvote + 1);
                        btn.siblings('.upvote-btn:first').attr('disabled', false);
                    }
                }
            },
            error: function(jqxhr, textStatus, errorThrown) {
                error(jqxhr);
            }
        });
    });
});

$(function() {
    $('input.ui-widget-content').on('focus', function() {
        $('.tagit').css({
            border: '1px solid #ccc'
        }).next().remove();
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

var remove_tag_from_most_pop = function(tagname) {

    var elem = $('#most-pop-tags li').filter(function() {
        var self = $(this);
        if (self.children('a').text() === tagname) {
            return true;
        }
        return false;
    });

    if ($.isEmptyObject(elem)) {
        return false;
    }

    var btn = elem.children('button');

    btn.removeClass('btn-success').addClass('btn-info').children().text('Subscribe');

    return true;

};

//Tags Single tag subsription 
$(function() {
    $('.subs-tag').on('click', function() {
        var self = $(this);
        var url = '/user-tags';

        $.ajax({
            url: url,
            type: 'POST',
            data: {
                tag: self.data('id')
            },
            beforeSend: function() {
                self.attr('disabled', true);
            },
            success: function(data) {
                var count = self.text().split('|')[1];
                var list = $('.col-md-2 .list-group');

                if (self.hasClass('btn-info')) {
                    self.removeClass('btn-info').addClass('btn-success');
                    self.children().text('Subscribed');

                    make_tag_elem(list, data);
                } else {
                    self.removeClass('btn-success').addClass('btn-info');
                    self.children().text('Subscribe');

                    list.children().each(function() {
                        var self = $(this);

                        if (self.text().contains(data.tagname)) {
                            self.remove();
                            return false;
                        }

                    });
                }

                self.attr('disabled', false);
            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });
    });
});

var make_tag_elem = function(list, data) {
        list.children().remove();
        $.each(data, function(key, value) {
            var badge = '<span class="badge">' + value.count + '</span>';
            var cross = '<a href="#" data-id="' + value['id'] + '" class="close" type="button">&times;</a>';
            var link = '/tags/' + key;
            var tag = '<a href="' + link + '">' + key + '</a>'

            var elem = '<list class="list-group-item">' +
                tag +
                badge +
                cross +
                '</li>';
            list.append(elem);
        });
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

                    make_tag_elem(list, data);

                    $('#tags').tagit('removeAll');
                    //$('input.ui-widget-content').val('');

                    QUESTION_LIST = {};

                    window.location.reload();

                },
                error: function(jqxhr, textStatus, errorThrown) {
                    error(jqxhr);
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
        var text = self.siblings('a').text();

        $.ajax({
            url: '/remove-user-tags',
            type: 'POST',
            beforeSend: function() {
                self.siblings('a').text('Deleting..');
                self.hide();
            },
            data: {
                'id': id
            },
            success: function(data) {
                self.parent().remove();

                remove_tag_from_most_pop(text);
            },
            error: function(jqxhr, textStatus, errorThrown) {
                error(jqxhr);
            }
        });
    });
});

var select_option = function($btn) {

    /*
    This sets up an event where each option is checked for the selected
    class. If it has that class, the selected class is removed.
    HACK - Serialize() do not include fields which do not have names.
    Hence, we remove the name attribute if the option is not selected
    to stop it from showing in the form.
    */

    if ($btn.hasClass('btn-info') || $btn.hasClass('btn-danger')) {
        $btn.removeClass('btn-info').addClass('btn-default');
        $btn.removeClass('btn-danger').addClass('btn-default');
        $btn.next().removeAttr('name');
    } else {
        $btn.removeClass('btn-default').addClass('btn-info');
        $btn.next().attr('name', 'opt');
    }
}

//Kepresses bindings for options 
$(function() {
    $(document).on('keyup', function(event) {
        var key = String.fromCharCode(event.which);
        var options = $('.options .btn');

        if (event.target.nodeName !== "TEXTAREA" && event.target.nodeName !== "INPUT") {
            if (key === "1" || key === "A" || key === "a") {
                select_option($(options[0]));
            } else if (key === "2" || key === "B" || key === "b") {
                select_option($(options[1]));
            } else if (key === "3" || key === "C" || key === "c") {
                select_option($(options[2]));
            } else if (key === "4" || key === "D" || key === "d") {
                select_option($(options[3]));
            } else if (event.which === 13) {
                $('.option-form').trigger('submit');
            }
        }
    });
});

// Event on Selecting Options
$(function() {

    $('.question-box').on('click', '.options > .btn', function() {
        var $btn = $(this);
        select_option($btn);
    });
});

var get_questions = function(id = 0) {
    data = {};

    if (id) {
        data.question_id = id;
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

    MathJax.Hub.Queue(["Typeset", MathJax.Hub]);

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

// Check answer
$(function() {
    $('.question-box').on('submit', '.option-form', function(event) {
        event.preventDefault();
        var submit = $('.option-form #submit-options');

        if ($.trim(submit.text()) === "Next") {
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
                    submit.prop('disabled', true)
                        .just_text_node('Check');
                },
                complete: function() {

                    if (is_correct) {

                        if (auto_load()) {
                            var counter = 3;
                            var interval = setInterval(function() {
                                counter--;
                                submit.just_text_node(' Load in ' + counter);

                                if (counter === 0) {
                                    submit.just_text_node('Loading..');
                                    //submit.attr('value', 'Loading..')
                                    load_next_question();
                                    clearInterval(interval);
                                }
                            }, 1000);

                        } else {
                            submit.attr('disabled', false)
                                .just_text_node(' Next');
                        }

                    } else {
                        submit.attr('disabled', false).just_text_node(' Recheck');
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
                    submit.prop('disabled', false)
                        .just_text_node('Check');
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
    var height = $(document).height();

    var obj = {
        height: height - 70
    }

    $('.user-tags-col').css(obj);
    $('.sidebar').css(obj);

});

var markdown = function() {
    var convert = new Markdown.getSanitizingConverter().makeHtml;

};

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
        UpdateMath(elem.val(), "MathQues")
            .removeClass('placeholder-text');
    }
    elem.on('keyup', function() {
        var text = $(this).val();
        UpdateMath(text, "MathQues")
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
