'''Rough applet for Debian/Ubuntu Systems
Mirrorcast Version 0.3b'''
import socket, gi, subprocess, time, os, threading, logging, dbus
from hosts import Hosts as hosts
from displays import Displays
from audio import Audio
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GObject as gobject
from dbus.mainloop.glib import DBusGMainLoop

logging.basicConfig(filename='/opt/mirrorcast/mirrorcast.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

class TrayMenu:
    def __init__(self):
        logging.info("Started Mirrorcast")
        self.indicator = appindicator.Indicator.new("mirrorMenu", os.path.abspath('sample_icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.state = "stopped"
        self.menu = gtk.Menu()
        self.sleep = dbus_listen()
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

        '''Recievers/Hosts Menu'''
        self.hosts = hosts()
        #Varaibles for sorting receivers into sub-menus
        self.list_receivers = []
        self.sortedMenu = []
        sortSub = []
        subitems = []
        sortInd = 0
        sortInd2 = 0
        #Add receivers to menu
        self.list_receivers.append(gtk.RadioMenuItem('None'))
        for ind, i in enumerate(self.hosts.receivers):
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
                subitems[sortInd2].connect('toggled', self.hosts.set_receiver, subitems[sortInd2].get_label())
                self.sortedMenu[sortInd-1].append(subitems[sortInd2])
                sortInd2 = sortInd2 + 1
            else:    
                self.list_receivers.append(gtk.RadioMenuItem(str(i['host']),group=self.list_receivers[ind-1]))         
        for i in self.list_receivers:
            self.outputSub.append(i)
            i.connect('toggled', self.hosts.set_receiver, i.get_label())
        self.list_receivers[0].set_active(True)
        
        self.Display = Displays()
        self.displaysSub = gtk.Menu()
        displays = gtk.MenuItem("Select Display to Mirror")
        displays.set_submenu(self.displaysSub)
        self.list_displays = []
        #Add displays/monitors to menu
        for ind, i in enumerate(self.Display.monitors):
            if ind != 0:
                self.list_displays.append(gtk.RadioMenuItem(str(i[0]),group=self.list_displays[ind-1]))
            else:
                self.list_displays.append(gtk.RadioMenuItem(self.Display.monitors[0][0]))  
        for i in self.list_displays:
            self.displaysSub.append(i)
            i.connect('toggled', self.Display.set_display, i.get_label())
        self.list_displays[0].set_active(True)
        self.menu.append(output)
        self.menu.append(displays)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
        self.sound = Audio()
        
    #the following function is run when the user clicks "Start/Stop Mirroring"
    def start(self, w):
        notify.init("mirrorMenu")
        logging.info("Detected Audio Device: " + str(self.sound.audioDev))
        if w.get_label() == 'Start Mirroring':
            #If the user did not select a receiver
            if self.hosts.receiver == "None":
                notify.init("mirrorMenu")
                notify.Notification.new("Error", "You did not select a receiver", None).show()
                return
            #If we cannot connect to the receiver
            if self.connect() == False:
                notify.init("mirrorMenu")
                notify.Notification.new("Connection Error", "Could not connect to" + self.hosts.receiver + ". please try again and if problem persists then please contact your system administrator.", None).show()
                logging.warning("Failed to connect to " + self.hosts.receiver)
                return
            logging.info("User connected to " + self.hosts.receiver)
            notify.Notification.new("Connecting to Receiver", "Attempting to establish connection to " + self.hosts.receiver, None).show()
            self.menu = gtk.Menu()
            self.start_casting()
            w.set_label('Stop Mirroring')
            self.menu = gtk.Menu()
            #Create and start loop that checks if receiver can still be reached
            connection=threading.Thread(target=self.alive,args=[w])
            connection.start()
        else:
            self.sound.audio(False)
            self.Display.display(False, self.hosts.aspect)
            subprocess.call("killall ffmpeg", shell=True)
            w.set_label('Start Mirroring')
            self.state = "stopped"
            self.menu = gtk.Menu()
            return
    
    def start_casting(self):
            res = self.Display.resolution
            self.sleep.sleep = False
            #woffset = 0
            #If receiver is set to display 4:3 and the client is 16:9 then change screen resoltion to 1024x768
            if (self.hosts.aspect == "wide" or self.hosts.aspect == "16:9" or self.hosts.aspect == "16:10") and self.Display.get_ratio(res) == "16:9":
                self.hosts.aspect = "16:9"     
            else:
                self.hosts.aspect = "4:3"
                if self.Display.get_ratio(self.Display.resolution) != "4:3":
                    res = "1024x768"
                    try:
                        subprocess.call("xrandr --output " + self.Display.type + " --mode 1024x768", shell=True)
                    except:
                        logging.warning("Could now change screen resolution to 4:3")
                        notify.Notification.new("Resolution Error", "Failed to change screen resolution to match receiver.", None).show()
                        return
            subprocess.call("killall ffmpeg", shell=True)
            self.sound.audio(True)
            #Start encoding and sending the stream to the receiver
            self.state = "casting"
            time.sleep(1)
            display = os.environ['DISPLAY']#get display of current user
            subprocess.call("ffmpeg -loglevel warning -f pulse -ac 2 -i default -async 1 -f x11grab -r 25 -s " + str(res) + " -i " + str(display) + "+" + str(int(self.Display.xoffset)) + "," + str(self.Display.yoffset) + " -aspect " + self.hosts.aspect + " -vcodec libx264 -pix_fmt yuv420p -tune zerolatency -preset ultrafast -vf scale=" + str(res).replace('x', ':') + " -f mpegts udp://" + self.hosts.receiver + ":8090 &", shell=True)
            self.sound.monitor_audio()
            notify.Notification.new("Connection Established", "Connection to " + self.hosts.receiver + " established.", None).show()
            
    def alive(self,  w):
        timestamp = time.localtime()
        timeout = 10
        retries = 40
        i=0
        command = "active," + socket.gethostname()
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.hosts.receiver, 8091))
                #If the user's computer is going to sleep
                if self.sleep.sleep == True:
                    w.set_label('Start Mirroring')
                    self.menu = gtk.Menu()
                if self.state == "stopped":
                    command = "stop," + socket.gethostname()
                    sock.send(command.encode('ascii'))              
                    sock.close()
                    logging.info("User stopped casting")
                    return
                sock.send(command.encode('ascii'))
                status = sock.recv(1024)
                if status.decode('ascii') == "ok":
                    timestamp = time.localtime()
                time.sleep(1)
                sock.close()            
            except:
                time.sleep(1)
                if (time.mktime(time.localtime()) - time.mktime(timestamp)) >= timeout and self.state != "stopped":
                    i = i + 1
                    if i == 1:
                        logging.warning("Attempting to reconnect to " + self.hosts.receiver)
                        subprocess.call("killall ffmpeg", shell=True)
                        notify.Notification.new("Reconnecting", "Connection to " + self.hosts.receiver + " has been lost. Attempting to reconnect.", None).show()
                    if self.connect() == True:
                        logging.info("Reconnected to " + self.hosts.receiver)
                        self.start_casting()
                        i = 0
                    if i == retries:
                        self.state = "stopped"
                        w.set_label('Start Mirroring')
                        self.menu = gtk.Menu()
                        notify.init("mirrorMenu")
                        notify.Notification.new("Connection Lost", "Connection to " + self.hosts.receiver + " timed out.", None).show()
                        logging.warning("Connection Lost: Connection to " + self.hosts.receiver + " timed out.")
                        return
                
    def quit(self, w):
        self.sound.audio(False)
        self.state = "stopped"
        self.Display.display(False, self.hosts.aspect)
        #kill ffmpeg incase user forgot to click "stop"
        subprocess.call("killall ffmpeg", shell=True)
        time.sleep(1)
        gtk.main_quit()
                    
    def connect(self):
        command = "play," + socket.gethostname()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.hosts.receiver, 8091))
            sock.send(command.encode('ascii'))
            while True:
                status = sock.recv(1024)
                #if server returns busy then some one else is already using this receiver
                if status.decode('ascii') == "busy":
                    notify.init("mirrorMenu")
                    logging.info("User attempted to connect to " + self.hosts.receiver + " but receiver was busy")
                    notify.Notification.new("Error", "Sorry some one else is already  connected to this receiver, please try again later.", None).show()
                    sock.close()
                    return False
                #If client succeeds  in connecting to receiver
                elif status.decode('ascii') == "ready":
                    logging.info("Server is ready")
                    break
                time.sleep(1)
            sock.close()
        except:
            return False
        self.state = "casting"
        return True

class dbus_listen():
    
    def handle_sleep(self, *args):
        logging.info("User computer is going to sleep, killing ffmpeg")
        subprocess.call("killall ffmpeg", shell=True)
        self.sleep = True
        self.state = "stopped"
    
    def __init__(self):
        self.sleep = False
        DBusGMainLoop(set_as_default=True)     # integrate into gobject main loop
        bus = dbus.SystemBus()                 # connect to system wide dbus
        bus.add_signal_receiver(               # define the signal to listen to
        self.handle_sleep,                  # callback function
        'PrepareForSleep',                  # signal name
        'org.freedesktop.login1.Manager',   # interface
        'org.freedesktop.login1'            # bus name
        )
        
def main():
    gtk.main()
    return 0
    
if __name__ == "__main__":
    indicator = TrayMenu()
    main()
    
