#!/bin/sh
cd ./..
rm -rf DamnVid.app required-files.txt
python build-required-files.py
python ./build-app/py2app-osx.py py2app
mv ./dist/DamnVid.app ./DamnVid.app
rm -rf build dist
chmod 0777 ./DamnVid.app/Contents/Resources/bin/ffmpegosx