# -*- coding: utf-8 -*-
import logging, subprocess, time, gi, logging.handlers
gi.require_version('Notify', '0.7')
from gi.repository import Notify as notify

mirror_logger = logging.getLogger()
mirror_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter(' mirrorcast - %(name)s -  %(levelname)s - %(message)s')
handler.setFormatter(formatter)
mirror_logger.addHandler(handler)
#mirror_logger.basicConfig(filename='/opt/mirrorcast/mirrorcast.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

class Audio():
    def __init__(self):
        try:
            subprocess.call("pulseaudio &", shell=True)
            self.audioDev = subprocess.check_output("pacmd list-sinks | grep -o -P '(?<=name: \<).*.analog-stereo(?=>)'", shell=True).decode("utf-8").rstrip()
        except:
            mirror_logger.warning("Failed to detect audio device, defaulting to sink port 0")
            self.audioDev = "0"
            
    def audio(self, toggle):
        if toggle == True:
            try:
                #Mute microphone
                subprocess.call("amixer set Capture nocap", shell=True)
                time.sleep(1)
                #Change laptop audio to headphones which are hopefully not plugged in.
                #by doing so, the sound will not be echoing from playing on 2 devices(the receiver will be delayed)
                subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-headphones &", shell=True)
                #subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-lineout &", shell=True)
                #subprocess.call("amixer set Capture toggle", shell=True)
            except:
                mirror_logger.warning("Cannot change audio output to headphones")
            return
        else:
            try:
                #subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-speaker &", shell=True)
                subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-speaker &", shell=True)
                time.sleep(1)
                subprocess.call("amixer set Capture cap", shell=True)
            except:
                mirror_logger.warning("Failed to revert audio settings")
                
    def monitor_audio(self):
        try:
            #Attempt to automate correct audio settings so that audio can be played via receiving device
            time.sleep(2)#First give ffmpeg time to start
            #Get the source id for ffmpeg
            audiostreams = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=Source Output #).*(?=.*)'", shell=True)
            audiostreams = audiostreams.splitlines()
            audiostream_names = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=application.name = \").*(?=\")'", shell=True)
            audiostream_names = audiostream_names.splitlines()
            #Search for ffmpeg audio stream and change its settings so we can make it capture desktop audio
            for i in range(len(audiostreams)):
                if "Lav" in str(audiostream_names[i]):
                    stream = int(audiostreams[i])
                    break
            audiosource = subprocess.check_output("pactl list short sources | grep -o -P '(?<=\d\t).*analog-stereo(?=.monitor)'", shell=True)
            audiosource = audiosource.splitlines()
            subprocess.call("pactl move-source-output " + str(stream) + " " + str(audiosource[0])[1:].strip('\'') + ".monitor", shell=True)
        except:
            mirror_logger.warning("Something went wrong when attempting to change ffmpeg audio to monitor desktop audio")
            notify.init("mirrorMenu")
            notify.Notification.new("Audio Error", "There was an issue trying to change your audio settings, you may not be able to send audio to receiver.", None).show()
