
/**
	Resolves API resource IDs in given elements with corresponding name data
	Example:
	  Before: <span class='foo'>/api/device/1/</span>
	  $('.foo').resolveName();
	  After:  <span class='foo'>DeviceName</span>

	Name is cached across multiple calls to the same resource ID.
*/
jQuery.fn.resolveName = function(key) {
	var key = key || "name";
	return $(this).each(function(){
			var $this = $(this),
				resource_uri = $this.text();
			if (resource_uri.indexOf("/api") === -1) // doesn't look like api resource
				return;
			API.getCached(resource_uri, {}, function(data) {
				$this.text(data[key]);
			});
		});
};

/**
 * Make table header fixed
 */
jQuery.fn.fixedHeader = function(s) {
	return $(this).each(function() {
		// Add a clone of header to table
		var $this = $(this),
			addedOffset = $this.data('offset'),
			$header = $("thead", $this).clone()
					.data('offset',addedOffset)
					.prependTo($this);

		// Explicitly set widths of every column		
		$("th",$header).each(function(index){
		    var index2 = index;
		    $(this).width(function(index2){
		        return $("th",$this).eq(index).width();
		    });
		});

		// Affix clone
		$header.css('opacity',0);
		window.setTimeout(function(){
			$header.css('opacity','');
			$header.affix();
		}, 1); // Sometimes the offset() calculates wrongly if not waiting for a repaint.
	});
}
jQuery.fn.affix = function(s) {
	return $(this).each(function() {
		var $this = $(this),
			addedOffset = $this.data('offset') || 0,
			elemOffset = $this.offset().top,
			scrollOffset = elemOffset - addedOffset;
		
		$this.addClass('fixed').css({'top':addedOffset,'width':$this.width()});
			
		$(window).bind("scroll", function() {
			var offset = $(this).scrollTop();

			if (offset >= scrollOffset && !$this.is(".visible")) {
				$this.addClass('visible');
			}
			else if (offset < scrollOffset) {
				$this.removeClass('visible');
			}
		});
	});

}

$(function(){
	$('.data').fixedHeader();
	$('.affix').affix();
});

