# Mirrorcast - Open Source Alternative to Chromecast

The idea is to replicate what Chromecast can do in regards to screen mirroring and streaming media to a remote display. 
Google chromes screen mirroring feature works well when used with a receiver such as Chromecast but this is a proprietary solution and audio does not work for desktop mirroring on some operating systems.

At the moment, there is only a client for Debian/Ubuntu Operating systems and a server/receiver application for Raspberry pi..

Mirrorcast aims to be a low latency screen mirroring solution with high quality video and audio at 25-30fps, the later is why we will not use something like VNC.

Mirrorcast uses up about the same amount of system resources as google chromes cast feature. The delay is less than 1 second on most networks.

To achieve this we will use existing FOSS software such as ffmpeg, mpv, and omxplayer.

At the moment you can stream your screen(with audio), play youtube videos, play media files and DVD's.

<p>Video Demo(Updated 15 Sep 2018) <a href="https://www.youtube.com/watch?v=yQ11EVcUL9I">https://www.youtube.com/watch?v=yQ11EVcUL9I</a> </p>

<h2>TO DO:</h2>

<b>DEBIAN/UBUNTU APPLET</b>

<p>The debian/ubuntu app is working but could do with improvements</p>

<ul><li>Automate audio settings(This is partially done, you might need to modify some code to automate audio settings for some computers)</li>
<li>Add option mirror selected application (Using Xlib and composite(redirect and pixmap) so that applications will still mirror if covered by another window, resized or minimised), this might require a full C+ conversion, unfortunately I lack practice in C and C+</li>
<li>Tidy up code (Find simplier and more pythonic solutions where possible)</li></ul>

<b>Other (If you want to help out with creating a client for the following then that would be great)</b>
<ul><li>Create Windows client application</li>
<li>Create MacOs client application</li>
<li>Create Android client application</li>
<li>Other bug fixes; additionial features and improvements</li>
<li>Improve this documentation.</ul>


<h2>How to use</h2>

Currently this is a rough prototype that I have only tested on computers running Ubuntu 16.04 and Lubuntu and a raspberry pi as the receiver. The applet will add a option to start mirroring the selected display to the selected receiver. It has been deployed at a High School where it is used so the teachers can use the projectors without cables.

To install the mirrorcast client on debian/ubuntu
First download and install the latest mirrorcast deb file from releases
```sh
sudo dpkg -i mirrorcast_version_number.deb
```
If you are missing dependencies install them with:
```sh 
sudo apt-get update && sudo apt-get -f install
```
Then add/edit the hostnames or ip addresses of your receivers in /opt/mirrorcast/receivers (if the receiver is widescreen then put '16:9' as the aspect)

<h2>Setting up the raspberry pi server/receiver.</h2>

Install omxplayer. 
Install youtube-dl and python-omxplayer-wrapper for python3. Make sure you install the requirements for both of these.

Then download mirrorcast_server_pi.py and omx.py from the server folder or just clone the whole repo.

Install python-mpv
```
npm3 python-mpv
```
Add the following to /etc/rc.local
```
python3 /path/to/mirrorcast_server_pi.py
modprobe nbd
```
If you want to be able to play DVD's then you will need the mpeg2 license from the pi store and mpv compiled with mmal and libmpv support, you will also need libass and ffmpeg with mmal support.

If you do not want to compile them yourself then I have some pre-compiled packages I compiled for Respbian that you can try but first lets make sure the pi is up to date(including firmware).
```
sudo apt-get update
sudo apt-get upgrade
sudo rpi-update
```
Some dependencies are needed for mpv which is used for DVD playback.
```
sudo apt-get install libgles2-mesa libsdl2-dev libva-dev nbd-client
```
Create links to libraries
NOTE: If the links already exist then ignore this part.
```
sudo ln -s /usr/lib/arm-linux-gnueabihf/pkgconfig/glesv2.pc /opt/vc/lib/pkgconfig/
sudo ln -s /usr/lib/arm-linux-gnueabihf/pkgconfig/egl.pc /opt/vc/lib/pkgconfig/
sudo ln -s /usr/lib/arm-linux-gnueabihf/libGLESv2.so /opt/vc/lib/
sudo ln -s /usr/lib/arm-linux-gnueabihf/libEGL.so /opt/vc/lib/
sudo ldconfig
```
Download for pre-compiled packages. 
```
mkdir mpv-mmal && cd mpv-mmal
#For stretch, try these
wget https://3djakedesigns.org/debian/stretch/fdk-aac_0.1.5-1_armhf.deb https://3djakedesigns.org/debian/stretch/ffmpeg_20180831-1_armhf.deb https://3djakedesigns.org/debian/stretch/lame_3.100-1_armhf.deb https://3djakedesigns.org/debian/stretch/libass_0.14.0-1_armhf.deb https://3djakedesigns.org/debian/stretch/libvpx_1.6.1-1_armhf.deb https://3djakedesigns.org/debian/stretch/mpv_0.29.0-1_armhf.deb https://3djakedesigns.org/debian/stretch/opus_1.2.1-1_armhf.deb https://3djakedesigns.org/debian/stretch/x264-snapshot-20180125-2245_20180125-1_armhf.deb
#For Jessie, try these
wget https://3djakedesigns.org/debian/jessie/fdk-aac_0.1.5-1_armhf.deb https://3djakedesigns.org/debian/jessie/ffmpeg_20180907-1_armhf.deb https://3djakedesigns.org/debian/jessie/lame_3.100-1_armhf.deb https://3djakedesigns.org/debian/jessie/libass_0.14.0-1_armhf.deb https://3djakedesigns.org/debian/jessie/libvpx_1.7.0-1_armhf.deb https://3djakedesigns.org/debian/jessie/mpv_0.29.0-1_armhf.deb https://3djakedesigns.org/debian/jessie/opus_1.2.1-1_armhf.deb https://3djakedesigns.org/debian/jessie/x264-snapshot-20180125-2245_20180125-1_armhf.deb
```
Install the packages and prevent apt from replacing them.
```
sudo apt-mark hold libass ffmpeg fdk-acc libvpx mpv opus x264 lame libass5 libvpx1 opus-tools
sudo dpkg -i *.deb
sudo apt-get -f install

```
If you want to play DVD's then you need to install libdvd-pkg
```
sudo apt-get install libdvd-pkg
sudo dpkg-reconfigure libdvd-pkg
```
For DVD's you will also need to buy an mpeg2 license from the pi store <a href="https://www.raspberrypi.com/mpeg-2-license-key/">https://www.raspberrypi.com/mpeg-2-license-key/</a> </p>

Verify mpv has all its dependencies.
```
mpv --version
```
Restart the pi



By default the Mirrorcast server uses udp port 8090 and tcp port 8092. If the client wants to stream files, then TCP port 8090 needs to be open on the client side. For DVD's, the default nbd-server port also needs to be open on client side too.

To start mirroring your desktop, start the mirrorcast application, it will add an applet to your toolbar, first select the display you want to mirror(if you have more than one), then select your receiver, then click "start mirroring"

<p>NOTE: This is a work in progress, the code is rushed, messy and not at all elegant at this stage. </p>
