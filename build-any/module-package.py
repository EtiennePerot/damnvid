#!/usr/bin/python2.5
# -*- coding: utf-8 -*-

import os
import sys
import tarfile

def out(*args):
    s=[]
    for i in args:
        s.append(str(i))
    s=' '.join(s)
    try:
        exec('print s',globals(),locals())
    except:
        exec('print(s)',globals(),locals())
args=sys.argv
if len(args)!=2:
    out('Invalid arguments.')
    out('Usage: python ./module-package.py ./path-to-modules-folder/module')
    out('Aborting.')
    exit()
module=args[1]
if not os.path.lexists(module):
    out('Module not found in filesystem. Aborting.')
    exit()
if not os.path.isdir(module):
    out('Module is not a folder. Aborting.')
    exit()
out('Searching for module declaration file...')
foundfile=None
for i in os.listdir(module):
    if i[-8:]=='.damnvid' and not foundfile:
        out('Found',i)
        out('Searching for module declaration.')
        f=open(module+os.sep+i,'r')
        if f.readline().strip()[0:17].lower()=='#~damnvid-module:':
            out('Confirmed',i,'as module declaration file.')
            foundfile=module+os.sep+i
        f.close()
if foundfile is None:
    out('Could not find module declaration file. Aborting.')
    exit()
moduleinfo=None
class DamnVideoModule:
    pass
DV=DamnVideoModule()
DV.preference_type_audio=None
DV.preference_type_video=None
DV.preference_type_profile=None
DV.preference_type_misc=None
def DamnRegisterModule(info):
    global moduleinfo
    moduleinfo=info
try:
    execfile(foundfile)
except:
    exec(open(foundfile).read())
if moduleinfo is None:
    out('Could not find module info within module declaration file. Aborting.')
    exit()
try:
    test=str(moduleinfo['name'])+str(moduleinfo['version'])==moduleinfo['name']+moduleinfo['version']
except:
    out('Could not find name/version info in module info. Aborting.')
    exit()
out('Module name is',moduleinfo['name'],'and version is',moduleinfo['version'])
out('Packaging module...')
name=moduleinfo['name']+'-'+moduleinfo['version']+'.module.damnvid'
out('File name is',name)
out('Building files list.')
files=[]
def parseDir(d):
    global files
    for i in os.listdir(d):
        if i.find('.svn')==-1 and i[0]!='.':
            if os.path.isdir(d+os.sep+i):
                parseDir(d+os.sep+i)
            else:
                files.append(d+os.sep+i)
                out('Adding',d+os.sep+i)
parseDir(module)
out('Done, writing module file.')
tar=tarfile.open(name,'w:gz')
for i in range(len(files)):
    out('Writing',files[i])
    tar.add(files[i],moduleinfo['name']+'/'+files[i][len(module)+len(os.sep):].replace(os.sep,'/'),recursive=False)
tar.close()
out('Module created:',name)
