#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

path2src='./../'
versionfile=open(path2src+'version.d','r')
version=versionfile.readline().strip()
versionfile.close()
reqdirs=[]
reqfiles=[]
reqfile=open(path2src+'required-files.txt','r')
for l in reqfile.readlines():
	l=l.strip()
	reqfiles.append('"/usr/share/damnvid/'+l+'"')
	if l.find('/')!=-1:
		if l[0:l.find('/')+1] not in reqdirs:
			reqdirs.append(l[0:l.find('/')+1])
reqdirs='%dir "/usr/share/damnvid/'+'"\n%dir "/usr/share/damnvid/'.join(reqdirs)+'"'
reqfiles='\n'.join(reqfiles)
reqfile.close()
spec=open(path2src+'build-rpm/damnvid.spec','r')
specout=open(path2src+'damnvid.spec','w')
for l in spec.readlines():
	specout.write(l.strip().replace('{version}',version).replace('$HOME',os.path.expanduser('~')).replace('{files}',reqdirs+'\n'+reqfiles)+'\n')
spec.close()
specout.close()
