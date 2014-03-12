$(function(){
	/*--- List devices ---*/
	var listDevices = function(objects, extend) {
		var $table = $('#device-table tbody'),
			extend = extend || false,
			table_html = (extend ? $table.html() : ''),
			getLabel = function(text, type) {
				return '<span class="device-status label label-'+type+'">'+text+'</span>';
			};
		for (var k in objects) {
			var device = objects[k];
			var until;
			if (device.is_reserved) {
				until = device.reserved_until;
			} else {
				until = device.free_until;
			}
			var until_str = (until?" until " + Date.parse( until ).toString('dd/MM/yyyy'):"");
			table_html = table_html + "<tr data-id=\"" + device.resource_uri + "\">"
							+ "<td><span class=\"device-name\">" + device.name + "</span></td>"
							+ "<td><span class=\"device-class\">" + device.deviceClasses.join("</span>, <span class=\"device-class\">") + "</span></td>"
							+ "<td>" + device.model + "</td>"
							+ "<td>" + (device.is_reserved?
									getLabel('reserved'+until_str, 'warning') :
									getLabel('free'+until_str,     'success')
									) + "</td>"
							+ "<td><div class=\"btn-group\">" +
							'<a href="javascript:void(0);" class="btn btn-small btn-primary btn-add-to-reservation"><i class="icon-signin"></i> Reserve</a>'
							+
							'<a href="javascript:void(0);" class="btn btn-small btn-show-details"><i class="icon-link"></i> Links</a>' +
							"</div> </td>" +
							+ "</tr>";
		}
		$table.html( table_html );

		$('.btn-add-to-reservation').click( add_to_reservation );
		$('.btn-show-details').click( show_details );

		/* Resolve device classes */
		$('.device-class').resolveName();

		$('#page-status').text("Showing "+ (total_objects-more_objects) + " of " + total_objects + " entries.");
	};

	var per_page = 40,
		more_objects = 0,
		offset = 0,
		total_objects = 0,
		order_by = 'name',
		order_asc = true,
		loading_html = $('#device-table tbody').html();
	/*--- Init device list ---*/
	var init_list = function(){
		$('.load-actions').hide();
		$('#device-table tbody').html(loading_html);
		var order_string = (order_asc?'':'-') + order_by;
		API.get('device', {'limit': per_page, 'order_by': order_string}, function(data){
			more_objects = data.meta.total_count - (data.objects.length + data.meta.offset);
			total_objects = data.meta.total_count;
			if (data.objects)
				listDevices(data.objects);
			if (more_objects)
				$('.btn-load-more').show();
			else
				$('.btn-load-more').hide();
			offset += data.objects.length;
			$('.load-actions').show();
		});
	};
	init_list();

	/*--- Reset reservation container ---*/
	var reset_reservation_container = function() {
		$('#reservation-device-list').empty();
		$('.reservation-container').slideUp(200);
	};

	/*--- Live Search ---*/
	var search_timer;
	$('#livesearch-loading').hide();
	$('#livesearch').keyup(function(){
		var $this = $(this);
		// Debounce
		var delay = 400;
		if (search_timer)
			window.clearTimeout(search_timer);
		search_timer = window.setTimeout(function(){
			var query = $this.val();

			// If query is empty, use default init_list method
			if (query == '') {
				init_list();
				return;
			}

			$('#livesearch-loading').show();
			$('#device-table tbody').html(loading_html);

			API.get('device', {'name__contains': query,'limit':0}, function(data){
				offset = more_objects = 0;
				if ('objects' in data) {
					total_objects = data.meta.total_count;
					listDevices(data.objects);
				}
				$('.btn-load-more').hide();
				$('#livesearch-loading').hide();
			});
		}, delay);
	});

	/*--- Load more items (paging) ---*/
	$('.btn-load-more').click(function(e){
		e.preventDefault();
		var $btn = $(this);
		$btn.text('Loading ...').attr('disabled', true);
		API.get('device', {'limit':per_page,'offset':offset}, function(data){
			more_objects = data.meta.total_count - (data.objects.length + data.meta.offset);
			console.log("There are " + more_objects + " more objects.");
			if (data.objects) {
				total_objects = data.meta.total_count;
				listDevices(data.objects,true);
			}
			if (more_objects)
				$('.btn-load-more').show();
			else
				$('.btn-load-more').hide();
			offset += data.objects.length;

			$btn.text('Load more').attr('disabled', false);
		});
	});

	/*--- Show details for device ---*/
	var show_details = function(e) {
		e.stopPropagation();
		var btn = $(this);

		var tr = $(this).closest('tr'),
			resource_uri = tr.data('id'),
			new_tr = tr.next();

		// Add a details row after the current row
		if (!new_tr.is('.details-row')) {
			new_tr =  $('<tr class="details-row">').html(
				'<td colspan="100%" class="details-box"><div class="details-box-content cf" style="display:none">'
				+ "" + '</div></td>'
				).insertAfter(tr);
		}
		var box = $('.details-box', new_tr),
			box_content = $('.details-box-content', box);

		if (box.is('.visible')) {
			box_content.slideUp(300,function(){
				box.removeClass('visible');
			});
		} else {
			box.addClass('visible');
			box_content.slideDown(300);
		}

		// Populate row with data
		if (!box_content.data('populated')) {
			if (!resource_uri) {
				console.log("Error gathering device's resource_uri.");
				return;
			}
			var device_id = resource_uri.replace(/[^0-9]+/g, '');
			console.log("Populating box for device "+ resource_uri+"...");
			API.get(resource_uri, {}, function(data){
				var powerPort = data.power;
				var consolePort = data.console;

				html = "";
				if (window.user.is_superuser)
					html += "<a href='/device/links/"+device_id+"/' class='btn right'>Edit links</a>"
				box_content.html(html);

				if (powerPort) {
					API.get(powerPort, {}, function(data) {
						$("<div>").html(
							"<span class='label label-info'>Power</span> <i class='icon-resize-horizontal'></i> " +
							"<span class='label label-info'>" + data.socketId+"</span> " +
							"<span class='label label-success device-name'>" + data.device + "</span>"
							).appendTo(box_content);
						$('.device-name').resolveName();
					});
				} else {
					// This might be a powerport itself, so search for devices attached to it
					API.get('powerport',{'device': device_id,'limit':0}, function(data) {
						if ('objects' in data) {
							for(var key in data.objects) {
								var port = data.objects[key];

								(function(port){
									// Gather device connected to this port
									API.get('device', {'power': port.id}, function(data) {
										if ('objects' in data) {
											for (var key in data.objects) {
												var device = data.objects[key];
												$("<div>").html(
													"<span class='label label-info'>" + port.socketId+"</span> <i class='icon-resize-horizontal'></i> " +
													"<span class='label label-info'>Power</span> " +
													"<span class='label label-success'>" + device.name + "</span>"
													).appendTo(box_content);
											}
										}
									});
								})(port);
							}
						}
					});
				}

				if (consolePort) {
					API.get(consolePort, {}, function(data) {
						$("<div>").html(
							"<span class='label label-info'>Console</span> <i class='icon-resize-horizontal'></i> " +
							"<span class='label label-info'>" + data.portId+"</span> " +
							"<span class='label label-success device-name'>" + data.device + "</span>"
							).appendTo(box_content);
						$('.device-name').resolveName();
					});
				}

				// Gather links
				API.get('linklist', {'device':device_id,'limit':0}, function(data){
					if ('objects' in data) {
						for (var k in data.objects) {
							var link = data.objects[k];
							$('<div>').html(
							    " <span class='label label-success'>" + link.deviceA.name + "</span>"+
								" <span class='label label-info'>" + link.switchPortA.name + "</span>" +
								" <i class='icon-resize-horizontal'></i> " +
								" <span class='label label-info'>" + link.switchPortB.name+"</span>" +
								" <span class='label label-success'>" + link.deviceB.name + "</span>" 
							).appendTo(box_content);
						}
					}
				});
			});

			box_content.data('populated',true);
		}
	}

	/*--- Devices add to reservation ---*/
	$('.reservation-container').hide();
	var add_to_reservation = function(e){
		e.stopPropagation();
		var btn = $(this);
		if (btn.is('.disabled')) return false;
		$('.reservation-container:hidden').slideDown(200);

		var tr = $(this).closest('tr'),
			device_name = $('.device-name', tr),
			device_status = $('.device-status',tr),
			device_list = $('#reservation-device-list');

		device_list.append( $('<li>').text( device_name.text() ) );
		var list_item = device_list.children().last();
		list_item.addClass( 'status-'+device_status.text() );
		list_item.attr('data-id', tr.data('id'));

		list_item.click(function(){
			$(this).fadeOut(100,function(){
				$(this).remove();
				btn.removeClass("disabled");
			});
		});

		/* Clone device name, animate clone to final position, remove clone */
		var clone = device_name.clone(),
			position = device_name.offset(),
			position_end = list_item.offset(),
			bezier_params = {
		    	start: {
		    		x: position.left,
		    		y: position.top,
		    		angle: 300,
		    	},
		    	end: {
		    		x:position_end.left,
		    		y:position_end.top,
		    		angle: 90,
		    		length: 0.2,
		    	}
		  	};
		list_item.hide();
		clone.appendTo(device_list);
		clone.css({
			'transform':'scale(0,0);',
			'position':'absolute',
			'opacity':1,
			'left':position.left,
			'top':position.top
		});
		list_item.fadeIn(400);
		clone.animate({opacity:0.5, path : new $.path.bezier(bezier_params)}, 400, function(){
			$(this).remove();
		});


		btn.addClass('disabled');

	};

	/*--- Finish device reservation ---*/
	$('#reservation-modal').hide();
	var current_reservation = {};
	$('.reserve-select-date').click(function(e){
		e.preventDefault();
		var str = '<h2>Select Reservation Date</h2>' +
					'<small>Selected devices: ' +
					'<ul class="reservation-container-list">' +
					$('#reservation-device-list').html() + "</ul></small>" + 
					'<div id="range-selector">' + $('#reservation-modal').html() + '</div>';
		var box = bootbox.dialog( str , [
				{'class':'btn-primary','label':'Save reservation','callback':function(){
					box.modal('hide');

					var devices = [];
					$('#reservation-device-list li').each(function(){
						devices.push( $(this).data('id') );
					});

					current_reservation.devices = devices;

					API.createReservation( current_reservation, function(data) {
						bootbox.alert('<h2>Sucess!</h2>Your reservation has been saved.');
						init_list();
						reset_reservation_container();
					} );

				}},
				{'class':'btn','label':'Cancel'}]);

		var format_selection = function(start, end) {
				//$('.input-startDate').val( start.toString('dd/MM/yyyy HH:mm') );
				//$('.input-endDate').val( end.toString('dd/MM/yyyy HH:mm') );
				current_reservation.start = start;
				current_reservation.end = end;
		};


		window.setTimeout(function(){
			/*--- Date picker ---*/
			$('.datepicker').empty().daterangepicker(
				{
				format: 'dd/MM/yyyy HH:mm',
				startDate: Date.parse( $('.input-startDate').val() ),
				endDate: Date.parse( $('.input-endDate').val() ),
				minDate: Date.today().toString('dd/MM/yyyy'),
				maxDate: Date.today().add('365 days').toString('dd/MM/yyyy'),
				locale: {
					applyLabel: 'Apply',
					fromLabel: 'From',
					toLabel: 'To',
					customRangeLabel: 'Custom Range',
					daysOfWeek: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr','Sa'],
					monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
					firstDay: 1
				},
				showWeekNumbers: false,
				buttonClasses: ['btn-primary']
				},
				format_selection
			);
			current_reservation.start = Date.parse( $('.input-startDate').val() );
			current_reservation.end = Date.parse( $('.input-endDate').val() );
		}, 1);
	});

	$('.add-to-existing-reservation').click(function(e){
		e.preventDefault();

		var existing_reservations = {};

		API.get('reservation',{'user':window.user.id,'limit':0,'scope':'not_past'},function(data){
			var select = $('<select>').attr("name","reservation_id").addClass('select-reservation').append( $('<option>').text('- Please choose -').attr("value","") );
			if ('objects' in data) {
				for (var k in data.objects) {
					var reservation = data.objects[k],
						label = reservation.id + ": " + Date.parse(reservation.startTime).toString('dd/MM/yyyy HH:mm') +
						" – " + Date.parse(reservation.endTime).toString('dd/MM/yyyy HH:mm'),
						$option = $('<option>').text(label).attr("value", reservation.id );
					existing_reservations[ reservation.id ] = reservation;
					if (data.objects.length == 1) $option.attr('selected',true);
					select.append( $option );
				}

			}
			var html = "<h2>Add to existing reservation</h2>" +
				"<p>Choose the reservation you would like to add these devices to.</p>" +
				select[0].outerHTML +
				"<div class='reservation-info'></div>";
			var box = bootbox.dialog( html , [
					{'class':'btn-primary','label':'Add to reservation','callback':function(){
						var reservation_id = $('select[name=reservation_id]').val();
						if (reservation_id == "")
							return false;
						box.modal('hide');

						var devices = [];
						$('#reservation-device-list li').each(function(){
							devices.push( $(this).data('id') );
						});

						current_reservation = existing_reservations[ reservation_id ];

						$.merge( current_reservation.devices, devices);

						API.patch('/api/reservation/' + reservation_id + '/', {'devices': current_reservation.devices }, function(data) {
							bootbox.alert('<h2>Sucess!</h2>Your reservation has been appended.');
							init_list();
							reset_reservation_container();
						} );
					}},
					{'class':'btn','label':'Cancel'}]);

			var selected_reservation = function(){
				var reservation_id = $(this).val(),
					reservation = existing_reservations[ reservation_id ];
				if (!reservation_id) return;
				$('.reservation-info').text('Reservation includes: ');
				$('.reservation-info').append( $('<ul>').addClass('reservation-container-list') );
				
				for(var d in reservation.devices) {
					$('.reservation-info ul').append(
						$('<li>').append(
							$('<span class="device-name">').text( reservation.devices[d] )
						)
					);
				}
				$('.device-name').resolveName();
			};
			$('.select-reservation').change(selected_reservation);
			selected_reservation.apply( $('.select-reservation') );
		});
		
	});

	/*--- Sort table ---*/
	$('#device-table thead th').click(function(){
		var new_field = $(this).attr('data-orderby');
		if (!new_field) return;
		// Set new order. Reverse if same field as before, else default to ascending
		order_asc = (new_field==order_by ? !order_asc : true);
		// Set new order field
		order_by = new_field;
		// Update DOM elements
		$(this).parent().find('th').attr('class', '');
		$(this).attr('class','header ' + (order_asc?'headerSortDown':'headerSortUp'));
		// Re-initialize list
		init_list();
	});

});
