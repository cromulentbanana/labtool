from helper import mapResources
ERROR_UNKNOWN = 100

def generic_error(errno, title, message, extra):
	d = {
		"errno": errno,
		"title": title,
		"message": message,
	}

	# map resources to rest-api locations
	if extra:
		extra = mapResources(extra)
		d.update(extra)

	return d

def unknown_error():
	return generic_error(ERROR_UNKNOWN, "Unknown error", "An unknown/unexpected error occured.")

