#!/bin/bash

function listen {
	killall ffplay*
	fuser -k 8090/tcp
	nohup ffplay -fs -probesize 8000 -sync ext tcp://0.0.0.0:8090?listen &
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
			echo "lost connection"
			killall ffplay*
			fuser -k 8090/tcp
			break
		fi
	done
	listen
}

listen
