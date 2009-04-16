#!/bin/bash

# Yes, I am aware that this is not the really right way to build .deb's. But hey, if you wanna help me build .deb's, feel free to help! :)

orig=$(pwd)
cd ..
timestamp=$(date "+%a, %d %b %Y %H:%m:%S %Z")
rm -rf ./package damnvid*.deb damnvid*.rpm required-files.txt
python build-deb/bbfreeze-unix.py
read version < version.damnvid
python build-any/build-required-files.py
ls -1 package >> required-files.txt
mv package/* ./
tar -czvf build.tar.gz --files-from=required-files.txt
mv build.tar.gz ./package/build.tar.gz
cd package
mkdir -p debian/DEBIAN
cd debian/DEBIAN
echo "damnvid ($version) unstable; urgency=low

  * See http://code.google.com/p/damnvid/source/list

 -- WindPower <windypower@gmail.com> $timestamp">changelog.Debian
echo "Package: damnvid
Version: $version-1
Architecture: all
Maintainer: WindPower <windypower@gmail.com>
Section: sound
Priority: standard
Homepage: http://damnvid.googlecode.com/
Description: A versatile video downloader/converter, written in Python.
 DamnVid is a video downloader and converter based on FFmpeg. It can download videos from YouTube, Google Video, and other video sharing sites, and can convert them on-the-fly, while downloading.">control
cp $orig/copyright ./copyright
cp $orig/dirs ./dirs
cp $orig/rules ./rules
cd .. # Back to /package/debian
mkdir -p usr/share/damnvid
cd usr/share/damnvid
tar -xvf ../../../../build.tar.gz
rm ../../../../build.tar.gz
cd .. # Now we're in /package/debian/usr/share
mkdir applications
cp $orig/damnvid.desktop applications/damnvid.desktop
mkdir -p doc/damnvid
cp ../../DEBIAN/copyright doc/damnvid/copyright
echo "damnvid for Debian" > doc/damnvid/README.Debian
gzip -c ../../DEBIAN/changelog.Debian > doc/damnvid/changelog.Debian.gz
cd ../../.. # Now we're back in package
dpkg-deb -b debian damnvid_$version-1_all.deb
mv damnvid_$version-1_all.deb ./../damnvid_$version-1_all.deb
# deb file okay, now going to make RPM
cd debian
rm -rf ./DEBIAN
cd ..
mv ./debian/usr ./usr
rm -rf ./debian
cd ../build-rpm
python ./build-spec.py
cd ../package
rpmbuild -bb --clean --target noarch damnvid.spec
cd ..
python build-any/cleanup.py
echo "All done!"
