import os
import sys
import tarfile

args=sys.argv
if len(args)!=2:
    print 'Invalid arguments.'
    print 'Usage: python ./module-package.py ./path-to-modules-folder/module'
    print 'Aborting.'
    exit()
module=args[1]
if not os.path.lexists(module):
    print 'Module not found in filesystem. Aborting.'
    exit()
if not os.path.isdir(module):
    print 'Module is not a folder. Aborting.'
    exit()
print 'Searching for module declaration file...'
foundfile=None
for i in os.listdir(module):
    if i[-8:]=='.damnvid' and not foundfile:
        print 'Found',i
        print 'Searching for module declaration.'
        f=open(module+os.sep+i,'r')
        if f.readline().strip()[0:17].lower()=='#~damnvid-module:':
            print 'Confirmed',i,'as module declaration file.'
            foundfile=module+os.sep+i
        f.close()
if foundfile is None:
    print 'Could not find module declaration file. Aborting.'
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
execfile(foundfile)
if moduleinfo is None:
    print 'Could not find module info within module declaration file. Aborting.'
    exit()
if not moduleinfo.has_key('name') or not moduleinfo.has_key('version'):
    print 'Could not find name/version info in module info. Aborting.'
print 'Module name is',moduleinfo['name'],'version',moduleinfo['version']
print 'Packaging module...'
name='Module-'+moduleinfo['name']+'-'+moduleinfo['version']+'.module.damnvid'
tar=tarfile.open(name,'w:gz')
tar.add(module,moduleinfo['name'])
tar.close()
print 'Module created:',name
