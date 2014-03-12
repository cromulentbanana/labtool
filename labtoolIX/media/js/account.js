$(function(){

	var disable_enable_user = function(){
		var $this = $(this),
			user_resource = $this.closest("tr").data('id'),
			disable = $this.hasClass('btn-disable-user'),
			text = "", // Text of confirm dialog
			api_uri = user_resource, // API url being called
			new_btn_html = ""; // new button HTML if call was succesful
		
		if (disable) {
			text = '<h2>Disable User</h2>Are you sure you want to disable this user?';
			api_uri += 'active/disable';
			new_btn_html = '<i class="icon-ok-circle"></i> Enable';
		} else {
			text = '<h2>Enable User</h2>Are you sure you want to enable this user again?';
			api_uri += 'active/enable';
			new_btn_html = '<i class="icon-remove-circle"></i> Disable';
		}
		bootbox.confirm(text, function(result){
			if (!result) return;
			$this.attr("disabled",true);
			API.post(api_uri, {}, function(data){
				bootbox.alert(data); // TODO Remove as soon as backend works
				$this.attr("disabled",false);

				/* TODO Un-comment as soon as backend works
				$this.toggleClass('btn-danger btn-success btn-disable-user btn-enable-user')
					.html(new_btn_html)
					.click(enable_user);
				*/
			});
		});
	};

	var show_user_details = function(e){
		var $this = $(this),
			tr = $this.closest('tr'),
			box = $('.details-box', tr.next()),
			box_content = $('.details-box-content', box);;

		if (box.is('.visible')) {
			box_content.slideUp(300,function(){
				box.removeClass('visible');
			});
		} else {
			box.addClass('visible');
			box_content.slideDown(300);
		}

		e.preventDefault();
	};

	$('.btn-disable-user,.btn-enable-user').click(disable_enable_user);
	$('.btn-show-details').click(show_user_details);
});
