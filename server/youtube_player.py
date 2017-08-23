# -*- coding: utf-8 -*-

from omxplayer import OMXPlayer
import subprocess, socket

class youtube():
    def __init__(self):
        self.url = "None"
        self.player = None
       
    def start(self):
        proc = subprocess.Popen(['youtube-dl', '-g', '-f', 'mp4', self.url], stdout=subprocess.PIPE)
        url = proc.stdout.read()
        self.player = OMXPlayer(url.decode("utf-8", "strict")[:-1])
    

'''sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ""
sock.bind((host,8092))

sock.listen(5)

while True:
    client, address = sock.accept()
    status = client.recv(8024)
    command = status.decode('ascii')
    command = command.split(",")
    print(command)
    #User started casting or reconnected
    if command[0] == "tube-load":
        print(command[2])
        tube = youtube()
        tube.url = command[2]
        tube.start()
        while True:
            if tube.player.is_playing():
                client.send("ready".encode('ascii'))
                break
    if command[0] == "tube-stop":
        tube.player.quit()
    if command[0] == "tube-forward":
        tube.player.seek(3)
    if command[0] == "tube-back":
        tube.player.seek(-3)
    if command[0] == "tube-pause":
        tube.player.play_pause()
    client.close()'''
