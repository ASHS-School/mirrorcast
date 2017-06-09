<h1>Mirrorcast - Open Source Solution to Screen Mirroring</h1>

<p>This is a work in progress, the code is rushed, messy and not at all elegant at this stage.</p>

<p>The idea is to replicate what chromecast can do in regards to screen mirroring. 
Google chromes screen mirroring feature is very good when used with a receiver such as chromecast but this solution is proprietary.</p>

<p>This application is ideal for wireless projection, no more cables, just send your desktop over the network to a receiver</P>

<p>At the moment, there is only a client for Debian/Ubuntu Operating systems and I have no plans to create a client application. There is a server/receiver application for raspberry pi and Linux</p>

<p>Mirrorcast aims to be a low latency screen mirroring solution with high quality video and audio at 25-30fps, the later is why will not use VNC.</p>

<p>Mirrorcast uses up about the same amount of system resources as google chromes cast feature. The delay is less than 1 second on most networks.</p>

<p>To acheive this we will use existing FOSS software such as ffmpeg, ffplay and omxplayer</p>

<h2>TO DO:</h2>

<b>DEBIAN/UBUNTU APPLET</b>
<ul><li>Automate audio settings(This is partially done, you might need to add or modify some code to automate audio settings for some machines)</li>
<li>Add option mirror selected application</li>
<li>Verify receiver is online and ready before attempting to connect</li>
<li>Tidy up code</li></ul>

<b>Other</b>
<ul><li>Create Windows client application</li>
<li>Create MacOs client application</li>
<li>Create Android client application</li></ul>


<h2>How to use</h2>

<p>Currently this is a rough prototype that I have only tested using my laptop and raspberry pi as the receiver. The applet will add a option to start mirroring the selected display to the selected receiver.</p>

<p>If you are using a raspberry pi as a receiver you need omxplayer installed. Once omxplayer is installed, you just need to run mirror-pi.sh.</br> If your receiver is not a raspberry pi then you can run the other script in the server folder, for that you will need to install ffplay which is included with ffmpeg.<br/>On the device you wish to mirror you will need python3 and ffmpeg installed, the python script will add a applet to your toolbar which gives you the option to select a receiver and a display to you wish to mirror. You need to add either the hostnames or the ip addresses of your receivers to the receivers file.(this python script is for debian and ubuntu based systems)</p>
