#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Mirrorcast Server for Raspberry Pi.
#Please use python3 and not 2.7, 2.7 will cause problems
#Mirrorcast Server Version 0.7.0b
import socket,subprocess,time,logging, threading, os, datetime
from omx import Omx

logging.basicConfig(filename='/var/log/mirrorcast_server.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
logging.info("Started Server")

timestamp = time.localtime()
connected = ""
ready = False
playing = False
tube = None
sub = 0
audio = 0
#subprocess.call("modprobe nbd",shell=True)

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
        
        global tube 
        tube = Omx()
        
        while True:
            client, address = sock.accept()
            status = client.recv(8024)
            command = status.decode('ascii')
            print(command)
            command = command.split(",")
            #Some else is already connected
            if connected != command[1] and connected != "":              
                client.send("busy".encode('ascii'))
                logging.info(str(command[1]) + " tried to connect but " + str(connected) + " is already connected")
            #User started casting/mirroring or reconnected
            if command[0] == "play":
                if connected == "":
                    connected = command[1]
                    logging.info(connected + " has connected")
                if connected == command[1]:
                    ready == False
                    timestamp = time.localtime()
                    if tube.player != None:
                        kill(tube.player)
                    subprocess.call("tvservice -p &",shell=True)   
                    tube.mirror()
                    time.sleep(1)
                    #Inform client that it is now ok to start ffmpeg
                    client.send("ready".encode('ascii'))
                    
            #Client intiated stop mirroring
            elif command[0] == "stop" and connected == command[1]: 
                ready = False
                logging.info(connected + " has disconnected")
                connected = ""
                kill(tube.player)
                #subprocess.call("tvservice -o &",shell=True)
                
            #Client wants to freeze the screen
            elif command[0] == "freeze" and connected == command[1]:     
                ready = False
                connected = ""
                logging.info(connected + " has froozen their screen")
                #client.send("paused".encode('ascii'))
            elif command[0] == "freezee" and connected == command[1]:     
                ready = False
                connected = ""
                if tube.player != None:
                    time.sleep(1)
                    tube.player.pause()
                logging.info(connected + " has froozen their screen")
                client.send("paused".encode('ascii'))
               
            #WIP, for playing youtube videos
            elif "tube" in command[0] and connected == "":
                if command[0] == "tube-load":
                    if tube.player != None:
                        kill(tube.player)
                    tube.url = command[2]
                    subprocess.call("tvservice -p &",shell=True)
                    if tube.youtube() == False:
                            client.send("error".encode('ascii'))
                            playing = True
                    else:
                        while True:
                            if tube.player.is_playing():
                                client.send("ready".encode('ascii'))
                                playing = True
                                break
                elif command[0] == "tube-stop" and tube.player != None:
                    kill(tube.player)
                    #subprocess.call("tvservice -o &",shell=True)
                    tube.player = None
                elif command[0] == "tube-forward" and tube.player != None:
                    if tube.player.can_control():
                        tube.player.seek(30)
                elif command[0] == "tube-back" and tube.player != None:
                    if tube.player.can_control():
                        tube.player.seek(-30)
                elif command[0] == "tube-pause":
                    if tube.player.can_control():
                        tube.player.play_pause()
                elif command[0] == "tube-up" and tube.player != None:
                    if tube.player.can_control():
                        if tube.player.volume() < 700.0:
                            tube.player.set_volume(tube.player.volume() + 100.0)
                elif command[0] == "tube-down" and tube.player != None:
                    if tube.player.can_control():
                        if tube.player.volume() > -1550.0:
                            tube.player.set_volume(tube.player.volume() - 100.0)
                elif command[0] == "tube-track-down" and tube.player != None:
                    if tube.player.can_control():
                        tube.player.action(6)
                elif command[0] == "tube-track-up" and tube.player != None:
                    if tube.player.can_control():
                        tube.player.action(7)
                elif command[0] == "tube-vol" and tube.player != None:
                    if tube.player.can_control():
                        tube.player.set_volume(float(command[2]))
                        
            #This condition is met if the user wants to play a DVD or Media file.
            elif command[0] == "media" and connected == "":
                logging.info(connected + " is trying to play a video file or DVD")
                subprocess.call("tvservice -p &",shell=True)
                if tube.player != None:
                    kill(tube.player)
                    tube.player = None
                if tube.dvdplayer != None:
                    tube.dvdplayer.quit()
                time.sleep(1)
                client.send("ready".encode('ascii'))
                
            elif  command[0] == "media-start" and connected == "":
                logging.info(connected + "is attempting to play http://" + str(address) + ":8090/" + command[1])
                if tube.start_media(address[0], command[1]):
                    logging.info("Playing " + command[1])
                else:
                    logging.info("Error Playing " + command[1])
            elif "dvd" in command[0] and connected == "":
                if command[0] == "dvd-start" and connected == "":
                    logging.info(connected + "is attempting to play a DVD")
                    subprocess.call("tvservice -p &",shell=True)
                    newpath = r'/tmp/DVD' 
                    if not os.path.exists(newpath):
                        os.makedirs(newpath)
                    subprocess.call("umount /tmp/DVD",shell=True)
                    subprocess.call("nbd-client -d /dev/nbd0",shell=True)
                    subprocess.call("nbd-client " + str(address[0]) + " -name dvd /dev/nbd0 -b 2048", shell=True)
                    subprocess.call("mount /dev/nbd0 /tmp/DVD",shell=True)
                    tube.start_dvd()
                    sub = 0
                    #Get the amount of audio tracks and subtitles avaible on DVD(May cause issues when more than 1 movie on DVD)
                    tube.get_tracks()
                elif command [0] == "dvd-pause" and tube.dvdplayer != None:
                    if not tube.dvdplayer._get_property("pause"):
                        tube.dvdplayer.command('show_text', "Paused")
                        tube.dvdplayer._set_property("pause", True)
                    else:
                        tube.dvdplayer._set_property("pause", False)
                        tube.dvdplayer.command('show_text', "Resumed")
                elif command[0] == "dvd-forward" and tube.dvdplayer != None:
                        tube.dvdplayer.seek(30)
                        tube.dvdplayer.command('show_text', "Seeking 30 seconds " + str(datetime.timedelta(seconds=int(tube.dvdplayer._get_property("time-pos")))) + "/" + str(datetime.timedelta(seconds=int(tube.dvdplayer._get_property("duration")))))
                elif command[0] == "dvd-back" and tube.dvdplayer != None:
                        tube.dvdplayer.seek(-30)
                        tube.dvdplayer.command('show_text', "Seeking back 30 seconds " + str(datetime.timedelta(seconds=int(tube.dvdplayer._get_property("time-pos")))) + "/" + str(datetime.timedelta(seconds=int(tube.dvdplayer._get_property("duration")))))
                elif command[0] == "dvd-stop" and tube.dvdplayer != None:
                        tube.dvdplayer.quit(0)
                elif command[0] == "dvd-n-chapt" and tube.dvdplayer != None:
                        tube.dvdplayer._set_property("chapter", tube.dvdplayer._get_property('chapter') + 1)
                        tube.dvdplayer.command('show_text', "Next Chapter")
                elif command[0] == "dvd-p-chapt" and tube.dvdplayer != None:
                        tube.dvdplayer._set_property("chapter", tube.dvdplayer._get_property('chapter') - 1)
                        tube.dvdplayer.command('show_text', "Prevoius Chapter")
                elif command[0] == "dvd-vol" and tube.dvdplayer != None:
                        tube.dvdplayer._set_property("volume", int(command[2]))
                        tube.dvdplayer.command('show_text', "Volume is now at " + str(int(command[2])) + "%")
                elif command[0] == "dvd-track-down" and tube.dvdplayer != None:
                        tube.dvdplayer.cycle("audio", "down")
                        tube.dvdplayer.command('show_text', "Previous Audio Track")
                elif command[0] == "dvd-track-up" and tube.dvdplayer != None:
                        tube.dvdplayer.cycle("audio", "up")
                        tube.dvdplayer.command('show_text', "Next Audio Track")
                elif command[0] == "dvd-subtitle" and tube.dvdplayer != None:
                        tube.get_tracks()
                        if tube.subs >= 1:
                            sub += 1
                            tube.dvdplayer.command('show_text', "Subtitle Track: " + str(sub))
                            if sub >= tube.subs:
                                tube.dvdplayer._set_property("sub", 0)
                                sub = 0
                            else:
                                tube.dvdplayer.cycle("sub", "up")
                        else:
                            tube.dvdplayer.command('show_text', "No Subtitles Found")
            elif command[0] == "tu-media" and connected == "":
                logging.info(connected + " is trying to stream a youtube video")
                subprocess.call("tvservice -p &",shell=True)
                if tube.player != None:
                    kill(tube.player)
                    tube.player = None
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
            if tube.player != None:
                kill(tube.player)
                #subprocess.call("tvservice -o &",shell=True)
                tube.player = None
            time.sleep(1)
            connected = ""
    return
    
def kill(player):
    try:
        player.quit()
    except:
        pass
    
loop = threading.Thread(target=timeout)
loop.start()
while True:
    connection()
