# -*- coding: utf-8 -*-
import logging, os, csv, logging.handlers

mirror_logger = logging.getLogger()
mirror_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = '/dev/log')
formatter = logging.Formatter(' mirrorcast - %(name)s -  %(levelname)s - %(message)s')
handler.setFormatter(formatter)
mirror_logger.addHandler(handler)

#logging.basicConfig(filename='/opt/mirrorcast/mirrorcast.log',level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

class Hosts():
    def __init__(self):
        
        self.receivers = []
        self.receiver = "None"
        #load list of receivers from file
        try:
            with open(os.path.dirname(os.path.abspath(__file__)) + "/receivers") as csvfile:
                file = csv.DictReader(csvfile)
                for line in file:
                    self.receivers.append(line)
        except:
            mirror_logger.error("Failed to load host names")
            exit(0)
        csvfile.close()
        self.aspect = self.receivers[0]['aspect']
    
    #set receiver to the one picked by the user     
    def set_receiver(self, but, name):    
        self.receiver = str(but.get_label())
        for i in self.receivers:
            if i['host'] == self.receiver and but.get_active():
                self.aspect = i['aspect']
                mirror_logger.info("Receiver set to: " + i['host'] + " Receivers aspect: " + self.aspect)
                return
        if but.get_active():
            self.receiver = "None"
            self.aspect = "16:9"
            mirror_logger.info("Receiver set to: " + self.receiver)
