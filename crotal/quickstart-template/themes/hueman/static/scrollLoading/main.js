(function($){
  // Image scroll loading
  $('.main-body-content img').each(function() {
    $(this).attr('data-url', $(this).attr('src'));
    $(this).removeAttr('src');
    $(this).addClass('scrollLoading');
    $(this).wrap('<div class="scrollLoading-wrap"></div>');
  });
  function setScrollLoading(){
    var scrollLoadings = $('.scrollLoading');
    scrollLoadings.scrollLoading();
    for(var i = 0; i < scrollLoadings.length; i++){
      if(scrollLoadings[i].complete){
        $('.scrollLoading').eq(i).unwrap();
      } else {
        $('.scrollLoading').eq(i).load(function(){
          $(this).parent().unwrap();
        })
      }
    }
  }
  setScrollLoading();
})(jQuery);
