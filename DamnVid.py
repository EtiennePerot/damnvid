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


import wx # Oh my, it's wx.
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin # Mixin for wx.ListrCtrl, to enable autowidth on columns
import wx.lib.hyperlink # Fancy hyperlinks instead of hacked StaticText's
import os # Filesystem functions.
import re # Regular expressions \o/
import subprocess # Spawn sub-processes (ffmpeg)
import time # Sleepin'
import urllib2 # Fetch data from the tubes, encode/decode URLs
import htmlentitydefs # HTML entities dictionaries
import signal # Process signals
import webbrowser # Open a page in default browser
import tempfile,random # Generate temporary files
import shutil # Shell utilities (copyfile)
import sys # System stuff
import ConfigParser # INI file parsing and writing

# Begin constants
DV_VERSION='0.2.2'
DV_URLLIB2_OPENER=urllib2.build_opener()
DV_URLLIB2_OPENER.addheaders=[('User-agent','DamnVid/'+DV_VERSION)]
urllib2.install_opener(DV_URLLIB2_OPENER) # All urllib2.urlopen() calls will have the DamnVid user-agent
DV_URL='http://code.google.com/p/damnvid/'
DV_URL_HALP='http://code.google.com/p/damnvid/wiki/Help'
DV_URL_UPDATE='http://code.google.com/p/damnvid/wiki/CurrentVersion'
DV_URL_DOWNLOAD='http://code.google.com/p/damnvid/downloads/'
DV_ICON=None # This will be defined when DamnMainFrame is initialized
DV_MY_VIDEOS_PATH=''
DV_APPDATA_PATH=''
DV_OS_NAME=os.name
if DV_OS_NAME=='posix' and sys.platform=='darwin':
    DV_OS_NAME='mac'
if DV_OS_NAME=='nt':
    import win32process
    # Need to determine the location of the "My Videos" and "Application Data" folder.
    import ctypes
    from ctypes import wintypes
    DV_MY_VIDEOS_PATH=ctypes.create_string_buffer(wintypes.MAX_PATH)
    DV_APPDATA_PATH=ctypes.create_string_buffer(wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathA(None,0xE,None,0,DV_MY_VIDEOS_PATH)
    ctypes.windll.shell32.SHGetFolderPathA(None,0x1A,None,0,DV_APPDATA_PATH)
    DV_MY_VIDEOS_PATH=str(DV_MY_VIDEOS_PATH.value)
    DV_APPDATA_PATH=str(DV_APPDATA_PATH.value)
    del ctypes
    del wintypes
else:
    DV_MY_VIDEOS_PATH='~'+os.sep+'Videos'
try:
    import threading as thr # Threads
except ImportError:
    import dummy_threading as thr # Moar threads
DV_CURDIR=os.path.dirname(os.path.abspath(sys.argv[0]))+os.sep
DV_CONF_FILE_LOCATION={
    'nt':DV_APPDATA_PATH+os.sep+'DamnVid',
    'posix':'~'+os.sep+'.damnvid',
    'mac':'~'+os.sep+'Library'+os.sep+'Preferences'+os.sep+'DamnVid'
}
DV_CONF_FILE_DIRECTORY=DV_CONF_FILE_LOCATION[DV_OS_NAME]+os.sep
DV_CONF_FILE=DV_CONF_FILE_DIRECTORY+'damnvid.ini'
DV_FIRST_RUN=False
if not os.path.lexists(DV_CONF_FILE):
    if not os.path.lexists(os.path.dirname(DV_CONF_FILE)):
        os.makedirs(os.path.dirname(DV_CONF_FILE))
    shutil.copyfile(DV_CURDIR+'conf'+os.sep+'conf.ini',DV_CONF_FILE)
    lastversion=open(DV_CONF_FILE_DIRECTORY+'lastversion.damnvid','w')
    lastversion.write(DV_VERSION)
    lastversion.close()
    del lastversion
    DV_FIRST_RUN=True
DV_IMAGES_PATH=DV_CURDIR+'img/'.replace('/',os.sep)
DV_BIN_PATH=DV_CURDIR+'bin/'.replace('/',os.sep)
DV_TMP_PATH=tempfile.gettempdir()
if DV_TMP_PATH[-1]!=os.sep:
    DV_TMP_PATH+=os.sep
DV_TMP_PATH+='damnvid-'
DV_FILE_EXT={
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
    '3g2':'3g2'
}
DV_FILE_EXT_BY_CODEC={
    'rv10':'rm',
    'rv20':'rm',
    'flv':'flv',
    'theora':'ogg',
    'wmv1':'wmv',
    'wmv2':'wmv'
} # Just in case the format isn't defined, fall back to DV_FILE_EXT_BY_CODEC. Otherwise, fall back to .avi (this is why only codecs that shouldn't get a .avi extension are listed here).
DV_CODEC_ADVANCED_CL={
    'mpeg4':[('g','300'),('cmp','2'),('subcmp','2'),('trellis','2'),'+4mv']
}
DV_PREFERENCES=None
try:
    execfile(DV_CURDIR+'conf'+os.sep+'preferences.damnvid') # Load preferences
except:
    pass # Someone's been messing around with the conf.py file?
# Begin ID constants
ID_MENU_EXIT=101
ID_MENU_ADD_FILE=102
ID_MENU_ADD_URL=103
ID_MENU_GO=104
ID_MENU_PREFERENCES=105
ID_MENU_OUTDIR=106
ID_MENU_HALP=107
ID_MENU_UPDATE=108
ID_MENU_ABOUT=109
ID_COL_VIDNAME=0
ID_COL_VIDPROFILE=1
ID_COL_VIDSTAT=2
ID_COL_VIDPATH=3
# Begin regex constants
REGEX_DAMNVID_VERSION_CHECK=re.compile('<tt>([^<>]+)</tt>',re.IGNORECASE)
REGEX_PATH_MULTI_SEPARATOR_CHECK=re.compile('/+')
REGEX_FFMPEG_DURATION_EXTRACT=re.compile('^\\s*Duration: (\\d+):(\\d\\d):([.\\d]+),',re.IGNORECASE)
REGEX_FFMPEG_TIME_EXTRACT=re.compile('time=([.\\d]+)',re.IGNORECASE)
REGEX_HTTP_GENERIC=re.compile('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/;{}\w]*)?$',re.IGNORECASE)
REGEX_HTTP_YOUTUBE=re.compile('^https?://(?:[-_\w]+\.)*youtube\.com.*(?:v|(?:video_)?id)[/=]([-_\w]{6,})',re.IGNORECASE)
REGEX_HTTP_GVIDEO=re.compile('^https?://(?:[-_\w]+\.)*video\.google\.com.*(?:v|id)[/=]([-_\w]{10,})',re.IGNORECASE)
REGEX_HTTP_VEOH=re.compile('^https?://(?:[-_\w]+\.)*veoh\.com/videos/',re.IGNORECASE)
REGEX_HTTP_DAILYMOTION=re.compile('^https?://(?:[-_\w]+\.)*dailymotion\.com/',re.IGNORECASE)
REGEX_HTTP_EXTRACT_FILENAME=re.compile('^.*/|[?#].*$')
REGEX_HTTP_EXTRACT_DIRNAME=re.compile('^([^?#]*)/.*?$')
REGEX_FILE_CLEANUP_FILENAME=re.compile('[\\/:?"|*<>]+')
REGEX_URI_EXTENSION_EXTRACT=re.compile('^(?:[^?|<>]+[/\\\\])?[^/\\\\|?<>#]+\\.(\\w{1,3})(?:$|[^/\\\\\\w].*?$)')
REGEX_HTTP_GENERIC_TITLE_EXTRACT=re.compile('<title>([^<>]+)</title>',re.IGNORECASE)
REGEX_HTTP_YOUTUBE_TITLE_EXTRACT=re.compile('<title>YouTube - ([^<>]+)</title>',re.IGNORECASE)
REGEX_HTTP_YOUTUBE_TICKET_EXTRACT=re.compile('(["\']?)t\\1\\s*:\\s*([\'"])((?:(?!\\2).)+)\\2')
REGEX_HTTP_GVIDEO_TITLE_EXTRACT=REGEX_HTTP_GENERIC_TITLE_EXTRACT
REGEX_HTTP_GVIDEO_TICKET_EXTRACT=re.compile('If the download does not start automatically, right-click <a href="([^"]+)"',re.IGNORECASE)
REGEX_HTTP_VEOH_TITLE_EXTRACT=re.compile('<title>\\s*([^<>]+)(?: : Online Video)? \\| Veoh Video Network</title>',re.IGNORECASE)
REGEX_HTTP_VEOH_ID_EXTRACT=re.compile('permalinkId=(\\w+)',re.IGNORECASE)
REGEX_HTTP_VEOH_SUBID_EXTRACT=re.compile('^\\w+?(\\d+).*$')
REGEX_HTTP_VEOH_TICKET_EXTRACT=re.compile('fullPreviewHashPath="([^"]+)"',re.IGNORECASE)
"""To redo!"""#REGEX_HTTP_DAILYMOTION_TITLE_EXTRACT=re.compile('<title>(?:Video\\s*)?([^<>]+?)\\s*-[^-<>]+-[^-<>]+</title>',re.IGNORECASE)
REGEX_HTTP_DAILYMOTION_TICKET_EXTRACT=re.compile('\\.addVariable\\s*\\(\\s*([\'"])video\\1\\s*,\\s*([\'"])((?:(?!\\2).)+)\\2\\s*\\)',re.IGNORECASE)
REGEX_HTTP_DAILYMOTION_QUALITY=re.compile('(\d+)x(\d+)')
# End constants
def DamnSpawner(cmd,shell=False,stderr=None,stdout=None,stdin=None,cwd=None):
    if cwd==None:
        cwd=os.getcwd()
    if DV_OS_NAME=='nt':
        return subprocess.Popen(cmd,shell=shell,creationflags=win32process.CREATE_NO_WINDOW,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE,cwd=cwd) # Yes, ALL std's must be PIPEd, otherwise it doesn't work on win32 (see http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions)
    else:
        return subprocess.Popen(cmd,shell=shell,stderr=stderr,stdout=stdout,stdin=stdin,cwd=cwd)
def DamnURLPicker(urls,urlonly=False):
    for i in urls:
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
                for i in range(-1,self.parent.parent.prefs.profiles):
                    if uniprofile!=-2:
                        prof=wx.MenuItem(self,-1,self.parent.parent.prefs.getp(i,'name'),kind=wx.ITEM_RADIO)
                        profile.AppendItem(prof) # Item has to be appended before being checked, otherwise error. Annoying code duplication.
                        prof.Check(i==uniprofile)
                    else:
                        prof=wx.MenuItem(self,-1,self.parent.parent.prefs.getp(i,'name'))
                        profile.AppendItem(prof)
                    self.Bind(wx.EVT_MENU,DamnCurry(self.parent.parent.onChangeProfile,i),prof)
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
class DamnEEgg(wx.Dialog):
    def __init__(self,parent,id):
        wx.Dialog.__init__(self,parent,id,'Salute the Secret Stoat!')
        topvbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topvbox)
        self.panel=wx.Panel(self,-1)
        topvbox.Add(self.panel,1,wx.EXPAND)
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.vbox)
        self.vbox.Add(wx.StaticBitmap(self.panel,-1,wx.Bitmap(DV_IMAGES_PATH+'stoat.jpg')),0,wx.ALIGN_CENTER)
        self.AddText('DamnVid '+DV_VERSION+' is *100% stoat-powered*, and *proud* of it.',True)
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
        normfont=wx.Font(8,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL)
        boldfont=wx.Font(8,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD)
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
        wx.Dialog.__init__(self,parent,id,'About DamnVid '+DV_VERSION)
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
        icon=wx.StaticBitmap(panel,-1,wx.Bitmap(DV_IMAGES_PATH+'icon256.png'))
        icon.Bind(wx.EVT_LEFT_DCLICK,self.eEgg)
        vbox1.Add(icon,1,wx.ALIGN_CENTER)
        title=wx.StaticText(panel,-1,'DamnVid '+DV_VERSION)
        title.SetFont(wx.Font(24,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_BOLD))
        vbox2.Add(title,1)
        author=wx.StaticText(panel,-1,'By WindPower')
        author.SetFont(wx.Font(16,wx.FONTFAMILY_DEFAULT,wx.FONTSTYLE_NORMAL,wx.FONTWEIGHT_NORMAL))
        vbox2.Add(author,1)
        link=wx.lib.hyperlink.HyperLinkCtrl(panel)
        link.SetURL(DV_URL)
        link.SetLabel(DV_URL)
        link.SetToolTipString('Click here to go to DamnVid '+DV_VERSION+'\'s homepage.')
        vbox2.Add(link)
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
        dlg.SetIcon(DV_ICON)
        dlg.ShowModal()
        dlg.Destroy()
    def onOK(self,event):
        self.Close(True)
class DamnVidPrefs: # Preference manager
    def __init__(self):
        self.conf={}
        f=open(DV_CONF_FILE,'r')
        #for i in re.finditer('(?m)^([_\\w]+)=(.*)$',f.read()):
            #self.conf[i.group(1)]=i.group(2).replace('%CWD%',DV_CURDIR[0:-1]).replace('/',os.sep).strip()
        self.ini=ConfigParser.SafeConfigParser()
        self.ini.readfp(f)
        f.close()
        self.profiles=0
        self.pathprefs=['outdir','lastfiledir','defaultoutdir']
        for i in self.ini.sections():
            if i[0:16]=='damnvid-profile-':
                self.profiles=self.profiles+1
    def expandPath(self,value):
        value=REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/',value.replace(os.sep,'/').replace('?DAMNVID_MY_VIDEOS?',DV_MY_VIDEOS_PATH.replace(os.sep,'/'))).replace('/',os.sep)
        if value[-1:]!=os.sep:
            value+=os.sep
        return value
    def reducePath(self,value):
        value=REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/',value.replace(os.sep,'/').replace(DV_MY_VIDEOS_PATH.replace(os.sep,'/'),'?DAMNVID_MY_VIDEOS?')).replace('/',os.sep)
        if value[-1:]!=os.sep:
            value+=os.sep
        return value
    def get(self,name):
        name=name.lower()
        if not self.ini.has_option('damnvid',name):
            self.ini.set('damnvid',name,'')
        value=self.ini.get('damnvid',name)
        if name in self.pathprefs:
            value=self.expandPath(value)
        return value
    def set(self,name,value):
        name=name.lower()
        if name in self.pathprefs:
            value=self.reducePath(value)
        self.ini.set('damnvid',name,value)
        return value
    def gets(self,section,name):
        name=name.lower()
        if self.ini.has_section(section):
            value=self.ini.get(section,name)
            if name in self.pathprefs:
                value=self.expandPath(value)
            return value
        else:
            print 'No such section:',section
    def sets(self,section,name,value):
        name=name.lower()
        if self.ini.has_section(section):
            if name in self.pathprefs:
                value=self.reducePath(value)
            return self.ini.set(section,name,value)
        else:
            print 'No such section:',section
    def lists(self,section):
        if self.ini.has_section(section):
            return self.ini.options(section)
        else:
            print 'No such section.'
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
    def addp(self):
        self.ini.add_section('damnvid-profile-'+str(self.profiles))
        for i in self.ini.options('damnvid-typical-profile'):
            self.ini.set('damnvid-profile-'+str(self.profiles),i,self.ini.get('damnvid-typical-profile',i))
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
    def save(self):
        f=open(DV_CONF_FILE,'w')
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
        dlg.SetIcon(DV_ICON)
        path=None
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            self.filefield.SetValue(path)
        dlg.Destroy()
        if path!=None:
            self.callback(self,path)
class DamnVidPrefEditor(wx.Dialog): # Preference dialog (not manager)
    def __init__(self,parent,id,title,main):
        # Dialog init
        wx.Dialog.__init__(self,parent,id,title)
        self.parent=main
        self.prefs=self.parent.prefs
        self.toppanel=wx.Panel(self,-1)
        self.bestsize=[0,0]
        # Top part of the toppanel
        self.topsizer=wx.BoxSizer(wx.VERTICAL)
        self.uppersizer=wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.uppersizer,1,wx.EXPAND)
        # - Left part of the upperpanel
        self.upperleftpanel=wx.Panel(self.toppanel,-1)
        self.uppersizer.Add(self.upperleftpanel,0)
        self.upperleftsizer=wx.BoxSizer(wx.VERTICAL)
        self.tree=wx.TreeCtrl(self.upperleftpanel,-1,size=(180,280),style=wx.TR_LINES_AT_ROOT|wx.TR_HAS_BUTTONS|wx.TR_FULL_ROW_HIGHLIGHT)
        self.upperleftsizer.Add(self.tree,1,wx.EXPAND)
        # - - Tree construction
        self.treeroot=self.tree.AddRoot('DamnVid Preferences')
        self.defaultprofiles=self.tree.AppendItem(self.treeroot,'Default profiles')
        self.profileroot=self.tree.AppendItem(self.treeroot,'Encoding profiles')
        self.profiles=[]
        for i in range(0,self.prefs.profiles):
            self.profiles.append(self.tree.AppendItem(self.profileroot,self.prefs.getp(i,'name')))
        self.tree.ExpandAll()
        # - - End tree construction
        self.addProfileButton=wx.Button(self.upperleftpanel,-1,'Add profile')
        self.upperleftsizer.Add(self.addProfileButton,0,wx.EXPAND)
        self.deleteProfileButton=wx.Button(self.upperleftpanel,-1,'Delete profile')
        self.upperleftsizer.Add(self.deleteProfileButton,0,wx.EXPAND)
        self.importButton=wx.Button(self.upperleftpanel,-1,'Import preferences')
        self.upperleftsizer.Add(self.importButton,0,wx.EXPAND)
        self.exportButton=wx.Button(self.upperleftpanel,-1,'Export preferences')
        self.upperleftsizer.Add(self.exportButton,0,wx.EXPAND)
        self.resetButton=wx.Button(self.upperleftpanel,-1,'Reset all')
        self.upperleftsizer.Add(self.resetButton,0,wx.EXPAND)
        self.upperleftpanel.SetSizer(self.upperleftsizer)
        # - Right part of the upperpanel
        self.upperrightpanel=wx.Panel(self.toppanel,-1)
        self.uppersizer.Add(self.upperrightpanel,1,wx.EXPAND)
        self.prefpanelabel=wx.StaticBox(self.upperrightpanel,-1,'')
        self.upperrightsizer=wx.StaticBoxSizer(self.prefpanelabel,wx.VERTICAL)
        # - - Preference pane creation
        self.prefpane=wx.Panel(self.upperrightpanel,-1)
        self.prefpanesizer=wx.GridBagSizer(2,2)
        self.prefpane.SetSizer(self.prefpanesizer)
        # - - End preference pane creation
        self.upperrightsizer.Add(self.prefpane,1,wx.EXPAND)
        self.upperrightpanel.SetSizer(self.upperrightsizer)
        # Bottom part of the toppanel
        self.lowersizer=wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.lowersizer,0,wx.EXPAND)
        self.lowersizer.AddStretchSpacer(1)
        self.okButton=wx.Button(self.toppanel,wx.ID_OK,'OK')
        self.lowersizer.Add(self.okButton,0,wx.ALIGN_RIGHT)
        self.closeButton=wx.Button(self.toppanel,wx.ID_CLOSE,'Cancel')
        self.lowersizer.Add(self.closeButton,0,wx.ALIGN_RIGHT)
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
        self.toppanel.SetFocus()
        self.tree.SelectItem(self.treeroot,True) # Will also resize the window
        self.Center()
    def onTreeSelectionChanged(self,event):
        item=event.GetItem()
        self.prefpanelabel.SetLabel(self.tree.GetItemText(item))
        if item==self.treeroot:
            self.updatePrefPane('damnvid')
        elif item==self.defaultprofiles:
            self.updatePrefPane('damnvid-default-profiles')
        elif item==self.profileroot:
            self.updatePrefPane('special:profileroot')
        elif item in self.profiles:
            count=0
            profile=None
            for i in self.profiles:
                if i!=item:
                    count=count+1
                else:
                    profile=str(count)
            self.updatePrefPane('damnvid-profile-'+profile)
        else:
            self.updatePrefPane('special:error')
    def updatePrefPane(self,pane):
        self.prefpanesizer.Clear(True) # Delete all controls in prefpane
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
        else:
            prefprefix=pane
            profile=None
            if prefprefix[0:16].lower()=='damnvid-profile-':
                prefprefix=prefprefix[0:15]
                profile=int(pane[16:])
            prefprefix+=':'
            self.controls={}
            currentprefs=[]
            maxheight={str(DV_PREFERENCE_TYPE_VIDEO):0,str(DV_PREFERENCE_TYPE_AUDIO):0,str(DV_PREFERENCE_TYPE_PROFILE):0,str(DV_PREFERENCE_TYPE_MISC):0}
            maxwidth={str(DV_PREFERENCE_TYPE_VIDEO):0,str(DV_PREFERENCE_TYPE_AUDIO):0,str(DV_PREFERENCE_TYPE_PROFILE):0,str(DV_PREFERENCE_TYPE_MISC):0}
            count=0
            for i in self.prefs.lists(pane):
                if prefprefix+i in DV_PREFERENCES.keys():
                    desc=DV_PREFERENCES[prefprefix+i]
                    width=1
                    if i in DV_PREFERENCE_ORDER[prefprefix[0:-1]]:
                        currentprefs.insert(DV_PREFERENCE_ORDER[prefprefix[0:-1]].index(i),prefprefix+i)
                    else:
                        currentprefs.append(prefprefix+i)
                    maxheight[str(desc['type'])]+=1
                    maxwidth[str(desc['type'])]=max((maxwidth[str(desc['type'])],self.getPrefWidth(prefprefix+i)))
            maxwidth[str(DV_PREFERENCE_TYPE_PROFILE)]=max((maxwidth[str(DV_PREFERENCE_TYPE_MISC)],maxwidth[str(DV_PREFERENCE_TYPE_PROFILE)],maxwidth[str(DV_PREFERENCE_TYPE_VIDEO)]+maxwidth[str(DV_PREFERENCE_TYPE_AUDIO)]))
            maxwidth[str(DV_PREFERENCE_TYPE_MISC)]=maxwidth[str(DV_PREFERENCE_TYPE_PROFILE)]
            count=0
            currentprefsinsection={str(DV_PREFERENCE_TYPE_VIDEO):0,str(DV_PREFERENCE_TYPE_AUDIO):0,str(DV_PREFERENCE_TYPE_PROFILE):0,str(DV_PREFERENCE_TYPE_MISC):0}
            for i in currentprefs:
                shortprefname=i[i.find(':')+1:]
                if profile==None:
                    val=self.prefs.gets(pane,shortprefname)
                else:
                    val=self.prefs.getp(profile,shortprefname)
                position=[0,0]
                maxspan=[1,maxwidth[str(DV_PREFERENCES[i]['type'])]]
                if DV_PREFERENCES[i]['type']==DV_PREFERENCE_TYPE_AUDIO:
                    position[1]+=maxwidth[str(DV_PREFERENCE_TYPE_VIDEO)]
                elif DV_PREFERENCES[i]['type']==DV_PREFERENCE_TYPE_PROFILE:
                    position[0]+=max((maxheight[str(DV_PREFERENCE_TYPE_VIDEO)],maxheight[str(DV_PREFERENCE_TYPE_AUDIO)]))
                elif DV_PREFERENCES[i]['type']==DV_PREFERENCE_TYPE_MISC:
                    position[0]+=maxheight[str(DV_PREFERENCE_TYPE_PROFILE)]+max((maxheight[str(DV_PREFERENCE_TYPE_VIDEO)],maxheight[str(DV_PREFERENCE_TYPE_AUDIO)]))
                position[0]+=currentprefsinsection[str(DV_PREFERENCES[i]['type'])]
                currentprefsinsection[str(DV_PREFERENCES[i]['type'])]+=1
                if DV_PREFERENCES[i]['kind']!='bool':
                    label=wx.StaticText(self.prefpane,-1,DV_PREFERENCES[i]['name']+':')
                    self.prefpanesizer.Add(label,(position[0],position[1]),(1,1),wx.ALIGN_RIGHT)
                if type(DV_PREFERENCES[i]['kind']) is type({}):
                    choices=['(default)']
                    for f in DV_PREFERENCES[i]['order']:
                        choices.append(DV_PREFERENCES[i]['kind'][f])
                    if not val:
                        val='(default)'
                    else:
                        val=DV_PREFERENCES[i]['kind'][val]
                    self.controls[i]=self.makeList(DV_PREFERENCES[i]['strict'],choices,self.prefpane,val) # makeList takes care of the event binding
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                elif DV_PREFERENCES[i]['kind'][0]=='%':
                    self.controls[i]=wx.SpinCtrl(self.prefpane,-1,initial=int(100.0*float(val)/float(str(DV_PREFERENCES[i]['kind'][1:]))),min=0,max=200)
                    self.Bind(wx.EVT_SPINCTRL,self.onPrefChange,self.controls[i])
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                elif DV_PREFERENCES[i]['kind']=='bool':
                    self.controls[i]=wx.CheckBox(self.prefpane,-1,DV_PREFERENCES[i]['name'])
                    self.controls[i].SetValue(val=='True')
                    self.Bind(wx.EVT_CHECKBOX,self.onPrefChange,self.controls[i])
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]),wx.EXPAND)
                elif DV_PREFERENCES[i]['kind'][0:3]=='int':
                    choices=['(default)']
                    if len(DV_PREFERENCES[i]['kind'])>3:
                        for f in range(int(DV_PREFERENCES[i]['kind'][DV_PREFERENCES[i]['kind'].find(':')+1:DV_PREFERENCES[i]['kind'].find('-')]),int(DV_PREFERENCES[i]['kind'][DV_PREFERENCES[i]['kind'].find('-')+1:])):
                            choices.append(str(pow(2,f))+'k')
                    if not val:
                        val='(default)'
                    self.controls[i]=self.makeList(DV_PREFERENCES[i]['strict'],choices,self.prefpane,val) # makeList takes care of the event binding
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                elif DV_PREFERENCES[i]['kind']=='dir':
                    pathpanel=wx.Panel(self.prefpane,-1)
                    pathsizer=wx.BoxSizer(wx.HORIZONTAL)
                    pathpanel.SetSizer(pathsizer)
                    self.prefpanesizer.Add(pathpanel,(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                    self.controls[i]=wx.TextCtrl(pathpanel,-1,val)
                    self.Bind(wx.EVT_TEXT,self.onPrefChange,self.controls[i])
                    pathsizer.Add(self.controls[i],1,wx.EXPAND)
                    browseButton=DamnBrowseDirButton(pathpanel,-1,'Browse...',control=self.controls[i],title='Select DamnVid '+DV_VERSION+'\'s output directory.',callback=self.onBrowseDir)
                    self.Bind(wx.EVT_BUTTON,browseButton.onBrowse,browseButton)
                    pathsizer.Add(browseButton,0)
                elif DV_PREFERENCES[i]['kind']=='text':
                    self.controls[i]=wx.TextCtrl(self.prefpane,-1,val)
                    self.Bind(wx.EVT_TEXT,self.onPrefChange,self.controls[i])
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                elif DV_PREFERENCES[i]['kind']=='profile':
                    if self.prefs.profiles:
                        choices=[]
                        for p in range(-1,self.prefs.profiles):
                            choices.append(self.prefs.getp(p,'name'))
                        self.controls[i]=self.makeList(DV_PREFERENCES[i]['strict'],choices,self.prefpane,None) # makeList takes care of the event binding
                        self.controls[i].SetSelection(int(val)+1)
                    else:
                        self.controls[i]=wx.StaticText(self.prefpane,-1,'No encoding profiles found!')
                    self.prefpanesizer.Add(self.controls[i],(position[0],position[1]+1),(1,maxwidth[str(DV_PREFERENCES[i]['type'])]-1),wx.EXPAND)
                count=count+1
        self.prefpanesizer.Layout() # Mandatory
        newsize=self.toppanel.GetBestSize()
        if newsize[0]>self.bestsize[0]:
            self.bestsize[0]=newsize[0]
        if newsize[1]>self.bestsize[1]:
            self.bestsize[1]=newsize[1]
        self.SetClientSize(self.bestsize)
        self.Center()
    def getPrefWidth(self,pref):
        if type(DV_PREFERENCES[pref]['kind']) is type({}):
            return 2
        if DV_PREFERENCES[pref]['kind'][0:3]=='int':
            return 2
        if DV_PREFERENCES[pref]['kind']=='profile':
            return 2
        if DV_PREFERENCES[pref]['kind'][0]=='%':
            return 2
        if DV_PREFERENCES[pref]['kind']=='text':
            return 2
        if DV_PREFERENCES[pref]['kind']=='dir':
            return 2 # Label + Panel{TextCtrl + Button} = 2
        if DV_PREFERENCES[pref]['kind']=='bool':
            return 1
        return 0
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
            if type(DV_PREFERENCES[genericpref]['kind']) is type({}) or DV_PREFERENCES[genericpref]['kind'][0:3]=='int':
                if DV_PREFERENCES[genericpref]['strict']:
                    val=self.controls[i].GetSelection()
                    if val:
                        val=DV_PREFERENCES[genericpref]['order'][val-1]
                    else:
                        val=''
                else:
                    val=self.controls[i].GetValue()
                    if val=='(default)':
                        val=''
                    elif type(DV_PREFERENCES[genericpref]['kind']) is type({}) and val in DV_PREFERENCES[genericpref]['kind'].values():
                        for j in DV_PREFERENCES[genericpref]['kind'].iterkeys():
                            if val==DV_PREFERENCES[genericpref]['kind'][j]:
                                val=j
            elif DV_PREFERENCES[genericpref]['kind']=='profile':
                val=self.controls[i].GetSelection()-1
            elif DV_PREFERENCES[genericpref]['kind'][0]=='%':
                val=float(float(self.controls[i].GetValue())*256.0/100.0)
            elif DV_PREFERENCES[genericpref]['kind']=='dir' or DV_PREFERENCES[genericpref]['kind']=='text':
                val=self.controls[i].GetValue()
                if genericpref=='damnvid-profile:name':
                    name=val
            elif DV_PREFERENCES[genericpref]['kind']=='bool':
                val=self.controls[i].IsChecked() # The str() representation takes care of True/False
            if val!=None:
                self.prefs.sets(self.pane,prefname,str(val))
        if name!=None and self.tree.GetSelection()!=self.treeroot and self.tree.GetItemParent(self.tree.GetSelection())==self.profileroot:
            self.tree.SetItemText(self.tree.GetSelection(),name)
            self.prefpanelabel.SetLabel(name)
    def onBrowseDir(self,button,path):
        for i in self.controls.iterkeys():
            if self.controls[i]==button.filefield:
                self.prefs.sets(self.pane,self.splitLongPref(i)[1],path)
    def onAddProfile(self,event):
        self.prefs.addp()
        self.profiles.append(self.tree.AppendItem(self.profileroot,self.prefs.getp(self.prefs.profiles-1,'name')))
        self.tree.SelectItem(self.profiles[-1],True)
    def onDeleteProfile(self,event):
        if self.tree.GetSelection()!=self.treeroot and self.tree.GetItemParent(self.tree.GetSelection())==self.profileroot:
            if len(self.profiles)>1:
                profile=int(self.pane[16:])
                self.prefs.remp(profile)
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
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Please choose a profile to delete from the profile list.','No profile selected',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
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
            self.Bind(wx.EVT_TEXT,self.onPrefChange,cont)
        return cont
    def getListValue(self,name,strict):
        if strict:
            val=self.listvalues[name][self.controls[name].GetSelection()]
        else:
            val=self.controls[name].GetValue()
        if val=='(default)':
            val=''
        elif type(DV_PREFERENCE_TYPE[name]['kind']) is type({}):
            for key,i in DV_PREFERENCE_TYPE[name]['kind'].iteritems():
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
                if type(DV_PREFERENCE_TYPE[name]['kind']) is type({}):
                    value=DV_PREFERENCE_TYPE[name]['kind'][value]
                c=0
                for i in self.listvalues[name]:
                    if i==value:
                        self.controls[name].SetSelection(c)
                    c=c+1
            else:
                self.controls[name].SetValue(value)
    def onOK(self,event):
        self.prefs.save()
        del self.prefs,self.parent.prefs
        self.parent.prefs=DamnVidPrefs()
        self.Close(True)
    def onReset(self,event):
        dlg=wx.MessageDialog(None,'All changes to DamnVid\'s configuration will be lost. Continue?','Are you sure?',wx.YES_NO|wx.ICON_QUESTION)
        dlg.SetIcon(DV_ICON)
        if dlg.ShowModal()==wx.ID_YES:
            dlg.Destroy()
            checkupdates=self.prefs.get('checkforupdates')
            del self.prefs,self.parent.prefs
            os.remove(DV_CONF_FILE)
            shutil.copyfile(DV_CURDIR+'conf'+os.sep+'conf.ini',DV_CONF_FILE)
            self.parent.prefs=DamnVidPrefs()
            self.parent.prefs.set('checkforupdates',checkupdates)
            self.parent.prefs.save()
            self.prefs=self.parent.prefs
            self.tree.SelectItem(self.treeroot,True)
            self.tree.DeleteChildren(self.profileroot)
            self.profiles=[]
            for i in range(0,self.prefs.profiles):
                self.profiles.append(self.tree.AppendItem(self.profileroot,self.prefs.getp(i,'name')))
            self.tree.ExpandAll()
            dlg=wx.MessageDialog(None,'DamnVid\'s configuration has been successfully reset.','Configuration reset',wx.OK|wx.ICON_INFORMATION)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg.Destroy()
    def onImport(self,event):
        dlg=wx.FileDialog(None,'Where is located the configuration file to import?',self.prefs.get('lastprefdir'),'DamnVid-'+DV_VERSION+'-configuration.ini','INI files (*.ini)|*.ini|All files (*.*)|*.*',wx.FD_OPEN)
        dlg.SetIcon(DV_ICON)
        if dlg.ShowModal()==wx.ID_OK:
            self.tree.SelectItem(self.treeroot,True)
            path=dlg.GetPath()
            dlg.Destroy()
            self.prefs.set('lastprefdir',path)
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
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                dlg.Destroy()
            if allOK:
                keepgoing=True
                while keepgoing:
                    keepgoing=(self.prefs.remp(0)!=None)
                for i in testprefs.sections():
                    try:
                        self.prefs.ini.add_section(i)
                    except:
                        pass
                    for j in testprefs.options(i):
                        self.prefs.sets(i,j,testprefs.get(i,j))
                self.parent.reopenprefs=True
                self.onOK(None)
        else:
            dlg.Destroy()
    def onExport(self,event):
        dlg=wx.FileDialog(None,'Where do you want to export DamnVid '+DV_VERSION+'\'s configuration?',self.prefs.get('lastprefdir'),'DamnVid-'+DV_VERSION+'-configuration.ini','INI files (*.ini)|*.ini|All files (*.*)|*.*',wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetIcon(DV_ICON)
        if dlg.ShowModal()==wx.ID_OK:
            path=dlg.GetPath()
            self.prefs.set('lastprefdir',path)
            f=open(path,'w')
            self.prefs.ini.write(f)
            f.close()
        dlg.Destroy()
    def onKeyDown(self,event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE,wx.WXK_CANCEL):
            self.onClose(event)
        elif event.GetKeyCode() in (wx.WXK_NUMPAD_ENTER,wx.WXK_RETURN,wx.WXK_EXECUTE):
            self.onOK(event)
    def onClose(self,event):
        del self.prefs,self.parent.prefs # Delete modified object
        self.parent.prefs=DamnVidPrefs() # Reload from ini
        self.Close(True)
class DamnConverter(thr.Thread): # The actual converter
    def __init__(self,parent):
        self.parent=parent
        self.uris=self.getURI(parent.videos[self.parent.converting])
        thr.Thread.__init__(self)
    def getURI(self,uri):
        if uri[0:3]=='yt:':
            # YouTube video, must grab download ticket before continuing.
            html=urllib2.urlopen('http://www.youtube.com/watch?v='+uri[3:])
            for i in html:
                res=REGEX_HTTP_YOUTUBE_TICKET_EXTRACT.search(i)
                if res:
                    return ['http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res.group(3)+'&fmt=22','http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res.group(3)+'&fmt=18','http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res.group(3)] # If there's no match, ffmpeg will error by itself.
        elif uri[0:3]=='gv:':
            html=urllib2.urlopen('http://video.google.com/videoplay?docid='+uri[3:])
            for i in html:
                res=REGEX_HTTP_GVIDEO_TICKET_EXTRACT.search(i)
                if res:
                    return [res.group(1)]
        elif uri[0:3]=='vh:':
            print uri
            html=urllib2.urlopen('http://www.veoh.com/rest/v2/execute.xml?method=veoh.video.findById&videoId='+REGEX_HTTP_VEOH_SUBID_EXTRACT.sub('\\1',uri[3:])+'&apiKey=54709C40-9415-B95B-A5C3-5802A4E91AF3') # Onoes it's an API key
            for i in html:
                res=REGEX_HTTP_VEOH_TICKET_EXTRACT.search(i)
                if res:
                    return [res.group(1)]
        elif uri[0:3]=='dm:':
            html=urllib2.urlopen(uri[3:])
            for i in html:
                res=REGEX_HTTP_DAILYMOTION_TICKET_EXTRACT.search(i)
                if res:
                    urls=urllib2.unquote(res.group(3)).split('||')
                    qualitys={}
                    for j in urls:
                        res2=REGEX_HTTP_DAILYMOTION_QUALITY.search(j)
                        if res2:
                            qualitys[j]=int(res2.group(1))*int(res2.group(2))
                    if len(qualitys):
                        # This is quite ugly but it works
                        keys=qualitys.values()
                        keys.sort()
                        finalurls=[]
                        for j in keys:
                            for l in qualitys.keys():
                                if qualitys[l]==j:
                                    if l.find('@@')!=-1:
                                        l=l[0:l.find('@@')]
                                    finalurls.append('http://www.dailymotion.com'+l)
                        finalurls.reverse() # From best to worst quality. Note: this doesn't return a new reverse'd, array, it actually modifies the array itself
                        return finalurls
        return [uri]
    def cmd2str(self,cmd):
        s=''
        for i in cmd:
            i=i.replace('?DAMNVID_VIDEO_STREAM?',self.stream).replace('?DAMNVID_VIDEO_PASS?',str(self.passes)).replace('?DAMNVID_OUTPUT_FILE?',DV_TMP_PATH+self.tmpfilename)
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
        return tmpfilename
    def getfinalfilename(self,path,prefix,ext):
        if not os.path.lexists(path+prefix+ext):
            return prefix
        c=2
        while os.path.lexists(path+prefix+' ('+str(c)+')'+ext):
            c=c+1
        return prefix+' ('+str(c)+')'
    def run(self):
        self.abort=False
        if not self.abort:
            self.uri=self.uris[0]
            self.parent.gauge1.SetValue(0.0)
            self.parent.thisvideo.append(self.parent.videos[self.parent.converting])
            self.filename=REGEX_FILE_CLEANUP_FILENAME.sub('',self.parent.meta[self.parent.videos[self.parent.converting]]['name'])
            self.profile=int(self.parent.meta[self.parent.videos[self.parent.converting]]['profile'])
            self.outdir=self.parent.prefs.getp(self.profile,'Outdir')
            if self.outdir[-1:]==os.sep:
                self.outdir=self.outdir[0:-1]
            if not os.path.lexists(self.outdir):
                os.makedirs(self.outdir)
            elif not os.path.isdir(self.outdir):
                os.remove(self.outdir)
                os.makedirs(self.outdir)
            self.outdir=self.outdir+os.sep
            if os.path.lexists(self.uri):
                self.stream=self.uri # It's a file stream, ffmpeg will take care of it
            else:
                self.stream='-' # It's another stream, spawn a downloader thread to take care of it and feed the content to ffmpeg via stdin
            if self.profile==-1: # Do not encode, just copy
                try:
                    failed=False
                    if self.stream=='-': # Spawn a downloader
                        src=DamnURLPicker(self.uris)
                        total=int(src.info()['Content-Length'])
                        try:
                            tmpuri=src.info()['Content-Disposition'][src.info()['Content-Disposition'].find('filename=')+9:]
                        except:
                            tmpuri='video.avi' # And pray for the best!
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
                    self.parent.SetStatusText('Copying '+self.parent.meta[self.parent.videos[self.parent.converting]]['name']+' to '+self.filename+ext+'...')
                    while keepgoing and not self.abort:
                        i=src.read(256)
                        if len(i):
                            dst.write(i)
                            copied+=256.0
                        else:
                            copied=total
                            keepgoing=False
                        self.parent.gauge1.SetValue(min((100.0,copied/total*100.0)))
                except:
                    failed=True
                self.grabberrun=False
                if self.abort or failed:
                    self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Failure.'
                    self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,'Failure.')
                else:
                    self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Success!'
                    self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,'Success!')
                self.parent.go(aborted=self.abort)
                return
            os_exe_ext=''
            if DV_OS_NAME=='nt':
                os_exe_ext='.exe'
            elif DV_OS_NAME=='mac':
                os_exe_ext='osx'
            self.passes=1
            cmd=[DV_BIN_PATH+'ffmpeg'+os_exe_ext,'-i','?DAMNVID_VIDEO_STREAM?','-y','-title',self.parent.meta[self.parent.videos[self.parent.converting]]['name'],'-comment','Converted by DamnVid '+DV_VERSION+'.','-deinterlace','-passlogfile',DV_TMP_PATH+'pass']
            for i in DV_PREFERENCES.keys():
                if i[0:25]=='damnvid-profile:encoding_':
                    i=i[16:]
                    pref=self.parent.prefs.getp(self.profile,i)
                    if pref:
                        if type(DV_PREFERENCES['damnvid-profile:'+i]['kind']) is type(''):
                            if DV_PREFERENCES['damnvid-profile:'+i]['kind'][0]=='%':
                                pref=str(round(float(pref),0)) # Round
                        if i=='encoding_pass':
                            pref='?DAMNVID_VIDEO_PASS?'
                        cmd.extend(['-'+i[9:],pref])
            vidformat=self.parent.prefs.getp(self.profile,'Encoding_f')
            self.vcodec=self.parent.prefs.getp(self.profile,'Encoding_vcodec')
            self.totalpasses=self.parent.prefs.getp(self.profile,'Encoding_pass')
            if not self.totalpasses:
                self.totalpasses=1
            else:
                self.totalpasses=int(self.totalpasses)
            if vidformat and DV_FILE_EXT.has_key(vidformat):
                ext='.'+DV_FILE_EXT[vidformat]
            else:
                if self.vcodec and DV_FILE_EXT_BY_CODEC.has_key(self.vcodec):
                    ext='.'+DV_FILE_EXT_BY_CODEC[self.vcodec]
                else:
                    ext='.avi'
            flags=[]
            if self.vcodec and DV_CODEC_ADVANCED_CL.has_key(self.vcodec):
                for o in DV_CODEC_ADVANCED_CL[self.vcodec]:
                    if type(o) is type(''):
                        if o not in flags: # If the flag is already there, don't add it again
                            flags.append(o)
                    else:
                        if '-'+o[0] not in cmd: # If the option is already there, don't overwrite it
                            cmd.extend(['-'+o[0],o[1]])
            if len(flags):
                cmd.extend(['-flags',''.join(flags)])
            self.filename=self.getfinalfilename(self.outdir,self.filename,ext)
            self.filenamenoext=self.filename
            self.tmpfilename=self.gettmpfilename(DV_TMP_PATH,self.filenamenoext,ext)
            cmd.append('?DAMNVID_OUTPUT_FILE?')
            self.filename=self.filenamenoext+ext
            self.duration=None
            self.parent.SetStatusText('Converting '+self.parent.meta[self.parent.videos[self.parent.converting]]['name']+' to '+self.filename+'...')
            while int(self.passes)<=int(self.totalpasses) and not self.abort:
                if self.totalpasses!=1:
                    self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Pass '+str(self.passes)+'/'+str(self.totalpasses)+'...'
                    self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,'Pass '+str(self.passes)+'/'+str(self.totalpasses)+'...')
                if self.passes!=1:
                    self.stream=DV_TMP_PATH+self.tmpfilename
                    self.tmpfilename=self.gettmpfilename(DV_TMP_PATH,self.filenamenoext,ext)
                self.process=DamnSpawner(self.cmd2str(cmd),stderr=subprocess.PIPE,stdin=subprocess.PIPE,cwd=os.path.dirname(DV_TMP_PATH))
                if self.stream=='-':
                    self.feeder=DamnDownloader(self.uris,self.process.stdin)
                    self.feeder.start()
                curline=''
                while self.process.poll()==None and not self.abort:
                    c=self.process.stderr.read(1)
                    curline+=c
                    if c=="\r" or c=="\n":
                        self.parseLine(curline)
                        curline=''
                self.passes+=1
            self.parent.gauge1.SetValue(100.0)
            result=self.process.poll() # The process is complete, but .poll() still returns the process's return code
            time.sleep(.25) # Wait a bit
            self.grabberrun=False # That'll make the DamnConverterGrabber wake up just in case
            if result and os.path.lexists(DV_TMP_PATH+self.tmpfilename):
                os.remove(DV_TMP_PATH+self.tmpfilename) # Delete the output file if ffmpeg has exitted with a bad return code
            for i in os.listdir(os.path.dirname(DV_TMP_PATH)):
                if i[0:8]=='damnvid-':
                    i=i[8:]
                    if i==self.tmpfilename and not result:
                        try:
                            os.rename(DV_TMP_PATH+i,self.outdir+self.filename)
                        except: # Maybe the file still isn't unlocked, it happens... Wait moar and retry
                            try:
                                time.sleep(2)
                                os.rename(DV_TMP_PATH+i,self.outdir+self.filename)
                            except: # Now this is really bad, alert the user
                                dlg=wx.MessageDialog(None,'DamnVid successfully converted the file but something prevents it from moving it to the output directory.\nAll hope is not lost, you can still move the file by yourself. It is here:\n'+DV_TMP_PATH+i,'Cannot move file!',wx.OK|wx.ICON_EXCLAMATION)
                                dlg.SetIcon(DV_ICON)
                                dlg.ShowModal()
                                dlg.Destroy()
                    else:
                        try:
                            os.remove(DV_TMP_PATH+i)
                        except:
                            pass
            if not result:
                self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Success!'
                self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,'Success!')
                self.parent.go(aborted=self.abort)
                return
            self.parent.meta[self.parent.videos[self.parent.converting]]['status']='Failure.'
            self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,'Failure.')
            self.parent.go(aborted=self.abort)
    def parseLine(self,line):
        if self.duration==None:
            res=REGEX_FFMPEG_DURATION_EXTRACT.search(line)
            if res:
                self.duration=int(res.group(1))*3600+int(res.group(2))*60+float(res.group(3))
        else:
            res=REGEX_FFMPEG_TIME_EXTRACT.search(line)
            if res:
                self.parent.gauge1.SetValue(float(float(res.group(1))/self.duration/float(self.totalpasses)+float(float(self.passes-1)/float(self.totalpasses)))*100.0) # Uhm, maybe too many float()s in there?
                self.parent.list.SetStringItem(self.parent.converting,ID_COL_VIDSTAT,self.parent.meta[self.parent.videos[self.parent.converting]]['status']+' ['+str(int(100.0*float(res.group(1))/self.duration))+'%]') # This one doesn't care about the number of passes
    def abortProcess(self): # Cannot send "q" because it's not a shell'd subprocess. Got to kill ffmpeg.
        self.abort=True # This prevents the converter from going to the next file
        if self.profile!=-1:
            if DV_OS_NAME=='nt':
                DamnSpawner('TASKKILL /PID '+str(self.process.pid)+' /F').wait()
            elif DV_OS_NAME=='mac':
                DamnSpawner('kill -SIGTERM '+str(self.process.pid)).wait() # Untested, from http://www.cs.cmu.edu/~benhdj/Mac/unix.html but with SIGTERM instead of SIGSTOP
            else:
                os.kill(self.process.pid,signal.SIGTERM)
            time.sleep(.5) # Wait a bit, let the files get unlocked
            try:
                os.remove(self.outdir+self.tmpfilename)
            except:
                pass # Maybe the file wasn't created yet
class DamnDownloader(thr.Thread): # Retrieves video by HTTP and feeds it back to ffmpeg via stdin
    def __init__(self,uri,pipe):
        self.uri=uri
        self.pipe=pipe
        thr.Thread.__init__(self)
    def run(self):
        self.http=DamnURLPicker(self.uri)
        if self.http==None:
            print 'HTTP error'
            try:
                self.pipe.close() # This tells ffmpeg that it's the end of the stream
            except:
                pass
            return None
        writing=''
        direct=False
        for i in self.http:
            try:
                if direct:
                    self.pipe.write(i)
                else:
                    writing+=i
                    if len(writing)>102400: # Cache the first 100 KB and write them all at once (solves ffmpeg's "moov atom not found" problem)
                        self.pipe.write(writing)
                        direct=True
                        del writing
            except:
                break
        if not direct:  # Video weighs less than 100 KB (!)
            try:
                self.pipe.write(writing)
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
class DamnMainFrame(wx.Frame): # The main window
    def __init__(self,parent,id,title):
        global DV_ICON
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(780,580),style=wx.DEFAULT_FRAME_STYLE)
        if os.path.lexists(DV_CONF_FILE_DIRECTORY+'lastversion.damnvid'):
            lastversion=open(DV_CONF_FILE_DIRECTORY+'lastversion.damnvid','r')
            dvversion=lastversion.readline().strip()
            lastversion.close()
            del lastversion
        else:
            dvversion='old' # This is not an arbitrary erroneous value, it's handy in the concatenation on the wx.FileDialog line below
        if dvversion!=DV_VERSION: # Just updated to new version, ask what to do about the preferences
            dlg=wx.MessageDialog(self,'DamnVid was updated to '+DV_VERSION+'.\nIf anything fails, try to uninstall DamnVid before updating it again.\n\nFrom a version to another, DamnVid\'s default preferences may vary, and their structure may change.\nIf that is the case, your current preferences may not work anymore.\nAdditionally, new versions of DamnVid often come with new or updated encoding profiles. That is why DamnVid is going to overwrite your current configuration.\nDo you want to export your current preferences, before they get overwritten? You might then try to import them back using the "Import" button in the Preferences pane.','DamnVid was successfully updated',wx.YES|wx.NO|wx.ICON_QUESTION)
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
            os.remove(DV_CONF_FILE)
            shutil.copyfile(DV_CURDIR+'conf'+os.sep+'conf.ini',DV_CONF_FILE)
            lastversion=open(DV_CONF_FILE_DIRECTORY+'lastversion.damnvid','w')
            lastversion.write(DV_VERSION)
            lastversion.close()
            del lastversion
            tmpprefs=DamnVidPrefs()
            tmpprefs.set('CheckForUpdates',checkupdates)
            tmpprefs.save()
            del tmpprefs
        self.CreateStatusBar()
        filemenu=wx.Menu()
        filemenu.Append(ID_MENU_ADD_FILE,'&Add files...','Adds damn videos from local files.')
        self.Bind(wx.EVT_MENU,self.onAddFile,id=ID_MENU_ADD_FILE)
        filemenu.Append(ID_MENU_ADD_URL,'Add &URL...','Adds a damn video from a URL.')
        self.Bind(wx.EVT_MENU,self.onAddURL,id=ID_MENU_ADD_URL)
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_EXIT,'E&xit','Terminates DamnVid '+DV_VERSION+'.')
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
        halpmenu.Append(ID_MENU_ABOUT,'&About DamnVid '+DV_VERSION+'...','Displays information about DamnVid.')
        self.Bind(wx.EVT_MENU,self.onAboutDV,id=ID_MENU_ABOUT)
        self.menubar=wx.MenuBar()
        self.menubar.Append(filemenu,'&File')
        self.menubar.Append(vidmenu,'&DamnVid')
        self.menubar.Append(halpmenu,'&Help')
        self.SetMenuBar(self.menubar)
        vbox=wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        panel=wx.Panel(self,-1)
        vbox.Add(panel,1,wx.EXPAND)
        grid=wx.FlexGridSizer(2,2,7,7)
        panel1=wx.Panel(panel,-1)
        grid.Add(panel1,1,wx.EXPAND)
        panel2=wx.Panel(panel,-1)
        grid.Add(panel2,0)
        panel3=wx.Panel(panel,-1)
        grid.Add(panel3,0,wx.EXPAND)
        panel4=wx.Panel(panel,-1)
        grid.Add(panel4,0)
        panel.SetSizer(grid)
        hbox1=wx.BoxSizer(wx.HORIZONTAL)
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
        il=wx.ImageList(16,16,True)
        self.ID_ICON_LOCAL=il.Add(wx.Bitmap(DV_IMAGES_PATH+'video.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_ONLINE=il.Add(wx.Bitmap(DV_IMAGES_PATH+'online.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_YOUTUBE=il.Add(wx.Bitmap(DV_IMAGES_PATH+'youtube.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_YOUTUBEHD=il.Add(wx.Bitmap(DV_IMAGES_PATH+'youtubehd.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_GVIDEO=il.Add(wx.Bitmap(DV_IMAGES_PATH+'googlevideo.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_VEOH=il.Add(wx.Bitmap(DV_IMAGES_PATH+'veoh.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_DAILYMOTION=il.Add(wx.Bitmap(DV_IMAGES_PATH+'dailymotion.png',wx.BITMAP_TYPE_PNG))
        self.list.AssignImageList(il,wx.IMAGE_LIST_SMALL)
        self.list.SetDropTarget(DamnDropHandler(self))
        self.list.Bind(wx.EVT_RIGHT_DOWN,self.list.onRightClick)
        hbox1.Add(self.list,1,wx.EXPAND)
        sizer2=wx.BoxSizer(wx.VERTICAL)
        panel2.SetSizer(sizer2)
        self.addByFile=wx.Button(panel2,-1,'Add Files')
        sizer2.Add(self.addByFile,0)
        self.Bind(wx.EVT_BUTTON,self.onAddFile,self.addByFile)
        self.addByURL=wx.Button(panel2,-1,'Add URL')
        sizer2.Add(self.addByURL,0)
        self.Bind(wx.EVT_BUTTON,self.onAddURL,self.addByURL)
        self.btnRename=wx.Button(panel2,-1,'Rename')
        sizer2.Add(self.btnRename,0)
        self.Bind(wx.EVT_BUTTON,self.onRename,self.btnRename)
        self.btnMoveUp=wx.Button(panel2,-1,'Move up')
        sizer2.Add(self.btnMoveUp,0)
        self.Bind(wx.EVT_BUTTON,self.onMoveUp,self.btnMoveUp)
        self.btnMoveDown=wx.Button(panel2,-1,'Move down')
        sizer2.Add(self.btnMoveDown,0)
        self.Bind(wx.EVT_BUTTON,self.onMoveDown,self.btnMoveDown)
        self.delSelection=wx.Button(panel2,-1,'Remove')
        sizer2.Add(self.delSelection,0)
        self.Bind(wx.EVT_BUTTON,self.onDelSelection,self.delSelection)
        self.delAll=wx.Button(panel2,-1,'Remove all')
        sizer2.Add(self.delAll,0)
        self.Bind(wx.EVT_BUTTON,self.onDelAll,self.delAll)
        self.gobutton1=wx.Button(panel2,-1,'Let\'s go!')
        sizer2.Add(self.gobutton1,0)
        self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton1)
        hbox3=wx.BoxSizer(wx.HORIZONTAL)
        panel3.SetSizer(hbox3)
        hbox3.Add(wx.StaticText(panel3,-1,'Current video: '),0,wx.ALIGN_CENTER_VERTICAL)
        self.gauge1=wx.Gauge(panel3,-1)
        hbox3.Add(self.gauge1,1,wx.EXPAND)
        #self.gobutton2=wx.Button(bottompanel,-1,'Let\'s go!')
        #self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton2)
        #grid.Add(wx.StaticText(bottompanel,-1,''),0)
        #grid.Add(self.gobutton2,0)
        #grid.Add(wx.StaticText(bottompanel,-1,'Total progress:'),0)
        #self.gauge2=wx.Gauge(bottompanel,-1)
        #grid.Add(self.gauge2,1,wx.EXPAND)
        hbox4=wx.BoxSizer(wx.VERTICAL)
        panel4.SetSizer(hbox4)
        self.stopbutton=wx.Button(panel4,-1,'Stop')
        hbox4.Add(self.stopbutton)
        self.stopbutton.Disable()
        self.Bind(wx.EVT_BUTTON,self.onStop,self.stopbutton)
        grid.AddGrowableRow(0,1)
        grid.AddGrowableCol(0,1)
        self.Bind(wx.EVT_CLOSE,self.onClose,self)
        DV_ICON=wx.Icon(DV_IMAGES_PATH+'icon.ico',wx.BITMAP_TYPE_ICO)
        self.SetIcon(DV_ICON)
        self.videos=[]
        self.thisbatch=0
        self.thisvideo=[]
        self.meta={}
        self.prefs=DamnVidPrefs()
        self.converting=-1
        self.isclosing=False
        self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
        if DV_FIRST_RUN:
            dlg=wx.MessageDialog(self,'Welcome to DamnVid '+DV_VERSION+'!\nWould you like DamnVid to check for updates every time it starts?','Welcome to DamnVid '+DV_VERSION+'!',wx.YES|wx.NO|wx.ICON_QUESTION)
            if dlg.ShowModal()==wx.ID_YES:
                self.prefs.set('CheckForUpdates','True')
            else:
                self.prefs.set('CheckForUpdates','False')
        if self.prefs.get('CheckForUpdates')=='True':
            self.onCheckUpdates(None)
    def onExit(self,event):
        self.Close(True)
    def onListKeyDown(self,event):
        if (event.GetKeyCode()==8 or event.GetKeyCode()==127) and self.list.GetSelectedItemCount(): # Backspace or delete, but only when there's at least one selected video
            self.onDelSelection(None)
    def onAddFile(self,event):
        d=os.getcwd()
        if os.path.lexists(self.prefs.get('LastFileDir')):
            if os.path.isdir(self.prefs.get('LastFileDir')):
                d=self.prefs.get('LastFileDir')
        elif os.path.lexists(self.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
            if os.path.isdir(self.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
                d=self.prefs.expandPath('?DAMNVID_MY_VIDEOS?')
        dlg=wx.FileDialog(self,'Choose a damn video.',d,'','All files|*.*|AVI files (*.avi)|*.avi|MPEG Videos (*.mpg)|*.mpg|QuickTime movies (*.mov)|*.mov|Flash Video (*.flv)|*.flv|Windows Media Videos (*.wmv)|*.wmv',wx.OPEN|wx.FD_MULTIPLE)
        dlg.SetIcon(DV_ICON)
        if dlg.ShowModal()==wx.ID_OK:
            vids=dlg.GetPaths()
            self.prefs.set('LastFileDir',os.path.dirname(vids[0]))
            self.prefs.save()
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
                if not REGEX_HTTP_GENERIC.match(default):
                    default='' # Only set that as default text if the clipboard's text content is not a URL
        except:
            default=''
        try:
            wx.TheClipboard.Close() # In case there's been an error before the clipboard could be closed, try to close it now
        except:
            pass # There's probably wasn't any error, just pass
        dlg=wx.TextEntryDialog(self,'Enter the URL of the video you wish to download.','Enter URL.',default)
        dlg.SetIcon(DV_ICON)
        if dlg.ShowModal()==wx.ID_OK:
            self.addVid([dlg.GetValue()])
        dlg.Destroy()
    def validURI(self,uri):
        if REGEX_HTTP_GENERIC.match(uri):
            if REGEX_HTTP_YOUTUBE.match(uri):
                return 'YouTube Video'
            else:
                # Add elif's?
                return 'Online video' # Not necessarily true, but ffmpeg will tell
        elif os.path.lexists(uri):
            return 'Local file'
        return None
    def getVidName(self,uri):
        # Veoh is not in this list because it's taken directly from the addVid function in order to prevent redownloading the page
        if uri[0:3]=='yt:':
            try:
                ret=[]
                html=urllib2.urlopen('http://www.youtube.com/watch?v='+uri[3:])
                for i in html:
                    res=REGEX_HTTP_YOUTUBE_TITLE_EXTRACT.search(i)
                    if res:
                        ret.append(self.noHtmlEnt(res.group(1)))
                    else:
                        res=REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                        if res:
                            ret.append(self.noHtmlEnt(res.group(1)))
                    res2=REGEX_HTTP_YOUTUBE_TICKET_EXTRACT.search(i)
                    if res2:
                        url=DamnURLPicker(['http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res2.group(3)+'&fmt=22','http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res2.group(3)+'&fmt=18','http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res2.group(3)],True)
                        if url=='http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res2.group(3)+'&fmt=22':
                            ret.append('HD')
                return ret
            except:
                pass # Can't grab this? Return Unknown title
        elif uri[0:3]=='gv:':
            try:
                html=urllib2.urlopen('http://video.google.com/videoplay?docid='+uri[3:])
                for i in html:
                    res=REGEX_HTTP_GVIDEO_TITLE_EXTRACT.search(i)
                    if res:
                        return self.noHtmlEnt(res.group(1))
                    else:
                        res=REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                        if res:
                            return self.noHtmlEnt(res.group(1))
                        else:
                            pass # Return Unknown title
            except:
                pass # Can't grab this? Return Unknown title
        elif uri[0:3]=='dm:':
            try:
                html=urllib2.urlopen(uri[3:])
                for i in html:
                    res=REGEX_HTTP_DAILYMOTION_TITLE_EXTRACT.search(i)
                    if res:
                        return self.noHtmlEnt(res.group(1))
                    else:
                        res=REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                        if res:
                            return self.noHtmlEnt(res.group(1))
                        else:
                            pass # Return Unknown title
            except:
                pass # Can't grab this? Return Unknown title
        else:
            try:
                html=urllib2.urlopen(uri[3:])
                for i in html:
                    res=REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                    if res:
                        return self.noHtmlEnt(res.group(1))
            except:
                pass # Can't grab this? Return Unknown title
        return 'Unknown title'
    def noHtmlEnt(self,html): # Replaces HTML entities from html
        for i in htmlentitydefs.entitydefs.iterkeys():
            html=html.replace('&'+str(i)+';',htmlentitydefs.entitydefs[i])
        return html
    def addVid(self,uris):
        for uri in uris:
            if self.validURI(uri):
                if REGEX_HTTP_GENERIC.match(uri):
                    # It's a URL
                    match=REGEX_HTTP_YOUTUBE.search(uri)
                    if match:
                        uri='yt:'+match.group(1)
                        name=self.getVidName(uri)
                        profile='youtube'
                        icon=self.ID_ICON_YOUTUBE
                        if type(name) is not type(''):
                            if len(name)>1 and name[1]=='HD':
                                profile='youtubehd'
                                icon=self.ID_ICON_YOUTUBEHD
                            name=name[0]
                        self.addValid({'name':name,'profile':int(self.prefs.getd(profile)),'profilemodified':False,'fromfile':name,'dirname':'http://www.youtube.com/watch?v='+match.group(1),'uri':uri,'status':'Pending.','icon':icon})
                    elif REGEX_HTTP_GVIDEO.search(uri):
                        match=REGEX_HTTP_GVIDEO.search(uri)
                        uri='gv:'+match.group(1)
                        name=self.getVidName(uri)
                        self.addValid({'name':name,'profile':int(self.prefs.getd('googlevideo')),'profilemodified':False,'fromfile':name,'dirname':'http://video.google.com/videoplay?docid='+match.group(1),'uri':uri,'status':'Pending.','icon':self.ID_ICON_GVIDEO})
                    elif REGEX_HTTP_VEOH.search(uri):
                        html=urllib2.urlopen(uri) # Gotta download it right there instead of downloading it twice with the getVidName function
                        name='Unknown title'
                        Id=''
                        for i in html:
                            match=REGEX_HTTP_VEOH_TITLE_EXTRACT.search(i)
                            if match:
                                name=self.noHtmlEnt(match.group(1))
                            else:
                                match=REGEX_HTTP_VEOH_ID_EXTRACT.search(i)
                                if match:
                                    Id=match.group(1)
                        if Id:
                            uri='vh:'+Id
                            self.addValid({'name':name,'profile':int(self.prefs.getd('veoh')),'profilemodified':False,'fromfile':name,'dirname':'http://www.veoh.com/videos/'+Id,'uri':uri,'status':'Pending.','icon':self.ID_ICON_VEOH})
                        else:
                            self.SetStatusText('Couldn\'t detect Veoh video.')
                    elif REGEX_HTTP_DAILYMOTION.search(uri):
                        uri='dm:'+uri
                        name=self.getVidName(uri)
                        self.addValid({'name':name,'profile':int(self.prefs.getd('dailymotion')),'profilemodified':False,'fromfile':name,'dirname':uri[3:],'uri':uri,'status':'Pending.','icon':self.ID_ICON_DAILYMOTION})
                    else:
                        name=self.getVidName(uri)
                        if name=='Unknown title':
                            name=REGEX_HTTP_EXTRACT_FILENAME.sub('',uri)
                        self.addValid({'name':name,'profile':int(self.prefs.getd('web')),'profilemodified':False,'fromfile':name,'dirname':REGEX_HTTP_EXTRACT_DIRNAME.sub('\\1/',uri),'uri':uri,'status':'Pending.','icon':self.ID_ICON_ONLINE})
                else:
                    # It's a file or a directory
                    if os.path.isdir(uri):
                        if self.prefs.get('DirRecursion')=='True':
                            for i in os.listdir(uri):
                                self.addVid([uri+os.sep+i]) # This is recursive; if i is a directory, this block will be executed for it too
                        else:
                            if len(uris)==1: # Only one dir, so an alert here is tolerable
                                dlg=wx.MessageDialog(None,'This is a directory, but recursion is disabled in the preferences. Please enable it if you want DamnVid to go through directories.','Recursion is disabled.',wx.OK|wx.ICON_EXCLAMATION)
                                dlg.SetIcon(DV_ICON)
                                dlg.ShowModal()
                                dlg.Destroy()
                            else:
                                self.SetStatusText('Skipped '+uri+' (directory recursion disabled).')
                    else:
                        filename=os.path.basename(uri)
                        if uri in self.videos:
                            self.SetStatusText('Skipped '+filename+' (already in list).')
                            if len(uris)==1: # There's only one file, so an alert here is tolerable
                                dlg=wx.MessageDialog(None,'This video is already in the list!','Duplicate found',wx.ICON_EXCLAMATION|wx.OK)
                                dlg.SetIcon(DV_ICON)
                                dlg.ShowModal()
                                dlg.Destroy()
                        else:
                            self.addValid({'name':filename[0:filename.rfind('.')],'profile':int(self.prefs.getd('file')),'profilemodified':False,'fromfile':filename,'uri':uri,'dirname':os.path.dirname(uri),'status':'Pending.','icon':self.ID_ICON_LOCAL})
            else:
                if len(uris)==1: # There's only one URI, so an alert here is tolerable
                    dlg=wx.MessageDialog(None,'This is not a valid video!','Invalid video',wx.ICON_EXCLAMATION|wx.OK)
                    dlg.SetIcon(DV_ICON)
                    dlg.ShowModal()
                    dlg.Destroy()
                self.SetStatusText('Skipped '+uri+' (invalid video).')
    def addValid(self,meta):
        curvid=len(self.videos)
        self.list.InsertStringItem(curvid,meta['name'])
        self.list.SetStringItem(curvid,ID_COL_VIDPROFILE,self.prefs.getp(meta['profile'],'name'))
        self.list.SetStringItem(curvid,ID_COL_VIDPATH,meta['dirname'])
        self.list.SetStringItem(curvid,ID_COL_VIDSTAT,meta['status'])
        self.list.SetItemImage(curvid,meta['icon'],meta['icon'])
        self.videos.append(meta['uri'])
        self.meta[meta['uri']]=meta
        self.SetStatusText('Added '+meta['name']+'.')
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
                self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
                if not aborted:
                    dlg=wx.MessageDialog(None,'Done!','Done!',wx.OK|wx.ICON_INFORMATION)
                else:
                    dlg=wx.MessageDialog(None,'Video conversion aborted.','Aborted',wx.OK|wx.ICON_INFORMATION)
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                self.converting=-1
                self.stopbutton.Disable()
                self.gobutton1.Enable()
                self.prefmenuitem.Enable()
                self.gauge1.SetValue(0.0)
    def onGo(self,event):
        if not len(self.videos):
            dlg=wx.MessageDialog(None,'Put some videos in the list first!','No videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.converting!=-1:
            dlg=wx.MessageDialog(None,'DamnVid '+DV_VERSION+' is already converting!','Already converting!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            success=0
            for i in self.videos:
                if self.meta[i]['status']=='Success!':
                    success=success+1
            if success==len(self.videos):
                dlg=wx.MessageDialog(None,'All videos in the list have already been processed!','Already done',wx.OK|wx.ICON_INFORMATION)
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.thisbatch=0
                self.thisvideo=[]
                self.stopbutton.Enable()
                self.gobutton1.Disable()
                self.prefmenuitem.Enable(False)
                self.go()
    def onStop(self,event):
        self.thread.abortProcess()
    def onRename(self,event):
        item=self.list.getAllSelectedItems()
        if len(item)>1:
            dlg=wx.MessageDialog(None,'You can only rename one video at a time.','Multiple videos selected.',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
        elif not len(item):
            dlg=wx.MessageDialog(None,'Select a video in order to rename it.','No videos selected',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            item=item[0]
            dlg=wx.TextEntryDialog(None,'Enter the new name for "'+self.meta[self.videos[item]]['name']+'".','Rename',self.meta[self.videos[item]]['name'])
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            self.meta[self.videos[item]]['name']=dlg.GetValue()
            self.list.SetStringItem(item,ID_COL_VIDNAME,dlg.GetValue())
            dlg.Destroy()
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
    def onMoveUp(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            if items[0]:
                for i in items:
                    self.invertVids(i,i-1)
            else:
                dlg=wx.MessageDialog(None,'You\'ve selected the first item in the list, which cannot be moved further up!','Invalid selection',wx.OK|wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Select some videos in the list first.','No videos selected!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
    def onMoveDown(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            if items[-1]<self.list.GetItemCount()-1:
                for i in reversed(self.list.getAllSelectedItems()):
                    self.invertVids(i,i+1)
            else:
                dlg=wx.MessageDialog(None,'You\'ve selected the last item in the list, which cannot be moved further down!','Invalid selection',wx.OK|wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV_ICON)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg=wx.MessageDialog(None,'Select some videos in the list first.','No videos selected!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
    def onChangeProfile(self,profile,event):
        items=self.list.getAllSelectedItems()
        for i in items:
            if self.meta[self.videos[i]]['profile']!=profile:
                self.meta[self.videos[i]]['profile']=profile
                self.meta[self.videos[i]]['profilemodified']=True
                self.list.SetStringItem(i,ID_COL_VIDPROFILE,self.prefs.getp(profile,'name'))
    def onPrefs(self,event):
        self.reopenprefs=False
        prefs=DamnVidPrefEditor(None,-1,'DamnVid '+DV_VERSION+' preferences',main=self)
        prefs.ShowModal()
        prefs.Destroy()
        if self.reopenprefs:
            self.onPrefs(event)
        else:
            for i in range(len(self.videos)):
                if self.meta[self.videos[i]]['profile']>=self.prefs.profiles or not self.meta[self.videos[i]]['profilemodified']:
                    # Yes, using icons as source identifiers, why not? Lol
                    if self.meta[self.videos[i]]['icon']==self.ID_ICON_LOCAL:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('file')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_ONLINE:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('web')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_VEOH:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('veoh')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_YOUTUBE:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('youtube')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_YOUTUBEHD:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('youtubehd')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_DAILYMOTION:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('dailymotion')
                    elif self.meta[self.videos[i]]['icon']==self.ID_ICON_GVIDEO:
                        self.meta[self.videos[i]]['profile']=self.prefs.getd('googlevideo')
                self.list.SetStringItem(i,ID_COL_VIDPROFILE,self.prefs.getp(self.meta[self.videos[i]]['profile'],'name'))
        try:
            del self.reopenprefs
        except:
            pass
    def onOpenOutDir(self,event):
        if DV_OS_NAME=='nt':
            os.system('explorer.exe "'+self.prefs.get('Outdir').replace('%CWD%',DV_CURDIR[0:-1]).replace('/',OS_+_SEPARATOR)+'"')
        else:
            pass # Halp here?
    def onHalp(self,event):
        webbrowser.open(DV_URL_HALP,2)
    def onCheckUpdates(self,event):
        msg=False
        try:
            html=urllib2.urlopen(DV_URL_UPDATE)
            for i in html:
                if REGEX_DAMNVID_VERSION_CHECK.search(i):
                    v=REGEX_DAMNVID_VERSION_CHECK.search(i).group(1)
                    if v==DV_VERSION:
                        msg='No new version available. You are running the latest version of DamnVid ('+DV_VERSION+').'
                        if event!=None: # event = None when checking for updates at startup
                            dlg=wx.MessageDialog(None,msg,'Already running latest version.',wx.ICON_INFORMATION|wx.OK)
                            dlg.SetIcon(DV_ICON)
                            dlg.ShowModal()
                    else:
                        msg='A new version ('+v+') is available! You are running DamnVid '+DV_VERSION+'.\nDo you want want to go to the download page?'
                        dlg=wx.MessageDialog(None,msg,'New version available!',wx.ICON_QUESTION|wx.YES_NO|wx.YES_DEFAULT)
                        dlg.SetIcon(DV_ICON)
                        if dlg.ShowModal()==wx.ID_YES:
                            webbrowser.open(DV_URL_DOWNLOAD,2)
                    raise IOError # Raise dummy error just to skip to the rest of the loop
        except:
            pass
        if not msg:
            dlg=wx.MessageDialog(None,'Could not retrieve latest version. Make sure you are connected to the Internet, and that no firewall is blocking DamnVid from the Internet.','Error',wx.ICON_ERROR|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
        try:
            dlg.Destroy()
        except:
            pass
        return None
    def onAboutDV(self,event):
        dlg=DamnAboutDamnVid(None,-1,main=self)
        dlg.SetIcon(DV_ICON)
        dlg.ShowModal()
        dlg.Destroy()
    def delVid(self,i):
        self.list.DeleteItem(i)
        for vid in range(len(self.thisvideo)):
            if self.thisvideo[vid]==self.videos[i]:
                self.thisvideo.pop(vid)
                self.thisbatch=self.thisbatch-1
        self.videos.pop(i)
        if self.converting>i:
            self.converting=self.converting-1
    def onDelSelection(self,event):
        items=self.list.getAllSelectedItems()
        if len(items):
            for i in reversed(items): # Sequence MUST be reversed, otherwise the first items get deleted first, which changes the indexes of the following items
                self.delVid(i)
        else:
            dlg=wx.MessageDialog(None,'You must select some videos from the list first!','Select some videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.SetIcon(DV_ICON)
            dlg.ShowModal()
            dlg.Destroy()
    def onDelAll(self,event):
        if len(self.videos):
            dlg=wx.MessageDialog(None,'Are you sure? (This will not delete any files, it will just remove them from the list.)','Confirmation',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
            dlg.SetIcon(DV_ICON)
            if dlg.ShowModal()==wx.ID_YES:
                if self.converting!=-1:
                    self.onStop(None) # Stop conversion if it's in progress
                self.list.DeleteAllItems()
                self.videos=[]
                self.thisvideo=[]
                self.thisbatch=0
        else:
            dlg=wx.MessageDialog(None,'Add some videos in the list first.','No videos!',wx.OK|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV_ICON)
        dlg.Destroy()
    def onClose(self,event):
        if self.converting!=-1:
            dlg=wx.MessageDialog(None,'DamnVid is currently converting a video! Closing DamnVid will cause it to abort the conversion.\r\nContinue?','Conversion in progress',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV_ICON)
            if dlg.ShowModal()==wx.ID_YES:
                self.isclosing=True
                self.onStop(None)
                self.Destroy()
        else:
            self.isclosing=True
            self.Destroy()
class DamnVid(wx.App):
    def OnInit(self):
        frame=DamnMainFrame(None,-1,'DamnVid '+DV_VERSION+' by WindPower')
        frame.Show(True)
        frame.Center()
        return True
app=DamnVid(0)
app.MainLoop()
