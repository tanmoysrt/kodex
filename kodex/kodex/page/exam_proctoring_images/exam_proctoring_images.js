frappe.pages['exam-proctoring-images'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Exam Proctoring Images',
		single_column: true
	});

	let ecr_field = page.add_field({
		fieldname: 'name',
		label: __('Select Examination Candidate Registration'),
		fieldtype:'Link',
		options:'Examination Candidate Registration',
		change: function() {
			if(!ecr_field.get_value()) return
			frappe.call({
				method:'kodex.kodex.doctype.examination_candidate_registration.examination_candidate_registration.get_proctoring_images',
				args: {
					exam_candidate_registration_name: ecr_field.get_value()
				},
				callback: function(r) {
					if (r.exc) {
						frappe.msgprint(r.exc);
					} else {
						get_exam_proctoring_images(r.message);
					}
				}
			})
		},
	});

	window.ecr_field = ecr_field;

	ecr_field.set_value((new URLSearchParams(window.location.search)).get("id"));
}

function get_exam_proctoring_images(images_list) {
	let exam_proctoring_images_div = document.getElementById('exam-proctoring-images-list');
	if(!exam_proctoring_images_div) {
		exam_proctoring_images_div = document.createElement('div');
		exam_proctoring_images_div.id = 'exam-proctoring-images-list';
		exam_proctoring_images_div.classList.add('container');
		exam_proctoring_images_div.style.marginTop = '20px';
		exam_proctoring_images_div.style.flexWrap = 'wrap';
		exam_proctoring_images_div.style.display = 'flex';
		exam_proctoring_images_div.style.gap = '20px';
		cur_page.page.appendChild(exam_proctoring_images_div);
	} else {
		exam_proctoring_images_div.innerHTML = '';
	}
	if (!images_list || images_list.length == 0) {
		exam_proctoring_images_div.innerHTML = '<i>No images found</i>';
	}
	for(let i = 0; i < images_list.length; i++) {
		let img = document.createElement('img');
		img.src = images_list[i];
		img.style.width = '300px';
		img.style.height = '200px';
		img.style.objectFit = 'cover';
		img.style.borderRadius = '10px';
		img.style.cursor = 'pointer';
		exam_proctoring_images_div.appendChild(img);
	}
}