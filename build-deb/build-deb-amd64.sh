#!/bin/bash

# Yes, I am aware that this is absolutely not the right way to build .deb's. But hey, if you wanna help me build .deb's, feel free! :)

origcurdir=$(pwd)
mv ../bin/ffmpeg ../bin/ffmpeg-i386-temp
mv ../bin/ffmpeg-amd64 ../bin/ffmpeg
sh build-deb.sh
cd $origcurdir
mv ../bin/ffmpeg ../bin/ffmpeg-amd64
mv ../bin/ffmpeg-i386-temp ../bin/ffmpeg