function get_preview_dom_element () {
	var id_for_preview = 'preview';
	return document.getElementById(id_for_preview);
}

/* this function return string I want to preview */
function get_data_to_preview (textarea) {
	/* https://developer.mozilla.org/en/DOM/TextArea */
	start = textarea.selectionStart;
	end = textarea.selectionEnd;

	/* textarea must be a textarea DOM element */
	var is_selected_something = (start == end);

	if(!is_selected_something)
		return textarea.value.slice(start, end);

	return textarea.value;
}

function submit_preview (id_with_value) {
	/* shows the loading message */
	$('#loader').css("display", "block");

	/* save the data from form */
	data = get_data_to_preview(document.getElementById(id_with_value));

	/**/
	var preview = get_preview_dom_element();

	/* send content for preview */
	xhr = $.ajax({
		/* FIXME: DRY */
		url: '/preview/',
		type: "POST",
		data: ({content: data}),
		success: function (rdata, textStatus) {
			preview.innerHTML = rdata;
			$('#loader').css("display", "none");
		}
	});

	return false;
}
