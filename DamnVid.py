# Copyright 2008 Etienne Perot

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Uhm, yeah. I'm not really sure if I'm proud of this source code or not.
# I mean, some parts of the code are awesome, some parts are definitely not. I'm undecided.


import wx # Oh my wx, it's wx.
import wx.animate # wx gif animations, oh my gif!
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin # Mixin for wx.ListrCtrl, to enable autowidth on columns
import os # Filesystem functions.
import re # Regular expressions \o/
import subprocess # Spawn sub-processes (ffmpeg, taskkill)
import time # Sleepin'
import urllib2 # Fetch data from the tubes, encode/decode URLs
import urllib # Sadly required as well, for its urlencode function
import cookielib # Cookie handling. Yum, warm, freshly-baked cookies.
import htmlentitydefs # HTML entities dictionaries
import signal # Process signals
import webbrowser # Open a page in default browser
import tempfile,random # Generate temporary files
import shutil # Shell utilities (copyfile)
import sys # System stuff
import ConfigParser # INI file parsing and writing
import base64 # Base64 encoding/decoding
import gdata.youtube # YouTube API client
import gdata.youtube.service # YouTube service
import xmlrpclib # XML RPC server communication
import BeautifulSoup # Tag soup parsing! From http://www.crummy.com/software/BeautifulSoup/
import unicodedata # Unicode normalization
import hashlib # MD5 hashes
import tarfile # Tar/gz file reading/writing (used for modules)
try:
    import threading as thr # Threads
except ImportError:
    import dummy_threading as thr # Moar threads

# Begin constants
class DamnVid:
    pass
DV=DamnVid() # The only global variable out there. Srsly.
DV.curdir=os.path.dirname(os.path.abspath(sys.argv[0]))+os.sep
versionfile=open(DV.curdir+'version.damnvid','r')
DV.version=versionfile.readline().strip()
DV.argv=sys.argv[1:]
versionfile.close()
del versionfile
DV.cookiejar=cookielib.CookieJar()
DV.urllib2_urlopener=urllib2.build_opener(urllib2.HTTPCookieProcessor(DV.cookiejar))
DV.urllib2_urlopener.addheaders=[('User-agent','DamnVid/'+DV.version)]
urllib2.install_opener(DV.urllib2_urlopener) # All urllib2.urlopen() calls will have the DamnVid user-agent
DV.url='http://code.google.com/p/damnvid/'
DV.url_halp='http://code.google.com/p/damnvid/wiki/Help'
DV.url_update='http://code.google.com/p/damnvid/wiki/CurrentVersion'
DV.url_download='http://code.google.com/p/damnvid/downloads/'
DV.gui_ok=False
DV.icon=None # This will be defined when DamnMainFrame is initialized
DV.my_videos_path=''
DV.appdata_path=''
DV.os=os.name
if DV.os=='posix' and sys.platform=='darwin':
    DV.os='mac'
    DV.border_padding=12
    DV.control_hgap=10
    DV.control_vgap=4
    DV.scroll_factor=2
else:
    DV.border_padding=8
    DV.control_hgap=8
    DV.control_vgap=4
    DV.scroll_factor=3
if DV.os=='nt':
    import win32process
    # Need to determine the location of the "My Videos" and "Application Data" folder.
    import ctypes
    from ctypes import wintypes
    DV.my_videos_path=ctypes.create_string_buffer(wintypes.MAX_PATH)
    DV.appdata_path=ctypes.create_string_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathA(None,0xE,None,0,DV.my_videos_path)
    ctypes.windll.shell32.SHGetFolderPathA(None,0x1A,None,0,DV.appdata_path)
    DV.my_videos_path=str(DV.my_videos_path.value)
    DV.appdata_path=str(DV.appdata_path.value)
    del ctypes
    del wintypes
    # Do not delete win32process, it is used in the DamnSpawner class.
elif DV.os=='mac':
    DV.my_videos_path=os.path.expanduser('~'+os.sep+'Movies')
else:
    DV.my_videos_path=os.path.expanduser('~'+os.sep+'Videos')

DV.conf_file_location={
    'nt':DV.appdata_path+os.sep+'DamnVid',
    'posix':'~'+os.sep+'.damnvid',
    'mac':'~'+os.sep+'Library'+os.sep+'Preferences'+os.sep+'DamnVid'
}
if DV.os=='posix' or DV.os=='mac':
    DV.conf_file_location=os.path.expanduser(DV.conf_file_location[DV.os])
else:
    DV.conf_file_location=DV.conf_file_location[DV.os]
DV.conf_file_directory=DV.conf_file_location+os.sep
DV.conf_file=DV.conf_file_directory+'damnvid.ini'
DV.log_file=DV.conf_file_directory+'damnvid.log'
if os.path.lexists(DV.log_file):
    os.remove(DV.log_file)
class DamnLog:
    def __init__(self):
        self.stream=open(DV.log_file,'w')
        self.time=0
        self.stream.write(self.getPrefix()+u'Log opened.')
    def getPrefix(self):
        t=int(time.time())
        if self.time!=t:
            self.time=t
            return u'['+unicode(time.strftime('%H:%M:%S'))+u'] '
        return u''
    def log(self,message):
        s=u'\r\n'+self.getPrefix()+unicode(message.strip())
        print s
        return self.stream.write(s)
    def close(self):
        self.log('Closing log.')
        self.stream.close()
DV.log=DamnLog()
def Damnlog(*args):
    s=[]
    for i in args:
        s.append(unicode(i))
    return DV.log.log(' '.join(s))
Damnlog('DamnVid started')
DV.first_run=False
DV.updated=False
if not os.path.lexists(DV.conf_file):
    if not os.path.lexists(os.path.dirname(DV.conf_file)):
        os.makedirs(os.path.dirname(DV.conf_file))
    shutil.copyfile(DV.curdir+'conf'+os.sep+'conf.ini',DV.conf_file)
    lastversion=open(DV.conf_file_directory+'lastversion.damnvid','w')
    lastversion.write(DV.version)
    lastversion.close()
    del lastversion
    DV.first_run=True
else:
    if os.path.lexists(DV.conf_file_directory+'lastversion.damnvid'):
        lastversion=open(DV.conf_file_directory+'lastversion.damnvid','r')
        version=lastversion.readline().strip()
        lastversion.close()
        DV.updated=version!=DV.version
        del version
    else:
        DV.updated=True
        lastversion=open(DV.conf_file_directory+'lastversion.damnvid','w')
        lastversion.write(DV.version)
        lastversion.close()
    del lastversion
DV.images_path=DV.curdir+'img/'.replace('/',os.sep)
DV.bin_path=DV.curdir+'bin/'.replace('/',os.sep)
DV.tmp_path=tempfile.gettempdir()
if DV.tmp_path[-1]!=os.sep:
    DV.tmp_path+=os.sep
DV.tmp_path+='damnvid-'
DV.file_ext={
    'avi':'avi',
    'flv':'flv',
    'mpeg1video':'mpg',
    'mpeg2video':'mpg',
    'mpegts':'mpg',
    'mp4':'mp4',
    'ipod':'mp4',
    'psp':'mp4',
    'rm':'rm',
    'matroska':'mkv',
    'ogg':'ogg',
    'vob':'vob',
    '3gp':'3gp',
    '3g2':'3g2',
    'mp3':'mp3',
    'mp2':'mp2'
}
DV.file_ext_by_codec={
    'rv10':'rm',
    'rv20':'rm',
    'flv':'flv',
    'theora':'ogg',
    'wmv1':'wmv',
    'wmv2':'wmv',
    'ac3':'ac3',
    'vorbis':'ogg',
    'wmav1':'wma',
    'wmav2':'wma'
} # Just in case the format isn't defined, fall back to DV.file_ext_by_codec. Otherwise, fall back to .avi (this is why only codecs that shouldn't get a .avi extension are listed here).
DV.codec_advanced_cl={
    'mpeg4':[('g','300'),('cmp','2'),('subcmp','2'),('trellis','2'),'+4mv'],
    'libx264':[('coder','1'),'+loop',('cmp','+chroma'),('partitions','+parti4x4+partp8x8+partb8x8'),('g','250'),('subq','6'),('me_range','16'),('keyint_min','25'),('sc_threshold','40'),('i_qfactor','0.71'),('b_strategy','1')]
}
DV.youtube_service=gdata.youtube.service.YouTubeService()
Damnlog('Init underway, starting to declare fancier stuff.')
class DamnIconList(wx.ImageList): # An imagelist with dictionary-like association, not stupid IDs, and graceful failure. Can also be initialized with delay.
    def __init__(self,width=16,height=16,mask=True,initialCount=0,fail=None,initNow=False):
        self.list={}
        self.args=(width,height,mask,initialCount)
        self.init=False
        self.fail=fail
        if initNow:
            self.initWX()
    def initWX(self):
        wx.ImageList.__init__(self,self.args[0],self.args[1],self.args[2],self.args[3])
        self.init=True
        self.resetList(self.list)
    def add(self,bitmap,handle=None):
        Damnlog('Adding',bitmap,'to icon list, with handle',handle)
        while handle is None or handle in self.list.keys():
            Damnlog('!Icon conflict found with handle',handle)
            handle=hashlib.md5(str(random.random())+str(random.random())).hexdigest()
        if self.init:
            if type(bitmap) is type(''):
                bitmap=wx.Bitmap(bitmap)
            self.list[handle]=self.Add(bitmap)
        else:
            self.list[handle]=bitmap
        return handle
    def get(self,handle):
        if not self.init:
            return
        if type(handle) is type(''):
            if handle in self.list.keys():
                handle=self.list[handle]
            else:
                handle=self.blankid
        return handle
    def getBitmap(self,handle):
        return self.GetBitmap(self.get(handle))
    def resetList(self,items={}):
        self.list={}
        if self.init:
            self.RemoveAll()
            if self.fail is None:
                blank=wx.EmptyBitmap(width,height)
            else:
                blank=wx.Bitmap(self.fail)
            self.blankid=self.Add(blank)
        for i in items.keys():
            self.add(items[i],i)
DV.listicons=DamnIconList(16,16,fail=DV.images_path+'video.png')
def DamnGetListIcon(icon):
    return DV.listicons.get(icon)
def DamnInstallModule(module):
    Damnlog('Attempting to install module',module)
    if not os.path.lexists(module):
        return 'nofile'
    if not tarfile.is_tarfile(module):
        return 'nomodule'
    mod=tarfile.open(module,'r')
    files=mod.getnames()
    if not len(files):
        return 'nomodule'
    if files[0].find('/') in (-1,0):
        return 'nomodule'
    prefix=files[0][0:files[0].find('/')+1]
    for i in files:
        if i.find('/') in (-1,0):
            return 'nomodule'
        if i[0:i.find('/')+1]!=prefix:
            return 'nomodule'
    if os.path.lexists(DV.modules_path+prefix):
        if os.path.isdir(DV.modules_path+prefix):
            shutil.rmtree(DV.modules_path+prefix)
        else:
            os.remove(DV.modules_path+prefix)
    mod.extractall(DV.modules_path)
    try:
        DV.prefs.rems('damnvid-module-'+prefix[0:-1]) # Reset module preferences when installing it.
        DV.prefs.save()
    except:
        Damnlog('Resetting module preferences for module',module,'(probably not installed or left default before)')
    DamnLoadModule(DV.modules_path+prefix[0:-1])
    Damnlog('Success installing module',module)
    return 'success'
def DamnIterModules(keys=True): # Lawl, this spells "DamnIt"
    mods=DV.modules.keys()
    mods.sort()
    if keys:
        return mods
    ret=[]
    for i in mods:
        ret.append(DV.modules[i])
    return ret
def DamnRegisterModule(module):
    Damnlog('Attempting to register module',module)
    DV.modules[module['name']]=module
    DV.modulesstorage[module['name']]={}
    if module.has_key('register'):
        module['class'].register={}
        if module['register'].has_key('listicons'):
            module['class'].register['listicons']={}
            for icon in module['register']['listicons'].iterkeys():
                DV.listicons.add(DV.modules_path+module['name']+os.sep+module['register']['listicons'][icon],icon)
    if module.has_key('preferences'):
        for pref in module['preferences'].iterkeys():
            DV.preferences['damnvid-module-'+module['name']+':'+pref]=module['preferences'][pref]
            DV.defaultprefs['damnvid-module-'+module['name']+':'+pref]=module['preferences'][pref]['default']
            if module['preferences'][pref]['kind']=='dir':
                DV.path_prefs.append('damnvid-module-'+module['name']+':'+pref)
        if module.has_key('preferences_order'):
            DV.preference_order['damnvid-module-'+module['name']]=module['preferences_order']
        else:
            DV.preference_order['damnvid-module-'+module['name']]=module['preferences'].keys()
    Damnlog('Module registered:',module)
def DamnGetAlternateModule(uri):
    Damnlog('Got request to get new module for URI:',uri)
    urlgrabber=DamnVideoLoader(None,[uri],feedback=False)
    urlgrabber.start()
    time.sleep(.1)
    while not urlgrabber.done:
        time.sleep(.05)
    res=urlgrabber.result
    urlgrabber.done=False
    Damnlog('Module found, returning',res['module'])
    return res['module']
class DamnVideoModule:
    def __init__(self,uri):
        self.name='generic'
        self.uri=uri
        self.link=None
        self.id=None
        self.valid=None
        self.title=None
        self.ticket=None
        self.ticketdate=0
        self.regex={
            'title':DV.generic_title_extract
        }
    def isUp(self):
        return True
    def validURI(self):
        return not not self.valid
    def getLink(self):
        return self.link
    def getURI(self):
        return self.uri
    def getID(self):
        return self.id
    def getStorage(self):
        return DV.modulesstorage[self.name]
    def getTitle(self):
        if self.title is None:
            html=urllib2.urlopen(self.link)
            total=''
            for i in html:
                total+=i
            res=self.regex['title'].search(total)
            if res:
                self.title=DamnHtmlEntities(res.group(1))
        if self.title is not None:
            return self.title
        return u'Unknown title'
    def getIcon(self):
        return DamnGetListIcon(self.name)
    def pref(self,pref,value=None):
        if value is None:
            return DV.prefs.getm(self.name,pref)
        return DV.prefs.setm(self.name,pref,value)
    def newTicket(self,ticket):
        self.ticket=ticket
        self.ticketdate=time.time()
    def getProfile(self):
        return self.pref('profile')
    def getOutdir(self):
        return self.pref('outdir')
    def renewTicket(self):
        if self.ticket is None:
            self.newTicket(self.uri)
    def getDownload(self):
        self.renewTicket()
        return self.ticket
    def getFFmpegArgs(self):
        return []
    def getDownloadGetter(self):
        return self.getDownload
    def addVid(self,parent):
        parent.addValid(self.getVidObject())
    def getVidObject(self):
        obj={'name':self.getTitle(),'profile':self.getProfile(),'profilemodified':False,'fromfile':self.getTitle(),'dirname':self.getLink(),'uri':self.getID(),'status':'Pending.','icon':self.getIcon(),'module':self,'downloadgetter':self.getDownloadGetter()}
        Damnlog('Module',self.name,'returning video object:',obj)
        return obj
class DamnModuleUpdateCheck(thr.Thread):
    def __init__(self,parent,modules,byevent=True):
        Damnlog('Spawned module update checker for modules',modules,'by event:',byevent)
        self.parent=parent
        if type(modules) is not type([]):
            modules=[modules]
        self.modules=modules
        self.done={}
        self.downloaded=[]
        self.byevent=byevent
        thr.Thread.__init__(self)
    def postEvent(self,module,result):
        info={'module':module,'result':result}
        Damnlog('Update checker sending event:',info,'by event:',self.byevent)
        if self.byevent:
            wx.PostEvent(self.parent,DamnLoadingEvent(DV.evt_loading,-1,info))
        else:
            self.parent.onLoad(info)
    def run(self):
        for module in self.modules:
            if not module['about'].has_key('url'):
                self.postEvent(module,'cannot')
            elif module['about']['url'] not in self.downloaded:
                self.downloaded.append(module['about']['url'])
                http=urllib2.urlopen(module['about']['url'])
                checkingfor=[module]
                for module2 in self.modules:
                    if module2['about'].has_key('url'):
                        if module2['about']['url']==module['about']['url'] and module2 not in checkingfor:
                            checkingfor.append(module2)
                match=False
                html=''
                for i in http:
                    html+=i
                for module2 in checkingfor:
                    res=re.search('<tt>'+re.escape(module2['name'])+'</tt>.*?Latest\s+version\s*:\s*<tt>([^<>]+)</tt>.*?Available\s+at\s*:\s*<a href="([^"]+)"',html,re.IGNORECASE)
                    if not res:
                        self.postEvent(module2,'error')
                    else:
                        vers=DamnHtmlEntities(res.group(1))
                        if vers!=unicode(module2['version']):
                            url=DamnHtmlEntities(res.group(2)).strip()
                            if not REGEX_HTTP_GENERIC.match(url):
                                self.postEvent(module2,'error')
                            else:
                                try:
                                    http=urllib2.urlopen(url)
                                    tmpname=DamnTempFile()
                                    tmp=open(tmpname,'wb')
                                    for i in http:
                                        tmp.write(i)
                                    tmp.close()
                                    http.close()
                                    DamnInstallModule(tmpname)
                                    self.postEvent(module2,(vers,url))
                                except:
                                    self.postEvent(module2,'error')
                        else:
                            self.postEvent(module2,'uptodate')
class DamnVidUpdater(thr.Thread):
    def __init__(self,parent,verbose=False,main=True,modules=True):
        Damnlog('Spawned main updater thread')
        self.parent=parent
        self.todo={'main':main,'modules':modules}
        self.info={'main':None,'modules':{},'verbose':verbose}
        thr.Thread.__init__(self)
    def postEvent(self):
        Damnlog('Main updated thread sending event',self.info)
        wx.PostEvent(self.parent,DamnLoadingEvent(DV.evt_loading,-1,{'updateinfo':self.info}))
    def onLoad(self,info):
        if not info.has_key('module'):
            return
        self.info['modules'][info['module']['name']]=info['result']
    def run(self):
        if self.todo['main']:
            regex=re.compile('<tt>([^<>]+)</tt>',re.IGNORECASE)
            try:
                html=urllib2.urlopen(DV.url_update)
                for i in html:
                    if regex.search(i):
                        self.info['main']=regex.search(i).group(1).strip()
            except:
                pass
        if self.todo['modules']:
            updater=DamnModuleUpdateCheck(self,DamnIterModules(False),False)
            updater.run() # Yes, run(), not start(), this way we're waiting for it to complete.
        self.postEvent()
def DamnLoadModule(module):
    for i in os.listdir(module):
        if not os.path.isdir(module+os.sep+i) and i[-8:]=='.damnvid':
            execfile(module+os.sep+i)
def DamnLoadConfig(forcemodules=False):
    Damnlog('Loading config.')
    DV.preferences=None
    try:
        execfile(DV.curdir+'conf'+os.sep+'preferences.damnvid') # Load preferences
    except:
        pass # Someone's been messing around with the conf.py file?
    DV.path_prefs=[]
    DV.defaultprefs={
    }
    for i in DV.preferences.iterkeys():
        if DV.preferences[i].has_key('default'):
            DV.defaultprefs[i]=DV.preferences[i]['default']
        else:
            DV.defaultprefs[i]=None
        if DV.preferences[i]['kind']=='dir':
            DV.path_prefs.append(i)
    DV.prefs=None # Will be loaded later
    # Load modules
    Damnlog('Loading modules.')
    DV.modules_path=DV.conf_file_directory+'modules'+os.sep
    if not os.path.lexists(DV.modules_path):
        os.makedirs(DV.modules_path)
    DV.modules={}
    DV.modulesstorage={}
    DV.generic_title_extract=re.compile('<title>\s*([^<>]+?)\s*</title>',re.IGNORECASE)
    DV.listicons.resetList({
        'damnvid':DV.images_path+'video.png',
        'generic':DV.images_path+'online.png'
    })
    if forcemodules:# or True: # Fixme: DEBUG ONLY
        Damnlog('forcemodules is on; resetting modules.')
        shutil.rmtree(DV.modules_path)
        os.makedirs(DV.modules_path)
        """if True: # Fixme: DEBUG ONLY; rebuilds all modules
            for i in os.listdir('./'):
                if i[-15:]=='.module.damnvid':
                    os.remove(i)
            for i in os.listdir('./modules/'):
                if i[-15:]=='.module.damnvid':
                    os.remove('modules/'+i)
            for i in os.listdir('modules'):
                if os.path.isdir('modules/'+i) and i.find('svn')==-1:
                    print 'Building module '+i
                    p=os.popen('python build-any/module-package.py modules/'+i)
                    try:
                        p.close()
                    except:
                        pass
            for i in os.listdir('./'):
                if i[-15:]=='.module.damnvid':
                    os.rename(i,'modules/'+i)"""
        for i in os.listdir(DV.curdir+'modules'):
            if i[-15:]=='.module.damnvid':
                print 'Installing',i
                print DamnInstallModule(DV.curdir+'modules'+os.sep+i)
    for i in os.listdir(DV.modules_path):
        if os.path.isdir(DV.modules_path+i):
            DamnLoadModule(DV.modules_path+i)
    # End load modules
Damnlog('Loading initial config and modules.')
DamnLoadConfig(DV.first_run or DV.updated)
# Begin ID constants
ID_MENU_EXIT=wx.ID_EXIT
ID_MENU_ADD_FILE=102
ID_MENU_ADD_URL=103
ID_MENU_GO=104
ID_MENU_PREFERENCES=wx.ID_PREFERENCES
ID_MENU_OUTDIR=106
ID_MENU_HALP=wx.ID_HELP
ID_MENU_UPDATE=108
ID_MENU_ABOUT=wx.ID_ABOUT
ID_COL_VIDNAME=0
ID_COL_VIDPROFILE=1
ID_COL_VIDSTAT=2
ID_COL_VIDPATH=3
# Begin regex constants
REGEX_PATH_MULTI_SEPARATOR_CHECK=re.compile('/+')
REGEX_FFMPEG_DURATION_EXTRACT=re.compile('^\\s*Duration:\\s*(\\d+):(\\d\\d):([.\\d]+)',re.IGNORECASE)
REGEX_FFMPEG_TIME_EXTRACT=re.compile('time=([.\\d]+)',re.IGNORECASE)
REGEX_HTTP_GENERIC=re.compile('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}#\w]*)?$',re.IGNORECASE)
REGEX_HTTP_GENERIC_LOOSE=re.compile('https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}\w]*)?',re.IGNORECASE)
REGEX_HTTP_EXTRACT_FILENAME=re.compile('^.*/|[?#].*$')
REGEX_HTTP_EXTRACT_DIRNAME=re.compile('^([^?#]*)/.*?$')
REGEX_FILE_CLEANUP_FILENAME=re.compile('[\\/:?"|*<>]+')
REGEX_URI_EXTENSION_EXTRACT=re.compile('^(?:[^?|<>]+[/\\\\])?[^/\\\\|?<>#]+\\.(\\w{1,3})(?:$|[^/\\\\\\w].*?$)')
REGEX_HTTP_GENERIC_TITLE_EXTRACT=re.compile('<title>([^<>]+)</title>',re.IGNORECASE)
REGEX_THOUSAND_SEPARATORS=re.compile('(?<=[0-9])(?=(?:[0-9]{3})+(?![0-9]))')
# End regex constants
# End constants
Damnlog('End init, begin declarations.')
def DamnSpawner(cmd,shell=False,stderr=None,stdout=None,stdin=None,cwd=None):
    finalcmd=[]
    oldcmd=cmd
    while cmd:
        if cmd[0]=='"':
            arg=cmd[1:cmd.find('"',1)]
            cmd=cmd[2+len(arg):]
        else:
            if cmd.find(' ')!=-1:
                arg=cmd[0:cmd.find(' ')]
            else:
                arg=cmd
            cmd=cmd[len(arg):]
        cmd=cmd.strip()
        finalcmd.append(arg)
    exe=finalcmd[0]
    if cwd==None:
        cwd=os.getcwd()
    if DV.os=='nt':
        Damnlog('Spawning subprocess',oldcmd)
        return subprocess.Popen(oldcmd,shell=shell,creationflags=win32process.CREATE_NO_WINDOW,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE,cwd=cwd,executable=exe,bufsize=128) # Yes, ALL std's must be PIPEd, otherwise it doesn't work on win32 (see http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions)
    else:
        Damnlog('Spawning subprocess',finalcmd)
        return subprocess.Popen(finalcmd,shell=shell,stderr=stderr,stdout=stdout,stdin=stdin,cwd=cwd,executable=exe,bufsize=128) # Must specify bufsize, or it might be too big to actually get any data (happened to me on Ubuntu)
def DamnURLPicker(urls,urlonly=False):
    tried=[]
    Damnlog('URL picker summoned. URLs:',urls)
    for i in urls:
        if i not in tried:
            tried.append(i)
            request=urllib2.Request(i)
            try:
                pipe=urllib2.urlopen(request)
                if urlonly:
                    try:
                        pipe.close()
                    except:
                        pass
                    return i
                return pipe
            except IOError, err:
                if not hasattr(err,'reason') and not hasattr(err,'code'):
                    return None
                pass
    return None
def DamnURLPickerBySize(urls,array=False):
    Damnlog('URL picker by size summoned. URLs:',urls)
    tried=[]
    maxlen=[]
    maxurl=[]
    for i in urls:
        if i not in tried:
            tried.append(i)
            try:
                handle=urllib2.urlopen(i)
                size=int(handle.info()['Content-Length'])
                handle.close()
                maxlen.append(size)
                maxurl.append(i)
            except:
                pass
    if not len(maxurl):
        return urls[0]
    maxlen2=maxlen
    maxlen2.sort()
    maxlen2.reverse()
    assoc=[]
    finalurls=[]
    for i in maxlen2:
        for f in range(len(maxlen)):
            if i==maxlen[f] and f not in assoc:
                assoc.append(f)
                finalurls.append(maxurl[f])
    for i in tried:
        if i not in finalurls:
            finalurls.append(i)
    if array:
        return finalurls
    return finalurls[0]
def DamnTempFile():
    name=DV.tmp_path+str(random.random())+'.tmp'
    while os.path.lexists(name):
        name=DV.tmp_path+str(random.random())+'.tmp'
    Damnlog('Temp file requested. Return:',name)
    return name
def DamnFriendlyDir(d):
    if DV.os=='mac':
        myvids='Movies'
    else:
        myvids='My Videos'
    d=d.replace('?DAMNVID_MY_VIDEOS?',myvids)
    d=os.path.expanduser(d).replace(DV.my_videos_path,myvids).replace('/',os.sep).replace('\\',os.sep)
    while d[-1:]==os.sep:
        d=d[0:-1]
    return d
def DamnHtmlEntities(html):
    return unicode(BeautifulSoup.BeautifulStoneSoup(html,convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)).replace(u'&amp;',u'&') # Because BeautifulSoup, as good as it is, puts &amp;badentity where &badentitity; are. Gotta convert that back.
DV.evt_progress=wx.NewEventType()
DV.evt_prog=wx.PyEventBinder(DV.evt_progress,1)
class DamnProgressEvent(wx.PyCommandEvent):
    def __init__(self,eventtype,eventid,eventinfo):
        wx.PyCommandEvent.__init__(self,eventtype,eventid)
        self.info=eventinfo
    def GetInfo(self):
        return self.info
DV.evt_loading=wx.NewEventType()
DV.evt_load=wx.PyEventBinder(DV.evt_loading,1)
class DamnLoadingEvent(wx.PyCommandEvent):
    def __init__(self,eventtype,eventid,eventinfo):
        wx.PyCommandEvent.__init__(self,eventtype,eventid)
        self.info=eventinfo
    def GetInfo(self):
        return self.info
class DamnDropHandler(wx.FileDropTarget): # Handles files dropped on the ListCtrl
    def __init__(self,parent):
        wx.FileDropTarget.__init__(self)
        self.parent=parent
    def OnDropFiles(self,x,y,filenames):
        self.parent.addVid(filenames)
class DamnCurry:
    # From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549
    def __init__(self,func,*args,**kwargs):
        self.func=func
        self.pending=args[:]
        self.kwargs=kwargs
    def __call__(self,*args,**kwargs):
        if kwargs and self.kwargs:
            kw=self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw=kwargs or self.kwargs
        return self.func(*(self.pending+args),**kw)
class DamnListContextMenu(wx.Menu): # Context menu when right-clicking on the DamnList
    def __init__(self,parent):
        wx.Menu.__init__(self)
        self.parent=parent
        self.items=self.parent.getAllSelectedItems()
        if len(self.items): # If there's at least one item selected
            rename=wx.MenuItem(self,-1,'Rename')
            self.AppendItem(rename)
            if len(self.items)!=1:
                rename.Enable(False)
            else:
                if self.items[0]==self.parent.parent.converting:
                    rename.Enable(False)
            self.Bind(wx.EVT_MENU,self.parent.parent.onRename,rename)
            moveup=wx.MenuItem(self,-1,'Move up')
            self.AppendItem(moveup)
            moveup.Enable(self.items[0]>0)
            self.Bind(wx.EVT_MENU,self.parent.parent.onMoveUp,moveup)
            movedown=wx.MenuItem(self,-1,'Move down')
            self.AppendItem(movedown)
            movedown.Enable(self.items[-1]<self.parent.GetItemCount()-1)
            self.Bind(wx.EVT_MENU,self.parent.parent.onMoveDown,movedown)
            stop=wx.MenuItem(self,-1,'Stop')
            self.AppendItem(stop)
            stop.Enable(self.parent.parent.converting in self.items)
            self.Bind(wx.EVT_MENU,self.parent.parent.onStop,stop)
            remove=wx.MenuItem(self,-1,'Remove from list')
            self.AppendItem(remove)
            remove.Enable(self.parent.parent.converting not in self.items)
            self.Bind(wx.EVT_MENU,self.parent.parent.onDelSelection,remove)
            if self.parent.parent.converting not in self.items:
                profile=wx.Menu()
                uniprofile=int(self.parent.parent.meta[self.parent.parent.videos[self.items[0]]]['profile'])
                for i in self.items:
                    if int(self.parent.parent.meta[self.parent.parent.videos[i]]['profile'])!=uniprofile:
                        uniprofile=-2
                for i in range(-1,DV.prefs.profiles):
                    if uniprofile!=-2:
                        prof=wx.MenuItem(self,-1,DV.prefs.getp(i,'name'),kind=wx.ITEM_RADIO)
                        profile.AppendItem(prof) # Item has to be appended before being checked, otherwise error. Annoying code duplication.
                        prof.Check(i==uniprofile)
                    else:
                        prof=wx.MenuItem(self,-1,DV.prefs.getp(i,'name'))
                        profile.AppendItem(prof)
                    self.Bind(wx.EVT_MENU,DamnCurry(self.parent.parent.onChangeProfile,i),prof)    # Of course, on one platform it's self.Bind...
                    profile.Bind(wx.EVT_MENU,DamnCurry(self.parent.parent.onChangeProfile,i),prof) # ... and on the other it's profile.Bind. *sigh*
                self.AppendMenu(-1,'Encoding profile',profile)
            else:
                profile=wx.MenuItem(self,-1,'Encoding profile')
                self.AppendItem(profile)
                profile.Enable(False)
        else: # Otherwise, display a different context menu
            addfile=wx.MenuItem(self,-1,'Add Files')
            self.AppendItem(addfile)
            self.Bind(wx.EVT_MENU,self.parent.parent.onAddFile,addfile)
            addurl=wx.MenuItem(self,-1,'Add URL')
            self.AppendItem(addurl)
            self.Bind(wx.EVT_MENU,self.parent.parent.onAddURL,addurl)
class DamnHyperlink(wx.HyperlinkCtrl):
    def __init__(self,parent,id,label,url):
        wx.HyperlinkCtrl.__init__(self,parent,id,label,url)
class DamnList(wx.ListCtrl,ListCtrlAutoWidthMixin): # The ListCtrl, which inherits from the Mixin
    def __init__(self,parent,window):
        wx.ListCtrl.__init__(self,parent,-1,style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        self.parent=window # "parent" is the panel
    def onRightClick(self,event):
        p=self.HitTest(event.GetPosition())
        if p[0]!=-1:
            if not self.IsSelected(p[0]):
                self.clearAllSelectedItems()
                self.Select(p[0],on=1) # Select pointed item
        else:
            self.clearAllSelectedItems()
        self.PopupMenu(DamnListContextMenu(self),event.GetPosition())
    def getAllSelectedItems(self):
        items=[]
        i=self.GetFirstSelected()
        while i!=-1:
            items.append(i)
            i=self.GetNextSelected(i)
        return items
    def clearAllSelectedItems(self):
        for i in self.getAllSelectedItems():
            self.Select(i,on=0)
    def invertItems(self,i1,i2):
        for i in range(self.GetColumnCount()):
            tmp=[self.GetItem(i1,i).GetText(),self.GetItem(i1,i).GetImage()]
            self.SetStringItem(i1,i,self.GetItem(i2,i).GetText(),self.GetItem(i2,i).GetImage())
            self.SetStringItem(i2,i,tmp[0],tmp[1])
class DamnAddURLDialog(wx.Dialog):
    def __init__(self,parent,default):
        self.parent=parent
        wx.Dialog.__init__(self,parent,-1,'Add videos by URL...')
        absolutetopsizer=wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(absolutetopsizer)
        innertopsizer=wx.BoxSizer(wx.HORIZONTAL)
        innertopsizer2=wx.BoxSizer(wx.VERTICAL)
        self.toppanel=wx.Panel(self,-1)
        absolutetopsizer.Add(self.toppanel,1,wx.EXPAND)
        self.toppanel.SetSizer(innertopsizer)
        topsizer=wx.BoxSizer(wx.VERTICAL)
        innertopsizer.Add((DV.border_padding,0))
        innertopsizer.Add(innertopsizer2,1,wx.EXPAND)
        innertopsizer.Add((DV.border_padding,0))
        innertopsizer2.Add((0,DV.border_padding))
        innertopsizer2.Add(topsizer,1,wx.EXPAND)
        innertopsizer2.Add((0,DV.border_padding))
        # Finished paddings and stuff, now for the actual dialog construction
        topsizer.Add(wx.StaticText(self.toppanel,-1,'Enter the URL of the video you wish to download.'))
        topsizer.Add((0,DV.control_vgap))
        urlboxsizer=wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(urlboxsizer,0,wx.EXPAND)
        urllabel=wx.StaticText(self.toppanel,-1,'URL:')
        urlboxsizer.Add(urllabel,0,wx.ALIGN_CENTER_VERTICAL)
        urlboxsizer.Add((DV.control_hgap,0))
        self.urlbox=wx.TextCtrl(self.toppanel,-1,default,style=wx.TE_PROCESS_ENTER)
        urlboxsizer.Add(self.urlbox,1,wx.EXPAND)
        self.urlbox.Bind(wx.EVT_TEXT_ENTER,self.onAdd)
        self.urlbox.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
        urlboxsizer.Add((DV.control_hgap,0))
        self.addButton=wx.Button(self.toppanel,-1,'+')
        urlboxsizer.Add(self.addButton,0)
        btnheight=self.addButton.GetSizeTuple()[1]
        self.addButton.SetMinSize((btnheight,btnheight)) # Makes the button have a 1:1 aspect ratio
        self.addButton.Bind(wx.EVT_BUTTON,self.onAdd)
        topsizer.Add((0,DV.control_vgap))
        autoconvertchecksizer=wx.BoxSizer(wx.HORIZONTAL)
        self.autoconvertcheck=wx.CheckBox(self.toppanel,-1,'Automatically download and convert right away')
        self.autoconvertcheck.SetValue(DV.prefs.get('autoconvert')=='True')
        self.autoconvertcheck.Bind(wx.EVT_CHECKBOX,self.onAutoconvertCheck)
        autoconvertchecksizer.Add((DV.control_hgap+urllabel.GetSizeTuple()[0],0))
        autoconvertchecksizer.Add(self.autoconvertcheck)
        topsizer.Add(autoconvertchecksizer,0,wx.EXPAND)
        topsizer.Add((0,DV.control_vgap))
        topsizer.Add(wx.StaticLine(self.toppanel,-1,style=wx.HORIZONTAL),0,wx.EXPAND)
        topsizer.Add((0,DV.control_vgap))
        # Start building the bottom part, put sizers in place...
        bottomhorizontalsizer=wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(bottomhorizontalsizer,1,wx.EXPAND)
        bottomleftsizer=wx.BoxSizer(wx.VERTICAL)
        bottomhorizontalsizer.Add(bottomleftsizer,1,wx.EXPAND|wx.ALIGN_TOP)
        bottomhorizontalsizer.Add((DV.control_hgap,0))
        bottomhorizontalsizer.Add(wx.StaticLine(self.toppanel,-1,style=wx.VERTICAL),0,wx.EXPAND|wx.ALIGN_TOP)
        bottomhorizontalsizer.Add((DV.control_hgap,0))
        bottomrightsizer=wx.BoxSizer(wx.VERTICAL)
        bottomhorizontalsizer.Add(bottomrightsizer,1,wx.EXPAND|wx.ALIGN_TOP)
        # Now start building the bottom-left part
        bottomleftsizer.Add(wx.StaticText(self.toppanel,-1,'Go ahead, add some videos!'))
        bottomleftsizer.Add((0,DV.control_vgap))
        bottomleftsizer.Add(wx.StaticText(self.toppanel,-1,'The following sites are suported:'))
        scrollinglist=wx.ScrolledWindow(self.toppanel,-1)
        scrollinglistsizer=wx.BoxSizer(wx.VERTICAL)
        scrollinglist.SetSizer(scrollinglistsizer)
        bottomleftsizer.Add(scrollinglist,1,wx.EXPAND)
        for i in DamnIterModules(False):
            if i.has_key('sites'):
                for site in i['sites']:
                    scrollinglistsizer.Add((0,DV.control_vgap))
                    sitesizer=wx.BoxSizer(wx.HORIZONTAL)
                    scrollinglistsizer.Add(sitesizer)
                    sitesizer.Add(wx.StaticBitmap(scrollinglist,-1,wx.Bitmap(DV.modules_path+i['name']+os.sep+site['icon'])),0,wx.ALIGN_CENTER_VERTICAL)
                    sitesizer.Add((DV.control_hgap,0))
                    sitesizer.Add(DamnHyperlink(scrollinglist,-1,site['title'],site['url']),0,wx.ALIGN_CENTER_VERTICAL)
        scrollinglist.SetMinSize((-1,220))
        scrollinglist.SetScrollbars(0,DV.control_vgap*DV.scroll_factor,0,0)
        # Now start building the bottom-right part
        self.monitorcheck=wx.CheckBox(self.toppanel,-1,'Monitor clipboard for new URLs')
        self.monitorcheck.Bind(wx.EVT_CHECKBOX,self.onMonitorCheck)
        self.monitorcheck.SetValue(DV.prefs.get('clipboard')=='True')
        bottomrightsizer.Add(self.monitorcheck)
        bottomrightsizer.Add((0,DV.control_vgap))
        self.monitorlabel=wx.StaticText(self.toppanel,-1,'')
        bottomrightsizer.Add(self.monitorlabel)
        bottomrightsizer.Add((0,DV.control_vgap))
        self.monitorlabel2=wx.StaticText(self.toppanel,-1,'')
        bottomrightsizer.Add(self.monitorlabel2)
        self.onMonitorCheck()
        bottomrightsizer.Add((0,DV.control_vgap))
        self.videolist=DamnList(self.toppanel,self)
        il=wx.ImageList(16,16,True)
        for i in range(DV.listicons.GetImageCount()):
            il.Add(DV.listicons.GetBitmap(i))
        self.videolist.AssignImageList(il,wx.IMAGE_LIST_SMALL)
        bottomrightsizer.Add(self.videolist,1,wx.EXPAND)
        self.videocolumn=self.videolist.InsertColumn(ID_COL_VIDNAME,'Videos')
        # We're done! Final touches...
        self.videos=[]
        self.SetClientSize(self.toppanel.GetBestSize())
        self.Center()
        self.Bind(wx.EVT_KEY_DOWN,self.onKeyDown,self.toppanel)
        self.Bind(wx.EVT_CLOSE,self.onClose)
    def onAdd(self,event=None,val=None):
        if val is None:
            val=self.urlbox.GetValue()
            self.urlbox.SetValue('')
        message=None
        if not val:
            message=('No URL entered','You must enter a URL!')
        elif not self.parent.validURI(val):
            message=('Invalid URL','This is not a valid URL!')
        if message is not None:
            dlg=wx.MessageDialog(None,message[1],message[0],wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.videolist.InsertStringItem(len(self.videos),val)
        self.videolist.SetItemImage(len(self.videos),DamnGetListIcon('generic'),DamnGetListIcon('generic'))
        self.videos.append(val)
        self.parent.addVid([val],DV.prefs.get('autoconvert')=='True')
        self.urlbox.SetFocus()
    def update(self,original,name,icon):
        for i in range(len(self.videos)):
            if self.videos[i]==original:
                self.videolist.SetStringItem(i,self.videocolumn,name)
                self.videolist.SetItemImage(i,DamnGetListIcon(icon),DamnGetListIcon(icon))
    def onAutoconvertCheck(self,event=None):
        DV.prefs.set('autoconvert',str(self.autoconvertcheck.GetValue()))
    def onMonitorCheck(self,event=None):
        newpref=self.monitorcheck.GetValue()
        DV.prefs.set('clipboard',str(newpref))
        if newpref:
            self.monitorlabel.SetLabel('Your clipboard is being monitored.')
            self.monitorlabel2.SetLabel('Simply copy a video URL and DamnVid will add it.')
        else:
            self.monitorlabel.SetLabel('Your clipboard is not being monitored.')
            self.monitorlabel2.SetLabel('Check the checkbox above if you want it to be monitored.')
        self.monitorlabel.Wrap(180)
        self.monitorlabel2.Wrap(180)
        self.toppanel.Layout()
    def onKeyDown(self,event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE,wx.WXK_CANCEL):
            self.onClose(event)
        else:
            event.Skip() # Let the event slide, otherwise the key press isn't even registered
    def onClose(self,event):
        DV.prefs.save() # Save eventually-changed-with-the-checkboxes prefs
        self.Destroy()
class DamnEEgg(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self,parent,id,'Salute the Secret Stoat!')
        topvbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topvbox)
        self.panel=wx.Panel(self,-1)
        topvbox.Add(self.panel,1,wx.EXPAND)
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.vbox)
        self.vbox.Add(wx.StaticBitmap(self.panel,-1,wx.Bitmap(DV.images_path+'stoat.jpg')),0,wx.ALIGN_CENTER)
        self.AddText('DamnVid '+DV.version+' is *100% stoat-powered*, and *proud* of it.',True)
        self.AddText('*No stoats were harmed* (much) during DamnVid\'s development. Ya rly.',True)
        self.vbox.Add((0,5))
        self.AddText('Praise the *Secret Stoat* and all it stands for: *WIN*.',True)
        self.vbox.Add((0,5))
        self.AddText('Definitions of *WIN* on the Web:',True)
        self.vbox.Add((0,5))
        self.AddText('- be the winner in a contest or competition; be victorious; "He won the Gold Medal in skating"; "Our home team won"; "Win the game"')
        self.AddText('- acquire: win something through one\'s efforts; "I acquired a passing knowledge of Chinese"; "Gain an understanding of international finance"')
        self.AddText('- gain: obtain advantages, such as points, etc.; "The home team was gaining ground"')
        self.AddText('- a victory (as in a race or other competition); "he was happy to get the win"')
        self.AddText('- winnings: something won (especially money)')
        self.AddText('- succeed: attain success or reach a desired goal; "The enterprise succeeded"; "We succeeded in getting tickets to the show"; "she struggled to overcome her handicap and won"')
        btn=wx.Button(self.panel,-1,'Secret Stoat!')
        self.vbox.Add(btn,0,wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON,self.onBtn,btn)
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
    def AddText(self,s,center=False):
        strings=['']
        for i in s:
            if i=='*':
                strings.append('')
            else:
                strings[-1]+=i
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        bold=False
        sysfont=wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        normfont=wx.Font(sysfont.GetPointSize(),sysfont.GetFamily(),sysfont.GetStyle(),sysfont.GetWeight())
        boldfont=wx.Font(sysfont.GetPointSize(),sysfont.GetFamily(),sysfont.GetStyle(),wx.FONTWEIGHT_BOLD)
        for i in strings:
            t=wx.StaticText(self.panel,-1,i)
            t.Wrap(500)
            if bold:
                t.SetFont(boldfont)
            else:
                t.SetFont(normfont)
            bold=not bold
            hbox.Add(t)
        if center:
            self.vbox.Add(hbox,0,wx.ALIGN_CENTER)
        else:
            self.vbox.Add(hbox,0)
    def onBtn(self,event):
        self.Close(True)
class DamnAboutDamnVid(wx.Dialog):
    def __init__(self,parent,id,main):
        self.parent=main
        wx.Dialog.__init__(self,parent,id,'About DamnVid '+DV.version)
        topvbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topvbox)
        panel=wx.Panel(self,-1)
        topvbox.Add(panel,1,wx.EXPAND)
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)
        vbox1=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(vbox1,0,wx.EXPAND)
        vbox2=wx.BoxSizer(wx.VERTICAL)
        hbox.Add(vbox2,1,wx.EXPAND)
        icon=wx.StaticBitmap(panel,-1,wx.Bitmap(DV.images_path+'icon256.png'))
        icon.Bind(wx.EVT_LEFT_DCLICK,self.eEgg)
        vbox1.Add(icon,1,wx.ALIGN_CENTER)
        title=wx.StaticText(panel,-1,'DamnVid '+DV.version)
        title.SetFont(wx.Font(24,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD))
        vbox2.Add(title,1)
        author=wx.StaticText(panel,-1,'By Etienne Perot')
        author.SetFont(wx.Font(16,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
        vbox2.Add(author,1)
        vbox2.Add(DamnHyperlink(panel,-1,DV.url,DV.url))
        vbox2.Add(wx.StaticText(panel,-1,'Contributors:'))
        vbox2.Add(wx.StaticText(panel,-1,'- Tatara (Linux compatibility/packaging)'))
        vbox2.Add(wx.StaticText(panel,-1,'- Palmer (Graphics)'))
        vbox2.Add(wx.StaticText(panel,-1,'Special thanks to:'))
        vbox2.Add(wx.StaticText(panel,-1,'- The FFmpeg team'))
        vbox2.Add(wx.StaticText(panel,-1,'- Every stoat on the planet'))
        vbox2.Add(wx.StaticText(panel,-1,'- You!'))
        hbox2=wx.BoxSizer(wx.HORIZONTAL)
        vbox2.Add(hbox2,0,wx.ALIGN_RIGHT)
        okButton=wx.Button(panel,-1,'OK')
        self.Bind(wx.EVT_BUTTON,self.onOK,okButton)
        hbox2.Add(okButton)
        self.SetClientSize(panel.GetBestSize())
        self.Center()
    def eEgg(self,event):
        dlg=DamnEEgg(None,-1)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def onOK(self,event):
        self.Close(True)
class DamnSplashScreen(wx.SplashScreen):
    def __init__(self):
        wx.SplashScreen.__init__(self,wx.Bitmap(DV.images_path+'splashscreen.png',wx.BITMAP_TYPE_PNG),wx.SPLASH_CENTRE_ON_SCREEN,10000,None)
class DamnVidPrefs: # Preference manager (backend, not GUI)
    def __init__(self):
        self.conf={}
        f=open(DV.conf_file,'r')
        self.ini=ConfigParser.SafeConfigParser()
        self.ini.readfp(f)
        f.close()
        self.profiles=0
        for i in self.ini.sections():
            if i[0:16]=='damnvid-profile-':
                self.profiles=self.profiles+1
    def expandPath(self,value):
        value=REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/',value.replace(os.sep,'/').replace('?DAMNVID_MY_VIDEOS?',DV.my_videos_path.replace(os.sep,'/'))).replace('/',os.sep)
        if value[-1:]!=os.sep:
            value+=os.sep
        return value
    def reducePath(self,value):
        value=REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/',value.replace(os.sep,'/').replace(DV.my_videos_path.replace(os.sep,'/'),'?DAMNVID_MY_VIDEOS?')).replace(os.sep,'/')
        if value[-1:]!='/':
            value+='/'
        return value
    def gets(self,section,name):
        name=name.lower()
        shortsection=section
        if shortsection[0:16]=='damnvid-profile-':
            shortsection='damnvid-profile'
        if self.ini.has_section(section):
            if self.ini.has_option(section,name):
                value=self.ini.get(section,name)
            elif DV.defaultprefs.has_key(shortsection+':'+name):
                value=DV.defaultprefs[shortsection+':'+name]
                self.sets(section,name,value)
            else:
                value=''
            if shortsection+':'+name in DV.path_prefs:
                value=self.expandPath(value)
            return value
        elif DV.defaultprefs.has_key(section+':'+name):
            value=DV.defaultprefs[section+':'+name]
            self.ini.add_section(section)
            self.sets(section,name,value)
            return self.gets(section,name)
        print 'No such pref:',section+':'+name
    def sets(self,section,name,value):
        name=name.lower()
        if self.ini.has_section(section):
            if section+':'+name in DV.path_prefs:
                value=self.reducePath(value)
            return self.ini.set(section,name,str(value))
        else:
            print 'No such section:',section
    def rems(self,section,name=None):
        try:
            if name is None:
                self.ini.remove_section(section)
            else:
                self.ini.remove_option(section,name)
        except:
            print 'No such section/option'
    def lists(self,section):
        prefs=[]
        if DV.preference_order.has_key(section):
            prefs.extend(DV.preference_order[section])
        if self.ini.has_section(section):
            for i in self.ini.options(section):
                if i not in prefs:
                    prefs.append(i)
        if len(prefs):
            return prefs
        print 'No such section.'
    def listsections(self):
        return self.ini.sections()
    def get(self,name):
        return self.gets('damnvid',name)
    def set(self,name,value):
        return self.sets('damnvid',name,value)
    def getp(self,profile,name):
        if int(profile)==-1:
            if name.lower()=='name':
                return '(Do not encode)'
            if name.lower()=='outdir':
                return self.get('defaultoutdir')
        return self.gets('damnvid-profile-'+str(profile),name)
    def setp(self,profile,name,value):
        return self.sets('damnvid-profile-'+str(profile),name,value)
    def listp(self,profile):
        return self.lists('damnvid-profile-'+str(profile))
    def getd(self,name):
        return self.gets('damnvid-default-profiles',name)
    def setd(self,name,value):
        return self.sets('damnvid-default-profiles',name,value)
    def listd(self):
        return self.lists('damnvid-default-profiles')
    def getm(self,module,name):
        return self.gets('damnvid-module-'+module,name)
    def setm(self,module,name,value):
        return self.sets('damnvid-module-'+module,name,value)
    def addp(self):
        self.ini.add_section('damnvid-profile-'+str(self.profiles))
        for i in DV.defaultprefs.iterkeys():
            if i[0:16]=='damnvid-profile:':
                self.ini.set('damnvid-profile-'+str(self.profiles),i,DV.defaultprefs[i])
        self.profiles=self.profiles+1
    def remp(self,profile):
        if self.profiles>1:
            for i in self.ini.options('damnvid-default-profiles'):
                if str(self.ini.get('damnvid-default-profiles',i))==str(profile):
                    self.ini.set('damnvid-default-profiles',i,'0')
                elif int(self.ini.get('damnvid-default-profiles',i))>int(profile):
                    self.ini.set('damnvid-default-profiles',i,str(int(self.ini.get('damnvid-default-profiles',i))-1))
            for i in range(profile,self.profiles-1):
                for j in self.ini.options('damnvid-profile-'+str(i)):
                    self.ini.remove_option('damnvid-profile-'+str(i),j)
                for j in self.ini.options('damnvid-profile-'+str(i+1)):
                    self.ini.set('damnvid-profile-'+str(i),j,self.ini.get('damnvid-profile-'+str(i+1),j))
            self.profiles=self.profiles-1
            self.ini.remove_section('damnvid-profile-'+str(self.profiles))
            return self.profiles
        else:
            print 'Denied~'
            return None
    def geta(self,section,name):
        return eval(base64.b64decode(self.gets(section,name)))
    def seta(self,section,name,value):
        return self.sets(section,name,base64.b64encode(str(value)))
    def save(self):
        f=open(DV.conf_file,'w')
        self.ini.write(f)
        f.close()
class DamnBrowseDirButton(wx.Button): # "Browse..." button for directories
    def __init__(self,parent,id,label,control,title,callback):
        self.filefield=control
        self.title=title
        self.callback=callback
        wx.Button.__init__(self,parent,id,label)
    def onBrowse(self,event):
        dlg=wx.DirDialog(self,self.title,self.filefield.GetValue(),style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        dlg.SetIcon(DV.icon)
        path=None
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            self.filefield.SetValue(path)
        dlg.Destroy()
        if path!=None:
            self.callback(self,path)
class DamnYouTubeService(thr.Thread):
    def __init__(self,parent,query=None):
        self.parent=parent
        thr.Thread.__init__(self)
        if query is None:
            self.queries=None
        else:
            self.queries=[query]
    def query(self,query):
        if self.queries is None:
            self.queries=[query]
        else:
            self.queries.append(query)
    def stillAlive(self):
        return True
    def postEvent(self,info):
        info['self']=self
        try:
            wx.PostEvent(self.parent,DamnLoadingEvent(DV.evt_loading,-1,info))
        except:
            pass # Window might have been closed
    def returnResult(self,result,index=0):
        return self.postEvent({'index':index,'query':self.queries[index],'result':result})
    def getTempFile(self):
        name=DV.tmp_path+str(random.random())+'.tmp'
        while os.path.lexists(name):
            name=DV.tmp_path+str(random.random())+'.tmp'
        return name
    def run(self):
        while self.queries is None:
            time.sleep(.025)
        try:
            self.parent.loadlevel+=1
        except:
            pass # Window might have been closed
        while len(self.queries):
            query=self.queries[0]
            if query[0]=='feed':
                self.returnResult(DV.youtube_service.GetYouTubeVideoFeed(query[1]))
            elif query[0]=='image':
                http=urllib2.urlopen(query[1])
                tmpf=self.getTempFile()
                tmpfstream=open(tmpf,'wb')
                for i in http.readlines():
                    tmpfstream.write(i)
                http.close()
                tmpfstream.close()
                self.returnResult(tmpf)
            self.queries.pop(0)
            if not len(self.queries):
                time.sleep(.5) # Hang around for a moment, wait for work
        self.postEvent({'query':('done',)})
        try:
            self.parent.loadlevel-=1
        except:
            pass # Window might have been closed
class DamnVidBrowser(wx.Dialog):
    def __init__(self,parent):
        self.parent=parent
        wx.Dialog.__init__(self,parent,-1,'Search for videos...')
        topsizer=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topsizer)
        self.toppanel=wx.Panel(self,-1)
        topsizer.Add(self.toppanel,1,wx.EXPAND)
        topvbox=wx.BoxSizer(wx.VERTICAL)
        tophbox=wx.BoxSizer(wx.HORIZONTAL)
        self.toppanel.SetSizer(tophbox)
        tophbox.Add((DV.border_padding,0))
        tophbox.Add(topvbox,1,wx.EXPAND)
        tophbox.Add((DV.border_padding,0))
        topvbox.Add((0,DV.border_padding))
        searchhbox=wx.BoxSizer(wx.HORIZONTAL)
        topvbox.Add(searchhbox,0,wx.EXPAND)
        searchhbox.Add(wx.StaticText(self.toppanel,-1,'Search:'),0,wx.ALIGN_CENTER_VERTICAL)
        searchhbox.Add((DV.control_hgap,0))
        self.standardchoices=('Most popular','Most viewed','Top rated','Recently featured','Most recent','Most discussed','Top favorites','Most linked','Most responded')
        self.searchbox=wx.SearchCtrl(self.toppanel,-1,'',style=wx.TE_PROCESS_ENTER)
        self.searchbox.SetSearchMenuBitmap(wx.Bitmap(DV.images_path+'searchctrl.png'))
        self.searchbox.Bind(wx.EVT_TEXT_ENTER,self.search)
        searchhbox.Add(self.searchbox,1,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        self.searchbutton=wx.animate.GIFAnimationCtrl(self.toppanel,-1,DV.images_path+'search.gif')
        self.searchbutton.Bind(wx.EVT_LEFT_DOWN,self.search)
        searchhbox.Add((DV.control_hgap,0))
        searchhbox.Add(self.searchbutton,0,wx.ALIGN_CENTER_VERTICAL)
        self.scrollpanel=wx.ScrolledWindow(self.toppanel,-1,size=(360,270+3*DV.control_vgap))
        self.scrollpanel.SetMinSize((360,270+3*DV.control_vgap))
        self.scrollpanel.SetScrollbars(0,DV.control_vgap*DV.scroll_factor,0,0)
        scrollpanelsizer=wx.BoxSizer(wx.HORIZONTAL)
        self.scrollpanel.SetSizer(scrollpanelsizer)
        self.resultpanel=wx.Panel(self.scrollpanel,-1)
        scrollpanelsizer.Add(self.resultpanel,1,wx.EXPAND)
        self.resultsizer=wx.BoxSizer(wx.VERTICAL)
        self.resultpanel.SetSizer(self.resultsizer)
        topvbox.Add((0,DV.control_vgap))
        topvbox.Add(self.scrollpanel,1,wx.EXPAND)
        self.Bind(wx.EVT_CLOSE,self.onClose)
        self.Bind(DV.evt_load,self.onLoad)
        self.boxmenu=wx.Panel(self,-1) # Temp panel, gonna be deleted in buildSearchbox anyway
        self.buildSearchbox()
        self.loadlevel=0
        self.results=[]
        self.displayedurls=[]
        self.resultctrls=[]
        self.service=None
        self.scrollpanel.Hide()
        self.waitingpanel=wx.Panel(self.toppanel,-1,size=(360,270+3*DV.control_vgap))
        waitingsizer=wx.BoxSizer(wx.VERTICAL)
        self.waitingpanel.SetSizer(waitingsizer)
        waitingsizer.Add((0,int(DV.control_vgap*1.5)))
        waitingsizer2=wx.BoxSizer(wx.HORIZONTAL)
        waitingsizer.Add(waitingsizer2)
        waitingsizer2.Add((DV.control_hgap,0))
        topvbox.Add(self.waitingpanel)
        self.searchingimg=wx.StaticBitmap(self.waitingpanel,-1,wx.Bitmap(DV.images_path+'searchpanel.png'))
        waitingsizer2.Add(self.searchingimg)
        defaultsearch=DV.prefs.gets('damnvid-search','default_search')
        if defaultsearch:
            self.search(search=defaultsearch)
        else:
            pass
        topvbox.Add((0,DV.control_vgap))
        self.downloadAll=wx.Button(self.toppanel,-1,'Download all')
        self.downloadAll.Bind(wx.EVT_BUTTON,self.onDownloadAll)
        topvbox.Add(self.downloadAll,0,wx.ALIGN_RIGHT)
        topvbox.Add((0,DV.border_padding))
        self.SetClientSize(self.GetBestSize())
        self.Center()
    def cleanString(self,s):
        return DamnHtmlEntities(s)
    def getService(self):
        if self.service is None:
            self.service=DamnYouTubeService(self)
            self.service.start()
        else:
            try:
                if self.service.stillAlive():
                    return self.service
            except:
                self.service=None
                return self.getService()
        return self.service
    def search(self,event=None,search=''):
        self.scrollpanel.Hide()
        self.waitingpanel.Show()
        self.toppanel.Layout()
        if not search:
            search=self.searchbox.GetValue()
        if not search:
            return
        self.searchbox.SetValue(search)
        self.searchbutton.LoadFile(DV.images_path+'searching.gif')
        self.searchbutton.Play()
        prefix='http://gdata.youtube.com/feeds/api/videos?racy=include&orderby=viewCount&vq='
        if search in self.standardchoices:
            prefix='http://gdata.youtube.com/feeds/api/standardfeeds/'
            search=search.lower().replace(' ','_')
        else:
            history=DV.prefs.geta('damnvid-search','history')
            if search not in history:
                history.append(search)
                while len(history)>int(DV.prefs.gets('damnvid-search','history_length')):
                    history.pop(0)
            DV.prefs.seta('damnvid-search','history',history)
        self.buildSearchbox()
        self.getService().query(('feed',prefix+urllib2.quote(search)))
        for i in self.resultctrls:
            i.Destroy()
        self.resultctrls=[]
        self.scrollpanel.AdjustScrollbars()
        self.resultsizer.Clear(True)
        self.displayedurls=[]
    def onLoad(self,event):
        info=event.GetInfo()
        if info['query'][0]=='feed':
            results=info['result']
            boldfont=wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            boldfont.SetWeight(wx.FONTWEIGHT_BOLD)
            tmpscrollbar=wx.ScrollBar(self.resultpanel,-1,style=wx.SB_VERTICAL)
            panelwidth=self.scrollpanel.GetSizeTuple()[0]-tmpscrollbar.GetSizeTuple()[0]
            tmpscrollbar.Destroy()
            del tmpscrollbar
            for i in range(len(results.entry)):
                tmpvbox=wx.BoxSizer(wx.VERTICAL)
                tmpsizer=wx.BoxSizer(wx.HORIZONTAL)
                tmpvbox.Add((0,DV.border_padding))
                tmpvbox.Add(tmpsizer)
                tmppanel=wx.Panel(self.resultpanel,-1,style=wx.SIMPLE_BORDER)
                self.resultctrls.append(tmppanel)
                tmppanel.SetBackgroundColour(wx.WHITE)
                tmppanel.SetMinSize((panelwidth,-1))
                self.resultsizer.Add(tmppanel)
                tmppanel.SetSizer(tmpvbox)
                tmpsizer.Add((DV.border_padding,0))
                thumb=wx.animate.GIFAnimationCtrl(tmppanel,-1,DV.images_path+'thumbnail.gif')
                self.getService().query(('image',results.entry[i].media.thumbnail[0].url,thumb))
                tmpsizer.Add(thumb)
                thumb.Play()
                tmpsizer.Add((DV.control_hgap,0))
                infobox=wx.BoxSizer(wx.VERTICAL)
                tmpsizer.Add(infobox,1,wx.EXPAND)
                title=DamnHyperlink(tmppanel,-1,self.cleanString(results.entry[i].media.title.text),self.cleanString(results.entry[i].media.player.url))
                infobox.Add(title)
                #infobox.Add((0,DV.control_vgap))
                desc=self.makeDescPanel(results.entry[i].media.description.text,tmppanel,panelwidth-2*DV.border_padding)
                tmpvbox.Add(desc,0,wx.EXPAND)
                desc.Hide()
                videoinfo=wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(videoinfo)
                #infobox.Add((0,DV.control_vgap))
                tmplabel=wx.StaticText(tmppanel,-1,results.entry[i].media.category[0].text)
                tmplabel.SetFont(boldfont)
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel=wx.StaticText(tmppanel,-1,', ')
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel=wx.StaticText(tmppanel,-1,self.sec2time(results.entry[i].media.duration.seconds))
                tmplabel.SetFont(boldfont)
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel=wx.StaticText(tmppanel,-1,'.')
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                statistics=wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(statistics)
                infobox.Add((0,DV.control_vgap))
                statistics2=wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(statistics2)
                viewcount=wx.StaticText(tmppanel,-1,self.numFormat(results.entry[i].statistics.view_count))
                viewcount.SetFont(boldfont)
                viewcount.SetForegroundColour(wx.BLACK)
                statistics.Add(viewcount)
                tmplabel=wx.StaticText(tmppanel,-1,' views.')
                tmplabel.SetForegroundColour(wx.BLACK)
                statistics.Add(tmplabel)
                tmplabel=wx.StaticText(tmppanel,-1,'Rating: ')
                tmplabel.SetForegroundColour(wx.BLACK)
                statistics2.Add(tmplabel,0,wx.ALIGN_CENTER_VERTICAL)
                if results.entry[i].rating is None:
                    tmplabel=wx.StaticText(tmppanel,-1,'(None)')
                    tmplabel.SetForegroundColour(wx.BLACK)
                    statistics2.Add(tmplabel,0,wx.ALIGN_CENTER_VERTICAL)
                else:
                    statistics2.Add(wx.StaticBitmap(tmppanel,-1,wx.Bitmap(DV.images_path+'stars_'+str(int(round(float(results.entry[i].rating.average),0)))+'.png')),0,wx.ALIGN_CENTER_VERTICAL)
                infobox.Add((0,DV.control_vgap))
                buttonrow=wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(buttonrow)
                btnDesc=wx.Button(tmppanel,-1,'Description')
                buttonrow.Add(btnDesc)
                buttonrow.Add((DV.control_hgap,0))
                btnDesc.Bind(wx.EVT_BUTTON,DamnCurry(self.onDescButton,desc,tmppanel))
                btnDownload=wx.Button(tmppanel,-1,'Download')
                btnDownload.Bind(wx.EVT_BUTTON,DamnCurry(self.onDownload,results.entry[i].media.player.url))
                self.displayedurls.append(results.entry[i].media.player.url)
                buttonrow.Add(btnDownload)
                tmpsizer.Add((DV.border_padding,0))
                tmpvbox.Add((0,DV.border_padding))
                if i+1!=len(results.entry):
                    self.resultsizer.Add((0,DV.control_vgap))
                    self.resultsizer.Add(wx.StaticLine(tmppanel,-1),0,wx.EXPAND)
                    self.resultsizer.Add((0,DV.control_vgap))
            self.waitingpanel.Hide()
            self.scrollpanel.Show()
            self.resultpanel.Fit()
            self.scrollpanel.AdjustScrollbars()
            self.toppanel.Layout()
        elif info['query'][0]=='image':
            try:
                ctrl=info['query'][2]
                ctrl.Stop()
                ctrl.SetInactiveBitmap(wx.Bitmap(info['result']))
            except:
                pass
            try:
                os.remove(info['result'])
            except:
                pass
        elif info['query'][0]=='done':
            try:
                self.service=None
                self.searchbutton.Stop()
                self.searchbutton.LoadFile(DV.images_path+'search.gif')
            except:
                pass
    def buildSearchbox(self):
        val=self.searchbox.GetValue().strip().lower()
        self.boxmenu.Destroy()
        del self.boxmenu
        self.boxmenu=wx.Menu('')
        history=DV.prefs.geta('damnvid-search','history')
        if len(history):
            history.reverse() # Recent entries appear on top
            for i in history:
                item=wx.MenuItem(self.boxmenu,-1,i,kind=wx.ITEM_RADIO)
                self.boxmenu.AppendItem(item) # Once again, item has to be appended before being checked
                item.Check(i.lower()==val)
                self.boxmenu.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,i),item)
                self.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,i),item)
            item=wx.MenuItem(self.boxmenu,-1,'(Clear search history)',kind=wx.ITEM_RADIO) # Ironic, but necessary to put this one as a radio, otherwise wx guesses that the menu is actually two separated radio menus
            self.boxmenu.AppendItem(item)
            self.boxmenu.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,None),item)
            self.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,None),item)
        for i in self.standardchoices:
            item=wx.MenuItem(self.boxmenu,-1,i,kind=wx.ITEM_RADIO)
            self.boxmenu.AppendItem(item)
            item.Check(i.lower()==val)
            self.boxmenu.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,i),item)
            self.Bind(wx.EVT_MENU,DamnCurry(self.onSearchMenu,i),item)
        self.searchbox.SetMenu(self.boxmenu)
    def onSearchMenu(self,query,event):
        if query is None: # Clear history
            DV.prefs.seta('damnvid-search','history',[])
            DV.prefs.save()
            self.buildSearchbox()
        else:
            self.searchbox.SetValue(query)
            self.search()
    def makeDescPanel(self,desc,parent,width):
        desc=self.cleanString(desc)
        panel=wx.Panel(parent,-1)
        wrapper=wx.BoxSizer(wx.HORIZONTAL)
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0,DV.control_vgap))
        wrapper.Add((DV.border_padding,0))
        wrapper.Add(sizer)
        wrapper.Add((DV.border_padding,0))
        panel.SetSizer(wrapper)
        descfont=wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        descfont.SetWeight(wx.FONTWEIGHT_BOLD)
        txt=wx.StaticText(panel,-1,'Description:')
        txt.SetFont(descfont)
        txt.SetForegroundColour(wx.BLACK)
        sizer.Add(txt)
        descs=[]
        lastindex=0
        urls=[]
        curmatch=1
        for link in REGEX_HTTP_GENERIC_LOOSE.finditer(desc):
            before=desc[lastindex:link.start()].strip()
            if before:
                descs.extend((before,link.group()))
            else:
                descs.append(link.group())
                curmatch-=1
            urls.append(curmatch)
            lastindex=link.end()
            curmatch+=2
        if not len(descs):
            descs=[desc]
        for i in range(len(descs)):
            if i in urls:
                link=DamnHyperlink(panel,-1,descs[i],descs[i])
                sizer.Add(link)
            else:
                txt=wx.StaticText(panel,-1,descs[i])
                txt.SetForegroundColour(wx.BLACK)
                txt.Wrap(width)
                sizer.Add(txt)
        return panel
    def sec2time(self,sec):
        t=(0,0,int(sec))
        t=(t[0],(t[2]-t[2]%60)/60,t[2]%60)
        t=(str((t[1]-t[1]%60)/60),str(t[1]%60),str(t[2]))
        if t[0]=='0':
            return t[1]+':'+self.numFormat(t[2],True)
        return t[0]+':'+self.numFormat(t[1],True)+':'+self.numFormat(t[2],True)
    def numFormat(self,num,doublezero=False):
        num=REGEX_THOUSAND_SEPARATORS.sub(',',str(num))
        if doublezero and len(num)==1:
            num='0'+num
        return num
    def onDownload(self,url,event):
        self.parent.addVid([url],DV.prefs.get('autoconvert')=='True')
    def onDownloadAll(self,event):
        self.parent.addVid(self.displayedurls,DV.prefs.get('autoconvert')=='True')
    def onDescButton(self,ctrl,panel,event):
        position=self.scrollpanel.GetViewStart()
        ctrl.Show(not ctrl.IsShown())
        panel.Fit()
        panel.Layout()
        self.resultpanel.Fit()
        self.scrollpanel.AdjustScrollbars()
        self.scrollpanel.Scroll(position[0],position[1])
    def onClose(self,event=None):
        self.parent.searchopen=False
        DV.prefs.save() # Saves search history
        self.Destroy()
class DamnVidPrefEditor(wx.Dialog): # Preference dialog (not manager)
    def __init__(self,parent,id,title,main):
        # Dialog init
        wx.Dialog.__init__(self,parent,id,title)
        self.parent=main
        DV.prefs.save() # Save just in case, we're gonna modify stuff!
        self.toppanel=wx.Panel(self,-1)
        self.bestsize=[0,0]
        # Top part of the toppanel
        self.topsizer=wx.BoxSizer(wx.VERTICAL)
        self.topsizer.Add((0,DV.border_padding))
        self.uppersizer=wx.BoxSizer(wx.HORIZONTAL)
        self.uppersizer.Add((DV.border_padding,0))
        self.topsizer.Add(self.uppersizer,1,wx.EXPAND)
        # - Left part of the upperpanel
        self.upperleftpanel=wx.Panel(self.toppanel,-1)
        self.uppersizer.Add(self.upperleftpanel,0)
        self.uppersizer.Add((DV.control_hgap,0))
        self.upperleftsizer=wx.BoxSizer(wx.VERTICAL)
        self.tree=wx.TreeCtrl(self.upperleftpanel,-1,size=(260,280),style=wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT)
        self.upperleftsizer.Add(self.tree,1,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.control_vgap))
        self.buildTree()
        self.addProfileButton=wx.Button(self.upperleftpanel,-1,'Add profile')
        self.upperleftsizer.Add(self.addProfileButton,0,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.control_vgap))
        self.deleteProfileButton=wx.Button(self.upperleftpanel,-1,'Delete profile')
        self.upperleftsizer.Add(self.deleteProfileButton,0,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.control_vgap))
        self.importButton=wx.Button(self.upperleftpanel,-1,'Import preferences')
        self.upperleftsizer.Add(self.importButton,0,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.control_vgap))
        self.exportButton=wx.Button(self.upperleftpanel,-1,'Export preferences')
        self.upperleftsizer.Add(self.exportButton,0,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.control_vgap))
        self.resetButton=wx.Button(self.upperleftpanel,-1,'Reset all')
        self.upperleftsizer.Add(self.resetButton,0,wx.EXPAND)
        self.upperleftsizer.Add((0,DV.border_padding))
        self.upperleftpanel.SetSizer(self.upperleftsizer)
        # - Right part of the upperpanel
        self.upperrightpanel=wx.Panel(self.toppanel,-1)
        self.uppersizer.Add(self.upperrightpanel,1,wx.EXPAND)
        self.prefpanelabel=wx.StaticBox(self.upperrightpanel,-1,'')
        self.upperrightsizer=wx.StaticBoxSizer(self.prefpanelabel,wx.VERTICAL)
        # - - Preference pane creation
        self.prefpane=wx.Panel(self.upperrightpanel,-1)
        self.prefpanesizer=wx.GridBagSizer(DV.control_vgap,DV.control_hgap) # Yes, it's vgap then hgap
        self.prefpane.SetSizer(self.prefpanesizer)
        # - - End preference pane creation
        self.upperrightsizer.Add(self.prefpane,1,wx.EXPAND)
        self.uppersizer.Add((DV.border_padding,0))
        self.upperrightpanel.SetSizer(self.upperrightsizer)
        self.topsizer.Add((0,DV.control_vgap))
        # Bottom part of the toppanel
        self.lowersizer=wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.lowersizer,0,wx.EXPAND)
        self.lowersizer.AddStretchSpacer(1)
        self.okButton=wx.Button(self.toppanel,wx.ID_OK,'OK')
        self.lowersizer.Add(self.okButton,0,wx.ALIGN_RIGHT)
        self.lowersizer.Add((DV.control_hgap,0))
        self.closeButton=wx.Button(self.toppanel,wx.ID_CLOSE,'Cancel')
        self.lowersizer.Add(self.closeButton,0,wx.ALIGN_RIGHT)
        self.lowersizer.Add((DV.border_padding,0))
        self.topsizer.Add((0,DV.border_padding))
        # Final touches, binds, etc.
        self.toppanel.SetSizer(self.topsizer)
        self.Bind(wx.EVT_BUTTON,self.onAddProfile,self.addProfileButton)
        self.Bind(wx.EVT_BUTTON,self.onDeleteProfile,self.deleteProfileButton)
        self.Bind(wx.EVT_BUTTON,self.onOK,self.okButton)
        self.Bind(wx.EVT_BUTTON,self.onImport,self.importButton)
        self.Bind(wx.EVT_BUTTON,self.onExport,self.exportButton)
        self.Bind(wx.EVT_BUTTON,self.onReset,self.resetButton)
        self.Bind(wx.EVT_BUTTON,self.onClose,self.closeButton)
        self.Bind(wx.EVT_TREE_SEL_CHANGED,self.onTreeSelectionChanged,self.tree)
        self.Bind(wx.EVT_KEY_DOWN,self.onKeyDown,self.toppanel)
        self.Bind(DV.evt_load,self.onLoad)
        self.toppanel.SetFocus()
        self.forceSelect(self.treeroot) # Will also resize the window on certain platforms since it fires the selection events, but not on Ubuntu it seems, so...
        self.updatePrefPane('damnvid')
        self.Center()
    def buildTree(self):
        self.tree.DeleteAllItems()
        treeimages=wx.ImageList(16,16,True)
        self.tree.AssignImageList(treeimages)
        self.treeroot=self.tree.AddRoot('DamnVid Preferences')
        self.tree.SetItemImage(self.treeroot,treeimages.Add(wx.Bitmap(DV.images_path+'icon16.png')))
        self.searchprefs=self.tree.AppendItem(self.treeroot,'YouTube browser')
        self.tree.SetItemImage(self.searchprefs,treeimages.Add(wx.Bitmap(DV.images_path+'youtubebrowser.png')))
        self.modulelistitem=self.tree.AppendItem(self.treeroot,'Modules')
        self.tree.SetItemImage(self.modulelistitem,treeimages.Add(wx.Bitmap(DV.images_path+'modules.png')))
        self.modules={}
        self.moduledescs={}
        for i in DamnIterModules():
            self.modules[i]=self.tree.AppendItem(self.modulelistitem,DV.modules[i]['title'])
            self.tree.SetItemImage(self.modules[i],treeimages.Add(wx.Bitmap(DV.modules_path+DV.modules[i]['name']+os.sep+DV.modules[i]['icon']['small'])))
        self.profileroot=self.tree.AppendItem(self.treeroot,'Encoding profiles')
        self.tree.SetItemImage(self.profileroot,treeimages.Add(wx.Bitmap(DV.images_path+'profiles.png')))
        self.profiles=[]
        for i in range(0,DV.prefs.profiles):
            treeitem=self.tree.AppendItem(self.profileroot,DV.prefs.getp(i,'name'))
            self.profiles.append(treeitem)
            self.tree.SetItemImage(treeitem,treeimages.Add(wx.Bitmap(DV.images_path+'profile.png')))
        self.tree.ExpandAll()
        self.forceSelect(self.treeroot)
    def forceSelect(self,item,event=None):
        self.tree.SelectItem(item,True)
    def onTreeSelectionChanged(self,event):
        item=event.GetItem()
        self.prefpanelabel.SetLabel(self.tree.GetItemText(item))
        if item==self.treeroot:
            self.updatePrefPane('damnvid')
        elif item==self.searchprefs:
            self.updatePrefPane('damnvid-search')
        elif item==self.modulelistitem:
            self.updatePrefPane('special:modules')
        elif item==self.profileroot:
            self.updatePrefPane('special:profileroot')
        elif item in self.profiles:
            self.updatePrefPane('damnvid-profile-'+str(self.profiles.index(item)))
        elif item in self.modules.values():
            for i in DamnIterModules():
                if self.modules[i]==item:
                    self.updatePrefPane('damnvid-module-'+i)
                    break
        else:
            self.updatePrefPane('special:error')
    def getLabel(self,panel,label,color='#000000',bold=False,hyperlink=None):
        if hyperlink is None:
            lbl=wx.StaticText(panel,-1,label)
        else:
            lbl=DamnHyperlink(panel,-1,label,hyperlink)
        if bold:
            sysfont=wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            boldfont=wx.Font(sysfont.GetPointSize(),sysfont.GetFamily(),sysfont.GetStyle(),wx.FONTWEIGHT_BOLD)
            lbl.SetFont(boldfont)
        if hyperlink is None and color is not None:
            lbl.SetForegroundColour(color)
        return lbl
    def buildModulePanel(self,parent,module,extended=False,buttons=True,withscrollbars=False):
        mod=DV.modules[module]
        tmppanel=wx.Panel(parent,-1,style=wx.SIMPLE_BORDER)
        tmppanel.SetBackgroundColour(wx.WHITE)
        panelwidth=parent.GetSizeTuple()[0]
        if withscrollbars:
            tmpscroll=wx.ScrollBar(tmppanel,-1,style=wx.SB_VERTICAL)
            panelwidth-=tmpscroll.GetSizeTuple()[0]
            tmpscroll.Destroy()
            del tmpscroll
        tmptop3sizer=wx.BoxSizer(wx.VERTICAL)
        tmppanel.SetSizer(tmptop3sizer)
        tmptop3sizer.Add((0,DV.border_padding))
        tmptop2sizer=wx.BoxSizer(wx.HORIZONTAL)
        tmptop3sizer.Add(tmptop2sizer,1,wx.EXPAND)
        tmptop3sizer.Add((0,DV.border_padding))
        tmptop2sizer.Add((DV.border_padding,0))
        tmptopsizer=wx.BoxSizer(wx.VERTICAL)
        tmptop2sizer.Add(tmptopsizer,1,wx.EXPAND)
        tmptop2sizer.Add((DV.border_padding,0))
        # Construct top row of the module item
        tehrow=wx.BoxSizer(wx.HORIZONTAL)
        tmptopsizer.Add(tehrow,1,wx.EXPAND)
        tehrow.Add(wx.StaticBitmap(tmppanel,-1,wx.Bitmap(DV.modules_path+module+os.sep+mod['icon']['large'])))
        tehrow.Add((DV.control_hgap,0))
        rightcol=wx.BoxSizer(wx.VERTICAL)
        tehrow.Add(rightcol,1,wx.EXPAND)
        toprow=wx.BoxSizer(wx.HORIZONTAL)
        rightcol.Add(toprow)
        if mod['about'].has_key('url'):
            toprow.Add(self.getLabel(tmppanel,mod['title'],hyperlink=mod['about']['url'],bold=True))
        else:
            toprow.Add(self.getLabel(tmppanel,mod['title'],bold=True))
        toprow.Add(self.getLabel(tmppanel,' (version '))
        toprow.Add(self.getLabel(tmppanel,mod['version'],bold=True))
        toprow.Add(self.getLabel(tmppanel, ')'))
        toprow.Add(self.getLabel(tmppanel,' by ',color='#707070'))
        if mod['author'].has_key('url'):
            toprow.Add(self.getLabel(tmppanel,mod['author']['name'],hyperlink=mod['author']['url'],bold=True))
        else:
            toprow.Add(self.getLabel(tmppanel,mod['author']['name'],bold=True))
        toprow.Add(self.getLabel(tmppanel,'.'))
        descwidth=parent.GetSizeTuple()[0]-2*DV.border_padding-72-DV.control_hgap
        if extended:
            rightcol.Add(self.getLabel(tmppanel,'Author:',bold=True))
            authorsizer=wx.BoxSizer(wx.HORIZONTAL)
            rightcol.Add(authorsizer)
            authorsizer.Add((DV.control_hgap*2,0)) # Indent a bit
            if mod['author'].has_key('url'):
                authorsizer.Add(self.getLabel(tmppanel,mod['author']['name'],bold=True,hyperlink=mod['author']['url']))
            else:
                authorsizer.Add(self.getLabel(tmppanel,mod['author']['name'],bold=True))
            if mod['author'].has_key('email'):
                authorsizer.Add(self.getLabel(tmppanel,' <',color='#707070'))
                authorsizer.Add(self.getLabel(tmppanel,mod['author']['email'],hyperlink='mailto:'+mod['author']['email']))
                authorsizer.Add(self.getLabel(tmppanel,'>',color='#707070'))
            desc=self.getLabel(tmppanel,mod['about']['long'])
        else:
            desc=self.getLabel(tmppanel,mod['about']['short'])
        desc.Wrap(descwidth)
        self.moduledescs[mod['name']]=(desc,descwidth)
        rightcol.Add((0,DV.control_vgap))
        rightcol.Add(desc)
        if buttons:
            rightcol.Add((0,DV.control_vgap))
            tmpbuttonsizer=wx.BoxSizer(wx.HORIZONTAL)
            rightcol.Add(tmpbuttonsizer,0,wx.ALIGN_RIGHT)
            config=wx.Button(tmppanel,-1,'Configure')
            config.Bind(wx.EVT_BUTTON,DamnCurry(self.forceSelect,self.modules[module]))
            tmpbuttonsizer.Add(config)
            tmpbuttonsizer.Add((DV.control_hgap,0))
            update=wx.Button(tmppanel,-1,'Update')
            update.Bind(wx.EVT_BUTTON,DamnCurry(self.onModuleUpdate,module))
            tmpbuttonsizer.Add(update)
            tmpbuttonsizer.Add((DV.control_hgap,0))
            uninstall=wx.Button(tmppanel,-1,'Uninstall')
            uninstall.Bind(wx.EVT_BUTTON,DamnCurry(self.onModuleUninstall,module))
            tmpbuttonsizer.Add(uninstall)
        return tmppanel
    def updatePrefPane(self,pane):
        self.prefpanesizer.Clear(True) # Delete all controls in prefpane
        for i in range(self.prefpanesizer.GetCols()):
            try:
                self.prefpanesizer.RemoveGrowableCol(i)
            except:
                pass
        for i in range(self.prefpanesizer.GetRows()):
            try:
                self.prefpanesizer.RemoveGrowableRow(i)
            except:
                pass
        self.pane=pane
        if pane[0:8].lower()=='special:':
            pane=pane[8:]
            if pane=='profileroot':
                txt=wx.StaticText(self.prefpane,-1,"""DamnVid lets you create multiple so-called "Encoding profiles". An encoding profile is a set of encoding preferences used to encode videos.

Being able to create multiple instances of these profiles allow you to easily convert a set of videos to the same format, while converting others to another format. For instance, you might want to convert some videos with low-quality settings so that they can be played on your iPod, while converting a few other videos with higher quality settings before burning them on a DVD.

Additionally, one of your encoding profiles may be set as the default one for new videos added in the video list from a specific source. This way, you can, for instance, convert all YouTube videos to iPod format, while converting all local files to DVD format. Use the "Default profiles" configuration panel to customize which profiles are used as default for a certain video source.""")
                txt.Wrap(max(self.prefpane.GetSize()[0],300))
                self.prefpanesizer.Add(txt,(0,0),(1,1))
            elif pane=='error':
                txt=wx.StaticText(self.prefpane,-1,'Error!')
                txt.Wrap(max(self.prefpane.GetSize()[0],300))
                self.prefpanesizer.Add(txt,(0,0),(1,1))
            elif pane=='modules':
                topsizer=wx.BoxSizer(wx.VERTICAL)
                self.prefpanesizer.Add(topsizer,(0,0),(1,1),wx.EXPAND)
                self.prefpanesizer.AddGrowableCol(0,1)
                self.prefpanesizer.AddGrowableRow(0,1)
                # Construct module list
                self.modulelist=wx.ScrolledWindow(self.prefpane,-1,size=(460,3*(72+2*DV.border_padding)))
                self.modulelist.SetMinSize((460,3*(72+2*DV.border_padding)))
                modlistsizer=wx.BoxSizer(wx.VERTICAL)
                self.modulelist.SetSizer(modlistsizer)
                topsizer.Add(self.modulelist,1,wx.EXPAND)
                topsizer.Add((0,DV.control_vgap))
                buttonsizer=wx.BoxSizer(wx.HORIZONTAL)
                topsizer.Add(buttonsizer,0,wx.ALIGN_RIGHT,border=1)
                if DV.os=='mac':
                    topsizer.Add((0,2)) # Annoying glitch with the buttons
                # Construct module list scrollable window
                for mod in DamnIterModules():
                    modlistsizer.Add(self.buildModulePanel(self.modulelist,mod,withscrollbars=True),0,wx.EXPAND)
                self.modulelist.SetScrollbars(0,DV.control_vgap*DV.scroll_factor,0,0)
                # Construct buttons under module list
                install=wx.Button(self.prefpane,-1,'Install...')
                install.Bind(wx.EVT_BUTTON,self.onModuleInstall)
                buttonsizer.Add(install)
                buttonsizer.Add((DV.control_hgap,0))
                reset=wx.Button(self.prefpane,-1,'Reset all...')
                reset.Bind(wx.EVT_BUTTON,self.onModuleAllReset)
                buttonsizer.Add(reset)
                buttonsizer.Add((DV.control_hgap,0))
                update=wx.Button(self.prefpane,-1,'Check for updates')
                update.Bind(wx.EVT_BUTTON,self.onModuleAllUpdate)
                buttonsizer.Add(update)
        else:
            prefprefix=pane
            profile=None
            module=None
            if prefprefix[0:16].lower()=='damnvid-profile-':
                prefprefix=prefprefix[0:15]
                profile=int(pane[16:])
            elif prefprefix[0:15].lower()=='damnvid-module-':
                module=prefprefix[15:]
            prefprefix+=':'
            self.controls={}
            currentprefs=[]
            maxheight={str(DV.preference_type_video):0,str(DV.preference_type_audio):0,str(DV.preference_type_profile):0,str(DV.preference_type_misc):0}
            maxwidth={str(DV.preference_type_video):0,str(DV.preference_type_audio):0,str(DV.preference_type_profile):0,str(DV.preference_type_misc):0}
            count=0
            availprefs=DV.prefs.lists(pane)
            for i in DV.preference_order[prefprefix[0:-1]]:
                if prefprefix+i in DV.preferences.keys() and i in availprefs:
                    if not DV.preferences[prefprefix+i].has_key('noedit'):
                        currentprefs.append(prefprefix+i)
            for i in availprefs:
                if prefprefix+i in DV.preferences.keys():
                    desc=DV.preferences[prefprefix+i]
                    if not desc.has_key('noedit'):
                        width=1
                        if prefprefix+i not in currentprefs:
                            currentprefs.append(prefprefix+i)
                        maxheight[str(desc['type'])]+=1
                        maxwidth[str(desc['type'])]=max((maxwidth[str(desc['type'])],self.getPrefWidth(prefprefix+i)))
            maxwidth[str(DV.preference_type_profile)]=max((maxwidth[str(DV.preference_type_misc)],maxwidth[str(DV.preference_type_profile)],maxwidth[str(DV.preference_type_video)]+maxwidth[str(DV.preference_type_audio)]))
            maxwidth[str(DV.preference_type_misc)]=maxwidth[str(DV.preference_type_profile)]
            count=0
            currentprefsinsection={str(DV.preference_type_video):0,str(DV.preference_type_audio):0,str(DV.preference_type_profile):0,str(DV.preference_type_misc):0}
            for i in currentprefs:
                shortprefname=i[i.find(':')+1:]
                if profile==None:
                    val=DV.prefs.gets(pane,shortprefname)
                else:
                    val=DV.prefs.getp(profile,shortprefname)
                position=[int(module is not None),0]
                maxspan=[1,maxwidth[str(DV.preferences[i]['type'])]]
                if DV.preferences[i]['type']==DV.preference_type_audio:
                    position[1]+=maxwidth[str(DV.preference_type_video)]
                elif DV.preferences[i]['type']==DV.preference_type_profile:
                    position[0]+=max((maxheight[str(DV.preference_type_video)],maxheight[str(DV.preference_type_audio)]))
                elif DV.preferences[i]['type']==DV.preference_type_misc:
                    position[0]+=maxheight[str(DV.preference_type_profile)]+max((maxheight[str(DV.preference_type_video)],maxheight[str(DV.preference_type_audio)]))
                position[0]+=currentprefsinsection[str(DV.preferences[i]['type'])]
                controlposition=(position[0],position[1]+1)
                controlspan=(1,maxwidth[str(DV.preferences[i]['type'])]-1)
                currentprefsinsection[str(DV.preferences[i]['type'])]+=1
                if DV.preferences[i]['kind']!='bool':
                    label=wx.StaticText(self.prefpane,-1,DV.preferences[i]['name']+':')
                    self.prefpanesizer.Add(label,(position[0],position[1]),(1,1),wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
                if type(DV.preferences[i]['kind']) is type({}):
                    choices=['(default)']
                    for f in DV.preferences[i]['order']:
                        choices.append(DV.preferences[i]['kind'][f])
                    if not val:
                        val='(default)'
                    else:
                        if val in DV.preferences[i]['kind']:
                            val=DV.preferences[i]['kind'][val]
                    self.controls[i]=self.makeList(DV.preferences[i]['strict'],choices,self.prefpane,val) # makeList takes care of the event binding
                    self.prefpanesizer.Add(self.controls[i],controlposition,controlspan,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
                elif DV.preferences[i]['kind'][0]=='%':
                    self.controls[i]=self.makeSlider(self.prefpane,self.prefpanesizer,(controlposition,controlspan),int(100.0*float(val)/float(str(DV.preferences[i]['kind'][1:]))),0,200)
                elif DV.preferences[i]['kind']=='bool':
                    if DV.preferences[i]['align']:
                        self.controls[i]=wx.CheckBox(self.prefpane,-1)
                        label=wx.StaticText(self.prefpane,-1,DV.preferences[i]['name'])
                        label.Bind(wx.EVT_LEFT_UP,DamnCurry(self.onFakeCheckboxLabelClick,self.controls[i]))
                        self.prefpanesizer.Add(self.controls[i],(position[0],position[1]),(1,1),wx.ALIGN_RIGHT)
                        self.prefpanesizer.Add(label,(position[0],position[1]+1),(1,1),wx.EXPAND)
                    else:
                        self.controls[i]=wx.CheckBox(self.prefpane,-1,DV.preferences[i]['name'])
                        self.prefpanesizer.Add(self.controls[i],(position[0],position[1]),(1,maxwidth[str(DV.preferences[i]['type'])]),wx.EXPAND)
                    self.controls[i].SetValue(val=='True')
                    self.Bind(wx.EVT_CHECKBOX,self.onPrefChange,self.controls[i])
                elif DV.preferences[i]['kind'][0:3]=='int':
                    choices=['(default)']
                    if DV.preferences[i]['kind'][0:5]=='intk:':
                        for f in range(int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':')+1:DV.preferences[i]['kind'].find('-')]),int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-')+1:])):
                            choices.append(str(pow(2,f))+'k')
                        if not val:
                            val='(default)'
                        self.controls[i]=self.makeList(DV.preferences[i]['strict'],choices,self.prefpane,val) # makeList takes care of the event binding
                        self.prefpanesizer.Add(self.controls[i],controlposition,controlspan,wx.EXPAND)
                    elif DV.preferences[i]['kind'][0:4]=='int:':
                        interval=(int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':')+1:DV.preferences[i]['kind'].find('-')]),int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-')+1:]))
                        if not val:
                            val='0'
                        self.controls[i]=self.makeSlider(self.prefpane,self.prefpanesizer,(controlposition,controlspan),int(val),min(interval),max(interval))
                    elif DV.preferences[i]['kind']=='int':
                        if not val:
                            val='(default)'
                        self.controls[i]=self.makeList(False,['(default)'],self.prefpane,val)
                        self.prefpanesizer.Add(self.controls[i],controlposition,controlspan,wx.EXPAND)
                elif DV.preferences[i]['kind']=='dir':
                    pathpanel=wx.Panel(self.prefpane,-1)
                    pathsizer=wx.BoxSizer(wx.HORIZONTAL)
                    pathpanel.SetSizer(pathsizer)
                    self.prefpanesizer.Add(pathpanel,controlposition,controlspan,wx.EXPAND)
                    self.controls[i]=wx.TextCtrl(pathpanel,-1,val)
                    self.Bind(wx.EVT_TEXT,self.onPrefChange,self.controls[i])
                    pathsizer.Add(self.controls[i],1,wx.EXPAND)
                    pathsizer.Add((DV.control_hgap,0))
                    browseButton=DamnBrowseDirButton(pathpanel,-1,'Browse...',control=self.controls[i],title='Select DamnVid '+DV.version+'\'s output directory.',callback=self.onBrowseDir)
                    self.Bind(wx.EVT_BUTTON,browseButton.onBrowse,browseButton)
                    pathsizer.Add(browseButton,0)
                elif DV.preferences[i]['kind']=='text':
                    self.controls[i]=wx.TextCtrl(self.prefpane,-1,val)
                    self.Bind(wx.EVT_TEXT,self.onPrefChange,self.controls[i])
                    self.prefpanesizer.Add(self.controls[i],controlposition,controlspan,wx.EXPAND)
                elif DV.preferences[i]['kind']=='profile':
                    if DV.prefs.profiles:
                        choices=[]
                        for p in range(-1,DV.prefs.profiles):
                            choices.append(DV.prefs.getp(p,'name'))
                        self.controls[i]=self.makeList(DV.preferences[i]['strict'],choices,self.prefpane,None) # makeList takes care of the event binding
                        self.controls[i].SetSelection(int(val)+1)
                    else:
                        self.controls[i]=wx.StaticText(self.prefpane,-1,'No encoding profiles found!')
                    self.prefpanesizer.Add(self.controls[i],controlposition,controlspan,wx.EXPAND)
                count=count+1
            self.prefpanesizer.Layout()
            cols=self.prefpanesizer.GetCols()
            totalwidth=float(self.prefpanesizer.GetMinSize()[0]-(cols-1)*self.prefpanesizer.GetHGap())
            splitwidth=round(totalwidth/float(cols)-.5)
            lastrow=self.prefpanesizer.GetRows()
            for i in range(cols):
                try:
                    self.prefpanesizer.AddGrowableCol(i)
                except:
                    pass
                curwidth=splitwidth
                if i==cols-1:
                    curwidth+=totalwidth-splitwidth*cols
                self.prefpanesizer.Add((int(curwidth),0),(lastrow,i),(1,1))
            if module is not None:
                self.prefpanesizer.Add(self.buildModulePanel(self.prefpane,module,extended=True,buttons=False),(0,0),(1,self.prefpanesizer.GetCols()),wx.EXPAND)
        self.prefpanesizer.Layout() # Mandatory
        newsize=self.toppanel.GetBestSize()
        if newsize[0]>self.bestsize[0]:
            self.bestsize[0]=newsize[0]
        if newsize[1]>self.bestsize[1]:
            self.bestsize[1]=newsize[1]
        self.SetClientSize(newsize)
        self.SetClientSize(self.bestsize)
        self.Center()
    def getPrefWidth(self,pref):
        if type(DV.preferences[pref]['kind']) is type({}):
            return 2
        if DV.preferences[pref]['kind'][0:3]=='int':
            return 2
        if DV.preferences[pref]['kind']=='profile':
            return 2
        if DV.preferences[pref]['kind'][0]=='%':
            return 2
        if DV.preferences[pref]['kind']=='text':
            return 2
        if DV.preferences[pref]['kind']=='dir':
            return 2 # Label + Panel{TextCtrl + Button} = 2
        if DV.preferences[pref]['kind']=='bool':
            return 1
        return 0
    def onFakeCheckboxLabelClick(self,checkbox,event):
        checkbox.SetValue(not checkbox.IsChecked())
    def splitLongPref(self,pref):
        if pref.find(':')==-1:
            return pref
        return (pref[0:pref.find(':')],pref[pref.find(':')+1:])
    def onPrefChange(self,event):
        name=None
        for i in self.controls.iterkeys():
            pref=self.splitLongPref(i)
            prefname=pref[1]
            if pref[0][0:16]=='damnvid-profile-':
                genericpref=pref[0][0:15]
            else:
                genericpref=pref[0]
            genericpref+=':'+pref[1]
            val=None
            if type(DV.preferences[genericpref]['kind']) is type({}) or (DV.preferences[genericpref]['kind'][0:3]=='int' and DV.preferences[genericpref]['kind'][0:4]!='int:'):
                if DV.preferences[genericpref]['strict']:
                    val=self.controls[i].GetSelection()
                    if val:
                        val=DV.preferences[genericpref]['order'][val-1]
                    else:
                        val=''
                else:
                    val=self.controls[i].GetValue()
                    if val=='(default)':
                        val=''
                    elif type(DV.preferences[genericpref]['kind']) is type({}) and val in DV.preferences[genericpref]['kind'].values():
                        for j in DV.preferences[genericpref]['kind'].iterkeys():
                            if val==DV.preferences[genericpref]['kind'][j]:
                                val=j
            elif DV.preferences[genericpref]['kind']=='profile':
                val=self.controls[i].GetSelection()-1
            elif DV.preferences[genericpref]['kind'][0:4]=='int:':
                val=int(self.controls[i].GetValue())
            elif DV.preferences[genericpref]['kind'][0]=='%':
                val=float(float(self.controls[i].GetValue())*float(int(DV.preferences[genericpref]['kind'][1:]))/100.0)
            elif DV.preferences[genericpref]['kind']=='dir' or DV.preferences[genericpref]['kind']=='text':
                val=self.controls[i].GetValue()
                if genericpref=='damnvid-profile:name':
                    name=val
            elif DV.preferences[genericpref]['kind']=='bool':
                val=self.controls[i].IsChecked() # The str() representation takes care of True/False
            if val is not None:
                DV.prefs.sets(self.pane,prefname,str(val))
        if name!=None and self.tree.GetSelection()!=self.treeroot and self.tree.GetItemParent(self.tree.GetSelection())==self.profileroot:
            self.tree.SetItemText(self.tree.GetSelection(),name)
            self.prefpanelabel.SetLabel(name)
    def onBrowseDir(self,button,path):
        for i in self.controls.iterkeys():
            if self.controls[i]==button.filefield:
                DV.prefs.sets(self.pane,self.splitLongPref(i)[1],path)
    def onAddProfile(self,event):
        DV.prefs.addp()
        self.profiles.append(self.tree.AppendItem(self.profileroot,DV.prefs.getp(DV.prefs.profiles-1,'name')))
        self.tree.SelectItem(self.profiles[-1],True)
    def onDeleteProfile(self,event):
        if self.tree.GetSelection()!=self.treeroot and self.tree.GetItemParent(self.tree.GetSelection())==self.profileroot:
            if len(self.profiles)>1:
                profile=int(self.pane[16:])
                DV.prefs.remp(profile)
                curprofile=self.tree.GetSelection()
                if not profile:
                    # User is deleting first profile
                    newprofile=self.tree.GetNextSibling(curprofile)
                else:
                    # User is not deleting first profile, all right
                    newprofile=self.tree.GetPrevSibling(curprofile)
                self.profiles.remove(curprofile)
                try:
                    self.tree.SelectItem(newprofile)
                except:
                    self.tree.SelectItem(self.profileroot)
                self.tree.Delete(curprofile)
            else:
                dlg=wx.MessageDialog(None,'Cannot delete all encoding profiles!','Cannot delete all profiles',wx.OK|wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Please choose a profile to delete from the profile list.','No profile selected',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onLoad(self,event):
        if self.tree.GetSelection()!=self.modulelistitem:
            return
        info=event.GetInfo()
        mod=info['module']['name']
        modtitle=info['module']['title']
        desc=self.moduledescs[mod]
        if type(info['result']) is type(''):
            if info['result']=='error':
                desc[0].SetLabel('There was an error while checking for updates to '+modtitle+'.')
                desc[0].Wrap(desc[1])
            elif info['result']=='uptodate':
                desc[0].SetLabel(modtitle+' is up-to-date.')
                desc[0].Wrap(desc[1])
            elif info['result']=='cannot':
                desc[0].SetLabel(modtitle+' has no update mechanism.')
                desc[0].Wrap(desc[1])
        elif type(info['result']) is type(()):
            self.buildTree()
            self.forceSelect(self.modulelistitem)
            desc=self.moduledescs[mod]
            desc[0].SetLabel(modtitle+' has been updated to version '+str(info['result'][0])+'.')
            desc[0].Wrap(desc[1])
        self.modulelist.Layout()
        self.modulelist.AdjustScrollbars()
    def onModuleUpdate(self,module=None,event=None):
        if not DV.modules.has_key(module):
            return
        module=DV.modules[module]
        desc=self.moduledescs[module['name']]
        if not module['about'].has_key('url'):
            desc[0].SetLabel(module['title']+' has no update mechanism.')
            desc[0].Wrap(desc[1])
            return
        desc[0].SetLabel('Checking for updates...')
        desc[0].Wrap(desc[1])
        updatecheck=DamnModuleUpdateCheck(self,module)
        updatecheck.start()
    def onModuleAllUpdate(self,event):
        modlist=[]
        for i in self.moduledescs.iterkeys():
            if DV.modules.has_key(i):
                modlist.append(DV.modules[i])
                self.moduledescs[i][0].SetLabel('Checking for updates...')
                self.moduledescs[i][0].Wrap(self.moduledescs[i][1])
        updatecheck=DamnModuleUpdateCheck(self,modlist)
        updatecheck.start()
    def onModuleAllReset(self,event):
        dlg=wx.MessageDialog(None,'Are you sure you want to reset all the default modules and their preferences?','Are you sure?',wx.YES_NO|wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_YES:
            for i in DV.prefs.listsections():
                if i[0:15]=='damnvid-module-':
                    DV.prefs.rems(i)
            DV.prefs.save()
            DamnLoadConfig(forcemodules=True)
            DV.prefs=DamnVidPrefs()
            self.buildTree()
            self.forceSelect(self.modulelistitem)
        dlg.Destroy()
    def onModuleInstall(self,event=None):
        dlg=wx.FileDialog(None,'Where is located the module to install?',DV.prefs.get('lastmoduledir'),'','DamnVid modules (*.module.damnvid)|*.module.damnvid|All files (*.*)|*.*',wx.FD_OPEN)
        dlg.SetIcon(DV.icon)
        result=None
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            DV.prefs.set('lastmoduledir',os.path.dirname(path))
            result=DamnInstallModule(path)
        dlg.Destroy()
        message=None
        if result is not None:
            if result=='success':
                message=('Success!','The module was successfully installed.',wx.ICON_INFORMATION)
            elif result=='nofile':
                message=('Error','Error: Could not find the module file.',wx.ICON_ERROR)
            elif result=='nomodule':
                message=('Error','Error: This file is not a valid DamnVid module.',wx.ICON_ERROR)
            else:
                message=('Error','Error: Unknown error while installing module.',wx.ICON_ERROR)
        if message is not None:
            DamnLoadConfig()
            DV.prefs=DamnVidPrefs()
            self.buildTree()
            self.forceSelect(self.modulelistitem)
            dlg=wx.MessageDialog(None,message[1],message[0],message[2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onModuleUninstall(self,module=None,event=None):
        if not DV.modules.has_key(module):
            return
        dlg=wx.MessageDialog(None,'Are you sure you want to uninstall the '+DV.modules[module]['title']+' module?','Are you sure?',wx.YES_NO|wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_YES:
            del DV.modules[module]
            try:
                shutil.rmtree(DV.modules_path+module)
            except:
                pass
            DV.prefs.rems('damnvid-module-'+module)
            self.buildTree()
            self.forceSelect(self.modulelistitem)
        dlg.Destroy()
    def makeList(self,strict,choices,panel,value):
        if strict:
            cont=wx.Choice(panel,-1,choices=choices)
            if value=='(default)':
                cont.SetSelection(0)
            else:
                for f in range(len(choices)):
                    if choices[f]==value:
                        cont.SetSelection(f)
            self.Bind(wx.EVT_CHOICE,self.onPrefChange,cont)
        else:
            cont=wx.ComboBox(panel,-1,choices=choices,value=value)
            cont.SetValue(value) # Fixes bug on OS X where the value wouldn't be set if it's not one of the choices
            self.Bind(wx.EVT_TEXT,self.onPrefChange,cont)
        return cont
    def makeSlider(self,panel,sizer,position,value,minval,maxval):
        value=min((maxval,max((int(minval),int(value)))))
        tmppanel=wx.Panel(panel,-1)
        tmpsizer=wx.BoxSizer(wx.HORIZONTAL)
        tmppanel.SetSizer(tmpsizer)
        containersizer=wx.BoxSizer(wx.VERTICAL)
        tmpsizer.Add(containersizer,7,wx.ALIGN_CENTER_VERTICAL)
        containersizer.Add((0,1))
        slider=wx.Slider(tmppanel,-1,value=value,minValue=minval,maxValue=maxval,style=wx.SL_HORIZONTAL)
        containersizer.Add(slider,1,wx.EXPAND)
        containersizer.Add((0,1))
        tmplabel=wx.StaticText(tmppanel,-1,str(value))
        tmpsizer.Add(tmplabel,1,wx.ALIGN_CENTER_VERTICAL)
        self.Bind(wx.EVT_SLIDER,DamnCurry(self.updateSlider,slider,tmplabel),slider)
        sizer.Add(tmppanel,position[0],position[1],wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        return slider
    def updateSlider(self,slider,label,event=None):
        label.SetLabel(str(slider.GetValue()))
        self.onPrefChange(event)
    def getListValue(self,name,strict):
        if strict:
            val=self.listvalues[name][self.controls[name].GetSelection()]
        else:
            val=self.controls[name].GetValue()
        if val=='(default)':
            val=''
        elif type(DV.preference_type[name]['kind']) is type({}):
            for key,i in DV.preference_type[name]['kind'].iteritems():
                if i==val:
                    return key
        return val
    def setListValue(self,name,strict,value):
        if not value:
            if strict:
                self.controls[name].SetSelection(0)
            else:
                self.controls[name].SetValue('(default)')
        else:
            if strict:
                if type(DV.preference_type[name]['kind']) is type({}):
                    value=DV.preference_type[name]['kind'][value]
                c=0
                for i in self.listvalues[name]:
                    if i==value:
                        self.controls[name].SetSelection(c)
                    c=c+1
            else:
                self.controls[name].SetValue(value)
    def onOK(self,event):
        DV.prefs.save()
        self.Close(True)
    def onReset(self,event):
        dlg=wx.MessageDialog(None,'All changes to DamnVid\'s configuration will be lost. Continue?','Are you sure?',wx.YES_NO|wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_YES:
            dlg.Destroy()
            checkupdates=DV.prefs.get('checkforupdates')
            DV.prefs=None
            os.remove(DV.conf_file)
            shutil.copyfile(DV.curdir+'conf'+os.sep+'conf.ini',DV.conf_file)
            DamnLoadConfig(forcemodules=True)
            DV.prefs=DamnVidPrefs()
            DV.prefs.set('checkforupdates',checkupdates)
            DV.prefs.save()
            self.buildTree()
            dlg=wx.MessageDialog(None,'DamnVid\'s configuration has been successfully reset.','Configuration reset',wx.OK|wx.ICON_INFORMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
        dlg.Destroy()
    def onImport(self,event):
        dlg=wx.FileDialog(None,'Where is located the configuration file to import?',DV.prefs.get('lastprefdir'),'DamnVid-'+DV.version+'-configuration.ini','INI files (*.ini)|*.ini|All files (*.*)|*.*',wx.FD_OPEN)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_OK:
            self.tree.SelectItem(self.treeroot,True)
            path=dlg.GetPath()
            dlg.Destroy()
            DV.prefs.set('lastprefdir',path)
            f=open(path,'r')
            testprefs=ConfigParser.SafeConfigParser()
            allOK=False
            try:
                testprefs.readfp(f)
                f.close()
                allOK=True
            except:
                try:
                    f.close()
                except:
                    pass
                dlg=wx.MessageDialog(None,'Invalid configuration file.','Invalid file',wx.OK|wx.ICON_ERROR)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            if allOK:
                keepgoing=True
                while keepgoing:
                    keepgoing=DV.prefs.remp(0) is not None
                for i in testprefs.sections():
                    try:
                        DV.prefs.ini.add_section(i)
                    except:
                        pass
                    for j in testprefs.options(i):
                        DV.prefs.sets(i,j,testprefs.get(i,j))
                self.parent.reopenprefs=True
                self.onOK(None)
        else:
            dlg.Destroy()
    def onExport(self,event):
        dlg=wx.FileDialog(None,'Where do you want to export DamnVid '+DV.version+'\'s configuration?',DV.prefs.get('lastprefdir'),'DamnVid-'+DV.version+'-configuration.ini','INI files (*.ini)|*.ini|All files (*.*)|*.*',wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            DV.prefs.set('lastprefdir',path)
            f=open(path,'w')
            DV.prefs.ini.write(f)
            f.close()
        dlg.Destroy()
    def onKeyDown(self,event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE,wx.WXK_CANCEL):
            self.onClose(event)
        elif event.GetKeyCode() in (wx.WXK_NUMPAD_ENTER,wx.WXK_RETURN,wx.WXK_EXECUTE):
            self.onOK(event)
    def onClose(self,event):
        DV.prefs=DamnVidPrefs() # Reload from ini
        self.Close(True)
class DamnVideoLoader(thr.Thread):
    def __init__(self,parent,uris,thengo=False,feedback=True):
        thr.Thread.__init__(self)
        self.uris=uris
        self.parent=parent
        self.thengo=thengo
        self.feedback=feedback
        self.done=False
        self.result=None
    def run(self):
        if self.feedback:
            self.parent.toggleLoading(True)
        self.vidLoop(self.uris)
        self.done=True
        if self.feedback:
            self.parent.toggleLoading(False)
        else:
            while self.done:
                time.sleep(.1)
    def postEvent(self,info):
        if self.feedback:
            wx.PostEvent(self.parent,DamnLoadingEvent(DV.evt_loading,-1,info))
    def getVidName(self,uri):
        return self.parent.getVidName(uri)
    def addValid(self,meta):
        meta['original']=self.originaluri
        self.result=meta
        self.postEvent({'meta':meta,'go':self.thengo})
    def SetStatusText(self,status):
        self.postEvent({'status':status})
    def showDialog(self,title,content,icon):
        self.postEvent({'dialog':(title,content,icon)})
    def getDefaultProfile(self,profile):
        return int(DV.prefs.getd(profile))
    def vidLoop(self,uris):
        for uri in uris:
            self.originaluri=uri
            bymodule=False
            for module in DamnIterModules(False):
                mod=module['class'](uri)
                if mod.validURI():
                    mod.addVid(self)
                    bymodule=True
                    break
            if not bymodule:
                if REGEX_HTTP_GENERIC.match(uri):
                    name=self.getVidName(uri)
                    if name=='Unknown title':
                        name=REGEX_HTTP_EXTRACT_FILENAME.sub('',uri)
                    self.addValid({'name':name,'profile':DV.prefs.get('defaultwebprofile'),'profilemodified':False,'fromfile':name,'dirname':REGEX_HTTP_EXTRACT_DIRNAME.sub('\\1/',uri),'uri':uri,'status':'Pending.','icon':DamnGetListIcon('generic')})
                else:
                    # It's a file or a directory
                    if os.path.isdir(uri):
                        if DV.prefs.get('DirRecursion')=='True':
                            for i in os.listdir(uri):
                                self.vidLoop([uri+os.sep+i]) # This is recursive; if i is a directory, this block will be executed for it too
                        else:
                            if len(uris)==1: # Only one dir, so an alert here is tolerable
                                self.showDialog('Recursion is disabled.','This is a directory, but recursion is disabled in the preferences. Please enable it if you want DamnVid to go through directories.',wx.OK|wx.ICON_EXCLAMATION)
                            else:
                                self.SetStatusText('Skipped '+uri+' (directory recursion disabled).')
                    else:
                        filename=os.path.basename(uri)
                        if uri in self.parent.videos:
                            self.SetStatusText('Skipped '+filename+' (already in list).')
                            if len(uris)==1: # There's only one file, so an alert here is tolerable
                                self.showDialog('Duplicate found','This video is already in the list!',wx.ICON_EXCLAMATION|wx.OK)
                        else:
                            self.addValid({'name':filename[0:filename.rfind('.')],'profile':DV.prefs.get('defaultprofile'),'profilemodified':False,'fromfile':filename,'uri':uri,'dirname':os.path.dirname(uri),'status':'Pending.','icon':DamnGetListIcon('damnvid')})
class DamnConverter(thr.Thread): # The actual converter, dammit
    def __init__(self,parent):
        self.parent=parent
        self.sourceuri=parent.videos[parent.converting]
        self.outdir=None
        self.filename=None
        self.tmpfilename=None
        self.moduleextraargs=[]
        thr.Thread.__init__(self)
    def getURI(self,uri):
        if self.parent.meta[self.sourceuri].has_key('downloadgetter') and self.parent.meta[self.sourceuri].has_key('module'):
            if self.parent.meta[self.sourceuri]['module'] is not None:
                uri=self.parent.meta[self.sourceuri]['downloadgetter']()
                self.moduleextraargs=self.parent.meta[self.sourceuri]['module'].getFFmpegArgs()
                if not self.parent.meta[self.sourceuri]['profilemodified']:
                    self.outdir=self.parent.meta[self.sourceuri]['module'].getOutdir()
                if type(uri) in (type(''),type(u'')):
                    uri=[uri]
                return uri
        return [uri]
    def cmd2str(self,cmd):
        s=''
        for i in cmd:
            i=i.replace('?DAMNVID_VIDEO_STREAM?',self.stream).replace('?DAMNVID_VIDEO_PASS?',str(self.passes)).replace('?DAMNVID_OUTPUT_FILE?',DV.tmp_path+self.tmpfilename)
            if i.find(' ')!=-1 or i.find('&')!=-1 or i.find('|')!=-1 or i.find('<')!=-1 or i.find('>')!=-1:
                s+='"'+i.replace('"','\'\'')+'" '
            else:
                s+=i+' '
        return s[0:len(s)-1]
    def gettmpfilename(self,path,prefix,ext):
        tmpfilename=prefix+'-0'+ext
        tmpcount=0
        while os.path.lexists(path+tmpfilename):
            tmpcount+=1
            tmpfilename=prefix+'-'+str(tmpcount)+ext
        f=open(path+tmpfilename,'wb')   # Just create the file
        f.close()
        return tmpfilename
    def getfinalfilename(self,path,prefix,ext):
        if not os.path.lexists(path+prefix+ext):
            return prefix
        c=2
        while os.path.lexists(path+prefix+' ('+str(c)+')'+ext):
            c=c+1
        return prefix+' ('+str(c)+')'
    def update(self,progress=None,statustext=None,status=None,dialog=None,go=None):
        info={}
        if progress is not None:
            info['progress']=float(progress)
        if statustext is not None:
            info['statustext']=unicode(statustext)
        if status is not None:
            info['status']=unicode(status)
        if dialog is not None:
            info['dialog']=dialog
        if go is not None:
            info['go']=go
        wx.PostEvent(self.parent,DamnProgressEvent(DV.evt_progress,-1,info))
    def run(self):
        self.uris=self.getURI(self.sourceuri)
        self.abort=False
        if not self.abort:
            try:
                self.uri=self.uris[0]
                self.update(0)
                self.parent.thisvideo.append(self.parent.videos[self.parent.converting])
                self.filename=unicodedata.normalize('NFKD',unicode(REGEX_FILE_CLEANUP_FILENAME.sub('',self.parent.meta[self.parent.videos[self.parent.converting]]['name']))).encode('utf8','ignore').replace('/','').replace('\\','').strip() # Gotta convert to utf-8, because subprocess doesn't handle unicode strings very nicely
                self.profile=int(self.parent.meta[self.parent.videos[self.parent.converting]]['profile'])
                if os.path.lexists(self.uri):
                    self.stream=self.uri # It's a file stream, ffmpeg will take care of it
                    if self.outdir is None:
                        self.outdir=DV.prefs.get('defaultoutdir')
                else:
                    self.stream='-' # It's another stream, spawn a downloader thread to take care of it and pipe the content to ffmpeg via stdin
                    if self.outdir is None:
                        self.outdir=DV.prefs.get('defaultweboutdir')
                if self.outdir[-1:]==os.sep:
                    self.outdir=self.outdir[0:-1]
                if not os.path.lexists(self.outdir):
                    os.makedirs(self.outdir)
                elif not os.path.isdir(self.outdir):
                    os.remove(self.outdir)
                    os.makedirs(self.outdir)
                self.outdir=self.outdir+os.sep
                if self.profile==-1: # Do not encode, just copy
                    try:
                        failed=False
                        if self.stream=='-': # Spawn a downloader
                            src=DamnURLPicker(self.uris)
                            total=int(src.info()['Content-Length'])
                            ext='avi'
                            try:
                                if src.info()['Content-Type'].lower().find('audio')!=-1:
                                    ext='mp3'
                            except:
                                ext='avi'
                            try:
                                tmpuri=src.info()['Content-Disposition'][src.info()['Content-Disposition'].find('filename=')+9:]
                            except:
                                tmpuri='Video.'+ext # And pray for the best!
                        else: # Just copy the file, lol
                            total=int(os.lstat(self.stream).st_size)
                            src=open(self.stream,'rb')
                            tmpuri=self.stream
                        if REGEX_URI_EXTENSION_EXTRACT.search(tmpuri):
                            ext='.'+REGEX_URI_EXTENSION_EXTRACT.sub('\\1',tmpuri)
                        else:
                            ext='.avi' # And pray for the best again!
                        self.filename=self.getfinalfilename(self.outdir,self.filename,ext)
                        dst=open(self.outdir+self.filename+ext,'wb')
                        keepgoing=True
                        copied=0.0
                        lasttime=0.0
                        self.update(statustext='Copying '+self.parent.meta[self.parent.videos[self.parent.converting]]['name']+' to '+self.filename+ext+'...')
                        while keepgoing and not self.abort:
                            i=src.read(4096)
                            if len(i):
                                dst.write(i)
                                copied+=4096.0
                            else:
                                copied=float(total)
                                keepgoing=False
                            progress=min((100.0,copied/total*100.0))
                            nowtime=float(time.time())
                            if lasttime+.5<nowtime or not keepgoing: # Do not send a progress update more than 2 times per second, otherwise the event queue can get overloaded. On some platforms, time() is an int, but that doesn't matter; the progress will be updated once a second instead of 2 times, which is still acceptable.
                                self.update(progress,status=self.parent.meta[self.parent.videos[self.parent.converting]]['status']+' ['+str(int(progress))+'%]')
                                lasttime=nowtime
                    except:
                        failed=True
                    self.grabberrun=False
                    if self.abort or failed:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Failure.'
                        self.update(status='Failure.')
                    else:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Success!'
                        self.update(status='Success!')
                        self.parent.resultlist.append((self.parent.meta[self.parent.videos[self.parent.converting]]['name'],self.outdir))
                    self.update(go=self.abort)
                    return
                os_exe_ext=''
                if DV.os=='nt':
                    os_exe_ext='.exe'
                elif DV.os=='mac':
                    os_exe_ext='osx'
                self.passes=1
                cmd=[DV.bin_path+'ffmpeg'+os_exe_ext,'-i','?DAMNVID_VIDEO_STREAM?','-y','-deinterlace','-passlogfile',DV.tmp_path+'pass']
                for i in DV.preferences.keys():
                    if i[0:25]=='damnvid-profile:encoding_':
                        i=i[16:]
                        pref=DV.prefs.getp(self.profile,i)
                        if pref:
                            if type(DV.preferences['damnvid-profile:'+i]['kind']) in (type(''),type(u'')):
                                if DV.preferences['damnvid-profile:'+i]['kind'][0]=='%':
                                    pref=str(round(float(pref),0)) # Round
                            if i=='encoding_pass':
                                pref='?DAMNVID_VIDEO_PASS?'
                            if i[9:]=='b' and pref=='sameq':
                                cmd.append('-sameq')
                            else:
                                cmd.extend(['-'+i[9:],pref])
                self.encodevideo=DV.prefs.getp(self.profile,'video')
                self.encodeaudio=DV.prefs.getp(self.profile,'audio')
                if not self.encodevideo:
                    cmd.append('-vn')
                if not self.encodeaudio:
                    cmd.append('-an')
                vidformat=DV.prefs.getp(self.profile,'Encoding_f')
                self.vcodec=DV.prefs.getp(self.profile,'Encoding_vcodec')
                self.acodec=DV.prefs.getp(self.profile,'Encoding_acodec')
                self.totalpasses=DV.prefs.getp(self.profile,'Encoding_pass')
                if not self.totalpasses:
                    self.totalpasses=1
                else:
                    self.totalpasses=int(self.totalpasses)
                if vidformat and DV.file_ext.has_key(vidformat):
                    ext='.'+DV.file_ext[vidformat]
                else:
                    if self.vcodec and self.encodevideo and DV.file_ext_by_codec.has_key(self.vcodec):
                        ext='.'+DV.file_ext_by_codec[self.vcodec]
                    elif self.encodeaudio and not self.encodevideo:
                        if DV.file_ext_by_codec.has_key(self.acodec):
                            ext='.'+DV.file_ext_by_codec[self.acodec]
                        else:
                            ext='.mp3'
                    else:
                        ext='.avi'
                flags=[]
                if self.vcodec and DV.codec_advanced_cl.has_key(self.vcodec):
                    for o in DV.codec_advanced_cl[self.vcodec]:
                        if type(o) in (type(''),type(u'')):
                            if o not in flags: # If the flag is already there, don't add it again
                                flags.append(o)
                        else:
                            if '-'+o[0] not in cmd: # If the option is already there, don't overwrite it
                                cmd.extend(['-'+o[0],o[1]])
                if len(flags):
                    cmd.extend(['-flags',''.join(flags)])
                self.filename=self.getfinalfilename(self.outdir,self.filename,ext)
                self.filenamenoext=self.filename
                self.tmpfilename=self.gettmpfilename(DV.tmp_path,self.filenamenoext,ext)
                cmd.append('?DAMNVID_OUTPUT_FILE?')
                if len(self.moduleextraargs):
                    cmd.extend(self.moduleextraargs)
                self.filename=self.filenamenoext+ext
                self.duration=None
                self.update(statustext=u'Converting '+unicode(self.parent.meta[self.parent.videos[self.parent.converting]]['name'])+u' to '+unicode(self.filename.decode('utf8'))+u'...')
                while int(self.passes)<=int(self.totalpasses) and not self.abort:
                    if self.totalpasses!=1:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Pass '+str(self.passes)+'/'+str(self.totalpasses)+'...'
                        self.update(status='Pass '+str(self.passes)+'/'+str(self.totalpasses)+'...')
                        if self.stream=='-':
                            if self.passes==1:
                                self.tmppassfile=DV.tmp_path+self.gettmpfilename(DV.tmp_path,self.filenamenoext,ext)
                            else:
                                self.stream=self.tmppassfile
                        if self.passes!=1:
                            self.tmpfilename=self.gettmpfilename(DV.tmp_path,self.filenamenoext,ext)
                    self.process=DamnSpawner(self.cmd2str(cmd),stderr=subprocess.PIPE,stdin=subprocess.PIPE,cwd=os.path.dirname(DV.tmp_path))
                    if self.stream=='-' and self.sourceuri[0:3]!='gv:':
                        if self.totalpasses!=1:
                            self.feeder=DamnDownloader(self.uris,self.process.stdin,self.tmppassfile)
                        else:
                            self.feeder=DamnDownloader(self.uris,self.process.stdin)
                        self.feeder.start()
                    curline=''
                    while self.process.poll()==None and not self.abort:
                        c=self.process.stderr.read(1)
                        curline+=c
                        if c=='\r' or c=='\n':
                            self.parseLine(curline)
                            curline=''
                    self.passes+=1
                self.update(100)
                result=self.process.poll() # The process is complete, but .poll() still returns the process's return code
                time.sleep(.25) # Wait a bit
                self.grabberrun=False # That'll make the DamnConverterGrabber wake up just in case
                if result and os.path.lexists(DV.tmp_path+self.tmpfilename):
                    os.remove(DV.tmp_path+self.tmpfilename) # Delete the output file if ffmpeg has exitted with a bad return code
            except:
                result=1
                Damnlog('Error in main conversion routine.')
            for i in os.listdir(os.path.dirname(DV.tmp_path)):
                if i[0:8]=='damnvid-':
                    i=i[8:]
                    if i==self.tmpfilename and not result and not self.abort:
                        try:
                            os.rename(DV.tmp_path+i,self.outdir+self.filename)
                        except: # Maybe the file still isn't unlocked, it happens... Wait moar and retry
                            try:
                                time.sleep(2)
                                os.rename(DV.tmp_path+i,self.outdir+self.filename)
                            except: # Now this is really bad, alert the user
                                try: # Manual copy, might be needed if we're working on two different filesystems on a non-Windows platform
                                    src=open(DV.tmp_path+i,'rb')
                                    dst=open(self.outdir+self.filename,'wb')
                                    for fileline in src.readlines():
                                        dst.write(fileline)
                                    try: # Another try block in order to avoid raising the huge except block with the dialog
                                        src.close()
                                        dst.close()
                                        os.remove(DV.tmp_path+i)
                                    except:
                                        pass
                                except:
	                            self.update(dialog=('Cannot move file!','DamnVid successfully converted the file but something (File permissions? Disconnected removable device?) prevents it from moving it to the output directory.\nAll hope is not lost, you can still move the file by yourself. It is here:\n'+DV.tmp_path+i,wx.OK|wx.ICON_EXCLAMATION))
                    else:
                        try:
                            os.remove(DV.tmp_path+i)
                        except:
                            pass
            if not result and not self.abort:
                self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Success!'
                self.parent.resultlist.append((self.parent.meta[self.parent.videos[self.parent.converting]]['name'],self.outdir))
                self.update(status='Success!',go=self.abort)
                return
            self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Failure.'
            self.update(status='Failure.',go=self.abort)
    def parseLine(self,line):
        print line.strip()
        if self.duration==None:
            res=REGEX_FFMPEG_DURATION_EXTRACT.search(line)
            if res:
                self.duration=int(res.group(1))*3600+int(res.group(2))*60+float(res.group(3))
                if not self.duration:
                    self.duration=None
        else:
            res=REGEX_FFMPEG_TIME_EXTRACT.search(line)
            if res:
                wx.PostEvent(self.parent,DamnProgressEvent(DV.evt_progress,-1,{
                    'progress':float(float(res.group(1))/self.duration/float(self.totalpasses)+float(float(self.passes-1)/float(self.totalpasses)))*100.0,
                    'status':self.parent.meta[self.parent.videos[self.parent.converting]]['status']+' ['+str(int(100.0*float(res.group(1))/self.duration))+'%]'
                }))
    def abortProcess(self): # Cannot send "q" because it's not a shell'd subprocess. Got to kill ffmpeg.
        self.abort=True # This prevents the converter from going to the next file
        if self.profile!=-1:
            if DV.os=='nt':
                DamnSpawner('"'+DV.bin_path+'taskkill.exe" /PID '+str(self.process.pid)+' /F').wait()
            elif DV.os=='mac':
                DamnSpawner('kill -SIGTERM '+str(self.process.pid)).wait() # From http://www.cs.cmu.edu/~benhdj/Mac/unix.html but with SIGTERM instead of SIGSTOP
            else:
                os.kill(self.process.pid,signal.SIGTERM)
            time.sleep(.5) # Wait a bit, let the files get unlocked
            try:
                os.remove(self.outdir+self.tmpfilename)
            except:
                pass # Maybe the file wasn't created yet
class DamnDownloader(thr.Thread): # Retrieves video by HTTP and feeds it back to ffmpeg via stdin
    def __init__(self,uri,pipe,copy=None):
        self.uri=uri
        self.pipe=pipe
        self.copy=copy
        thr.Thread.__init__(self)
    def run(self):
        self.http=DamnURLPicker(self.uri)
        if self.http==None:
            try:
                self.pipe.close() # This tells ffmpeg that it's the end of the stream
            except:
                pass
            return None
        writing=''
        direct=False
        if self.copy!=None:
            copystream=open(self.copy,'wb')
        for i in self.http:
            try:
                if direct:
                    self.pipe.write(i)
                    if self.copy!=None:
                        copystream.write(i)
                else:
                    writing+=i
                    if len(writing)>102400: # Cache the first 100 KB and write them all at once (solves ffmpeg's "moov atom not found" problem)
                        self.pipe.write(writing)
                        if self.copy!=None:
                            copystream.write(writing)
                        direct=True
                        del writing
            except:
                break
        if not direct:  # Video weighs less than 100 KB (!)
            try:
                self.pipe.write(writing)
                if self.copy!=None:
                    copystream.write(writing)
            except:
                pass
        try:
            self.http.close()
        except:
            pass
        try:
            self.pipe.close() # This tells ffmpeg that it's the end of the stream
        except:
            pass
        try:
            copystream.close() # Might not be defined, but doesn't matter
        except:
            pass
class DamnMainFrame(wx.Frame): # The main window
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(780,580),style=wx.DEFAULT_FRAME_STYLE)
        self.CreateStatusBar()
        filemenu=wx.Menu()
        filemenu.Append(ID_MENU_ADD_FILE,'&Add files...','Adds damn videos from local files.')
        self.Bind(wx.EVT_MENU,self.onAddFile,id=ID_MENU_ADD_FILE)
        filemenu.Append(ID_MENU_ADD_URL,'Add &URL...','Adds a damn video from a URL.')
        self.Bind(wx.EVT_MENU,self.onAddURL,id=ID_MENU_ADD_URL)
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_EXIT,'E&xit','Terminates DamnVid '+DV.version+'.')
        self.Bind(wx.EVT_MENU,self.onExit,id=ID_MENU_EXIT)
        vidmenu=wx.Menu()
        vidmenu.Append(ID_MENU_GO,'Let\'s &go!','Processes all the videos in the list.')
        self.Bind(wx.EVT_MENU,self.onGo,id=ID_MENU_GO)
        vidmenu.AppendSeparator()
        self.prefmenuitem=vidmenu.Append(ID_MENU_PREFERENCES,'Preferences','Opens DamnVid\'s preferences, allowing you to customize its settings.')
        self.Bind(wx.EVT_MENU,self.onPrefs,id=ID_MENU_PREFERENCES)
        #vidmenu.Append(ID_MENU_OUTDIR,'Output directory','Opens DamnVid\'s output directory, where all the videos are saved.')
        #self.Bind(wx.EVT_MENU,self.onOpenOutDir,id=ID_MENU_OUTDIR)
        halpmenu=wx.Menu()
        halpmenu.Append(ID_MENU_HALP,'DamnVid &Help','Opens DamnVid\'s help.')
        self.Bind(wx.EVT_MENU,self.onHalp,id=ID_MENU_HALP)
        halpmenu.Append(ID_MENU_UPDATE,'Check for updates...','Checks if a new version of DamnVid is available.')
        self.Bind(wx.EVT_MENU,self.onCheckUpdates,id=ID_MENU_UPDATE)
        halpmenu.AppendSeparator()
        halpmenu.Append(ID_MENU_ABOUT,'&About DamnVid '+DV.version+'...','Displays information about DamnVid.')
        self.Bind(wx.EVT_MENU,self.onAboutDV,id=ID_MENU_ABOUT)
        self.menubar=wx.MenuBar()
        self.menubar.Append(filemenu,'&File')
        self.menubar.Append(vidmenu,'&DamnVid')
        self.menubar.Append(halpmenu,'&Help')
        self.SetMenuBar(self.menubar)
        vbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        #vbox.Add((0,DV.border_padding)) Actually, do NOT add a padding there, it looks better when stuck on the edge
        panel=wx.Panel(self,-1)
        vbox.Add(panel,1,wx.EXPAND)
        grid=wx.FlexGridSizer(2,2,8,8)
        panel1=wx.Panel(panel,-1)
        grid.Add(panel1,1,wx.EXPAND)
        panel2=wx.Panel(panel,-1)
        grid.Add(panel2,0,wx.EXPAND)
        panel3=wx.Panel(panel,-1)
        grid.Add(panel3,0,wx.EXPAND)
        panel4=wx.Panel(panel,-1)
        grid.Add(panel4,0,wx.EXPAND)
        panel.SetSizer(grid)
        hbox1=wx.BoxSizer(wx.HORIZONTAL)
        #hbox1.Add((DV.border_padding,0)) Ditto
        panel1.SetSizer(hbox1)
        self.list=DamnList(panel1,window=self)
        self.list.InsertColumn(ID_COL_VIDNAME,'Video name')
        self.list.SetColumnWidth(ID_COL_VIDNAME,width=180)
        self.list.InsertColumn(ID_COL_VIDPROFILE,'Encoding profile')
        self.list.SetColumnWidth(ID_COL_VIDPROFILE,width=120)
        self.list.InsertColumn(ID_COL_VIDSTAT,'Status')
        self.list.SetColumnWidth(ID_COL_VIDSTAT,width=120)
        self.list.InsertColumn(ID_COL_VIDPATH,'Source')
        self.list.SetColumnWidth(ID_COL_VIDPATH,wx.LIST_AUTOSIZE)
        self.list.Bind(wx.EVT_KEY_DOWN,self.onListKeyDown)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED,self.onListSelect)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.onListSelect)
        DV.listicons.initWX()
        self.list.AssignImageList(DV.listicons,wx.IMAGE_LIST_SMALL)
        self.list.SetDropTarget(DamnDropHandler(self))
        self.list.Bind(wx.EVT_RIGHT_DOWN,self.list.onRightClick)
        hbox1.Add(self.list,1,wx.EXPAND)
        vboxwrap2=wx.BoxSizer(wx.HORIZONTAL)
        sizer2=wx.BoxSizer(wx.VERTICAL)
        vboxwrap2.Add(sizer2)
        vboxwrap2.Add((DV.border_padding,0))
        sizer2.Add((0,DV.border_padding))
        panel2.SetSizer(vboxwrap2)
        self.droptarget=wx.animate.GIFAnimationCtrl(panel2,-1,DV.images_path+'droptarget.gif')
        self.droptarget.Bind(wx.EVT_LEFT_UP,self.onDropTargetClick)
        sizer2.Add(self.droptarget,0,wx.ALIGN_CENTER)
        self.droptarget.SetDropTarget(DamnDropHandler(self))
        # Extra forced gap here
        sizer2.Add((0,DV.control_vgap+4))
        self.addByFile=wx.Button(panel2,-1,'Add Files')
        sizer2.Add(self.addByFile,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onAddFile,self.addByFile)
        self.addByURL=wx.Button(panel2,-1,'Add URL')
        sizer2.Add(self.addByURL,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onAddURL,self.addByURL)
        self.btnSearch=wx.Button(panel2,-1,'Search...')
        sizer2.Add(self.btnSearch,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onSearch,self.btnSearch)
        self.btnRename=wx.Button(panel2,-1,'Rename')
        sizer2.Add(self.btnRename,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onRename,self.btnRename)
        self.profilepanel=wx.Panel(panel2,-1)
        profilepanelsizer=wx.BoxSizer(wx.VERTICAL)
        self.profilepanel.SetSizer(profilepanelsizer)
        profilepanelsizer.Add(wx.StaticText(self.profilepanel,-1,'Profile:'),0,wx.ALIGN_CENTER)
        self.profiledropdown=wx.Choice(self.profilepanel,-1,choices=['(None)'])
        profilepanelsizer.Add((0,DV.control_vgap))
        profilepanelsizer.Add(self.profiledropdown,0,wx.ALIGN_CENTER)
        sizer2.Add(self.profilepanel)
        tmplistheight=self.profiledropdown.GetSizeTuple()[1]
        self.profilepanel.Hide()
        sizer2.Add((0,DV.control_vgap))
        self.btnMoveUp=wx.Button(panel2,-1,'Move up')
        sizer2.Add(self.btnMoveUp,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onMoveUp,self.btnMoveUp)
        self.btnMoveDown=wx.Button(panel2,-1,'Move down')
        sizer2.Add(self.btnMoveDown,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onMoveDown,self.btnMoveDown)
        self.delSelection=wx.Button(panel2,-1,'Remove')
        sizer2.Add(self.delSelection,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onDelSelection,self.delSelection)
        self.delAll=wx.Button(panel2,-1,'Remove all')
        sizer2.Add(self.delAll,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.control_vgap))
        self.Bind(wx.EVT_BUTTON,self.onDelAll,self.delAll)
        self.gobutton1=wx.Button(panel2,-1,'Let\'s go!')
        sizer2.Add(self.gobutton1,0,wx.ALIGN_CENTER)
        sizer2.Add((0,DV.border_padding))
        buttonwidth=sizer2.GetMinSizeTuple()[0]
        self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton1)
        hbox3=wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add((DV.border_padding,0))
        panel3.SetSizer(hbox3)
        hbox3.Add(wx.StaticText(panel3,-1,'Current video: '),0,wx.ALIGN_CENTER_VERTICAL)
        self.gauge1=wx.Gauge(panel3,-1)
        self.gauge1.SetSize((self.gauge1.GetSizeTuple()[0],hbox3.GetSizeTuple()[1]))
        hbox3.Add(self.gauge1,1,wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
        #self.gobutton2=wx.Button(bottompanel,-1,'Let\'s go!')
        #self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton2)
        #grid.Add(wx.StaticText(bottompanel,-1,''),0)
        #grid.Add(self.gobutton2,0)
        #grid.Add(wx.StaticText(bottompanel,-1,'Total progress:'),0)
        #self.gauge2=wx.Gauge(bottompanel,-1)
        #grid.Add(self.gauge2,1,wx.EXPAND)
        hboxwrapper4=wx.BoxSizer(wx.HORIZONTAL)
        hbox4=wx.BoxSizer(wx.VERTICAL)
        hboxwrapper4.Add(hbox4)
        hboxwrapper4.Add((0,DV.border_padding))
        panel4.SetSizer(hboxwrapper4)
        self.stopbutton=wx.Button(panel4,-1,'Stop')
        for button in (self.addByFile,self.addByURL,self.btnRename,self.btnMoveUp,self.btnMoveDown,self.delSelection,self.delAll,self.gobutton1,self.stopbutton,self.btnSearch):
            button.SetMinSize((buttonwidth,button.GetSizeTuple()[1]))
        self.profiledropdown.SetMinSize((buttonwidth,tmplistheight))
        self.profiledropdown.Bind(wx.EVT_CHOICE,self.onChangeProfileDropdown)
        self.profilepanel.Show()
        hbox4.Add(self.stopbutton)
        hbox4.Add((0,DV.border_padding))
        #vbox.Add((0,DV.border_padding)) Ditto
        self.stopbutton.Disable()
        self.Bind(wx.EVT_BUTTON,self.onStop,self.stopbutton)
        grid.AddGrowableRow(0,1)
        grid.AddGrowableCol(0,1)
        self.Bind(wx.EVT_CLOSE,self.onClose,self)
        self.Bind(wx.EVT_SIZE,self.onResize,self)
        self.Bind(DV.evt_prog,self.onProgress)
        self.Bind(DV.evt_load,self.onLoading)
        self.clipboardtimer=wx.Timer(self,-1)
        self.clipboardtimer.Start(1000)
        self.Bind(wx.EVT_TIMER,self.onClipboardTimer,self.clipboardtimer)
        DV.icon=wx.Icon(DV.images_path+'icon.ico',wx.BITMAP_TYPE_ICO)
        self.SetIcon(DV.icon)
    def init2(self):
        if os.path.lexists(DV.conf_file_directory+'lastversion.damnvid'):
            lastversion=open(DV.conf_file_directory+'lastversion.damnvid','r')
            dvversion=lastversion.readline().strip()
            lastversion.close()
            del lastversion
        else:
            dvversion='old' # This is not an arbitrary erroneous value, it's handy in the concatenation on the wx.FileDialog line below
        if dvversion!=DV.version: # Just updated to new version, ask what to do about the preferences
            dlg=wx.MessageDialog(self,'DamnVid was updated to '+DV.version+'.\nIf anything fails, try to uninstall DamnVid before updating it again.\n\nFrom a version to another, DamnVid\'s default preferences may vary, and their structure may change.\nIf that is the case, your current preferences may not work anymore.\nAdditionally, new versions of DamnVid often come with new or updated encoding profiles. That is why DamnVid is going to overwrite your current configuration.\nDo you want to export your current preferences, before they get overwritten? You might then try to import them back using the "Import" button in the Preferences pane.','DamnVid was successfully updated',wx.YES|wx.NO|wx.ICON_QUESTION)
            tmpprefs=DamnVidPrefs()
            checkupdates=tmpprefs.get('CheckForUpdates')
            if dlg.ShowModal()==wx.ID_YES:
                dlg.Destroy()
                dlg=wx.FileDialog(self,'Where do you want to export DamnVid\'s configuration?',tmpprefs.get('lastprefdir'),'DamnVid-'+dvversion+'-configuration.ini','INI files (*.ini)|*.ini|All files (*.*)|*.*',wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                if dlg.ShowModal()==wx.ID_OK:
                    path=dlg.GetPath()
                    f=open(path,'w')
                    tmpprefs.ini.write(f)
                    f.close()
                dlg.Destroy()
            else:
                dlg.Destroy()
            # Now, overwrite the preferences!
            del tmpprefs
            os.remove(DV.conf_file)
            shutil.copyfile(DV.curdir+'conf'+os.sep+'conf.ini',DV.conf_file)
            lastversion=open(DV.conf_file_directory+'lastversion.damnvid','w')
            lastversion.write(DV.version)
            lastversion.close()
            del lastversion
            tmpprefs=DamnVidPrefs()
            tmpprefs.set('CheckForUpdates',checkupdates)
            tmpprefs.save()
            del tmpprefs
        self.videos=[]
        self.clippedvideos=[]
        self.resultlist=[]
        self.thisbatch=0
        self.thisvideo=[]
        self.meta={}
        DV.prefs=DamnVidPrefs()
        self.converting=-1
        self.isclosing=False
        self.searchopen=False
        self.addurl=None
        self.loadingvisible=0
        self.onListSelect()
        self.Center()
        if DV.first_run:
            dlg=wx.MessageDialog(self,'Welcome to DamnVid '+DV.version+'!\nWould you like DamnVid to check for updates every time it starts?','Welcome to DamnVid '+DV.version+'!',wx.YES|wx.NO|wx.ICON_QUESTION)
            if dlg.ShowModal()==wx.ID_YES:
                DV.prefs.set('CheckForUpdates','True')
            else:
                DV.prefs.set('CheckForUpdates','False')
        if DV.prefs.get('CheckForUpdates')=='True':
            self.onCheckUpdates(None)
        self.SetStatusText('DamnVid ready.')
    def onExit(self,event):
        self.Close(True)
    def onListSelect(self,event=None):
        sel=self.list.getAllSelectedItems()
        gotstuff=bool(len(sel))
        self.btnRename.Enable(len(sel)==1)
        self.delSelection.Enable(gotstuff)
        self.delAll.Enable(gotstuff)
        self.profiledropdown.Enable(gotstuff)
        if gotstuff:
            self.btnMoveUp.Enable(sel[0])
            self.btnMoveDown.Enable(sel[-1]!=self.list.GetItemCount()-1)
            choices=[]
            uniprofile=int(self.meta[self.videos[sel[0]]]['profile'])
            for i in sel:
                if int(self.meta[self.videos[i]]['profile'])!=uniprofile:
                    uniprofile=-2
            for p in range(-1,DV.prefs.profiles):
                choices.append(DV.prefs.getp(p,'name'))
            if uniprofile==-2:
                choices.insert(0,'(Multiple)')
            self.profiledropdown.SetItems(choices)
            if uniprofile==-2:
                self.profiledropdown.SetSelection(0)
            else:
                self.profiledropdown.SetSelection(uniprofile+1)
        else:
            self.btnMoveUp.Disable()
            self.btnMoveDown.Disable()
            self.profiledropdown.SetItems(['(None)'])
    def onListKeyDown(self,event):
        if (event.GetKeyCode()==8 or event.GetKeyCode()==127) and self.list.GetSelectedItemCount(): # Backspace or delete, but only when there's at least one selected video
            self.onDelSelection(None)
    def onAddFile(self,event):
        d=os.getcwd()
        if os.path.lexists(DV.prefs.get('LastFileDir')):
            if os.path.isdir(DV.prefs.get('LastFileDir')):
                d=DV.prefs.get('LastFileDir')
        elif os.path.lexists(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
            if os.path.isdir(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
                d=DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')
        dlg=wx.FileDialog(self,'Choose a damn video.',d,'','All files|*.*|AVI files (*.avi)|*.avi|MPEG Videos (*.mpg)|*.mpg|QuickTime movies (*.mov)|*.mov|Flash Video (*.flv)|*.flv|Windows Media Videos (*.wmv)|*.wmv',wx.OPEN|wx.FD_MULTIPLE)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal()==wx.ID_OK:
            vids=dlg.GetPaths()
            DV.prefs.set('LastFileDir',os.path.dirname(vids[0]))
            DV.prefs.save()
            self.addVid(vids)
        dlg.Destroy()
    def onAddURL(self,event):
        default=''
        try:
            if wx.TheClipboard.Open():
                dataobject=wx.TextDataObject()
                wx.TheClipboard.GetData(dataobject)
                default=dataobject.GetText()
                wx.TheClipboard.Close()
                if not self.validURI(default):
                    default='' # Only set that as default text if the clipboard's text content is not a URL
        except:
            default=''
        try:
            wx.TheClipboard.Close() # In case there's been an error before the clipboard could be closed, try to close it now
        except:
            pass # There's probably wasn't any error, just pass
        self.addurl=DamnAddURLDialog(self,default)
        self.addurl.SetIcon(DV.icon)
        self.addurl.ShowModal()
        try:
            self.addurl.Destroy()
        except:
            pass # The addurl destroys itself, supposedly, and doing it again sometimes (sometimes!) generates errors.
        self.addurl=None
    def validURI(self,uri):
        if REGEX_HTTP_GENERIC.match(uri):
            for i in DamnIterModules(False):
                if i['class'](uri).validURI():
                    return 'Video site'
            return 'Online video' # Not necessarily true, but ffmpeg will tell
        elif os.path.lexists(uri):
            return 'Local file'
        return None
    def getVidName(self,uri):
        try:
            html=urllib2.urlopen(uri[3:])
            for i in html:
                res=REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                if res:
                    return DamnHtmlEntities(res.group(1)).strip()
        except:
            pass # Can't grab this? Return Unknown title
        return u'Unknown title'
    def onDropTargetClick(self,event):
        dlg=wx.MessageDialog(self,'This is a droptarget: You may drop video files and folders here (or in the big list as well).','DamnVid Droptarget',wx.ICON_INFORMATION)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def toggleLoading(self,show):
        isvisible=self.loadingvisible>0
        self.loadingvisible=max((0,self.loadingvisible+int(show)*2-1))
        if (isvisible and not self.loadingvisible) or (not isvisible and self.loadingvisible):
            wx.PostEvent(self,DamnLoadingEvent(DV.evt_loading,-1,{'show':bool(self.loadingvisible)}))
    def onLoading(self,event):
        info=event.GetInfo()
        if info.has_key('show'):
            if info['show']:
                self.droptarget.LoadFile(DV.images_path+'droptargetloading.gif')
                self.droptarget.Play()
            else:
                self.droptarget.Stop()
                self.droptarget.LoadFile(DV.images_path+'droptarget.gif')
        if info.has_key('status'):
            self.SetStatusText(info['status'])
        if info.has_key('dialog'):
            dlg=wx.MessageDialog(self,info['dialog'][1],info['dialog'][0],info['dialog'][2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        if info.has_key('meta'):
            self.addValid(info['meta'])
        if info.has_key('go') and self.converting==-1:
            if info['go']:
                self.onGo()
        if info.has_key('updateinfo'):
            if info['updateinfo'].has_key('verbose'):
                verbose=info['updateinfo']['verbose']
            else:
                verbose=True
            if info['updateinfo'].has_key('main'):
                msg=None
                if info['updateinfo']['main']!=DV.version and type(info['updateinfo']['main']) is type(''):
                    dlg=wx.MessageDialog(self,'A new version ('+info['updateinfo']['main']+') is available! You are running DamnVid '+DV.version+'.\nWant to go to the download page and download the update?','Update available!',wx.YES|wx.NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
                    dlg.SetIcon(DV.icon)
                    if dlg.ShowModal()==wx.ID_YES:
                        webbrowser.open(DV.url_download,2)
                    dlg.Destroy()
                elif verbose and type(info['updateinfo']['main']) is type(''):
                    msg=('DamnVid is up-to-date.','DamnVid is up-to-date! The latest version is '+DV.version+'.',wx.ICON_INFORMATION)
                elif verbose:
                    msg=('Error!','There was a problem while checking for updates. You are running DamnVid '+DV.version+'.\nMake sure you are connected to the Internet, and that no firewall is blocking DamnVid.',wx.ICON_INFORMATION)
                if msg is not None:
                    dlg=wx.MessageDialog(self,msg[1],msg[0],msg[2])
                    dlg.SetIcon(DV.icon)
                    dlg.ShowModal()
                    dlg.Destroy()
            if info['updateinfo'].has_key('modules'):
                msg=[]
                for i in info['updateinfo']['modules'].iterkeys():
                    if type(info['updateinfo']['modules'][i]) is type(()):
                        msg.append((True,DV.modules[i]['title']+' was updated to version '+info['updateinfo']['modules'][i][0]+'.'))
                    elif type(info['updateinfo']['modules'][i]) is type('') and verbose:
                        if info['updateinfo']['modules'][i]=='error':
                            msg.append((False,DV.modules[i]['title']+' is up-to-date (version '+DV.modules[i]['version']+').'))
                if len(msg):
                    msgs=[]
                    for i in msg:
                        if i[0]:
                            msgs.append(i[1])
                    if not len(msg) and verbose:
                        msgs=msg
                    if len(msgs):
                        msg='DamnVid also checked for updates to its modules.\n'
                        for i in msgs:
                            msg+='\n'+i
                        dlg=wx.MessageDialog(self,msg,'Module updates',wx.ICON_INFORMATION)
                        dlg.SetIcon(DV.icon)
                        dlg.ShowModal()
                        dlg.Destroy()
    def addVid(self,uris,thengo=False):
        DamnVideoLoader(self,uris,thengo).start()
    def addValid(self,meta):
        curvid=len(self.videos)
        self.list.InsertStringItem(curvid,meta['name'])
        self.list.SetStringItem(curvid,ID_COL_VIDPROFILE,DV.prefs.getp(meta['profile'],'name'))
        self.list.SetStringItem(curvid,ID_COL_VIDPATH,meta['dirname'])
        self.list.SetStringItem(curvid,ID_COL_VIDSTAT,meta['status'])
        self.list.SetItemImage(curvid,meta['icon'],meta['icon'])
        self.videos.append(meta['uri'])
        self.meta[meta['uri']]=meta
        self.SetStatusText('Added '+meta['name']+'.')
        if self.addurl is not None:
            self.addurl.update(meta['original'],meta['name'],meta['icon'])
        self.onListSelect()
    def onProgress(self,event):
        info=event.GetInfo()
        if info.has_key('progress'):
            self.gauge1.SetValue(info['progress'])
        if info.has_key('statustext'):
            self.SetStatusText(info['statustext'])
        if info.has_key('status'):
            self.list.SetStringItem(self.converting,ID_COL_VIDSTAT,info['status'])
        if info.has_key('dialog'):
            dlg=wx.MessageDialog(self,dialog[0],dialog[1],dialog[2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        if info.has_key('go'):
            self.go(info['go'])
    def go(self,aborted=False):
        self.converting=-1
        for i in range(len(self.videos)):
            if self.videos[i] not in self.thisvideo and self.meta[self.videos[i]]['status']!='Success!':
                self.converting=i
                break
        if self.converting!=-1 and not aborted:
            # Let's go for the actual conversion...
            self.meta[self.videos[self.converting]]['status']='In progress...'
            self.list.SetStringItem(self.converting,ID_COL_VIDSTAT,'In progress...')
            self.thisbatch=self.thisbatch+1
            self.thread=DamnConverter(parent=self)
            self.thread.start()
        else:
            if not self.isclosing:
                self.SetStatusText('DamnVid '+DV.version+', waiting for instructions.')
                if not aborted:
                    message='Done.'
                    if len(self.resultlist):
                        message='Done!\nAll videos have been put into their respective output folders:\n'
                        dirs={}
                        for i in self.resultlist:
                            if not dirs.has_key(i[1]):
                                dirs[i[1]]=[]
                            dirs[i[1]].append(i[0])
                        self.resultlist=[]
                        for i in dirs.iterkeys():
                            if len(dirs[i])==1:
                                haveverb='s'
                                vids='"'+dirs[i][0]+'"'
                            else:
                                haveverb='ve'
                                vids=''
                                for f in range(len(dirs[i])):
                                    if f==len(dirs[i])-1:
                                        vids+='and "'+dirs[i][f]+'"'
                                    else:
                                        vids+='"'+dirs[i][f]+'", '
                            message+='\n'+vids+' ha'+haveverb+' been put into '+DamnFriendlyDir(i)+'.'
                        del haveverb,dirs,vids
                    dlg=wx.MessageDialog(self,message,'Done!',wx.OK|wx.ICON_INFORMATION)
                else:
                    dlg=wx.MessageDialog(self,'Video conversion aborted.','Aborted',wx.OK|wx.ICON_INFORMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
                self.converting=-1
                self.stopbutton.Disable()
                self.gobutton1.Enable()
                self.gauge1.SetValue(0.0)
    def onGo(self,event=None):
        if not len(self.videos):
            dlg=wx.MessageDialog(None,'Put some videos in the list first!','No videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.converting!=-1:
            dlg=wx.MessageDialog(None,'DamnVid '+DV.version+' is already converting!','Already converting!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            success=0
            for i in self.videos:
                if self.meta[i]['status']=='Success!':
                    success=success+1
            if success==len(self.videos):
                dlg=wx.MessageDialog(None,'All videos in the list have already been processed!','Already done',wx.OK|wx.ICON_INFORMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.thisbatch=0
                self.thisvideo=[]
                self.stopbutton.Enable()
                self.gobutton1.Disable()
                self.go()
    def onStop(self,event):
        self.thread.abortProcess()
    def onRename(self,event):
        item=self.list.getAllSelectedItems()
        if len(item)>1:
            dlg=wx.MessageDialog(None,'You can only rename one video at a time.','Multiple videos selected.',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        elif not len(item):
            dlg=wx.MessageDialog(None,'Select a video in order to rename it.','No videos selected',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            item=item[0]
            dlg=wx.TextEntryDialog(None,'Enter the new name for "'+self.meta[self.videos[item]]['name']+'".','Rename',self.meta[self.videos[item]]['name'])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            self.meta[self.videos[item]]['name']=dlg.GetValue()
            self.list.SetStringItem(item,ID_COL_VIDNAME,dlg.GetValue())
            dlg.Destroy()
    def onSearch(self,event):
        if not self.searchopen:
            self.searchopen=True
            self.searchdialog=DamnVidBrowser(self)
            self.searchdialog.Show()
        else:
            self.searchdialog.Raise()
    def invertVids(self,i1,i2):
        tmp=self.videos[i1]
        self.videos[i1]=self.videos[i2]
        self.videos[i2]=tmp
        tmp=self.list.IsSelected(i2)
        self.list.Select(i2,on=self.list.IsSelected(i1))
        self.list.Select(i1,on=tmp)
        self.list.invertItems(i1,i2)
        if i1==self.converting:
            self.converting=i2
        elif i2==self.converting:
            self.converting=i1
        self.onListSelect()
    def onMoveUp(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            if items[0]:
                for i in items:
                    self.invertVids(i,i-1)
            else:
                dlg=wx.MessageDialog(None,'You\'ve selected the first item in the list, which cannot be moved further up!','Invalid selection',wx.OK|wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Select some videos in the list first.','No videos selected!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        self.onListSelect()
    def onMoveDown(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            if items[-1]<self.list.GetItemCount()-1:
                for i in reversed(self.list.getAllSelectedItems()):
                    self.invertVids(i,i+1)
            else:
                dlg=wx.MessageDialog(None,'You\'ve selected the last item in the list, which cannot be moved further down!','Invalid selection',wx.OK|wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Select some videos in the list first.','No videos selected!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        self.onListSelect()
    def onChangeProfileDropdown(self,event):
        sel=self.profiledropdown.GetCurrentSelection()
        if self.profiledropdown.GetItems()[0]=='(Multiple)':
            sel=sel-1
        if sel!=-1:
            self.onChangeProfile(sel-1,event)
    def onChangeProfile(self,profile,event):
        items=self.list.getAllSelectedItems()
        for i in items:
            if self.meta[self.videos[i]]['profile']!=profile:
                self.meta[self.videos[i]]['profile']=profile
                self.meta[self.videos[i]]['profilemodified']=True
                self.list.SetStringItem(i,ID_COL_VIDPROFILE,DV.prefs.getp(profile,'name'))
        self.onListSelect()
    def onPrefs(self,event):
        self.reopenprefs=False
        prefs=DamnVidPrefEditor(self,-1,'DamnVid preferences',main=self)
        prefs.ShowModal()
        prefs.Destroy()
        if self.reopenprefs:
            self.onPrefs(event)
        else:
            for i in range(len(self.videos)):
                if self.meta[self.videos[i]]['profile']>=DV.prefs.profiles or not self.meta[self.videos[i]]['profilemodified']:
                    # Yes, using icons as source identifiers, why not? Lol
                    if self.meta[self.videos[i]].has_key('module'):
                        self.meta[self.videos[i]]['profile']=self.meta[self.videos[i]]['module'].getProfile()
                    elif self.meta[self.videos[i]]['icon']==DamnGetListIcon('damnvid'):
                        self.meta[self.videos[i]]['profile']=DV.prefs.get('defaultprofile')
                    elif self.meta[self.videos[i]]['icon']==DamnGetListIcon('generic'):
                        self.meta[self.videos[i]]['profile']=DV.prefs.get('defaultwebprofile')
                self.list.SetStringItem(i,ID_COL_VIDPROFILE,DV.prefs.getp(self.meta[self.videos[i]]['profile'],'name'))
        try:
            del self.reopenprefs
        except:
            pass
        self.onListSelect()
    def onOpenOutDir(self,event):
        if DV.os=='nt':
            os.system('explorer.exe "'+DV.prefs.get('outdir')+'"')
        else:
            pass # Halp here?
    def onHalp(self,event):
        webbrowser.open(DV.url_halp,2)
    def onCheckUpdates(self,event=None):
        updater=DamnVidUpdater(self,verbose=event is not None)
        updater.start()
    def onAboutDV(self,event):
        dlg=DamnAboutDamnVid(None,-1,main=self)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def delVid(self,i):
        self.list.DeleteItem(i)
        for vid in range(len(self.thisvideo)):
            if self.thisvideo[vid]==self.videos[i]:
                self.thisvideo.pop(vid)
                self.thisbatch=self.thisbatch-1
        del self.meta[self.videos[i]]
        self.videos.pop(i)
        if self.converting>i:
            self.converting=self.converting-1
    def onDelSelection(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            if self.converting in items:
                dlg=wx.MessageDialog(None,'Stop the video conversion before deleting the video being converted.','Cannot delete this video',wx.ICON_EXCLAMATION|wx.OK)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                for i in reversed(items): # Sequence MUST be reversed, otherwise the first items get deleted first, which changes the indexes of the following items
                    self.delVid(i)
        else:
            dlg=wx.MessageDialog(None,'You must select some videos from the list first!','Select some videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onDelAll(self,event):
        if len(self.videos):
            dlg=wx.MessageDialog(None,'Are you sure? (This will not delete any files, it will just remove them from the list.)','Confirmation',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            dlg.SetIcon(DV.icon)
            if dlg.ShowModal()==wx.ID_YES:
                if self.converting!=-1:
                    self.onStop(None) # Stop conversion if it's in progress
                self.list.DeleteAllItems()
                self.videos=[]
                self.thisvideo=[]
                self.thisbatch=0
                self.meta={}
        else:
            dlg=wx.MessageDialog(None,'Add some videos in the list first.','No videos!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
        dlg.Destroy()
    def onResize(self,event):
        self.Layout()
    def onClipboardTimer(self,event):
        self.clipboardtimer.Stop()
        try:
            if DV.gui_ok and DV.prefs.get('clipboard')=='True':
                if wx.TheClipboard.Open():
                    dataobject=wx.TextDataObject()
                    wx.TheClipboard.GetData(dataobject)
                    clip=dataobject.GetText()
                    wx.TheClipboard.Close()
                    if self.validURI(clip)=='Video site' and clip not in self.clippedvideos:
                        self.clippedvideos.append(clip)
                        if self.addurl is not None:
                            self.addurl.onAdd(val=clip)
                        else:
                            self.addVid([clip],DV.prefs.get('autoconvert')=='True')
        except:
            pass # The clipboard might not get opened properly, or the prefs object might not exist yet. Just silently pass, gonna catch up at next timer event.
        try:
            wx.TheClipboard.Close() # Try to close it, just in case it's left open.
        except:
            pass
        try:
            self.clipboardtimer.Start(1000)
        except:
            pass # Sometimes the timer can still live while DamnMainFrame is closed, and if EVT_TIMER is then raised, error!
    def onClose(self,event):
        if self.converting!=-1:
            dlg=wx.MessageDialog(None,'DamnVid is currently converting a video! Closing DamnVid will cause it to abort the conversion.\r\nContinue?','Conversion in progress',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            if dlg.ShowModal()==wx.ID_YES:
                self.shutdown()
        else:
            self.shutdown()
    def shutdown(self):
        self.isclosing=True
        self.clipboardtimer.Stop()
        self.Destroy()
class DamnVid(wx.App):
    def OnInit(self):
        splash=DamnSplashScreen()
        clock=time.time()
        splash.Show()
        self.frame=DamnMainFrame(None,-1,'DamnVid')
        while clock+.5>time.time():
            time.sleep(.025) # Makes splashscreen stay at least half a second on screen, in case the loading was faster than that. I think it's a reasonable compromise between eyecandy and responsiveness/snappiness
        splash.Hide()
        splash.Destroy()
        del clock,splash
        self.frame.init2()
        self.frame.Show(True)
        self.loadArgs(DV.argv)
        return True
    def loadArgs(self,args):
        if len(args):
            vids=[]
            for i in args:
                if i[-15:].lower()=='.module.damnvid':
                    DamnInstallModule(i)
                elif i[-8:].lower()!='.damnvid':
                    DV.prefs.set('LastFileDir',os.path.dirname(i))
                    vids.append(i)
            if len(vids):
                self.frame.addVid(vids)
    def MacReopenApp(self):
        self.GetTopWindow().Raise()
    def MacOpenFile(self,name):
        if type(name) is not type([]):
            name=[name]
        self.loadArgs(name)
Damnlog('All done, starting wx app.')
app=DamnVid(0)
DV.gui_ok=True
Damnlog('App up, entering main loop.')
app.MainLoop()
Damnlog('Main loop ended, saving prefs.')
DV.prefs.save()
DV.log.close()
