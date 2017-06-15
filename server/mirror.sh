#!/bin/bash

function listen {
	killall ffplay*
	fuser -k 8090/tcp
	sleep 1
	nohup ffplay -fs -probesize 7000 -sync ext tcp://0.0.0.0:8090?listen &
	sleep 1
	while :
	do
		sleep 1
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .* LISTEN")
		sleep 1
		if [[ $connection = "" ]]
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
		client=$(netstat -tnpa 2>/dev/null|grep -o -P '(?<=8090).*(?=:)')
		ping=$(ping -c 1 -W 1 $client |grep "1 received")
		sleep 1
		if [[ $connection = "" || $ping = "" ]]
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
