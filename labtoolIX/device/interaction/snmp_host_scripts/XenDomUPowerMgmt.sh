#!/usr/bin/env bash
#
# This script will power {on,off,cycle} a virtual machine hosted on the XEN DomO it is run on
#
# Args: < on | off | cycle | state > < vm_name >
# Retr: 0 on success, 1 on error + Message to stderr
#
# @author: Bernd May <bm@dv-team.de>
#
# TODO: test this...

op="$1"
vm_name="$2"

# verify and sanitize input
if ! [[ "$op" =~ '^(on|off|cycle|state)$' ]]; then
	echo "Invalid operation '$op'!" >&2
	exit 1
elif ! [[ "$vm_name" =~ '^[A-Za-z0-9_.]+$' ]]; then
	echo "Invalid DomU Name!" >&2
	exit 1
fi

# test if we are run on Xen Dom0, whether xm command is there and xend is running
if ! pgrep -f xend &>/dev/null; then
	echo "Xend not running on $(hostname)!" >&2
	exit 1
elif ! which xm &>/dev/null; then
	echo "Xen mangement tool 'xm' not found!" >&2
	exit 1
fi

# test if vm exists
if [[ ! -e "/etc/xen/${vm_name}" ]]; then
	echo "$vm_name could not be found on $(hostname)!" >&2
	exit 1
fi

_is_vm_running(){
	if xm list "$vm_name" &>/dev/null; then
		return true
	else
		return false
	fi
}


# run appropriate command
case "$op" in
"on")
	if _is_vm_running; then
		echo "ERROR: VM $vm_name already exists!" >&2
		exit 1
	else
		echo "Will now spawn VM $vm_name"
#		xm create "$vm_name" 1>/dev/null
	fi
	;;
"off")
	if ! _is_vm_running; then
		echo "ERROR: VM $vm_name is not running!" >&2
		exit 1
	else
		echo "Will now destroy VM $vm_name"
#		xm destroy "$vm_name" 1>/dev/null
	fi
	;;
"cycle")
	if ! _is_vm_running; then
		echo "ERROR: VM $vm_name is not running!" >&2
		exit 1
	else
		echo "Will now destroy and respawn VM $vm_name"
#		xm destroy "$vm_name" 1>/dev/null && sleep 5 && xm create "$vm_name" 1>/dev/null
	fi
	;;
"status")
	if ! _is_vm_running; then
		echo "VM $vm_name is not running!"
	else
		list_output=$(xm list auth 2>/dev/null)
		if [ $? -eq 0 ]; then 
			state=$(echo "$list_output" | sed -rne 's/.*[:numeric:]*\s[:numeric:]*\s[:numeric:]*\s([rbpscd-]{6}).*/\1/p')
		fi
		if [[ "$state" =~ '(b|r)' ]]; then
			echo "VM $vm_name is running!"
		elif [[ "$state" =~ '(s|d)' ]]; then
			echo "VM $vm_name is shutting down!"
		elif [[ "$state" =~ '(p|c)' ]]; then
			echo "VM $vm_name requires administrative care!"
		else
			echo "VM $vm_name state unknown!" > &2
			exit 1
		fi
	fi

	;;
*)
	echo "ERROR: Operation $op not supported!" >&2
	exit 1
esac

exit $?
