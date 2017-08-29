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
        self.audioforwb.pack(side=LEFT)
        self.audiobackb.pack(side=LEFT)
        self.VOL=Label(controls,text="Volume")
        self.VOL.pack(side=LEFT)
        self.volb = Scale(controls, from_=-2500, to=700, orient=HORIZONTAL, command=self.vol)
        self.volb.set(0)
        self.volb.pack()
    def vol(self, vol):
        cmd = "tube-vol,"
        self.send_cmd(cmd)
        return   
    def audioforw(self):
        cmd = "tube-track-up,"
        self.send_cmd(cmd)
        return   
    def audioback(self):
        cmd = "tube-track-down,"
        self.send_cmd(cmd)
        return   
    def send_cmd(self, cmd):
        if cmd == "tube-vol,":
            command = cmd + socket.gethostname() + "," + str(self.volb.get())
        else:
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

