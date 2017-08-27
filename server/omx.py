# -*- coding: utf-8 -*-

from omxplayer import OMXPlayer
import subprocess

class Omx():
    def __init__(self):
        self.url = "None"
        self.player = None
       
    def youtube(self):
        proc = subprocess.Popen(['youtube-dl', '-g', '-f', 'mp4', self.url], stdout=subprocess.PIPE)
        url = proc.stdout.read()
        if url.decode("utf-8") == '':
            return False
        self.player = OMXPlayer(url.decode("utf-8", "strict")[:-1])
        return True

    def start_media(self, host):
        address = "http://" + str(host) + ":8090/video"
        self.player = OMXPlayer(address, args=['-o', 'hdmi', '--timeout',  '600', '--lavfdopts', 'probesize:15000', '--threshold', '1'])            
    
    def mirror(self):
        self.player = OMXPlayer("udp://0.0.0.0:8090?listen", args=['-o', 'hdmi', '--lavfdopts', 'probesize:8000', '--timeout', '0', '--threshold', '0'])
    
