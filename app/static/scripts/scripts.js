var QUESTION_LIST = {}

var checks = function () {
    if ($('#upvote').hasClass('btn-success')) {
        $('#downvote').attr('disabled', true);
    }

    var downvote = $('#downvote');
    if (downvote.hasClass('btn-success')) {
        $('#upvote').attr('disabled', true);
    }

};

var showAlert = function (message, category = "success") {
    /*
    It shows a bootstrap-styled alert box for notifications.
    */
    var alert = '<div class="alert alert-' + category + ' alert-dismissible" role="alert">' +
        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
        '<span aria-hidden="true">&times;</span>' +
        '</button>' + message + '</div>';
    $('#alert').append(alert);
};


var UpdateMath = function (TeX, elementID) {
    //set the MathOutput HTML
    //document.getElementById("MathOutput").innerHTML = TeX;
    $('#' + elementID).text(TeX);
    //reprocess the MathOutput Element
    MathJax.Hub.Queue(["Typeset", MathJax.Hub, elementID]);
    return $('#' + elementID);
};


var UpdateText = function (text, elementID) {
    $(elementID).text(text);
    return (elementID);
}


var preview = function (inputElem, previewElem) {
    var elem = $(inputElem);
    if (elem.val() != "") {
        UpdateMath(elem.val(), previewElem);
    }
    elem.on('keyup', function () {
        var text = $(this).val();
        UpdateMath(text, previewElem);
    });
}


var error = function(jqxhr) {
    var json = jqxhr.responseJSON;
    showAlert(json.message, 'danger');
}


$(function () {
    $('#tags').tagit({
        allowSpaces: true,
        autocomplete: {
            source: function (request, response) {
                $.ajax({
                    url: '/get-tags',
                    dataType: 'json',
                    data: {
                        query: request.term
                    },
                    success: function (data) {
                        response($.map(data, function (item) {
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


$(function(){
    var fav = $('#favourite');

    $('.question-box').on('click', '#favourite' ,function(){
        $.ajax({
            url: '/favourite-question',
            type: 'POST',
            data: $('input[name="question-id"]').serialize(),
            success: function(){
                var fav_star = fav.children();

                if (fav_star.hasClass('glyphicon-star-empty')) {
                    
                    fav_star.removeClass('glyphicon-star-empty')
                        .addClass('glyphicon-star');

                    fav.removeClass('btn-default')
                        .addClass('btn-success');
                }
                else {

                    fav_star.removeClass('glyphicon-star')
                        .addClass('glyphicon-star-empty');

                    fav.removeClass('btn-success')
                        .addClass('btn-default');
                }
                
            },
            error: function(jqxhr) {
                error(jqxhr);
            }
        });
    });
});


$(function(){
    /*Add or remove upvotes to a question. */

    $(document).on('click', '#upvote', function(){
        
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
                }
                else {
                    upvote.removeClass('btn-success')
                    .addClass('btn-default');

                    upvote_count.text(currentUpvote-1);

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


$(function(){
     /*Add or remove downvote*/
    $('.question-box').on('click', '#downvote', function(){
        
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
                }
                else {
                    downvote.removeClass('btn-success')
                            .addClass('btn-default');

                    upvote_count.text(currentUpvote+1);

                    $('#upvote').attr('disabled', false);
                }
            },
            error: function(jqxhr, textStatus, errorThrown) {
                error(jqxhr);
            }
        });
    });
});

$(function () {
    /*
    For adding tags to a User. 
    */
    $('#tags-form').on('submit', function (event) {
        event.preventDefault();
        var submit = $(this).children('input[type="submit"]');
        $.ajax({
            url: 'add-user-tags',
            type: 'POST',
            data: $(this).serialize(),
            beforeSend: function () {
                submit.attr('value', 'Adding ... ')
                    .attr('disabled', true);
            },
            complete: function () {
                $('#tags').attr('value', '');
                submit.attr('value', 'Add')
                    .attr('disabled', false);
            },
            success: function (data, textStatus, jqxhr) {
                var list = $('.list-group');
                var alt_msg = list.next();
                
                if (!$.isEmptyObject(alt_msg)) {
                    alt_msg.remove();
                }

                list.children().remove();
                $.each(data, function (key, value) {
                    var firstHalf = '<a href="#" data-id="';
                    var secondHalf = '" class="close" type="button">';
                    var link = firstHalf + value + secondHalf + 'x</a>';
                    list.append('<li class="list-group-item">' + key + link);
                });

                $('.tagit-choice').remove();
            },
            error: function (jqxhr, textStatus, errorThrown) {
                if (jqxhr.status === 406) {
                    showAlert('At least one tag is required.', 'info');
                } else {
                    showAlert('Error while adding tags', 'danger');
                }
            }
        });
    });
});


$(function () {
    /*
    For removing tags from the User.
    */
    $('.list-group').on('click', 'a[type="button"]', function () {
        var self = $(this);
        var id = self.data('id');
        $.ajax({
            url: '/remove-user-tags',
            type: 'POST',
            data: {
                'id': id
            },
            success: function (data) {
                self.parent().remove()
            },
            error: function (jqxhr, textStatus, errorThrown) {
                var json = jqxhr.responseJSON;
                showAlert(json.message, 'danger');
            }
        });
    });
});


$(function () {
    /*
    This sets up an event where each option is checked for the selected
    class. If it has that class, the selected class is removed.
    HACK - Serialize() do not include fields which do not have names.
    Hence, we remove the name attribute if the option is not selected
    to stop it from showing in the form.
    */
    $('.question-box').on('click','.options > p' ,function () {
        var p = $(this);
        if (p.hasClass('selected') || p.hasClass('incorrect')) {
            p.removeClass('selected');
            p.removeClass('incorrect');
            p.next().removeAttr('name');
        } else {
            p.addClass('selected');
            p.next().attr('name', 'opt');
        }
    });
});


var load_next_question = function(){
    
    if ($.isEmptyObject(QUESTION_LIST)) {
        
        $.ajax({
            url: '/get-questions',
            data: {}, // To show solved or not
            success: function(data, textStatus, jqxhr) {
                QUESTION_LIST = data;
            },
            error: function(jqxhr, textStatus, errorThrown) {
                error(jqxhr);
            }
        });

    } 

    for (var key in QUESTION_LIST) {
            var data = QUESTION_LIST[key];
            console.log(data);
            $('.question-box').html(data); // Replaces all the descendants
            
            delete QUESTION_LIST[key];
            break;
        }

    checks();

    return;
}


$(function () {
    $('.question-box').on('submit', '.option-form',function (event) {
        event.preventDefault();

        var is_correct = false;
        var submit = $('.option-form input[type="submit"]');

        $.ajax({
            url: '/check-answer',
            type: 'POST',
            data: $(this).serialize(),
            beforeSend: function () {
                submit.attr('value', 'Checking...')
                      .prop('disabled', true);
            },
            complete: function () {},
            success: function (data, textStatus, jqxhr) {
                
                var options = $('.selected');
                
                $.each(data, function (key, value) {
                    if (value) {
                        is_correct = true;
                    } else {
                        is_correct = false;
                       return false; // To exit the loop
                    }
                });


                if (is_correct) {
                    options.removeClass('selected')
                           .addClass('correct'); 
                } else {
                    options.removeClass('selected')
                            .addClass('incorrect'); 
                }
            },
            error: function (jqxhr, textStatus, errorThrown) {
                if (jqxhr.status === 406) {
                    showAlert('Choose at least one Option', 'info');
                } else {
                    showAlert('Something went wrong.', 'danger');
                }
                submit.attr('value', 'Check')
                      .prop('disabled', false);
            }
        }).done(function () {
            var auto_load = true;            
            
            if (is_correct) {
                submit.attr('disabled', true);

                if (auto_load) {
                    var counter = 5;
                    
                    var interval = setInterval(function(){
                        counter--;

                        submit.attr('value', 'Loading '+ counter)

                        if (counter === 0) {
                            clearInterval(interval);
                            load_next_question();
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

        });
    });
});

$(function(){
    /*
    For adding the disabled button on downvote if upvoted 
    and vice versa
    */
    checks();
});


// close boxes using data dismiss
$(function () {
    $('.close').on('click', function () {
        var id = $(this).data('dismiss');
        $('#' + id).hide(20).attr('style', '');
    });
});

// For showing the MathJax Preview
$(function () {
    var elem = $('form #body');
    if (elem.val() !== "") {
        UpdateMath(elem.val(), "MathQues").addClass('lead')
            .removeClass('placeholder-text');
    }
    elem.on('keyup', function () {
        var text = $(this).val();
        UpdateMath(text, "MathQues").addClass('lead')
            .removeClass('placeholder-text');
    });
});


$(function () {
    var elem = $('form #description');
    if (elem.val() != "") {
        UpdateText(elem.val(), "#desc-preview");
    }
    $('form #description').on('keyup', function () {
        var text = $(this).val();
        UpdateText(text, "#desc-preview");
    });
});


$(function () {
    preview('form #option1', 'option_preview_1')
});


$(function () {
    preview('form #option2', 'option_preview_2')
});


$(function () {
    preview('form #option3', 'option_preview_3')
});


$(function () {
    preview('form #option4', 'option_preview_4')
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

