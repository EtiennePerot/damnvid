#!/bin/sh

echo "Starting build process."
cd ./..
hdiutil detach /Volumes/DamnVid
rm -rf DamnVid.app required-files.txt DamnVid-*.dmg
echo "Compyling..."
python build-required-files.py
python ./build-app/py2app-osx.py py2app
echo "Adjusting..."
mv ./dist/DamnVid.app ./DamnVid.app
rm -rf build dist
chmod 0777 ./DamnVid.app/Contents/Resources/bin/ffmpegosx
echo "Building disk image..."
./build-app/buildDMG.pl -dmgName DamnVid -volName DamnVid -buildDir ./ -deleteHeaders -compressionLevel 9 ./DamnVid.app
read version<version.damnvid
mv DamnVid.dmg DamnVid-$version.dmg
rm -rf ./DamnVid.app ./sh ./required-files.txt
echo "All done!"