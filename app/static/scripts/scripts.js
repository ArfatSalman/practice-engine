$(function(){
  //jQuery.post( url [, data ] [, success ] [, dataType ] )
  $(".option-form").on("submit", function(event){
    event.preventDefault();
    $.post('/check-answer', $(this).serialize(), function(){
      
      console.log('success');

    });

  });

});


$(function(){

    $('#tags').tagit({
          allowSpaces: true,
                autocomplete : {
                  source: function (request, response) {
                    $.ajax({
                      url:'/get-tags',
                      dataType:'json',
                      data: {
                        query: request.term
                      },
                      success: function(data) {
                        response($.map(data, function(item){
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


 MathJax.Hub.Config({
  extensions: ["tex2jax.js","mml2jax.js","asciimath2jax.js"],
        tex2jax: {
    inlineMath: [ ['$','$'], ['\\(','\\)'] ]
  },
        asciimath2jax: {
    delimiters: [['`','`'], ['$','$']]
  }
       
      });

// close boxes using data dismiss
$(function(){ 
  $('.close').on('click', function(){
    var id = $(this).data('dismiss');
    $('#'+id).hide(20).attr('style','');
  });
});

var UpdateMath = function (TeX, elementID) {
    //set the MathOutput HTML
    //document.getElementById("MathOutput").innerHTML = TeX;
    $('#'+elementID).text(TeX);

    //reprocess the MathOutput Element
    
    MathJax.Hub.Queue(["Typeset",MathJax.Hub,elementID]);
    return $('#'+elementID);
};

var UpdateText = function(text, elementID) {
	$(elementID).text(text);
	return (elementID);
}


$(function(){

	var elem = $('form #body');
	if (elem.val() != "") {
		    UpdateMath(elem.val(), "MathQues").addClass('lead')
    				.removeClass('placeholder-text');
	}

  elem.on('keyup', function(){

    var text = $(this).val();
    
    UpdateMath(text, "MathQues").addClass('lead')
    .removeClass('placeholder-text');
       
  });
});

$(function(){
	var elem = $('form #description');

	if (elem.val() != "") {
			UpdateText(elem.val(), "#desc-preview");
	}

  $('form #description').on('keyup', function(){

    var text = $(this).val();

    UpdateText(text, "#desc-preview");

  });
});
