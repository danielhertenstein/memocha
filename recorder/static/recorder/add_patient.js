$(document).ready(function() {
    var prescription_list = $("#prescription_list");
	$("#add").click(function() {
		var intId = prescription_list.find("div").length + 1;
        var field_wrapper = $("<div id='field" + intId + "'/>");
        var medication = $("<input type='text' id='medication' placeholder='Medication' /><br/>");
        var dosage = $("<input type='text' placeholder='Dosage' />");
        var remove_button = $("<input type='button' value='Remove' />");
        var times = $("<br/><input type='text' placeholder='Times' />");
        remove_button.click(function() {
            $(this).parent().remove();
        });
        field_wrapper.append(medication);
        field_wrapper.append(dosage);
        field_wrapper.append(remove_button);
        field_wrapper.append(times);
        prescription_list.append(field_wrapper);
  });
});