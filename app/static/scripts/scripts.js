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
                            console.log(item);
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
                var list = $('.list-group')
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
                showAlert(json.message, 'danger')
            }
        });
    });
});


$(function () {
    /*
    This sets up an event where each option is checked for the selected
    class. If it has that class, the selected class is removed.
    HACK - Serialize() do not include fields which do not have names.
    Hence, we remove the name attribute if the class is not selected
    to stop it from showing in the form.
    */
    $('.options > p').on('click', function () {
        var p = $(this);
        if (p.hasClass('selected')) {
            p.removeClass('selected');
            p.next().removeAttr('name');
        } else {
            p.addClass('selected');
            p.next().attr('name', 'opt');
        }
    });
});


$(function () {
    $('.option-form').on('submit', function (event) {
        event.preventDefault();
        $.ajax({
            url: '/check-answer',
            type: 'POST',
            data: $(this).serialize(),
            beforeSend: function () {
                $('.option-form input[type="submit"]')
                    .attr('value', 'Checking...')
                    .prop('disabled', true);
            },
            complete: function () {},
            success: function (data, textStatus, jqxhr) {
                var options = $('.selected');
                $.each(data, function (key, value) {
                    var option = $('input[value=' + key + ']')
                        .prev()
                        .removeClass('selected');
                    if (value) {
                        option.addClass('correct');
                    } else {
                        option.addClass('incorrect');
                    }
                });
            },
            error: function (jqxhr, textStatus, errorThrown) {
                if (jqxhr.status === 406) {
                    showAlert('Choose at least one Option', 'info');
                } else {
                    showAlert('Something went wrong.', 'danger');
                }
            }
        }).done(function () {
            $('.option-form input[type="submit"]')
                .attr('value', 'Checked')
                .attr('disabled', true);
        });
    });
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
    if (elem.val() != "") {
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



