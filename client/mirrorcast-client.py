'''Rough applet for Debian/Ubuntu Systems
Mirrorcast Version 0.2.5b'''
import socket, csv, re, gi, subprocess, time, os
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
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
            with open(os.path.dirname(os.path.abspath(__file__)) + "/receivers") as csvfile:
                file = csv.DictReader(csvfile)
                for line in file:
                    self.receivers.append(line)
        except:
            print("failed to load host names")
            exit(0)
        csvfile.close()
        self.list_receivers = []
        #sorting
        self.sortedMenu = []
        sortSub = []
        subitems = []
        sortInd = 0
        sortInd2 = 0
        #Add receivers to menu
        self.list_receivers.append(gtk.RadioMenuItem('None'))
        for ind, i in enumerate(self.receivers):
            #allow user to sort their receivers into sublists
            if i['aspect'] == "sub":
                self.sortedMenu.append(gtk.Menu())
                sortSub.append(gtk.MenuItem(i['host']))
                sortSub[sortInd].set_submenu(self.sortedMenu[sortInd])
                self.outputSub.append(sortSub[sortInd])
                sortInd = sortInd + 1
            elif sortInd > 0:
                try:
                    subitems.append(gtk.RadioMenuItem(str(i['host']),group=self.subitems[sortInd2-1]))
                except:
                    subitems.append(gtk.RadioMenuItem(str(i['host']),group=self.list_receivers[0]))
                subitems[sortInd2].connect('toggled', self.set_host, subitems[sortInd2].get_label())
                self.sortedMenu[sortInd-1].append(subitems[sortInd2])
                sortInd2 = sortInd2 + 1
            else:    
                self.list_receivers.append(gtk.RadioMenuItem(str(i['host']),group=self.list_receivers[ind-1]))         
        for i in self.list_receivers:
            self.outputSub.append(i)
            i.connect('toggled', self.set_host, i.get_label())
        self.list_receivers[0].set_active(True)
        self.receiver = "None"
        self.aspect = self.receivers[0]['aspect']
        self.monitors = self.get_displays()
        self.resolution = self.monitors[0][1]
        self.xoffset = self.monitors[0][2]
        self.yoffset = self.monitors[0][3]
        self.displaysSub = gtk.Menu()
        displays = gtk.MenuItem("Select Display to Mirror")
        displays.set_submenu(self.displaysSub)
        self.list_displays = []
        #Add displays/monitors to menu
        for ind, i in enumerate(self.monitors):
            if ind != 0:
                self.list_displays.append(gtk.RadioMenuItem(str(i[0]),group=self.list_displays[ind-1]))
            else:
                self.list_displays.append(gtk.RadioMenuItem(self.monitors[0][0]))  
        for i in self.list_displays:
            self.displaysSub.append(i)
            i.connect('toggled', self.set_display, i.get_label())
        self.list_displays[0].set_active(True)
        self.type = self.monitors[0][4]
        self.menu.append(output)
        self.menu.append(displays)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        try:
            subprocess.call("pulseaudio &", shell=True)
            self.audioDev = subprocess.check_output("pacmd list-sinks | grep -o -P '(?<=name: \<).*.analog-stereo(?=>)'", shell=True).decode("utf-8").rstrip()
        except:
            print("Failed to detect audio device, defaulting to sink port 0")
            self.audioDev = "0"

    def set_display(self, but, nam):    
        for i in self.monitors:
            if but.get_label() == i[0] and but.get_active():
                self.resolution = i[1]
                self.xoffset = i[2]
                self.yoffset = i[3]
                self.type = i[4]
                print("Selected Monitor: " + i[0] + " res: " + i[1] + " offset: " + i[2] + ":" + i[3])

    #set receiver to the one picked by the user     
    def set_host(self, but, name):    
        self.receiver = str(but.get_label())
        for i in self.receivers:
            if i['host'] == self.receiver and but.get_active():
                self.aspect = i['aspect']
                print("Receiver set to: " + i['host'])
                return
        if but.get_active():
            self.receiver = "None"
            print("Receiver set to: " + self.receiver)
        
        
    def start(self, w):
        print("Detected Audio Device: " + str(self.audioDev))
        if w.get_label() == 'Start Mirroring':
            if self.receiver == "None":
                notify.init("mirrorMenu")
                notify.Notification.new("Error", "You did not select a receiver", None).show()
                return
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.receiver, 8091))
                sock.send("on".encode('ascii'))
                sock.close()
            except:
                print("Problem with sockets")
            res = self.resolution
            #woffset = 0
            #If receiver is set to display 4:3 and the client is 16:9 then change screen resoltion to 1024x768
            if (self.aspect == "wide" or self.aspect == "16:9" or self.aspect == "16:10") and self.get_ratio(self.resolution) == "16:9":
                self.aspect = "16:9"     
            else:
                self.aspect = "4:3"
                if self.get_ratio(self.resolution) != "4:3":
                    res = "1024x768"
                    #w1 = res.split('x')
                    #w2 = self.resolution.split('x')
                    #woffset = int(w2[0]) - int(w1[0])
                    subprocess.call("xrandr --output " + self.type + " --mode 1024x768", shell=True)
            notify.init("mirrorMenu")
            notify.Notification.new("Connecting", "Attempting to establish connection to " + self.receiver, None).show()
            self.menu = gtk.Menu()
            #In case ffmpeg is still running taking up the port needed
            #I know, doing both commands might be overkill
            os.system("fuser 8090/tcp && killall ffmpeg")
            self.audio(True)
            #Start encoding and sending the stream to the receiver
            time.sleep(1) #After checking port is open, it needs time to restart
            display = os.environ['DISPLAY']#get display of current user
            subprocess.call("ffmpeg -loglevel warning -f pulse -ac 2 -i default -async 1 -f x11grab -r 25 -s " + str(res) + " -i " + str(display) + "+" + str(int(self.xoffset)) + "," + str(self.yoffset) + " -aspect " + self.aspect + " -vcodec libx264 -pix_fmt yuv420p -tune zerolatency -preset ultrafast -vf scale=" + str(res).replace('x', ':') + " -f mpegts tcp://" + self.receiver + ":8090 &", shell=True)
            try:
                #Attempt to automate correct audio settings so that audio can be played via receiving device
                time.sleep(3)#give ffmpeg time to start
                audiostreams = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=Source Output #).*(?=.*)'", shell=True)
                audiostreams = audiostreams.splitlines()
                audiostream_names = subprocess.check_output("pactl list source-outputs |grep -o -P '(?<=application.name = \").*(?=\")'", shell=True)
                audiostream_names = audiostream_names.splitlines()
                #Search for ffmpeg audio stream
                for i in range(len(audiostreams)):
                    if "Lav" in str(audiostream_names[i]):
                        stream = int(audiostreams[i])
                        break
                audiosource = subprocess.check_output("pactl list short sources | grep -o -P '(?<=\d\t).*analog-stereo(?=.monitor)'", shell=True)
                audiosource = audiosource.splitlines()
                subprocess.call("pactl move-source-output " + str(stream) + " " + str(audiosource[0])[1:].strip('\'') + ".monitor", shell=True)
            except:
                print("Something went wrong when attempting to change ffmpeg audio to monitor desktop audio")
            #Check if connection was is established
            try:
                output = subprocess.check_output("netstat -napt 2>/dev/null|grep '8090 * ESTABLISHED'", shell=True)
            except:
                #IIF connection fails, revert changes.
                notify.Notification.new("Connection Failed", "Failed to establish connection to " + self.receiver + ". Is some one already connected? Please try again and if the problem persists then please contact your system administrator", None).show()
                self.audio(False)
                w.set_label('Start Mirroring')
                if self.aspect == "4:3" and self.get_ratio(self.resolution) != "4:3":
                    subprocess.call("xrandr --output " + self.type + " --mode " + self.resolution + " &", shell=True)
                    #self.aspect = self.get_ratio(self.resolution)
                self.menu = gtk.Menu()
                return
            notify.Notification.new("Connection Established", "Connection to " + self.receiver + " established.", None).show()
            w.set_label('Stop Mirroring')
            self.menu = gtk.Menu()
        else:
            #Switch audio back to laptop speakers and unmute microphone
            self.audio(False)
            #change screen resolution back to default
            if self.aspect == "4:3" and self.get_ratio(self.resolution) != "4:3":
                subprocess.call("xrandr --output " + self.type + " --mode " + self.resolution + " &", shell=True)
            subprocess.call("fuser 8090/tcp & killall ffmpeg", shell=True)
            w.set_label('Start Mirroring')
            self.menu = gtk.Menu()
            time.sleep(1)
    
    def quit(self, w):
        self.audio(False)
        if self.aspect == "4:3" and self.get_ratio(self.resolution) != "4:3":
            #change screen resolution back to original
            subprocess.call("xrandr --output " + self.type + " --mode " + self.resolution + " &", shell=True)
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
            ident = subprocess.check_output("xrandr -q|grep -o -P '.*(?= co.*\dx\d.*)'", shell=True)
            data = command.splitlines()
            data2 = command2.splitlines()
            data3 = ident.splitlines()
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
                l.append(str(data3[i]).strip(("b\'")))
                print(l)
                displays.append(l)
            print(displays)        
        except:
            print("something went wrong getting monitor")
        return displays
    
    def divisor(self, x, y):
        #To calculate aspect ratio
        if int(y) == 0:
            return int(x)
        return self.divisor(y, int(x) % int(y))
    
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
                print("Cannot change audio output to headphones")
            return
        else:
            try:
                #subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-speaker &", shell=True)
                subprocess.call("pacmd set-sink-port " + str(self.audioDev) + " analog-output-speaker &", shell=True)
                time.sleep(1)
                subprocess.call("amixer set Capture cap", shell=True)
            except:
                print("Failed to revert audio settings")
            
            
    
    def get_ratio(self, res):
        res = res.split('x')
        x = res[0]
        y = res[1]
        ratios = ['5:4', '4:3', '3:2', '8:5', '5:3', '16:9', '17:9', '16:10']
        gcd = self.divisor(x, y)
        ratio = str(int(x) / gcd) + ':' + str(int(y) / gcd)
        normalised = float(x) / float(y)
        if ratio not in ratios:
            error = 999
            index = -1
            for i in range(len(ratios)):
                ratio1 = ratios[i].split(':')
                w = ratio1[0]
                h = ratio1[1]
                known = int(w) / int(h)
                dist = abs(normalised - known)
                if dist < error:
                    index = i
                    error = dist
            ratio = ratios[index]
        return ratio
    
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
    
