#!/bin/bash

function listen {
	fuser -k 8090/tcp
	killall omxplayer*
	sleep 2
	nohup omxplayer -o hdmi --lavfdopts probesize:5000 --timeout 0 -live tcp://0.0.0.0:8090?listen &
	while :
	do
		sleep 1
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .* LISTEN")
		sleep 1
		if [[ "$connection" = "" ]]
		then
			echo "established"
			break
		fi
	done
	active
}

function active {
	sleep 5
	while :
	do
		sleep 1
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .*ESTABLISHED")
		sleep 1
		if [[ "$connection" = "" ]]
		then
			echo "connection dropped"
			killall omxplayer*
			fuser -k 8090/tcp
			break
		fi
	done
	listen
}

listen
