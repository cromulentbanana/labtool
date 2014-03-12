from __future__ import print_function

import sys
import datetime
import dateutil.parser
import dateutil.tz

import prettytable
from parsedatetime import parsedatetime

def gen_table(headers):
	table = prettytable.PrettyTable(headers)
	table.vrules = prettytable.ALL
	table.hrules = prettytable.ALL
	table.align = "l"

	return table

def lazytimeparse(rawstr, allow_none=True):
	""" wrapper arround dateutil.parser.parse to take away some pain """
	if type(rawstr) == datetime.datetime:
		return rawstr
	if rawstr is None and allow_none:
		return rawstr
	return dateutil.parser.parse(rawstr)

def tznow():
	return datetime.datetime.now(dateutil.tz.tzlocal())

def strtodatetime(rawstr, errorname=None):
	""" Parse all those nifty timestrs like 'in 1 hour' with parsedatetime. """
	dt, flag = parsedatetime.Calendar().parse(rawstr)
	tz = dateutil.tz.tzlocal()
	if flag == 0:
		# error
		extra = None
		if errorname:
			extra = "with parameter %s" % errorname
		else:
			extra = "somewhere"
		print("You supplied an unparseable datetime string %s (string was '%s')" % (extra, rawstr), file=sys.stderr)
		sys.exit(1)
	elif flag in (1, 2, 3):
		ret = datetime.datetime(*dt[:6], tzinfo=tz)
	else:
		# should never happen, guarding this with an exception
		raise ValueError("parsedatetime returnted unknown flag")

	# make it timezone aware
	return ret
