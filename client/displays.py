# -*- coding: utf-8 -*-
import os, subprocess, logging, re, logging.handlers

mirror_logger = logging.getLogger()
mirror_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter(' mirrorcast - %(name)s -  %(levelname)s - %(message)s')
handler.setFormatter(formatter)
mirror_logger.addHandler(handler)

#mirror_logger.basicConfig(filename='/opt/mirrorcast/mirrorcast.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

class Displays():
    def __init__(self):
        self.monitors = self.get_displays()
        self.resolution = self.monitors[0][1]
        self.xoffset = self.monitors[0][2]
        self.yoffset = self.monitors[0][3]
        self.type = self.monitors[0][4]
    
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
                displays.append(l)
            mirror_logger.info(displays)        
        except:
            mirror_logger.warning("Something went wrong getting monitor infomation, defaulting to generic names")
        return displays
        
        #If the user has more than 1 display plugged into their computer, they can select which one they want to cast
    def set_display(self, but, nam):    
        for i in self.monitors:
            if but.get_label() == i[0] and but.get_active():
                self.resolution = i[1]
                self.xoffset = i[2]
                self.yoffset = i[3]
                self.type = i[4]
                mirror_logger.info("Selected Monitor: " + i[0] + " res: " + i[1] + " offset: " + i[2] + ":" + i[3])
                
        #Changes display reslution back if it was altered to match receiver
    def display(self, val, aspect):
        if val == False:
            if aspect == "4:3" and self.get_ratio(self.resolution) != "4:3":
                subprocess.call("xrandr --output " + self.type + " --mode " + self.resolution + " &", shell=True)

    def divisor(self, x, y):
        #To calculate aspect ratio
        if int(y) == 0:
            return int(x)
        return self.divisor(y, int(x) % int(y))
              
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
        
    
