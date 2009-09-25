#!/bin/bash

# Install required packages
sudo apt-get install subversion mercurial python2.5 python2.5-dev python-setuptools python-wxgtk2.8 python-gdata python-beautifulsoup rpm

# Install BBfreeze
mkdir -p ~/.temp-bbfreeze
cd ~/.temp-bbfreeze
hg clone http://systemexit.de/repo/bbfreeze
cd bbfreeze
sudo python2.5 setup.py install
cd ~
sudo rm -rf ~/.temp-bbfreeze
