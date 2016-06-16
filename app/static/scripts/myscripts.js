var showAlert = function(message, category) {

  var alert = '<div class="alert alert-' + category || 'success' + ' alert-dismissible" role="alert">' +
  '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
  '<span aria-hidden="true">&times;</span>' + 
  '</button>'+ message +'</div>';
  $('#alert').append(alert);
};

// close boxes using data dismiss
$(function(){ 
  $('.close').on('click', function(){
    var id = $(this).data('dismiss');
    $('#'+id).hide(20).attr('style','');
  });
});

//MathJax Config
 MathJax.Hub.Config({
  extensions: ["tex2jax.js","mml2jax.js","asciimath2jax.js"],
        tex2jax: {
    inlineMath: [ ['$','$'], ['\\(','\\)'] ]
  },
        asciimath2jax: {
    delimiters: [['`','`'], ['$','$']]
  }
       
      });


var UpdateMath = function (TeX, elementID) {
    //set the MathOutput HTML
    //document.getElementById("MathOutput").innerHTML = TeX;
    $('#'+elementID).text(TeX);

    //reprocess the MathOutput Element
    
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,elementID]);
    return $('#'+elementID);
};

// Upvotes 
$(function () {

  if ($('#upvote').hasClass('btn-success'))
  {
    $('#downvote').attr('disabled','true');
  }

  $('#upvote').on('click', function () {

    var self = $(this);
    var upvoted = self.hasClass('btn-success');
    var id = $('input[name="question-id"]').val();
    if (!upvoted)
    {
      $.post('ajax/upvote', {
        id: id
      }, function () {
        self.addClass('btn-success').removeClass('btn-default');
        var upvote = self.siblings('h4');
        var currentUpvote = parseInt(upvote.text(), 10);
        upvote.text(currentUpvote + 1);
        $('#downvote').attr('disabled','true');
      });
    } 
    else {
      $.post('ajax/remove-upvote', {
        id: id
      }, function () {
        self.addClass('btn-default').removeClass('btn-success');
        var upvote = self.siblings('h4');
        var currentUpvote = parseInt(upvote.text(), 10);
        upvote.text(currentUpvote - 1);
        $('#downvote').removeAttr('disabled');
      });
    }
  });

});


// Favourite

$(function(){

  $('#favourite').on('click', function(){

    var self = $(this);
    var span = self.children();

    var favourited = span.hasClass('glyphicon-star');
    var id = $('input[name="question-id"]').val();

    if (!favourited)
    {
      $.post('ajax/add-favourite', {id:id}, function(data){
        span.removeClass('glyphicon-star-empty').addClass('glyphicon-star');
      }).fail(function(err){
        var msg = err.responseJSON;
        showAlert(msg.message, 'danger');
      });
    }
    else
    {
      $.post('ajax/remove-favourite', {id:id}, function(){
        span.removeClass('glyphicon-star').addClass('glyphicon-star-empty');
      }).fail(function(err){
        var d = err.responseJSON;
        alert(d.message);
      });
    }
  });
});

// Remove Chosen Subjects
$(function () {
  $('.list-group-item').on('click', 'a[type="button"]', function () {
    var self = $(this);
    var id = self.data('id');
    var subjectName = self.parent().clone().children().remove().end().text().trim();
    $.ajax({
      type: 'POST',
      url: 'ajax/remove-topics',
      data: {
        'id': id
      },
      success: function (data) {
        self.parent().remove();
        $('#topic').append('<option value="'+ id +'">' + subjectName +'</option>');
      }
    });
  });
});

// Preview

$(function(){

  $('form #body').on('keyup', function(){

    var text = $(this).val();
    
    UpdateMath(text, "MathQues").addClass('lead')
    .removeClass('placeholder-text');
       
  });
});

$(function(){

  $('#preview-form #description').on('keyup', function(){

    var text = $(this).val();

    UpdateMath(text, "MathDesc").removeClass('placeholder-text');

  });
});

$(function(){
  var spanStart = '<span class="label label-info">';
  var exit =  '<button type="button"  data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
  var spanEnd = '</span>';
  $('#preview-form #topics').change(function(){
   var spans = "";
   $('#preview-form #topics option:selected').each(function(){

    spans += spanStart+$(this).text()+spanEnd; 
  });

   var topics =  $('#preview .topics');
   topics.html(spans);
 });
});

// Answer box 

$(function(){
  $('#post-answer').on('click', function(e){
    e.preventDefault();

    $('#answer-wrapper').toggle();

  });
});


$(function(){

  $('#answer').on('keyup', function(){

    var text = $(this).val();

    UpdateMath(text, "answer-preview").css({
    'border': '1px solid lightblue',
    'min-height': '100px',
    'padding': '5px'});



  });

});

$(function(){

  $('#answer-wrapper > .form-group').on('submit',function(e){

    
    var details = $('input[name="question-id"], #answer-wrapper >.form-group').serialize();

    $.post('ajax/add-answer', details, function(){
      $('#answer-wrapper').fadeOut(0);
    }).fail();

    e.preventDefault();

  });
});


$(function(){

  $('#edit-answer').on('click',function(){

    $('#answer-wrapper').toggle();

  });
});

$(function(){
  $('#view-answer').on('click', function(){
    $('#answer-wrapper').hide();
    $('#other-answers').toggle();
  });
});

// POST answer
