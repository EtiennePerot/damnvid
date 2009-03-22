import os

path2src='./../../'
print os.listdir(path2src)
requiredfiles=open(path2src+'required-files.txt','r')
delete=[]
rmdirs=[]
files=[]
curdir='$INSTDIR'+os.sep
for f in requiredfiles.readlines():
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
        
