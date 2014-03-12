/*--- Populate port select field ---*/
jQuery.fn.populate_port_select = function(device_id) {
		return $(this).each(function(){
			var element = $(this),
				selected = element.data('selected'),
				box = $(this).closest('.link-box');
			console.log("Population switchport", element.attr("name"));
			element.removeAttr("disabled").empty();
			element.append( $('<option>').text( '- Choose port -' ).val("0") );
			API.getCached('switchport', {'device':device_id,'limit':0,'order_by':'name'}, function(data){
				if ('objects' in data) {
					for (var k in data.objects) {
						var port = data.objects[k],
							opt = $('<option>').val( port.id ).text( port.name );
						if (port.id == selected) 
							opt.attr("selected",true);
						element.append( opt );
					}
					if (data.objects.length==0)
						element.attr("disabled",true);
				}
				$('.loading:visible').fadeOut(250);
			});

		});
	};

$(function(){
	var link_container_selector = '.link-row';
	var link_messages = {
		'edit_existing': 'Changing existing link',
		'add_new': 'Adding a new link',
		'override': 'Overriding another link'
	};
	$('select.switchPortA').populate_port_select( $('.device-info').data('id') );

	$('select.deviceB').change(function(e){
		device_id = $(this).val();
		if (!device_id) return;
		$('select.switchPortB', $(this).closest(link_container_selector) ).populate_port_select( $(this).val() );
	});
	$('select.deviceB[data-selected]').change();
	if ( $('select.deviceB[data-selected]').length == 0) {
		$('.loading').hide();
	}

	$('select').change(function(e){
		var box = $(this).closest(link_container_selector);
	
		if ($(this).data('selected') && $(this).val() != $(this).data('selected')) {
			
			/* Check for existing links on the new switchPort
			   and print warning if found */
			var newPort = $(this).val();
			var link_callback = function(data){
				if (data.objects.length > 0) {
					$('.form-message',box).removeClass('text-info').addClass('text-warning')
						.text(link_messages['override']);
				}
			};
			API.get('link', {'switchPortA':newPort}, link_callback);
			API.get('link', {'switchPortB':newPort}, link_callback);

			$('.form-message',box).removeClass('text-warning').addClass('text-info')
				.text(link_messages['edit_existing']);
			$('.btn-reset',box).show();
		} else {
			$('.form-message',box).text("");
			$('.btn-reset',box).hide();
		}
	});

	/* Reset all selects to initial value */
	$('.btn-reset').hide().click(function(){
		var box = $(this).closest(link_container_selector);
		$(this).hide();
		$('select.switchPortA',box).val( $('select.switchPortA',box).data("selected") );
		$('select.deviceB',box).val( $('select.deviceB',box).data("selected") );
		$('select.deviceB',box).change();
		$('.form-message',box).text("");
		$('.add-new-input',box).hide();
	});

	$('.add-new-input').hide();

	$('.ports-filter a').click(function(){
		var sel = $(this).attr('href').substr(1);
		$('.ports-filter li').removeClass('active');
		$(this).parent().addClass('active');
		if (sel == '') {
			$('.filter-unused, .filter-used').show();
		}
		if (sel == 'used') {
			$('.filter-used').show();
			$('.filter-unused').hide();
		}
		if (sel == 'unused') {
			$('.filter-used').hide();
			$('.filter-unused').show();
		}
	});
});
