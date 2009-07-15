function get_preview_dom_element () {
	var id_for_preview = 'preview';
	return document.getElementById(id_for_preview);
}

function insert_as_nth_entry (id_container, el_to_insert, n) {
	var container = document.getElementById(id_container);
	container.insertBefore(el_to_insert, container.childNodes[n]);
}

function submit_new_entry (id_content) {
	/* shows the loading message */
	$('#loader').css("display", "block");

	/* save the data from form */
	data = document.getElementById(id_content).value;

	/* insert as child the new entry */
	var entry = document.createElement('div');
	entry.className = 'entry';
	insert_as_first_entry('container', entry);

	$('#loader').css("display", "none");

	/* first send the content to add*/
	xhr = $.ajax({
		url: '/entry/add/',
		type: "POST",
		data: ({content: document.getElementById(id_content).value}),
		success: function (rdata, textStatus) {
			entry.innerHTML = rdata;
			clean_preview();
		}
	});

	return false;
}

function show_submit_in_preview () {
	document.getElementById('save_button').style.display = 'block';
}

function hide_submit_in_preview () {
	document.getElementById('save_button').style.display = 'none';
}

function clean_preview () {
	preview = get_preview_dom_element();
	preview.innerHTML = '';
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
			show_submit_in_preview();
			$('#loader').css("display", "none");
		}
	});

	return false;
}
