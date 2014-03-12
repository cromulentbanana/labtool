#!/usr/bin/env python
from __future__ import print_function

from config import __version__

import argparse
import sys

from resthandler import RestHandler

class CustomArgstrHelpFormatter(argparse.HelpFormatter):
	def _format_args(self, action, default_metavar):
		""" Add custom metavar names for some actions """
		if action.dest == 'reserve':
			return "starttime endtime device1 [device2 ...]"
		elif action.dest == 'set_bootmode':
			return "device bootmode"
		elif action.dest == 'extend':
			return "reservation_id endtime"
		else:
			return super(CustomArgstrHelpFormatter, self)._format_args(action, default_metavar)

def _parser():
	parser = argparse.ArgumentParser(description="Labtool Command-line User Interface", formatter_class=CustomArgstrHelpFormatter, prog="lab")
	cmds = parser.add_mutually_exclusive_group(required=True)
	cmds.add_argument('--version', action='version', version='labcli %s' % (__version__,), help='')
	cmds.add_argument('--show-reservations', '--sr', nargs='?', choices=['past', 'current', 'future'], const='current', help='Show current, past or future reservations')
	cmds.add_argument('--show-devices', '--sd', nargs='?', choices=['all', 'free'], const='free', action='store', help='')
	cmds.add_argument('--reserve', '-r', nargs='+', help='Reserve one or more devices')
	cmds.add_argument('--extend', '-x', nargs=2, help='Extend a reservation')
	cmds.add_argument('--end', '-e', action='store', metavar='reservation_id', help='End a reservations')

	cmds.add_argument('--powercycle', '-p', action='store', metavar='device', help='Powercycle a device')
	cmds.add_argument('--console', '-c', action='store', metavar='device', help='Access the serial console of a device')
	cmds.add_argument('--set-bootmode', '--sb', nargs="+", action='store', metavar='device', help='Set the bootmode for a device')
	cmds.add_argument('--get-bootmode', '--gb', action='store', metavar='device', help='Get the bootmode for a device')
	cmds.add_argument('--list-bootmodes', '--lb', nargs='?', const=True, metavar='device', help='List all available bootmodes')

	parser.add_argument('--user', '-u', help='maunz')

	return parser

def main():
	# parse cli-arguments
	parser = _parser()
	args = parser.parse_args(sys.argv[1:])

	# initialize resthandler
	RestHandler.initialize("labcli.conf")


	# execute action
	from lablib import show_reservations, show_devices, reserve, powercycle, get_bootmode, set_bootmode, list_bootmodes, extend_reservation, end_reservation, access_serial_console

	if args.show_reservations:
		show_reservations(args.show_reservations)
	elif args.show_devices:
		if args.show_devices not in ('free', 'all'):
			parser.error("Argument to --show-devices must be either 'free' or 'all'")
		show_devices(show_free_only=args.show_devices=='free')
	elif args.reserve:
		if len(args.reserve) < 3:
			parser.error("For a reservation you need to supply a start time, an end time and at least one device")
		reserve(args.reserve[0], args.reserve[1], args.reserve[2:])
	elif args.extend:
		extend_reservation(args.extend[0], args.extend[1])
	elif args.end:
		end_reservation(args.end)
	elif args.powercycle:
		powercycle(args.powercycle)
	elif args.console:
		access_serial_console(args.console)
	elif args.get_bootmode:
		get_bootmode(args.get_bootmode)
	elif args.set_bootmode:
		if len(args.set_bootmode) == 1:
			print("You didn't supply a bootmode to set.")
			list_bootmodes(args.set_bootmode[0])
		elif len(args.set_bootmode) > 2:
			parser.error("Too many arguments for --set-bootmode")
		else:
			set_bootmode(args.set_bootmode[0], args.set_bootmode[1])
	elif args.list_bootmodes:
		list_bootmodes(args.list_bootmodes if args.list_bootmodes is not True else None)
	else:
		parser.error("No command given")
