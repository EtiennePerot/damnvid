from setuptools import setup
import os

path2src='./'
versionfile=open(path2src+'version.damnvid','r')
version=versionfile.readline().strip()
versionfile.close()
files=open(path2src+'required-files.txt','r')
data_files=[]
def addFile(dic,f,path=None):
    global path2src
    if path is None:
        path=path2src+f
    if f.find(os.sep)!=-1:
        subfile=f[f.find(os.sep)+1:]
        d=f[0:f.find(os.sep)]
        if not dic.has_key(d):
            dic[d]={}
        dic[d]=addFile(dic[d],subfile,path)
    else:
        dic[f]=path
    return dic
for f in files.readlines():
    curfile=f.strip()
    if curfile and curfile!='DamnVid.py':
        if curfile.find(os.sep)==-1:
            data_files.append(path2src+curfile)
        else:
            data_files.append((curfile[0:curfile.rfind(os.sep)],[path2src+curfile]))
        #data_files=addFile(data_files,curfile)
files.close()
print data_files
setup(
    app=[path2src+'DamnVid.py'],
    data_files=data_files,
    options={
        'py2app':{
            'argv_emulation':True,
            'iconfile': path2src+'img/icon.icns',
            'plist':{
                'CFBundleShortVersionString':version,
                'CFBundleGetInfoString':'DamnVid '+version,
                'CFBundleExecutable':'DamnVid',
                'CFBundleName':'DamnVid',
                'CFBundleIdentifier':'com.googlecode.DamnVid'
            }
        }
    },
    setup_requires=['py2app']
)
