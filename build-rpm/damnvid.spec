Buildroot: $HOME/dev/damnvid/package
Name: damnvid
Version: {version}
Release: 1
Summary: A versatile video downloader/converter, written in Python.
License: GPL
Group: Applications/Multimedia
URL: http://damnvid.googlecode.com/

%define _rpmdir ../
%define _rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm
%define _unpackaged_files_terminate_build 0

%description
DamnVid is a video downloader and converter based on FFmpeg. It can download videos from YouTube, Google Video, and other video sharing sites, and can convert them on-the-fly, while downloading.

%files
%dir "/"
%dir "/usr/"
%dir "/usr/share/"
%dir "/usr/share/damnvid/"
%dir "/usr/share/applications/"
"/usr/share/applications/damnvid.desktop"
%dir "/usr/share/doc/"
%dir "/usr/share/doc/damnvid/"
"/usr/share/doc/damnvid/changelog.Debian.gz"
"/usr/share/doc/damnvid/copyright"
"/usr/share/doc/damnvid/README.Debian"
{files}
