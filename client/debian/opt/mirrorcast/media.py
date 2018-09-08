# -*- coding: utf-8 -*-

from tkinter import *
import socket

class Media(object):
    def __init__(self,master):
        self.value=""
        self.receiver="None"
        top=self.top=master
        topframe = Frame(top)
        topframe.pack()
        self.l=Label(topframe,text="These are controls for the Receiving Device")
        self.l.pack()
        self.l3=Label(topframe,text="__________________________________________")
        self.l3.pack()
        self.l2=Label(topframe,text="Note: It may take up to 15 seconds to start your media on the receiver")
        self.l2.pack()
        self.l4=Label(topframe,text="This feature is experimental, if you file does not play please close this window and try again.")
        self.l4.pack()
        controls = Frame(top)
        controls.pack(side=BOTTOM)

        self.state=Label(controls,textvariable="")
        self.backb=Button(controls,text='Rewind',command=self.back)
        self.playb=Button(controls,text='Play/Pause',command=self.play)
        self.forwardb=Button(controls,text='Fast-Forward',command=self.forward)
        self.stopb=Button(controls,text='Stop',command=self.stop)
        self.volb = Scale(controls, from_=-2500, to=400, orient=HORIZONTAL, label="Volume", showvalue=0, command=self.vol)
        self.state.pack(side=LEFT)
        self.backb.pack(side=LEFT)
        self.playb.pack(side=LEFT)
        self.forwardb.pack(side=LEFT)
        self.audiobackb=Button(controls,text='Audio Track Back',command=self.audioback)
        self.audioforwb=Button(controls,text='Audio Track Up',command=self.audioforw)
        self.audioforwb.pack(side=LEFT)
        self.audiobackb.pack(side=LEFT)
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
    def play(self):
        cmd = "tube-pause,"
        self.send_cmd(cmd)
        return
    def back(self):
        cmd = "tube-back,"
        self.send_cmd(cmd)
        return
    def forward(self):
        cmd = "tube-forward,"
        self.send_cmd(cmd)
        return
    def stop(self):
        cmd = "tube-stop,"
        self.send_cmd(cmd)
        return

    def send_cmd(self, cmd):
        if cmd == "tube-vol,":
            command = cmd + socket.gethostname() + "," + str(self.volb.get())
        else:
            command = cmd + socket.gethostname()
        try:
            print(cmd)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.receiver, 8092))
            sock.settimeout(30)
            sock.send(command.encode('ascii'))
            sock.close()
        except:
            return False

    def on_closing(self):
        cmd = "tube-stop,"
        self.send_cmd(cmd)

