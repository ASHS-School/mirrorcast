# -*- coding: utf-8 -*-

from tkinter import *
import socket

class Media(object):
    def __init__(self,master):
        self.receiver="None"
        top=self.top=master
        topframe = Frame(top)
        topframe.pack()
        self.l=Label(topframe,text="These are controls for the Receiving Device")
        self.l.pack()
        self.l3=Label(topframe,text="You can change the volume and switch between audio tracks")
        self.l3.pack()
        self.l2=Label(topframe,text="Note: It may take up to 15 seconds to start your media on the receiver")
        self.l2.pack()
        controls = Frame(top)
        controls.pack(side=BOTTOM)
        self.audiobackb=Button(controls,text='Audio Track Back',command=self.audioback)
        self.audioforwb=Button(controls,text='Audio Track Up',command=self.audioforw)
        self.volupb=Button(controls,text='Vol Up',command=self.volup)
        self.voldownb=Button(controls,text='Vol Down',command=self.voldown)
        self.audioforwb.pack(side=LEFT)
        self.audiobackb.pack(side=LEFT)
        self.volupb.pack(side=LEFT)
        self.voldownb.pack(side=LEFT) 

    def audioforw(self):
        cmd = "tube-track-up,"
        self.value=""
        self.send_cmd(cmd)
        return   
    def audioback(self):
        cmd = "tube-track-down,"
        self.value=""
        self.send_cmd(cmd)
        return   
    def volup(self):
        cmd = "tube-up,"
        self.value=""
        self.send_cmd(cmd)
        return
    def voldown(self):
        cmd = "tube-down,"
        self.value=""
        self.send_cmd(cmd)
        return
    def send_cmd(self, cmd):
        command = cmd + socket.gethostname()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.receiver, 8092))
            #sock.settimeout(None)
            sock.send(command.encode('ascii'))
            sock.close()
        except:
            return False

