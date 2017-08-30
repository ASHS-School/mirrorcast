#!/bin/bash

wget http://epick.org/mirrorcast/mirrorcast-latest.deb -O /tmp/mirrorcast-latest.deb

cp /opt/mirrorcast/receivers /tmp/

gksudo -- bash -c 'dpkg -i -E /tmp/mirrorcast-latest.deb; cp /tmp/receivers /opt/mirrorcast/'
