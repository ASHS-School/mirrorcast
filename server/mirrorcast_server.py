# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 20:09:22 2017

@author: jacob
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Mirrorcast Server for Linux, make sure you install ffmpeg to make use of ffplay
#Please use python3 and not 2.7, 2.7 will cause problems

import socket,subprocess,time,logging, threading

logging.basicConfig(filename='/var/log/mirrorcast_server.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info("Started Server")

timestamp = time.localtime()
connected = ""
ready = False

def connection():
    retries = 10
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ""
        sock.bind((host,8092))
    
        sock.listen(5)
        
        global connected
        global timestamp
        global ready
        
        
        while True:
            client, address = sock.accept()
            status = client.recv(8024)
            command = status.decode('ascii')
            command = command.split(",")
            #Some else is already connected
            if connected != command[1] and connected != "":              
                client.send("busy".encode('ascii'))
                logging.info(str(command[1]) + " tried to connect but " + str(connected) + " is already connected")
            #User started casting or reconnected
            if command[0] == "play":
                if connected == "":
                    connected = command[1]
                    logging.info(connected + " has connected")
                if connected == command[1]:
                    ready == False
                    timestamp = time.localtime()
                    subprocess.call("fuser -k 8090/udp",shell=True)
                    subprocess.call("nohup ffplay -fs -probesize 10000 -sync ext udp://0.0.0.0:8090?listen > /tmp/nohup.out &",shell=True)
                    time.sleep(1)
                    #Inform client that it is now ok to start ffmpeg
                    client.send("ready".encode('ascii'))
                    
            #Client intiated a stop
            elif command[0] == "stop" and connected == command[1]: 
                ready = False
                logging.info(connected + " has disconnected")
                connected = ""
                subprocess.call("fuser -k 8090/udp &",shell=True)
                client.close()
     
            #Check if client is still online
            if command[0] == "active":
                timestamp = time.localtime()
                ready = True
                client.send("ok".encode('ascii'))
    
        client.close()
        retries = 10
    except:
        retries = retries - 1
        #To prevent logs from getting spammed if there is a problem
        if retries > 0:
            logging.warn("There was a issue with sockets, will retry in 20 seconds")
        time.sleep(20)
        return

def timeout():
    global connected
    global timestamp
    global ready
    while True:
        #Can no longer contact client, kill omxplayer
        now = time.mktime(time.localtime())
        stamp = time.mktime(timestamp)
        if (now - stamp) > 20 and connected != "" and ready == True:
            timestamp = time.localtime()
            logging.warn(connected + " timed out. " + str(now) + " :: " + str(stamp))
            ready = False
            subprocess.call("fuser -k 8090/udp &", shell=True)
            time.sleep(1)
            connected = ""
    return
    
loop = threading.Thread(target=timeout)
loop.start()
while True:
    connection()
