<h1>Mirrorcast - Open Source Solution to Screen Mirroring</h1>

<p>This is a work in progress, the code is rushed, messy and not at all elegant at this stage.</p>

<p>The idea is to replicate what chromecast can do in regards to screen mirroring. 
Google chromes screen mirroring feature is very good when used with a receiver such as chromecast but this solution is proprietary.</p>

<p>Mirrorcast aims to be a low latency screen mirrowing solution while remaining high quality video and audio at 30fps, the later is why will not use VNC.</p>

<p>To acheive this we will use existing FOSS software such as ffmpeg, ffplay and omxplayer</p>

<h2>TO DO:</h2>

<b>DEBIAN APPLET</b>
<ul><li>Automate audio settings(This is partially done, you might need to add some code some machines)</li>
<li>Make ffmpeg use up less of the CPU</li>
<li>Tidy up code</li></ul>

<h2>How to use</h2>

<p>Currently this is a rough prototype that I have only tested using my laptop and raspberry pi as the receiver. The applet will add a option to start mirroring the selected display to the selected receiver.</p>

<p>On the receiving raspberry pi you will need omxplayer installed and then you just need to run mirror-pi.sh, if your receiver is not a raspberry pi then you can run the other script in the server folder, for that you will need to install ffplay which is included with ffmpeg.<br/>On the device you wish to mirror you will need python3 and ffmpeg installed, the python script will add a applet to your toolbar which gives you the option to select a receiver and a display to you wish to mirror. You need to add either the hostnames or the ip addresses of your receivers to the receivers file.(this python script is for debian and ubuntu based systems)</p>
