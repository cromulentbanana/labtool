/**
 * Labfront API
 * Wrapper for jQuery AJAX calls
 */
var API;API||(API={});
(function () {
	var api_url = "/api/";
	var cache = {};

	/*
		Default error handler.
		Catches HTTP statuses and displays alerts accordingly.
	*/
	API.on_error = function(err) {
		var str = "<h2>An error occured.</h2>";
		console.log(err);
		switch(err.status) {
			/*case 400: str += "400: Invalid request format."; break;*/
			case 401: str += "401: You are not authorized for this action."; break;
			case 500: str += "500: Internal Server Error."; break;
			default:
				if (err.responseText)
					str += err.responseText;
				else
					str += err.statusText;
		}
		bootbox.alert(str);
	};

	/*
		Wrapper for generic requests to API.
		method can be something like "device" or a complete resource_uri like "/api/device/..."
		Works with all HTTP methods. Params for methods other than GET are JSON'ified.
	*/
	API.request = function(method, params, callback, callback_error, options, type) {
		var url = method;
		if (method.indexOf("api") === -1)
			url = api_url + method + '/';

		var type = type || 'GET';
		var callback_error = callback_error || API.on_error;
		var opt = {};

		if (type != "GET" && typeof params === 'object') {
			params = JSON.stringify(params);
			opt.contentType = 'application/json';
			opt.dataType = 'json';
		}

		options = $.extend({}, {
			type: type,
			url: url,
			data: params,
			success: callback,
			error: callback_error
		}, opt, options);

		$.ajax(options);
	};

	/* Wrapper for GET requests to API */
	API.get = function(method, params, callback, callback_error, options) {
		API.request(method, params, callback, callback_error, options, 'GET');
	};
	/* Wrapper for GET, results are cached for subsequent rerquest for the same resource */
	API.getCached = function(resource_uri, params, callback, callback_error, options) {
		if (typeof cache[resource_uri] != "undefined") {
			callback( cache[resource_uri] );
		} else {
			API.request(resource_uri, params, function(data) {
				if (data.resource_uri)
					cache[ data.resource_uri ] = data;
				callback(data);
			}, callback_error, options, 'GET');
		}
	}

	/* Wrapper for POST requests to API */
	API.post = function(method, params, callback, callback_error, options) {
		API.request(method, params, callback, callback_error, options, 'POST');
	};

	/* Wrapper for DELETE requests to API */
	API._delete = function(method, params, callback, callback_error, options) {
		API.request(method, params, callback, callback_error, options, 'DELETE');
	};

	/* Wrapper for PATCH requests to API */
	API.patch = function(method, params, callback, callback_error, options) {
		API.request(method, params, callback, callback_error, options, 'PATCH');
	};

	/* Wrapper for PATCH requests to API */
	API.put = function(method, params, callback, callback_error, options) {
		API.request(method, params, callback, callback_error, options, 'PUT');
	};

	/**
		Tries to create a new reservation via API.

		reservation = {
			start: Date object,
			end: Date object,
			devices: list of device_ids
		}
	*/
	API.createReservation = function( reservation, on_success ) {
		var on_success = on_success || function(data) {
			bootbox.alert('<h2>Sucess!</h2>Your reservation has been saved.');
			console.log(data);
		};
		var on_error = function(err) {
			var data = JSON.parse(err.responseText);
			if (data) {
				var str = "<h2>An error occured.</h2>";
				if (typeof data.conflicting != "undefined") {
					str += "This reservation conflicts with an existing reservation.<ul>";
					for (var k in data.conflicting.pairs) {
						var pair = data.conflicting.pairs[k];
						str += "<li><span class='device-name'>" + pair[0] + "</span> <span class='reservation-label'>" + pair[1] + "</span></li>";
					}
					str += "</ul>";
				}
				
				/* Show dialog */
				bootbox.dialog( str , [
					{'class':'btn-primary','label':'Try a different date','callback':function(){
						$('.reserve-select-date').click();
					}},
					{'class':'btn','label':'Cancel'}]);

				/* Resolve sub API ressources */
				$('.device-name').resolveName();
				$('.reservation-label').each(function(){
					var $this = $(this),
						resource_uri = $this.text();
					API.getCached(resource_uri, {}, function(data) {
						$this.html("by <span class='user-name'>" + data.user + "</span> from " + Date.parse(data.startTime).toString('dd/MM/yyyy HH:mm') +  " to " + Date.parse(data.endTime).toString('dd/MM/yyyy HH:mm'));
						$('.user-name').resolveName('username');
					});
				});


			} else {
				// if responseText is nothing meaningful, use the default error handler
				API.on_error(err);
			}
		}

		var params = {
			'startTime': reservation.start,
			'endTime': reservation.end,
			'devices': reservation.devices
		};
		var options = {
			contentType: 'application/json',
			dataType: 'json',
			processData: false
		}
		API.post('reservation', params, on_success, on_error, options);
	};

}());

/************ JSON *************/
var JSON;JSON||(JSON={});
(function () {function k(a) {return a<10?"0"+a:a}function o(a) {p.lastIndex=0;return p.test(a)?'"'+a.replace(p,function (a) {var c=r[a];return typeof c==="string"?c:"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)})+'"':'"'+a+'"'}function l(a,j) {var c,d,h,m,g=e,f,b=j[a];b&&typeof b==="object"&&typeof b.toJSON==="function"&&(b=b.toJSON(a));typeof i==="function"&&(b=i.call(j,a,b));switch(typeof b) {case "string":return o(b);case "number":return isFinite(b)?String(b):"null";case "boolean":case "null":return String(b);case "object":if (!b)return"null";
e += n;f=[];if (Object.prototype.toString.apply(b)==="[object Array]") {m=b.length;for (c=0;c<m;c += 1)f[c]=l(c,b)||"null";h=f.length===0?"[]":e?"[\n"+e+f.join(",\n"+e)+"\n"+g+"]":"["+f.join(",")+"]";e=g;return h}if (i&&typeof i==="object") {m=i.length;for (c=0;c<m;c += 1)typeof i[c]==="string"&&(d=i[c],(h=l(d,b))&&f.push(o(d)+(e?": ":":")+h))}else for (d in b)Object.prototype.hasOwnProperty.call(b,d)&&(h=l(d,b))&&f.push(o(d)+(e?": ":":")+h);h=f.length===0?"{}":e?"{\n"+e+f.join(",\n"+e)+"\n"+g+"}":"{"+f.join(",")+
"}";e=g;return h}}if (typeof Date.prototype.toJSON!=="function")Date.prototype.toJSON=function () {return isFinite(this.valueOf())?this.getUTCFullYear()+"-"+k(this.getUTCMonth()+1)+"-"+k(this.getUTCDate())+"T"+k(this.getUTCHours())+":"+k(this.getUTCMinutes())+":"+k(this.getUTCSeconds())+"Z":null},String.prototype.toJSON=Number.prototype.toJSON=Boolean.prototype.toJSON=function () {return this.valueOf()};var q=/[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
p=/[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,e,n,r={"\u0008":"\\b","\t":"\\t","\n":"\\n","\u000c":"\\f","\r":"\\r",'"':'\\"',"\\":"\\\\"},i;if (typeof JSON.stringify!=="function")JSON.stringify=function (a,j,c) {var d;n=e="";if (typeof c==="number")for (d=0;d<c;d += 1)n += " ";else typeof c==="string"&&(n=c);if ((i=j)&&typeof j!=="function"&&(typeof j!=="object"||typeof j.length!=="number"))throw Error("JSON.stringify");return l("",
{"":a})};if (typeof JSON.parse!=="function")JSON.parse=function (a,e) {function c(a,d) {var g,f,b=a[d];if (b&&typeof b==="object")for (g in b)Object.prototype.hasOwnProperty.call(b,g)&&(f=c(b,g),f!==void 0?b[g]=f:delete b[g]);return e.call(a,d,b)}var d,a=String(a);q.lastIndex=0;q.test(a)&&(a=a.replace(q,function (a) {return"\\u"+("0000"+a.charCodeAt(0).toString(16)).slice(-4)}));if (/^[\],:{}\s]*$/.test(a.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g,"@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,
"]").replace(/(?:^|:|,)(?:\s*\[)+/g,"")))return d=eval("("+a+")"),typeof e==="function"?c({"":d},""):d;throw new SyntaxError("JSON.parse");}})();