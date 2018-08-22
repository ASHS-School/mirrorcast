# -*- coding: utf-8 -*-

from omxplayer import OMXPlayer
import subprocess,time

class Omx():
    def __init__(self):
        self.url = "None"
        self.player = None
       
    def youtube(self):
        proc = subprocess.Popen(['youtube-dl', '-g', '-f', 'mp4', self.url], stdout=subprocess.PIPE)
        url = proc.stdout.read()
        if url.decode("utf-8") == '':
            return False
        self.player = OMXPlayer(url.decode("utf-8", "strict")[:-1], args=['-o', 'hdmi'])
        return True

    def start_media(self, host, file):
        #file = "The Pirates of Silicon Valley.avi"
        address = "http://" + str(host) + ":8090/" + file
        #address = address.replace(" ", "%20")
        self.player = OMXPlayer(address.replace(" ", "%20"), args=['-o', 'hdmi'])
        #self.player = OMXPlayer("/home/pi/Videos/Song of the Kauri.mp4", args=['-o', 'hdmi'])
        i = 0
        while not self.player.is_playing():
            time.sleep(2)
            i+=1
            if i >= 60:
                break
            return False
        return True
    
    def mirror(self):
        self.player = OMXPlayer("udp://0.0.0.0:8090?listen", args=['-o', 'hdmi', '--lavfdopts', 'probesize:8000', '--timeout', '0', '--threshold', '0'])
    
