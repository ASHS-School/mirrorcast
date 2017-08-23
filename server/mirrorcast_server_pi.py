#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Mirrorcast Server for Raspberry Pi, make sure to use supervisor to set up omxplayer as a daemon
#Please use python3 and not 2.7, 2.7 will cause problems

import socket,subprocess,time,logging, threading
from youtube_player import youtube

logging.basicConfig(filename='/var/log/mirrorcast_server.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info("Started Server")

timestamp = time.localtime()
connected = ""
ready = False
playing = False

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
        global playing
        
        tube = ""
        
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
                    subprocess.call("tvservice -p &",shell=True)
                    subprocess.call("fuser -k 8090/udp",shell=True)
                    subprocess.call("nohup omxplayer -o hdmi --lavfdopts probesize:8000 --timeout 0 --threshold 0 udp://0.0.0.0:8090?listen > /tmp/nohup.out &", shell=True)
                    time.sleep(1)
                    #Inform client that it is now ok to start ffmpeg
                    client.send("ready".encode('ascii'))
                    
            #Client intiated a stop
            elif command[0] == "stop" and connected == command[1]: 
                ready = False
                logging.info(connected + " has disconnected")
                connected = ""
                subprocess.call("fuser -k 8090/udp &",shell=True)
                subprocess.call("tvservice -p &",shell=True)
                
            elif command[0] == "freeze" and connected == command[1]: 
                ready = False
                connected = ""
                logging.info(connected + " has froozen their screen")
               
            #WIP, for playing youtube videos
            elif "tube" in command[0] and connected == "":
                if command[0] == "tube-load":
                    subprocess.call("tvservice -p &",shell=True)
                    subprocess.call("fuser -k 8090/udp",shell=True)
                    if tube != "":
                        tube.player.stop()
                    tube = youtube()
                    tube.url = command[2]
                    tube.start()
                    while True:
                        if tube.player.is_playing():
                            client.send("ready".encode('ascii'))
                            playing == True
                            break
                elif command[0] == "tube-stop" and tube != "":
                    tube.player.stop()
                    tube = ""
                elif command[0] == "tube-forward" and tube != "":
                    tube.player.seek(30)
                elif command[0] == "tube-back" and tube != "":
                    tube.player.seek(-30)
                elif command[0] == "tube-pause" and tube != "":
                    tube.player.play_pause()
                elif command[0] == "tube-up" and tube != "":
                    if tube.player.volume() < 700.0:
                        tube.player.set_volume(tube.player.volume() + 100.0)
                elif command[0] == "tube-down" and tube != "":
                    if tube.player.volume() > -1550.0:
                        tube.player.set_volume(tube.player.volume() - 100.0)
            
            #This condition is met if the user wants to play a DVD or Media file.
            elif command[0] == "media" and connected == "":
                logging.info(connected + " is trying to stream a Media file or DVD")
                subprocess.call("tvservice -p &",shell=True)
                subprocess.call("fuser -k 8090/udp",shell=True)
                subprocess.call("nohup omxplayer -o hdmi --lavfdopts probesize:8000 --timeout 60 --threshold 0 udp://0.0.0.0:8090?listen > /tmp/nohup.out &", shell=True)
                time.sleep(1)
                #Inform client that it is now ok to start ffmpeg
                client.send("ready".encode('ascii'))
    
            elif command[0] == "tu-media" and connected == "":
                logging.info(connected + " is trying to stream a youtube video")
                subprocess.call("tvservice -p &",shell=True)
                subprocess.call("fuser -k 8090/udp",shell=True)
                time.sleep(1)
                #Inform client that it is now ok to start ffmpeg
                client.send("ready".encode('ascii'))
     
            #Check if client is still online
            elif command[0] == "active":
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
