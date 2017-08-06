#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Standard Server for Linux that uses ffplay, for raspberry pi please use the other server

import socket,subprocess,time,logging, threading

logging.basicConfig(filename='/var/log/mirrorcast_server.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info("Started Server")

timestamp = time.localtime()
connected = ""

def connection():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        sock.bind((host,8091))

        sock.listen(5)
        
        global connected
        global timestamp
        while True:
    
            client, address = sock.accept()
            status = client.recv(1024)
            command = status.decode('ascii')
            command = command.split(",")
            #Some else is already connected
            if connected != command[1] and connected != "":              
                client.send("busy")
                logging.info(str(command[1]) + " tried to connect but some one else was already connected")
            #User started casting or reconnected
            if command[0] == "play":
                if connected == "":
                    connected = command[1]
                    timestamp = time.localtime()
                logging.info(connected + " has connected")
                subprocess.call("fuser -k 8090/udp",shell=True)
                time.sleep(1)
                subprocess.call("nohup ffplay -fs -probesize 10000 -sync ext udp://0.0.0.0:8090?listen > /tmp/nohup.out &",shell=True)
                time.sleep(2)
                #Inform client that it is now ok to start ffmpeg
                client.send("ready")
            #Client intiated a stop
            elif command[0] == "stop":
                logging.info(connected + " has disconnected")
                subprocess.call("fuser -k 8090/udp",shell=True)
                client.close()
                time.sleep(1)
                connected = ""
            #Check if client is still online
            if command[0] == "active":
                client.send("ok")
                timestamp = time.localtime()

        client.close()
    except:
        logging.warn("There was a issue with sockets, will retry in 20 seconds")
        time.sleep(20)
        return

def timeout():
    global connected
    global timestamp
    while True:
        #Can no longer contact client, kill omxplayer
        if (time.mktime(time.localtime()) - time.mktime(timestamp)) > 20 and connected != "":
            timestamp = time.localtime()
            logging.warn(connected + " timed out.")
            subprocess.call("fuser -k 8090/udp", shell=True)
            time.sleep(1)
            connected = ""
    return
    
loop = threading.Thread(target=timeout)
loop.start()
while True:
    connection()
