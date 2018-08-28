# -*- coding: utf-8 -*-

from tkinter import *
import socket

class Dvd(object):
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
        self.pchaptb=Button(controls,text='Previous Chapter',command=self.p_chapt)
        self.nchaptb=Button(controls,text='Next Chapter',command=self.n_chapt)
        self.subtitleb=Button(controls,text='Subtitle',command=self.subtitle)
        self.audioforwb.pack(side=LEFT)
        self.audiobackb.pack(side=LEFT)
        self.pchaptb.pack(side=LEFT)
        self.nchaptb.pack(side=LEFT)
        self.subtitleb.pack(side=LEFT)
        self.volb = Scale(controls, from_=-2500, to=400, orient=HORIZONTAL, label="Volume", showvalue=0, command=self.vol)
        self.volb.set(0)
        self.volb.pack()
    def vol(self, vol):
        cmd = "dvd-vol,"
        self.send_cmd(cmd)
        return   
    def audioforw(self):
        cmd = "dvd-track-up,"
        self.send_cmd(cmd)
        return   
    def audioback(self):
        cmd = "dvd-track-down,"
        self.send_cmd(cmd)
        return   
    def play(self):
        cmd = "dvd-pause,"
        self.send_cmd(cmd)
        return
    def back(self):
        cmd = "dvd-back,"
        self.send_cmd(cmd)
        return
    def forward(self):
        cmd = "dvd-forward,"
        self.send_cmd(cmd)
        return
    def n_chapt(self):
        cmd = "n_chapt,"
        self.send_cmd(cmd)
        return
    def p_chapt(self):
        cmd = "p_chapt,"
        self.send_cmd(cmd)
        return
    def subtitle(self):
        cmd = "subtitle,"
        self.send_cmd(cmd)
        return
    def stop(self):
        cmd = "dvd-stop,"
        self.send_cmd(cmd)
        return

    def send_cmd(self, cmd):
        if cmd == "dvd-vol,":
            command = cmd + socket.gethostname() + "," + str(self.volb.get())
        else:
            command = cmd + socket.gethostname()
        try:
            print(cmd)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.receiver, 8092))
            sock.settimeout(None)
            sock.send(command.encode('ascii'))
            sock.close()
        except:
            return False

    def on_closing(self):
        cmd = "dvd-stop,"
        self.send_cmd(cmd)

