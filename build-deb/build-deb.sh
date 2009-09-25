#!/bin/bash

# Yes, I am aware that this is absolutely not the right way to build .deb's. But hey, if you wanna help me build .deb's, feel free! :)

echo "This script does not check for dependencies - Please run ./dependencies.sh at least once!"

echo "Building DamnVid."
orig=$(pwd)
damnroot=$orig/..
builddir=$damnroot/package
damnarch=$(dpkg --print-architecture)
timestamp=$(date "+%a, %d %b %Y %H:%m:%S %Z")
cd "$damnroot"
rm -rf "$damnroot/package" "$damnroot/damnvid*.deb" "$damnroot/damnvid*.rpm" "$damnroot/required-files.txt"
mkdir "$builddir"
python2.5 "$damnroot/build-deb/bbfreeze-unix.py"
read version < "$damnroot/version.damnvid"
python2.5 "$damnroot/build-any/build-required-files.py"
ls -1 "$builddir" >> "$damnroot/required-files.txt"
cp "$builddir"/* "$damnroot/"
tar -czvf "$damnroot/build.tar.gz" --files-from="$damnroot/required-files.txt"
mv "$damnroot/build.tar.gz" "$builddir/build.tar.gz"
cd "$builddir"
mkdir -p "$builddir/debian/DEBIAN"
echo "damnvid ($version) unstable; urgency=low

  * See http://code.google.com/p/damnvid/source/list

 -- Etienne <etienneperot@gmail.com> $timestamp">"$builddir/debian/DEBIAN/changelog.Debian"
echo "Package: damnvid
Version: $version-1
Architecture: $damnarch
Maintainer: Etienne <etienneperot@gmail.com>
Section: sound
Priority: standard
Homepage: http://damnvid.googlecode.com/
Description: A versatile video downloader/converter, written in Python.
 DamnVid is a video downloader and converter based on FFmpeg. It can download videos from YouTube, Google Video, and other video sharing sites, and can convert them on-the-fly, while downloading.">"$builddir/debian/DEBIAN/control"
cp "$orig/copyright" "$builddir/debian/DEBIAN/copyright"
cp "$orig/dirs" "$builddir/debian/DEBIAN/dirs"
cp "$orig/rules" "$builddir/debian/DEBIAN/rules"
cd "$builddir/debian" # Back to /package/debian
mkdir -p "$builddir/debian/usr/share/damnvid"
cd "$builddir/debian/usr/share/damnvid"
tar -xvf "$builddir/build.tar.gz"
rm -f "$builddir/build.tar.gz"
cd "$builddir/debian/usr/share" # Now we're in /package/debian/usr/share
mkdir "$builddir/debian/usr/share/applications"
cp "$orig/damnvid.desktop" "$builddir/debian/usr/share/applications/damnvid.desktop"
mkdir -p "$builddir/debian/usr/share/doc/damnvid"
cp "$builddir/debian/DEBIAN/copyright" "$builddir/debian/usr/share/doc/damnvid/copyright"
echo "damnvid for Debian" > "$builddir/debian/usr/share/doc/damnvid/README.Debian"
gzip -c "$builddir/debian/DEBIAN/changelog.Debian" > "$builddir/debian/usr/share/doc/damnvid/changelog.Debian.gz"
cd "$builddir" # Now we're back in package
dpkg-deb -b debian "$builddir/damnvid_$version-1_$damnarch.deb"
mv "$builddir/damnvid_$version-1_$damnarch.deb" "$damnroot/damnvid_$version-1_$damnarch.deb"
echo "Debian package okay, now going to make RPM."
cd "$builddir/debian"
rm -rf "$builddir/debian/DEBIAN"
cd "$builddir"
rm -rf "$builddir/usr" # Just in case
mv "$builddir/debian/usr" "$builddir/usr"
rm -rf "$builddir/debian"
cd "$damnroot/build-rpm"
python2.5 "$damnroot/build-rpm/build-spec.py"
cd "$damnroot"
rpmbuild -bb --clean --target $damnarch "$damnroot/damnvid.spec"
mv "$damnroot/../damnvid-$version-1.$damnarch.rpm" "$damnroot/damnvid-$version-1.$damnarch.rpm"
python2.5 "$damnroot/build-any/cleanup.py"
echo "All done!"
