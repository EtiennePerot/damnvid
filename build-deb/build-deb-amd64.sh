#!/bin/bash

# Yes, I am aware that this is absolutely not the right way to build .deb's. But hey, if you wanna help me build .deb's, feel free! :)

origcurdir=$(pwd)
mv ../bin/ffmpeg ../bin/ffmpeg32
mv ../bin/ffmpeg64 ../bin/ffmpeg
sh build-deb.sh
cd $origcurdir
mv ../bin/ffmpeg ../bin/ffmpeg64
mv ../bin/ffmpeg32 ../bin/ffmpeg
