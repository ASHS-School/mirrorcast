<h1>Mirrorcast - Open Source Solution for Screen Mirroring</h1>

<p>The idea is to replicate what chromecast can do in regards to screen mirroring. 
Google chromes screen mirroring feature is very good when used with a receiver such as chromecast but this solution is proprietary and audio does not work for desktop screening on some operating systems.</p>

<p>This application is ideal for wireless projection, no more cables, just send your desktop over the network to a receiver</P>

<p>At the moment, there is only a client for Debian/Ubuntu Operating systems. There is a server/receiver application for raspberry pi and Linux</p>

<p>Mirrorcast aims to be a low latency screen mirroring solution with high quality video and audio at 25-30fps, the later is why we will not use VNC.</p>

<p>Mirrorcast uses up about the same amount of system resources as google chromes cast feature. The delay is less than 1 second on most networks.</p>

<p>To acheive this we will use existing FOSS software such as ffmpeg, ffplay and omxplayer</p>

<h2>TO DO:</h2>

<b>DEBIAN/UBUNTU APPLET</b>
<ul><li>Automate audio settings(This is partially done, you might need to modify some code to automate audio settings for some computers)</li>
<li>Add option mirror selected application</li>
<li>Add option to freeze/pause at current frame on the receiver so the user can continue working on their computer</li>
<li>Tidy up code (Create classes for displays and receivers)</li></ul>

<b>Other</b>
<ul><li>Create Windows client application</li>
<li>Create MacOs client application</li>
<li>Create Android client application</li></ul>

<h2>How to use</h2>

<p>Currently this is a rough prototype that I have only tested using my laptop running Ubuntu 16.04 and raspberry pi as the receiver. The applet will add a option to start mirroring the selected display to the selected receiver.</p>

<p>To install the mirrorcast client on debian/ubuntu<ul>
<li>download the latest mirrorcast deb file from releases</li>
<li>Install it</li>
<li>sudo dpkg -i mirrorcast_version_number.deb</li>
<li>if you are missing dependencies install them with</li>
<li>sudo apt-get update && sudo apt-get -f install</li>
<li>add/edit the hostnames or ip addresses of your receivers to /opt/mirrorcast/receivers (if the receiver is widescreen then put 'wide' as the aspect)</li></ul></p>

<p>On the raspberry pi receiver<ul>
<li>install supervisor and omxplayer and set the following command up as a deamon</li>
<li>nohup omxplayer -o hdmi --lavfdopts probesize:5000 --timeout 10 -live tcp://0.0.0.0:8090?listen > /tmp/nohup.out &</li>
</ul></p>

<p>To start mirroring your desktop start mirrorcast, it will add an applet to your toolbar, first select the display you want to mirror, then select your receiver, then click 'start mirroring'</p>

<p>NOTE: This is a work in progress, the code is rushed, messy and not at all elegant at this stage. I will do things such as create classes for displays and receivers to make it more elegant. </p>
