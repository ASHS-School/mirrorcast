#!/bin/bash

function listen {
	ffplay -fs -probesize 32 -sync ext tcp://127.0.0.1:8090?listen &
	while :
	do
		connection=$(netstat -tnpa 2>/dev/null| grep "0.0.0.0:8090 .* LISTEN")
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
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .* ESTABLISHED")
		sleep 2
		if [[ "$connection" = "" ]]
		then
			echo "kiling"
			killall ffplay
			fuser 8090/tcp
			break
		fi
	done
	listen
}

listen
