#!/bin/bash

function listen {
	fuser -k 8090/tcp
	killall omxplayer*
	sleep 1
	#You can change the position and dimesions of the output with --win "x1 y1 x2 y2"
	#For example, you might want this for projectors that overshoot their screens
	sleep 1
	nohup omxplayer -o hdmi --lavfdopts probesize:5000 --timeout 0 -live tcp://0.0.0.0:8090?listen &
	while :
	do
		sleep 1
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .* LISTEN")
		sleep 1
		if [[ "$connection" = "" ]]
		then
			echo "on 0" | cec-client -s
			echo "established"
			sleep 1
			echo "as" | cec-client -s
			break
		fi
	done
	active
}

function active {
	while :
	do
		sleep 1
		connection=$(netstat -tnpa 2>/dev/null| grep ":8090 .*ESTABLISHED")
		client=$(netstat -tnpa 2>/dev/null|grep -o -P '(?<=8090).*(?=:)')
		ping=$(ping -c 1 -W 1 $client |grep "1 received")
		sleep 1
		if [[ "$connection" = "" || $ping = "" ]]
		then
			echo "standby 0" | cec-client -s
			echo "connection dropped"
			killall omxplayer*
			fuser -k 8090/tcp
			break
		fi
	done
	listen
}

listen
