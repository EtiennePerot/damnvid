#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import os

path2src='./'
versionfile=open(path2src+'version.damnvid','r')
version=versionfile.readline().strip()
versionfile.close()
files=open(path2src+'required-files.txt','r')
data_files=[]
for f in files.readlines():
	curfile=f.strip()
	if curfile and curfile!='DamnVid.py':
		if curfile.find(os.sep)==-1:
			data_files.append(path2src+curfile)
		else:
			data_files.append((curfile[0:curfile.rfind(os.sep)],[path2src+curfile]))
files.close()
setup(
	app=[path2src+'DamnVid.py'],
	data_files=data_files,
	options={
		'py2app':{
			'argv_emulation':True,
			'iconfile':path2src+'img/icon.icns',
			'plist':{
				'CFBundleShortVersionString':version,
				'CFBundleGetInfoString':'DamnVid '+version,
				'CFBundleExecutable':'DamnVid',
				'CFBundleName':'DamnVid',
				'CFBundleIdentifier':'com.googlecode.DamnVid',
				'CFBundleTypeExtensions':['damnvid','avi','mkv','ogm','ogg','mp3','divx','x264','mov','mp4','mpg','mpeg','aac','flv','3gp''wma','wmv','rm','3g2','vob'],
				'CFBundleTypeRole':'Editor'
			}
		}
	},
	setup_requires=['py2app']
)
