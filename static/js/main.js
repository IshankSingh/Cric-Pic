$(document).ready(function(){


  $('.jss-live-score-btn').click(function() {
    $('html, body').animate({scrollTop: $('.jss-scroll-section').offset().top}, 1000);
  });


  $('.jss-predict-score-btn').click(function() {
    $('html, body').animate({scrollTop: $('.jss-section-efficiency').offset().top}, 1000);
  });


});
