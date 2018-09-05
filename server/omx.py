# -*- coding: utf-8 -*-
#Mirrorcast Server Version 0.7.0b

from omxplayer import OMXPlayer
import mpv
import subprocess,time

class Omx():
    def __init__(self):
        self.url = "None"
        self.player = None
        self.dvdplayer = None
        self.subs = 0
        self.audio_tracks = 0
        self.titles = 0
        
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

    def start_dvd(self):
        self.dvdplayer = mpv.MPV()
        self.dvdplayer.fullscreen = True
        self.dvdplayer['vo'] = 'rpi'
        self.dvdplayer['rpi-osd'] = 'yes'
        self.dvdplayer['osd-bar'] = 'yes'
        self.dvdplayer['osd-on-seek'] = 'msg-bar'
        self.dvdplayer['osd-level'] = '1'
        self.dvdplayer['osd-duration'] = '8000'
        self.dvdplayer['loop-file'] = 'no'
        self.dvdplayer['end'] = '-5'
        self.dvdplayer['osd-playing-msg'] = 'Now Playing Your DVD'
        self.dvdplayer['dvd-device'] = '/dev/nbd0'
        #self.dvdplayer.play('/tmp/DVD/')
        self.dvdplayer.play('dvd://')
        self.audio_tracks = 0
        self.subs = 0
        self.titles = 0
        #self.dvdplayer.play("/home/pi/mirrorcast/server/Big Buck Bunny-YE7VzlLtp-4.mp4")
        return True
        
    def get_tracks(self):
        #Get the amount of audio tracks and subtitles avaible on DVD(May cause issues when more than 1 movie on DVD)
        self.subs = 0
        self.audio_tracks = 0
        print(self.dvdplayer._get_property('disc-titles', 'length'))
        for item in self.dvdplayer._get_property("track-list"):
            if item['type'] == 'sub':
                self.subs += 1
            if item['type'] == 'audio':
                self.audio_tracks += 1
    
    def mirror(self):
        self.player = OMXPlayer("udp://0.0.0.0:8090?listen", args=['-o', 'hdmi', '--lavfdopts', 'probesize:8000', '--timeout', '0', '--threshold', '0'])
    
