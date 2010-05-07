# -*- coding: utf-8 -*-
import os

path2src='./../../'
curfiles = []
def addToCurFiles(d):
	global curfiles
	if len(d):
		d=d+os.sep
	for i in os.listdir(d):
		if os.path.isdir(d+i):
			addToCurFiles(d+i)
		else:
			curfiles.append(d+i)
addToCurFiles('')
requiredfiles=open(path2src+'required-files.txt','r')
reqfiles=requiredfiles.readlines()
reqfiles.extend(curfiles)
delete=[]
rmdirs=[]
files=[]
alreadydone=[]
curdir='$INSTDIR'+os.sep
for f in reqfiles:
	if f in alreadydone:
		continue
	alreadydone.append(f)
	curfile=f.strip()
	if curfile.find(os.sep)==-1 and curdir!='$INSTDIR'+os.sep:
		curdir='$INSTDIR'+os.sep
		files.append('setOutPath "$INSTDIR'+os.sep+'"')
	elif curfile.find(os.sep):
		newdir='$INSTDIR'+os.sep+curfile[0:curfile.rfind(os.sep)+1]
		if curdir!=newdir:
			curdir=newdir
			files.append('setOutPath "'+newdir[0:-1]+'"')
			if 'rmDir "'+newdir[0:-1]+'"' not in rmdirs:
				rmdirs.append('rmDir "'+newdir[0:-1]+'"')
	files.append('file "'+curfile+'"')
	delete.append('delete "$INSTDIR'+os.sep+curfile+'"')
newdirs=True
while newdirs:
	somethingchanged=False
	for i in rmdirs:
		if i[0:i.rfind(os.sep)]!='rmDir "$INSTDIR' and i[0:i.rfind(os.sep)]+'"' not in rmdirs:
			rmdirs.append(i[0:i.rfind(os.sep)]+'"')
			somethingchanged=True
	if not somethingchanged:
		newdirs=False
requiredfiles.close()
nsi=open(path2src+'build-exe'+os.sep+'NSIS-win32.nsi','r')
newnsi=open(path2src+'NSIS-win32.nsi','w')
for l in nsi.readlines():
	if l.strip()=='<files>':
		newnsi.write('\n'.join(files)+'\n')
	elif l.strip()=='<delete>':
		newnsi.write('\n'.join(delete)+'\n'+'\n'.join(rmdirs)+'\n')
	else:
		newnsi.write(l)
nsi.close()
newnsi.close()

