function hizligetir(item){
if (item=="start") {
	$('.alans1, .alan1').attr("style","display:none;");
    $('.alans2, .alan2').attr("style","display:block;");
    $('#ackapa').attr("onclick","hizligetir('turn')");
    $('#ackapa').html('<i class="fas fa-list"></i> Servislere Geç');
}
if (item=="turn") {
	$('.alans1, .alan1').attr("style","display:block;");
    $('.alans2, .alan2').attr("style","display:none;");
    $('#ackapa').attr("onclick","hizligetir('start')");
    $('#ackapa').html('<i class="fas fa-bolt"></i> Hızlı Siparişe Geç');
}
}