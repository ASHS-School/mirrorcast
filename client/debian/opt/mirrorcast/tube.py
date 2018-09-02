from tkinter import *
import socket

class Tube(object):
    def __init__(self,master):
        self.receiver="None"
        top=self.top=master
        topframe = Frame(top)
        topframe.pack()
        self.l=Label(topframe,text="This will play videos from both youtube and dailymotion")
        self.l.pack()
        self.l2=Label(topframe,text="Copy(ctrl+c) and Paste(Ctrl+v) the Youtube URL into the text box and then click 'load'")
        self.l2.pack()
        self.l3=Label(topframe,text="While the video is loading, the 'load' button will remain greyed out, this may take a few seconds.")
        self.l3.pack()
        self.e=Entry(topframe, width=80)
        self.e.pack(side=LEFT)
        self.loadb=Button(topframe,text='load',command=self.load)
        self.loadb.pack(side=LEFT)
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
        self.volb.set(0)
        self.volb.pack(side=LEFT)
        self.stopb.pack(side=LEFT)
    def load(self):
        cmd = "tube-load,"
        self.value=self.e.get()
        self.send_cmd(cmd, self.value)
        return
    def play(self):
        cmd = "tube-pause,"
        self.value=self.e.get()
        self.send_cmd(cmd, self.value)
        return
    def back(self):
        cmd = "tube-back,"
        self.send_cmd(cmd, self.value)
        return
    def forward(self):
        cmd = "tube-forward,"
        self.send_cmd(cmd, self.value)
        return
    def stop(self):
        cmd = "tube-stop,"
        self.value=""
        self.send_cmd(cmd, self.value)
        self.set_state("")
        return   
    def vol(self, vol):
        cmd = "tube-vol,"
        self.send_cmd(cmd, self.volb.get())
        return   
    def send_cmd(self, cmd, url):
        if cmd == "tube-vol,":
            command = cmd + socket.gethostname() + "," + str(self.volb.get())
        else:
            command = cmd + socket.gethostname() + "," + url
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.receiver, 8092))
            sock.settimeout(None)
            sock.send(command.encode('ascii'))
            if cmd == "tube-load,":
                status = sock.recv(8024)
                if status.decode('ascii') == "ready":
                    self.set_state("Playing")
                elif status.decode('ascii') == "error":
                    self.set_state("Invalid URL: Please check URL is valid")
            sock.close()
        except:
            self.set_state("Failed, Please make sure you copied the URL correctly")
            return False
            
    def set_state(self, state):
        self.state.configure(text=state)
        return
        
    def on_closing(self):
        cmd = "tube-stop,"
        self.value=""
        self.send_cmd(cmd, self.value)
        self.set_state("")