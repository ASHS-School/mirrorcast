#!/bin/bash

function listen {
	fuser 8090/tcp
	killall omxplayer
	sleep 2
	omxplayer -o hdmi --lavfdopts probesize:5000 --timeout 0 -live tcp://0.0.0.0:8090?listen &
	while :
	do
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .* LISTEN")
		sleep 2
		if [[ "$connection" = "" ]]
		then
			echo "listening"
			break
		fi
	done
	active
}

function active {
	sleep 5
	while :
	do
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .*ESTABLISHED")
		sleep 2
		if [[ "$connection" = "" ]]
		then
			echo "killing"
			killall omxplayer
			fuser -k 8090/tcp
			break
		fi
	done
	listen
}

listen
