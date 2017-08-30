#!/bin/bash

wget http://epick.org/mirrorcast/mirrorcast-latest.deb -O /tmp/mirrorcast-latest.deb

gksudo dpkg -i -E /tmp/mirrorcast-latest.deb

python3 /opt/mirrorcast/mirrorcast-client.py &
