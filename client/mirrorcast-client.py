'''Rough applet for Debian/Ubuntu Systems
Mirrorcast Version 0.2b'''
import os
import time
import subprocess
import gi
import re
import socket
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

class TrayMenu:
    def __init__(self):           
        self.indicator = appindicator.Indicator.new("mirrorMenu", os.path.abspath('sample_icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.status = "stop"
        self.menu = gtk.Menu()
        
        #Set up menu
        item_start= gtk.MenuItem('Start Mirroring') 
        item_start.connect('activate', self.start)
        self.menu.append(item_start)
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        self.menu.append(item_quit)
        sep = gtk.SeparatorMenuItem()
        self.menu.append(sep)
        self.outputSub = gtk.Menu()
        output = gtk.MenuItem("Cast To")
        output.set_submenu(self.outputSub)
        #load list of receivers from file
        self.receivers = []
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + "/receivers") as file:
                self.receivers = file.read().splitlines()
        except:
            print("failed to load host names")
            exit(0)
        file.close()
        print("vola" + str(self.receivers))
        self.list_receivers = []
        #Add receivers to menu
        for ind, i in enumerate(self.receivers):
            if ind != 0:
                self.list_receivers.append(gtk.RadioMenuItem(str(i),group=self.list_receivers[ind-1]))
            else:
                self.list_receivers.append(gtk.RadioMenuItem(self.receivers[0]))
        for i in self.list_receivers:
            self.outputSub.append(i)
            i.connect('toggled', self.set_host, i.get_label())
        self.list_receivers[0].set_active(True)
        self.receiver = self.receivers[0]
        self.monitors = self.get_displays()
        self.resolution = self.monitors[0][1]
        self.xoffset = self.monitors[0][2]
        self.yoffset = self.monitors[0][3]
        self.displaysSub = gtk.Menu()
        displays = gtk.MenuItem("Select Display to Mirror")
        displays.set_submenu(self.displaysSub)
        self.list_displays = []
        #Create Loop to list displays/monitors in menu
        for ind, i in enumerate(self.monitors):
            if ind != 0:
                self.list_displays.append(gtk.RadioMenuItem(str(i[0]),group=self.list_displays[ind-1]))
            else:
                self.list_displays.append(gtk.RadioMenuItem(self.monitors[0][0]))  
        for i in self.list_displays:
            self.displaysSub.append(i)
            i.connect('toggled', self.set_display, i.get_label())
        self.list_displays[0].set_active(True)
        self.menu.append(output)
        self.menu.append(displays)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def set_display(self, but, nam):    
        self.displaysSub = gtk.Menu()
        for i in self.monitors:
            if but.get_label() == i[0] and but.get_active():
                self.resolution = i[1]
                self.xoffset = i[2]
                self.yoffset = i[3]
                print("Selected Monitor: " + i[0] + " res: " + i[1] + " offset: " + i[2] + ":" + i[3])

    #set receiver to the one picked by the user     
    def set_host(self, but, name):
        self.outputSub = gtk.Menu()
        self.receiver = str(but.get_label())
        print("Receiver set to: " + but.get_label())
        
    def start(self, w):
 
        if w.get_label() == 'Start Mirroring':
            notify.init("mirrorMenu")
            notify.Notification.new("Connecting", "Attempting to establish connection to " + self.receiver, None).show()
            w.set_label('Connecting...')
            self.menu = gtk.Menu()
            #In case ffmpeg is still running taking up the port needed
            #I know, doing both commands might be overkill
            os.system("fuser 8090/tcp && killall ffmpeg")
            try:
                #Mute microphone
                subprocess.call("pulseaudio &", shell=True)
                subprocess.call("amixer set Capture nocap &", shell=True)
                subprocess.call("pacmd set-sink-port 0 analog-output-speaker &", shell=True)
                time.sleep(1)
                #Change laptop audio to headphones which are hopefully not plugged in.
                #by doing so, the sound will not be echoing from playing on 2 devices(the receiver will be delayed)
                subprocess.call("pacmd set-sink-port 0 analog-output-headphones &", shell=True)
                #subprocess.call("amixer set Capture toggle", shell=True)
            except:
                print("Cannot change pulse audio output to headphones")
            #Start encoding and sending the stream to the receiver
            time.sleep(1) #After checking port is open, it needs time to restart
            subprocess.call("ffmpeg -f pulse -ac 2 -i default -async 1 -f x11grab -r 25 -s " + str(self.resolution) + " -i :0.0+" + str(self.xoffset) + "," + str(self.yoffset) + " -aspect 16:9 -vcodec libx264 -pix_fmt yuv420p -tune zerolatency -preset ultrafast -vf scale=" + str(self.resolution).replace('x', ':') + " -f mpegts tcp://" + self.receiver + ":8090 &", shell=True)
            try:
                #Attempt to automate correct audio settings so that it can be played on receiving device
                time.sleep(3)#give ffmpeg time to start
                audiostreams = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=Source Output #).*(?=.*)'", shell=True)
                audiostreams = audiostreams.splitlines()
                audiostream_names = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=application.name = \").*(?=\")'", shell=True)
                audiostream_names = audiostream_names.splitlines()
                for i in range(len(audiostreams)):
                    if "Lav" in str(audiostream_names[i]):
                        stream = int(audiostreams[i])
                        break
                audiosource = subprocess.check_output("pactl list short sources | grep -o -P '(?<=\d\t).*analog-stereo(?=.monitor)'", shell=True)
                audiosource = audiosource.splitlines()
                subprocess.call("pactl move-source-output " + str(stream) + " " + str(audiosource[0])[1:].strip('\'') + ".monitor", shell=True)
            except:
                print("Failed changing pulse audio settings")
            #Check if connection was is established
            try:
                output = subprocess.check_output("netstat -napt 2>/dev/null|grep '8090 * ESTABLISHED'", shell=True)
            except:
                notify.Notification.new("Connection Failed", "Failed to establish connection to " + self.receiver + ". Is some one already connected? Please try again and if the problem persists then please contact your system administrator", None).show()
                subprocess.call("pacmd set-sink-port 0 analog-output-speaker &", shell=True)
                subprocess.call("amixer set Capture cap &", shell=True)
                w.set_label('Start Mirroring')
                self.menu = gtk.Menu()
                return
            notify.Notification.new("Connection Established", "Connection to " + self.receiver + " established.", None).show()
            w.set_label('Stop Mirroring')
            self.menu = gtk.Menu()
        else:
            try:
                #Switch audio back to laptop speakers and unmute microphone
                subprocess.call("pacmd set-sink-port 0 analog-output-speaker &", shell=True)
                subprocess.call("amixer set Capture cap &", shell=True)
            except:
                print("Cannot change pulse audio output back to speakers")
            subprocess.call("fuser 8090/tcp & killall ffmpeg", shell=True)
            w.set_label('Start Mirroring')
            self.menu = gtk.Menu()
            time.sleep(1)
    
    def quit(self, w):
        try:
            #Switch audio back to laptop speakers and unmute microphone
            os.system("pacmd set-sink-port 0 analog-output-speaker")
            subprocess.call("amixer set Capture nocap &", shell=True)
        except:
            print("Failed to change pulse audio output back to speakers")
        #kill ffmpeg incase user forgot to click "stop"
        subprocess.call("fuser 8090/tcp & killall ffmpeg", shell=True)
        gtk.main_quit()
        
    
    def get_displays(self):
        displays = []
        try:
            #Attempt to get names of displays
            command = subprocess.check_output("sh " + os.path.dirname(os.path.abspath(__file__)) + "/monitors.sh", shell=True)
            #Get resolutions
            command2 = subprocess.check_output("xrandr --verbose |grep -o -P '(?<=connected ).*(?= \(\d.*)'|grep -o -P '\d\d.*x.*'", shell=True)
            data = command.splitlines()
            data2 = command2.splitlines()
            h = len(data)
            for i in range(h):
                l = []
                if "\\" in str(data[i]):
                    #If there was a failure to get display names, give displays generic names
                    l.append("Display " + str(i+1))
                else:
                    l.append(str(data[i])[2:].strip('\''))
                setting = re.search(r'b\'(.*)\+(.*)\+(.*)', str(data2[i]), re.M)
                l.append(setting.group(1))
                l.append(setting.group(2))
                l.append(setting.group(3).strip('\''))
                displays.append(l)
            print(displays)        
        except:
            print("cannot get width and height")
        return displays
    
    def divisor(self, x, y):
        #To calculate aspect ratio
        if y == 0:
            return x
        return divisor(y, x % y)
    
    def ready(self, host, port):
        check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            check.connect((host, int(port)))
            check.shutdown(1)
            check.close()
            time.sleep(1)
            return False
        except:
            return True

def main():
    gtk.main()
    return 0
    
if __name__ == "__main__":
    indicator = TrayMenu()
    main()
    
