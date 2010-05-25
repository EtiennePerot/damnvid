#!/usr/bin/env bash

damnroot="`cd "\`dirname "$0"\`/.."; pwd`"
cd "$damnroot/.."
python "$damnroot/build-any/cleanup.py"
tarname="damnvid-`cat "$damnroot/version.damnvid"`-source.tar.bz2"
if [ -e "$tarname" ]; then
	rm "$tarname"
fi
tar -cvjf "$tarname" --exclude-vcs --exclude='debian' --exclude='ffmpeg' --exclude='ffmpeg64' "`basename "$damnroot"`"
echo "Source tarball $tarname has been created in `pwd`."
