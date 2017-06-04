#!/bin/bash

function listen {
	omxplayer -o hdmi -live tcp://127.0.0.1:8090?listen &
	while :
	do
		connection=$(netstat -tnpa 2>/dev/null| grep "127.0.0.1:8090 *LISTEN.*")
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
		connection=$(netstat -tnpa 2>/dev/null| grep "127.0.0.1:8090 *ESTABLISHED.*")
		sleep 2
		if [[ "$connection" = "" ]]
		then
			echo "killing"
			killall omxplayer
			fuser 8090/tcp
			break
		fi
	done
	listen
}

listen
