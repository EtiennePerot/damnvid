from distutils.core import setup
import py2exe
import os
import shutil

images=[]
version='0.1'
description='Converts any damn video to any format. Also supports online video downloading and converting.'
for i in os.listdir('img/'):
    if i[-4:].lower()=='.png' or i[-4:].lower()=='.jpg' or i[-4:].lower()=='.gif':
        images.append('img/'+i)
class Target:
    def __init__(self,**kw):
        self.__dict__.update(kw)
        self.version=version
        self.company_name='WindPower'
        self.copyright='',
        self.name='DamnVid'
RT_MANIFEST=24
manifest='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="DamnVid"
    type="win32"
/>
<description>'''+description+'''</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>'''
setup(
    name='DamnVid',
    options={
        'py2exe':{
            'compressed':1,
            'optimize':2,
            'ascii':1,
            'bundle_files':1
        }
    },
    zipfile=None,
    version=version,
    description=description,
    author='WindPower',
    author_email='windypower@gmail.com',
    url='http://code.google.com/p/damnvid/',
    windows=['DamnVid.py'],
    data_files=[
        ('output',['output/!readme.txt']),
        ('temp',['temp/!readme.txt']),
        ('bin',['bin/ffmpeg.exe','bin/SDL.dll']),
        ('img',images),
        ('conf',['conf/!readme.txt','conf/conf.ini','conf/default.ini'])
    ]
)
shutil.copyfile('DamnVid.exe.manifest','dist/DamnVid.exe.manifest')
shutil.copyfile('C:\\Python25\\lib\\site-packages\\wx-2.8-msw-unicode\\wx\\gdiplus.dll','dist/gdiplus.dll')
