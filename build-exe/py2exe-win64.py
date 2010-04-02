# This is just a building script for py2exe.

from distutils.core import setup
import py2exe
import os, sys
import shutil

path2src='../../DamnVid/'
sys.path.append(path2src)
versionfile=open(path2src+'version.damnvid','r')
version=versionfile.readline().strip()
versionfile.close()
description='DamnVid'
files=open(path2src+'required-files.txt','r')
data_files=[]
for f in files.readlines():
    curfile=f.strip()
    if curfile and curfile!='DamnVid.exe':
        if curfile.find(os.sep)==-1:
            data_files.append(path2src+curfile)
        else:
            data_files.append((curfile[0:curfile.rfind(os.sep)],[path2src+curfile]))
files.close()
class Target:
    def __init__(self,**kw):
        self.__dict__.update(kw)
        self.version=version
        self.company_name='Etienne Perot'
        self.copyright='',
        self.name='DamnVid'

setup(
    name='DamnVid',
    options={
        'py2exe':{
            'compressed':0,
            'optimize':2,
            'ascii':1,
            'bundle_files':0
        }
    },
    zipfile=None,
    version=version,
    description=description,
    author='Etienne Perot',
    author_email='windypower@gmail.com',
    url='http://code.google.com/p/damnvid/',
    windows=[
        {
            'script':path2src+'DamnVid.py',
            'icon_resources':[
                (0,path2src+'img/icon.ico')
            ]
        }
    ],
    data_files=data_files
)
shutil.copyfile('C:\\Python25\\lib\\site-packages\\wx-2.8-msw-unicode\\wx\\gdiplus.dll','dist/gdiplus.dll')
shutil.copyfile('C:\\Python25\\lib\\site-packages\\wx-2.8-msw-unicode\\wx\\msvcp71.dll','dist/MSVCP71.dll')
shutil.copyfile('C:\\Python25\\unicows.dll','dist/unicows.dll')
