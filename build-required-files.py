import os
import sys

OSNAME=os.name
if OSNAME=='posix' and sys.platform=='darwin':
    OSNAME='mac'
required_files=[]
while not os.path.lexists('./DamnVid.py'):
    os.chdir('./..')
ext='py'
if OSNAME=='nt':
    ext='exe'
required_files.extend(['DamnVid.'+ext,'version.damnvid','COPYING'])
del ext
if OSNAME=='nt':
    required_files.append('DamnVid.exe.manifest')
required_dirs=['img','conf','modules']
def addDir(d):
    global required_files
    for f in os.listdir(d):
        if f.find('.svn')==-1 and f.find('.psd')==-1 and f.find('.noinclude')==-1 and f.find('.module.damnvid')==-1 and f.find('.bmp')==-1 and f.find('.ai')==-1 and f.find('.exe')==-1 and f.find('.zip')==-1 and f.find('fireworks.png')==-1:
            if os.path.isdir(d+os.sep+f):
                addDir(d+os.sep+f)
            else:
                required_files.append(d+os.sep+f)
for d in required_dirs:
    addDir(d)
if OSNAME=='nt':
    required_files.extend(['bin'+os.sep+'ffmpeg.exe','bin'+os.sep+'taskkill.exe','bin'+os.sep+'SDL.dll'])
elif OSNAME=='mac':
    required_files.append('bin'+os.sep+'ffmpegosx')
else:
    required_files.append('bin'+os.sep+'ffmpeg')
required_file=open('required-files.txt','w')
for f in required_files:
    required_file.write(f+'\n')
required_file.close()
