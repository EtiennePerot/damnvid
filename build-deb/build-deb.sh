#!/bin/bash

# Yes, I am aware that this is not the really right way to build .deb's. But hey, if you wanna help me build deb's, feel free to help! :)

orig=$(pwd)
timestamp=$(date "+%a, %d %b %Y %H:%m:%S %Z")
rm -rf ~/build-damnvid
cd ..
read version < version.damnvid
tar -czvf build.tar.gz --exclude=*.svn --exclude=*~ DamnVid.py version.damnvid damnvid.desktop COPYING bin/ffmpeg conf img/*.jpg img/*.png img/*.ico
mkdir ~/build-damnvid
mkdir ~/build-damnvid/damnvid-$version
mv build.tar.gz ~/build-damnvid/damnvid-$version/damnvid-$version.tar.gz
cd ~/build-damnvid/damnvid-$version
mkdir -p debian/DEBIAN
cd debian/DEBIAN
echo "damnvid ($version) unstable; urgency=low

  * See http://code.google.com/p/damnvid/source/list

 -- WindPower <windypower@gmail.com>  $timestamp">changelog.Debian
echo "Package: damnvid
Version: $version-1
Architecture: all
Maintainer: WindPower <windypower@gmail.com>
Depends: python2.5 (>= 2.5-1), python-wxgtk2.6
Section: Multimedia
Priority: standard
Homepage: http://damnvid.googlecode.com/
Description: A versatile video downloader/converter, written in Python.
 DamnVid is a video downloader and converter based on FFmpeg. It can download videos from YouTube, Google Video, and other video sharing sites, and can convert them on-the-fly, while downloading.">control
cp $orig/copyright ./copyright
cp $orig/dirs ./dirs
cp $orig/rules ./rules
cd .. # Back to build-damnvid/damnvid-$version/debian
mkdir -p usr/share/damnvid
cd usr/share/damnvid
tar -xvf ../../../../damnvid-$version.tar.gz
rm ../../../../damnvid-$version.tar.gz
cd .. # Now we're in usr/share
mkdir applications
cp $orig/damnvid.desktop applications/damnvid.desktop
mkdir -p doc/damnvid
cp ../../DEBIAN/copyright doc/damnvid/copyright
echo "damnvid for Debian" > doc/damnvid/README.Debian
gzip -c ../../DEBIAN/changelog.Debian > doc/damnvid/changelog.Debian.gz
cd ../../.. # Now we're back in build-damnvid/damnvid-$version
dpkg-deb -b debian damnvid_$version-1_all.deb
fakeroot alien -r damnvid_$version-1_all.deb
rm -rf debian
cd $orig

