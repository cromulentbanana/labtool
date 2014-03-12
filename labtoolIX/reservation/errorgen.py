res_errno_dict = {
	"START_BEFORE_END": 200,
	"NO_RES_IN_PAST": 201,
	"PAST_RES_UNCHANGEABLE": 202,
	"NO_SELF_EXTENDING": 203,
	"EMPTY_RESERVATION": 204,

	# Extra data: conflicting: {devices: [unreservable devices], reservations: [conflicting reservations], pairs: [(device, reservation)]}
	"CONFLICTING_RESERVATION": 205,

	# Extra data: unreservable_devices: [unreservable devices]
	"DEV_NOT_ALLOWED": 206,

	# ?foruser=X can only be used by a superuser
	"FORUSER_ADMIN_ONLY": 207,
	"RESERVATION_404": 208,
	"NOT_YOUR_RESERVATION": 209,
}

