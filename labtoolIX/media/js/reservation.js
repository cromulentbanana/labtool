$(function(){
	var extend_reservation = function(){
		bootbox.alert('Not implemented');
	};

	var terminate_reservation = function(){
		var $this = $(this);
		bootbox.confirm('<h2>End reservation</h2>Are you sure you want to end this reservation?', function(result){
			if (!result) return;

			var tr = $this.closest('tr'),
				resource_uri = tr.data('id'),
				reservation_id = resource_uri.replace(/[^0-9]+/g, '');

			/* First try to delete reservation */
			var options = {
				contentType: 'application/json',
				dataType: 'json',
				processData: false
			};
			var on_success = function(data) {
				/* DELETE succeeded */
				$('.res_'+reservation_id).hide(500,function(){
					$(this).remove();
				})
			};
			var on_error = function(err) {
				/* DELETE failed, try to set time to now */
				if (err.status == 400) {
					var params = {
						'endTime': new Date().toGMTString(),
					};
					var on_success = function(data) {
						/* PATCH succeeded */
						$('.res_'+reservation_id).hide(500, function() {
							$(this).remove();
						})
					};
					API.patch(resource_uri, JSON.stringify(params), on_success, API.on_error, options);

				} else {
					API.on_error(err);
				}
			};
			API._delete(resource_uri, {}, on_success, on_error, options);
			/* If DELETE fails, the reservation is not running */
		});
	};

	var powercycle_device = function() {
		var $this = $(this),
			resource_uri = $this.data('id'),
			tr = $this.closest('tr');

		bootbox.confirm('<h2>Powercycle</h2>Are you sure you want to powercylce this device?', function(result){
			if (!result) return;
			
			$('.loading-indicator', tr).show();
			$this.addClass("disabled");

			var uri = resource_uri + "powercontrol/?command=powercycle";
			API.post(uri,{}, function(data) {
				console.log(data);
				$('.loading-indicator', tr).hide();
				$this.removeClass("disabled");
			},function(err){
				$('.loading-indicator', tr).hide();
				$this.removeClass("disabled");
				API.on_error(err);
			});

		});
	};

	var set_bootmode = function() {
		var $this = $(this),
			device_resource = $this.data('device-id'),
			bootmode_id = $this.data("id"),
			bootmode_name = $this.text(),
			bootmode_destructive = ($this.data("destructive")=="True"),
			tr = $this.closest('tr');

		var text = "<h2>Set Bootmode</h2><p>Are you sure you want to set the bootmode for this device to <i>"+bootmode_name+"</i>?</p>";
		if (bootmode_destructive)
			text += "<span class='text-warning'><i class='icon-warning-sign'></i> Attention, this bootmode will destroy local data!</span>";
		bootbox.confirm(text, function(result){
			if (!result) return;
			
			$('.loading-indicator', tr).show();
			$this.addClass("disabled");

			var options = {
				contentType: 'application/json',
				dataType: 'json',
				processData: false
			};
			var uri = device_resource;
			API.patch(uri, JSON.stringify({'bootmode':bootmode_id}), function(data) {
				console.log(data);
				$('.dropdown-bootmode',tr).html('<i class="icon-dashboard"></i> '+ bootmode_name).removeClass("btn-warning");
				if(bootmode_destructive) $('.dropdown-bootmode',tr).addClass("btn-warning");
				$('.loading-indicator', tr).hide();
				$this.removeClass("disabled");
				$('li', $this.parent().parent()).removeClass('active');
				$this.parent().addClass('active');
			},function(err){
				$('.loading-indicator', tr).hide();
				$this.removeClass("disabled");
				API.on_error(err);
			}, options);

		});
	};

	$('.btn-extend-reservation').click(extend_reservation);
	$('.btn-terminate-reservation').click(terminate_reservation);
	$('.btn-powercycle-device').click(powercycle_device);
	$('.btn-set-bootmode').click(set_bootmode);
	$('.loading-indicator').hide();
});
