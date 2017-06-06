import os
import time
import subprocess
import gi
import re
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

class TrayMenu:
    def __init__(self):           
        self.indicator = appindicator.Indicator.new("mirrorMenu", os.path.abspath('sample_icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.status = "stop"
        self.menu = gtk.Menu()
        
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
        #Create Loop to detect receivers
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
        for ind, i in enumerate(self.receivers):
            if ind != 0:
                self.list_receivers.append(gtk.RadioMenuItem(str(i),group=self.list_receivers[ind-1]))
            else:
                self.list_receivers.append(gtk.RadioMenuItem(self.receivers[0]))
        for i in self.list_receivers:
            self.outputSub.append(i)
            i.connect('toggled', self.set_host, i.get_label())
        self.list_receivers[0].set_active(True)
        #Create Loop to list displays/monitors
        self.receiver = self.receivers[0]
        self.monitors = self.get_displays()
        self.resolution = self.monitors[0][1]
        self.xoffset = self.monitors[0][2]
        self.yoffset = self.monitors[0][3]
        self.displaysSub = gtk.Menu()
        displays = gtk.MenuItem("Select Display to Mirror")
        displays.set_submenu(self.displaysSub)
        self.list_displays = []
        
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
                
    def set_host(self, but, name):
        self.outputSub = gtk.Menu()
        self.receiver = str(but.get_label())
        print("Receiver set to: " + but.get_label())
        
    def start(self, w):
        if w.get_label() == 'Start Mirroring':
            w.set_label('Stop Mirroring')
            self.menu = gtk.Menu()
            time.sleep(1)
            os.system("fuser 8090/tcp && killall ffmpeg")
            try:
                #Try to mute sound on laptop as it will be playing over hdmi
		#Pulse audio needs to be initalised first
                subprocess.call("pulseaudio &", shell=True)
                subprocess.call("pacmd set-sink-port 0 analog-output-speaker &", shell=True)
                time.sleep(1)
                subprocess.call("pacmd set-sink-port 0 analog-output-headphones &", shell=True)
                #subprocess.call("amixer set Capture toggle", shell=True)
            except:
                print("Cannot change pulse audio output to headphones")
            subprocess.call("ffmpeg -f pulse -ac 2 -i default -async 1 -f x11grab -r 30 -s " + str(self.resolution) + " -i :" + str(self.xoffset) + "." + str(self.yoffset) + " -aspect 16:9 -vcodec libx264 -pix_fmt yuv420p -tune zerolatency -preset ultrafast -vf scale=1280:720 -f mpegts tcp://" + self.receiver + ":8090 &", shell=True)
        else:
            try:
                #Switch audio back to laptop speakers
                subprocess.call("pacmd set-sink-port 0 analog-output-speaker &", shell=True)
            except:
                print("Cannot change pulse audio output back to speakers")
            subprocess.call("fuser 8090/tcp & killall ffmpeg &", shell=True)
            w.set_label('Start Mirroring')
            self.menu = gtk.Menu()
            time.sleep(1)
    
    def quit(self, w):
        try:
            #Switch audio back to laptop speakers
            os.system("pacmd set-sink-port 0 analog-output-speaker")
        except:
            print("Failed to change pulse audio output back to speakers")
        subprocess.call("fuser 8090/tcp & killall ffmpeg &", shell=True)
        gtk.main_quit()
    
    def get_displays(self):
        displays = []
        try:
            command = subprocess.check_output("sh " + os.path.dirname(os.path.abspath(__file__)) + "/monitors.sh", shell=True)
            command2 = subprocess.check_output("xrandr --verbose |grep -o -P '(?<=connected ).*(?= \(\d.*)'|grep -o -P '\d\d\d\dx.*'", shell=True)
            data = command.splitlines()
            data2 = command2.splitlines()
            h = len(data)
            for i in range(h):
                l = []
                if "\\" in str(data[i]):
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

def main():
    gtk.main()
    return 0
    
if __name__ == "__main__":
    indicator = TrayMenu()
    main()
