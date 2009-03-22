#!/bin/sh

echo "Customizing disk image..."
echo "Adding symlinks"
ln -sn /Applications /Volumes/DamnVid/Applications
ln -sn ./../Frameworks /Volumes/DamnVid/DamnVid.app/Contents/Resources/Frameworks
echo "Setting custom icon"
cp ./img/icon.icns /Volumes/DamnVid/.VolumeIcon.icns
SetFile -a C /Volumes/DamnVid
echo "Setting custom background"
mkdir /Volumes/DamnVid/.background
cp ./build-app/dmg-background.png /Volumes/DamnVid/.background/background.png
cp ./build-app/DS_Store /Volumes/DamnVid/.DS_Store
echo "Done, will resume Perl script and unmount DMG now."