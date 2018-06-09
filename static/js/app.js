$(document).ready(function(){
setTimeout(function(){
  	$(".alert").fadeOut(1400);
  },2000);
  jQuery(".responsive-text").fitText();
  jQuery(".radiobuttons").iCheck({
          radioClass: 'iradio_square-green',
          increaseArea: '30%'
  });

});