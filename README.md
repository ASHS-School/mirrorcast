<h1>Mirrorcast - Open Source Solution to Screen Mirroring</h1>

<p>This is a work in progress, the code is rushed, messy and not at all elegant at this stage.</p>

<p>The idea is to replicate what chromecast can do in regards to screen mirroring. 
Google chromes screen mirroring feature is very good when used with a receiver such as chromecast but this solution is proprietary.</p>

<p>Mirrorcast aims to be a low latency screen mirrowing solution while remaining high quality video and audio at 30fps, the later is why will not use VNC.</p>

<p>To acheive this we will use existing FOSS software such as ffmpeg, ffplay and omxplayer</p>

<h2>TO DO:</h2>

<b>DEBIAN APPLET</b>
<ul><li>Detect and set the correct audio settings for pulse and alsa(mute microphone and speakers while still playing sound via the receiver)</li>
<li>Make ffmpeg use up less of the CPU</li>
<li>Tidy up code</li></ul>

<h2>How to use</h2>

<p>Currently this is a rough prototype that I have only tested using my laptop and raspberry pi as the receiver. The applet will add a option to start mirroring the selected display to the selected receiver, you will have to maunally change the audio recording settings in pavucontrol to monitor your desktop audio and mute your microphone if you wish audio to be played on the receiver.</p>

<p>On the receiving raspberry pi you will need omxplayer installed and then you just need to run mirror-pi.sh<br/>On the device you wish to mirror you will need python3 and ffmpeg installed, the python script will add a applet to your toolbar which gives you the option to select a receiver and a display to mirror. You need to add either the hostname or the ip address of your receivers to the receivers file.(this python script is for debian and ubuntu based systems)</p>
