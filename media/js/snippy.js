function get_preview_dom_element () {
	var id_for_preview = 'preview';
	return document.getElementById(id_for_preview);
}

function submit_preview (id_with_value) {
	/* shows the loading message */
	$('#loader').css("display", "block");

	/* save the data from form */
	data = document.getElementById(id_with_value).value;

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
