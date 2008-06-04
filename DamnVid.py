import wx # Oh my, it's wx.
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin # Mixin for wx.ListrCtrl, to enable autowidth on columns
import os # Filesystem functions.
import re # Regular expressions \o/
import subprocess # Spawn sub-processes (ffmpeg)
import time # Sleepin'
import urllib # Fetch data from the tubes
import htmlentitydefs # HTML entities dictionaries
import signal # Process signals
import types # Names of built-in types
try:
    import threading as thr # Threads
except ImportError:
    import dummy_threading as thr # Moar threads
# Begin constants
if os.name=='nt':
    OS_PATH_SEPARATOR='\\'
else:
    OS_PATH_SEPARATOR='/'
DV_VERSION='1.0'
DV_CONF_FILE='conf/conf.ini'.replace('/',OS_PATH_SEPARATOR)
DV_LINE_PARSING_STEP=2
DV_IMAGES_PATH='img/'.replace('/',OS_PATH_SEPARATOR)
DV_BIN_PATH='bin/'.replace('/',OS_PATH_SEPARATOR)
DV_TMP_PATH='temp/'.replace('/',OS_PATH_SEPARATOR)
DV_FILE_EXT={
    'mpeg4':'avi',
    'mpeg1video':'avi',
    'mpeg2video':'avi',
    'flv':'flv',
    'h261':'avi',
    'h263':'avi',
    'h263p':'avi',
    'msmpeg4':'avi',
    'msmpeg4v1':'avi',
    'msmpeg4v2':'avi',
    'wmv1':'wmv',
    'wmv2':'wmv'
} # This needs to be completed, or just fixed, since the video codec doesn't really define the file extension
DV_PREFERENCE_TYPE_VIDEO=1
DV_PREFERENCE_TYPE_AUDIO=2
DV_PREFERENCE_TYPE_OTHER=3
DV_PREFERENCE_TYPE={
    'Encoding_vcodec':{
        'name':'Codec',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':{
            'mpeg4':'MPEG-4',
            'mpeg1video':'MPEG-1',
            'mpeg2video':'MPEG-2',
            'flv':'Flash Video',
            'h263p':'H.263+',
            'h263':'H.263',
            'h261':'H.261',
            'msmpeg4':'Microsoft MPEG-4 v3',
            'msmpeg4v2':'Microsoft MPEG-4 v2',
            'msmpeg4v1':'Microsoft MPEG-4 v1',
            'wmv2':'Windows Media Video v2',
            'wmv1':'Windows Media Video v1'
        },
        'order':['mpeg4','mpeg1video','mpeg2video','flv','h263p','h263','h261','msmpeg4','msmpeg4v2','msmpeg4v1','wmv2', 'wmv1'], # Because Python can't fucking remember the order of dictionaries, it seems.
        'strict':True,
        'default':'mpeg4'
    },
    'Encoding_pass':{
        'name':'Number of passes',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':{
            '1':'1 pass',
            '2':'2 passes'
        },
        'order':['1','2'],
        'strict':True,
        'default':'1'
    },
    'Encoding_b':{
        'name':'Bitrate',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'intk:7-13', # Int in kilobytes
        'strict':None,
        'default':'768k'
    },
    'Encoding_bufsize':{
        'name':'Buffer size',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'int',
        'strict':False,
        'default':''
    },
    'DirRecursion':{
        'name':'Enable directory Recursion',
        'type':DV_PREFERENCE_TYPE_OTHER,
        'kind':'bool',
        'strict':True,
        'default':'True'
    },
    'Encoding_ab':{
        'name':'Bitrate',
        'type':DV_PREFERENCE_TYPE_AUDIO,
        'kind':'intk:5-10',
        'strict':True,
        'default':'128k'
    },
    'Encoding_ac':{
        'name':'Channels',
        'type':DV_PREFERENCE_TYPE_AUDIO,
        'kind':{
            '1':'1 (Mono)',
            '2':'2 (Stereo)'
        },
        'order':['1','2'],
        'strict':True,
        'default':'1'
    },
    'Encoding_r':{
        'name':'Frames per second',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'int',
        'strict':False,
        'default':''
    },
    'Encoding_vol':{
        'name':'Volume (%)',
        'type':DV_PREFERENCE_TYPE_AUDIO,
        'kind':'%256',
        'strict':False,
        'default':'256.0'
    },
    'Encoding_minrate':{
        'name':'Minimum bitrate',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'intk:7-13',
        'strict':False,
        'default':''
    },
    'Encoding_maxrate':{
        'name':'Maximum bitrate',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'intk:7-13',
        'strict':False,
        'default':''
    },
    'Encoding_acodec':{
        'name':'Codec',
        'type':DV_PREFERENCE_TYPE_AUDIO,
        'kind':{
            'libmp3lame':'MP3',
            'mp2':'MP2',
            'ac3':'AC-3',
            'flac':'FLAC',
            'libfaac':'libfaac AAC',
            'vorbis':'Vorbis',
            'wmav2':'Windows Media Audio v2',
            'wmav1':'Windows Media Audio v1'
        },
        'order':['libmp3lame','mp2','ac3','flac','libfaac','vorbis','wmav2','wmav1'],
        'strict':True,
        'default':''
    },
    'Encoding_g':{
        'name':'Group of pictures size',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'int',
        'strict':False,
        'default':''
    },
    'Encoding_ar':{
        'name':'Sampling frequency',
        'type':DV_PREFERENCE_TYPE_AUDIO,
        'kind':{
            '11250':'11250 Hz',
            '22500':'11250 Hz',
            '44100':'44100 Hz',
            '48000':'48000 Hz',
            '96000':'96000 Hz'
        },
        'order':['11250','22500','44100','48000','96000'],
        'strict':True,
        'default':'44100'
    },
    'Encoding_bt':{
        'name':'Bitrate tolerance',
        'type':DV_PREFERENCE_TYPE_VIDEO,
        'kind':'intk:3-10',
        'strict':False,
        'default':''
    },
    'Outdir':{
        'name':'Output directory',
        'type':DV_PREFERENCE_TYPE_OTHER,
        'kind':'dir',
        'strict':True,
        'default':'%CWD%/output/'
    }
}
DV_PREFERENCE_ORDER=['Encoding_vcodec','Encoding_r','Encoding_b','Encoding_minrate','Encoding_maxrate','Encoding_bt','Encoding_bufsize','Encoding_pass','Encoding_g','Encoding_acodec','Encoding_vol','Encoding_ab','Encoding_ar','Encoding_ac','DirRecursion','Outdir']
# Begin ID constants
ID_MENU_EXIT=101
ID_MENU_ADD_FILE=102
ID_MENU_ADD_URL=103
ID_MENU_GO=104
ID_MENU_PREFERENCES=105
ID_MENU_OUTDIR=106
ID_MENU_HALP=107
ID_MENU_ABOUT=109
ID_COL_VIDNAME=0
ID_COL_VIDSTAT=1
ID_COL_VIDPATH=2
# Begin regex constants
REGEX_FFMPEG_DURATION_EXTRACT=re.compile('^\\s*Duration: (\\d+):(\\d\\d):([.\\d]+),',re.IGNORECASE)
REGEX_FFMPEG_TIME_EXTRACT=re.compile('time=([.\\d]+)',re.IGNORECASE)
REGEX_HTTP_GENERIC=re.compile('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/;\w]*)?$',re.IGNORECASE)
REGEX_HTTP_YOUTUBE=re.compile('^https?://(?:[-_\w]+\.)*youtube\.com.*(?:v|(?:video_)?id)[/=]([-_\w]{6,})',re.IGNORECASE)
REGEX_HTTP_GVIDEO=re.compile('^https?://(?:[-_\w]+\.)*video\.google\.com.*(?:v|id)[/=]([-_\w]{10,})',re.IGNORECASE)
REGEX_HTTP_VEOH=re.compile('^https?://(?:[-_\w]+\.)*veoh\.com/videos/',re.IGNORECASE)
REGEX_HTTP_EXTRACT_FILENAME=re.compile('^.*/|[?#].*$')
REGEX_HTTP_EXTRACT_DIRNAME=re.compile('^([^?#]*)/.*?$')
REGEX_FILE_CLEANUP_FILENAME=re.compile('[\\/:?"|*<>]+')
REGEX_HTTP_GENERIC_TITLE_EXTRACT=re.compile('<title>([^<>]+)</title>',re.IGNORECASE)
REGEX_HTTP_YOUTUBE_TITLE_EXTRACT=re.compile('<title>YouTube - ([^<>]+)</title>',re.IGNORECASE)
REGEX_HTTP_YOUTUBE_TICKET_EXTRACT=re.compile('(["\']?)t\\1\\s*:\\s*([\'"])((?:(?!\\2).)+)\\2')
REGEX_HTTP_GVIDEO_TITLE_EXTRACT=REGEX_HTTP_GENERIC_TITLE_EXTRACT
REGEX_HTTP_GVIDEO_TICKET_EXTRACT=re.compile('If the download does not start automatically, right-click <a href="([^"]+)"',re.IGNORECASE)
REGEX_HTTP_VEOH_TITLE_EXTRACT=re.compile('<title>\s*([^<>]+) : Online Video \| Veoh Video Network</title>',re.IGNORECASE)
REGEX_HTTP_VEOH_ID_EXTRACT=re.compile('permalinkId=(\\w+)',re.IGNORECASE)
REGEX_HTTP_VEOH_SUBID_EXTRACT=re.compile('^\\w+?(\\d+).*$')
REGEX_HTTP_VEOH_TICKET_EXTRACT=re.compile('fullPreviewHashPath="([^"]+)"',re.IGNORECASE)
# End constants
class DamnDropHandler(wx.FileDropTarget): # Handles files dropped on the ListCtrl
    def __init__(self,parent):
        wx.FileDropTarget.__init__(self)
        self.parent=parent
    def OnDropFiles(self,x,y,filenames):
        self.parent.addVid(filenames)
class DamnListContextMenu(wx.Menu): # Context menu when right-clicking on the DamnList
    def __init__(self,parent):
        wx.Menu.__init__(self)
        self.parent=parent
        self.items=self.parent.getAllSelectedItems()
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
        if self.GetSelectedItemCount():
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
class DamnVidPrefs: # Preference manager... Should have used wx.Config
    def __init__(self):
        self.conf={}
        f=open(DV_CONF_FILE)
        for i in re.finditer('(?m)^([_\\w]+)=(.*)$',f.read()):
            self.conf[i.group(1)]=i.group(2).replace('%CWD%',os.getcwd()).replace('/',OS_PATH_SEPARATOR).strip()
        f.close()
    def get(self,name):
        try:
            return self.conf[name]
        except:
            self.conf[name]=''
            self.save()
            return ''
    def set(self,name,value):
        self.conf[name]=value
        return value
    def save(self):
        f=open(DV_CONF_FILE,'w')
        f.write('[DamnVid]')
        for i in self.conf:
            f.write("\r\n"+i+'='+str(self.conf[i]).replace(OS_PATH_SEPARATOR,'/'))
        f.close()
class DamnBrowseDirButton(wx.Button): # "Browse..." button for directories
    def __init__(self,parent,id,label,filefield):
        self.filefield=filefield
        wx.Button.__init__(self,parent,id,label)
    def onBrowse(self,event):
        dlg=wx.DirDialog(self,'Select DamnVid '+DV_VERSION+'\'s output directory.',self.filefield.GetValue(),style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal()==wx.ID_OK:
            self.filefield.SetValue(dlg.GetPath())
        dlg.Destroy()
class DamnVidPrefEditor(wx.Dialog): # Preference dialog (not manager)
    def __init__(self,parent,id,title,main):
        wx.Dialog.__init__(self,parent,id,title)
        self.parent=main
        self.controls={}
        self.listvalues={}
        self.toppanel=wx.Panel(self,-1)
        self.topvbox=wx.BoxSizer(wx.VERTICAL)
        self.toppanel.SetSizer(self.topvbox)
        self.hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.audiovideopanel=wx.Panel(self.toppanel,-1)
        self.topvbox.Add(self.audiovideopanel,1,wx.EXPAND)
        self.audiovideopanel.SetSizer(self.hbox)
        self.toppanel.SetSizer(self.topvbox)
        panel1=wx.Panel(self.audiovideopanel,-1)
        panel2=wx.Panel(self.audiovideopanel,-1)
        vbox1=wx.StaticBoxSizer(wx.StaticBox(panel1,-1,'Video encoding options'),wx.VERTICAL)
        vbox2=wx.StaticBoxSizer(wx.StaticBox(panel2,-1,'Audio encoding options'),wx.VERTICAL)
        self.hbox.Add(panel1,1,wx.EXPAND)
        self.hbox.Add(panel2,1,wx.EXPAND)
        panel1.SetSizer(vbox1)
        panel2.SetSizer(vbox2)
        self.grid1=wx.GridSizer(0,2)
        self.grid2=wx.GridSizer(0,2)
        vbox1.Add(self.grid1,0)
        vbox2.Add(self.grid2,0)
        self.topvbox.Add((0,5))
        for name in DV_PREFERENCE_ORDER:
            i=DV_PREFERENCE_TYPE[name]
            add=False
            val=''
            if i['type']==DV_PREFERENCE_TYPE_VIDEO:
                panel=panel1
                sizer=self.grid1
            elif i['type']==DV_PREFERENCE_TYPE_AUDIO:
                panel=panel2
                sizer=self.grid2
            else:
                panel=self.toppanel
                sizer=wx.BoxSizer(wx.HORIZONTAL)
                self.topvbox.Add(sizer,0,wx.EXPAND)
            if i['kind']!='bool': # Otherwise it's a checkbox, the label goes with it
                sizer.Add(wx.StaticText(panel,-1,i['name']+': '))
            if not self.parent.prefs.get(name):
                val='(default)'
            if type(i['kind']) is types.DictType:
                choices=['(default)']
                for f in i['order']:
                    choices.append(i['kind'][f])
                if not val:
                    val=i['kind'][self.parent.prefs.get(name)]
                self.controls[name]=self.makeList(i['strict'],choices,panel,val)
                self.listvalues[name]=choices
                sizer.Add(self.controls[name])
            elif i['kind'][0:3]=='int':
                choices=['(default)']
                if len(i['kind'])>3:
                    for f in range(int(i['kind'][i['kind'].find(':')+1:i['kind'].find('-')]),int(i['kind'][i['kind'].find('-')+1:])):
                        choices.append(str(pow(2,f))+'k')
                if not val:
                    val=self.parent.prefs.get(name)
                self.controls[name]=self.makeList(i['strict'],choices,panel,val)
                self.listvalues[name]=choices
                sizer.Add(self.controls[name])
            elif i['kind'][0]=='%':
                self.controls[name]=wx.SpinCtrl(panel,-1,initial=int(100.0*float(self.parent.prefs.get(name))/float(i['kind'][1:])),min=0,max=200)
                sizer.Add(self.controls[name])
            elif i['kind']=='dir':
                self.controls[name]=wx.TextCtrl(panel,-1,self.parent.prefs.get(name))
                sizer.Add(self.controls[name],1,wx.EXPAND)
                button=DamnBrowseDirButton(panel,-1,'Browse...',self.controls[name])
                sizer.Add(button,0)
                self.Bind(wx.EVT_BUTTON,button.onBrowse,button)
            elif i['kind']=='bool':
                self.controls[name]=wx.CheckBox(panel,-1,i['name'])
                self.controls[name].SetValue(self.parent.prefs.get(name)=='True')
                sizer.Add(self.controls[name])
        tophbox=wx.BoxSizer(wx.HORIZONTAL)
        self.topvbox.Add(tophbox,0,wx.EXPAND)
        self.okButton=wx.Button(self.toppanel,wx.ID_OK,'OK')
        self.Bind(wx.EVT_BUTTON,self.onOK,self.okButton)
        self.closeButton=wx.Button(self.toppanel,wx.ID_CLOSE,'Cancel')
        self.Bind(wx.EVT_BUTTON,self.onClose,self.closeButton)
        reset=wx.Choice(self.toppanel,-1,choices=['Reset to default config...','DamnVid '+DV_VERSION+' default','FFmpeg default'])
        reset.SetSelection(0)
        self.Bind(wx.EVT_CHOICE,self.onReset,reset)
        tophbox.Add(reset,0,wx.ALIGN_LEFT)
        tophbox.Add(wx.StaticText(self.toppanel,-1,''),1,wx.ALIGN_LEFT)
        tophbox.Add(self.okButton,0,wx.ALIGN_RIGHT)
        tophbox.Add(self.closeButton,0,wx.ALIGN_RIGHT)
        self.SetClientSize(self.toppanel.GetBestSize())
        self.Centre()
    def makeList(self,strict,choices,panel,value):
        if strict:
            cont=wx.Choice(panel,-1,choices=choices)
            if value=='(default)':
                cont.SetSelection(0)
            else:
                for f in range(len(choices)):
                    if choices[f]==value:
                        cont.SetSelection(f)
        else:
            cont=wx.ComboBox(panel,-1,choices=choices,value=value)
        return cont
    def getListValue(self,name,strict):
        if strict:
            val=self.listvalues[name][self.controls[name].GetSelection()]
        else:
            val=self.controls[name].GetValue()
        if val=='(default)':
            val=''
        elif type(DV_PREFERENCE_TYPE[name]['kind']) is types.DictType:
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
                if type(DV_PREFERENCE_TYPE[name]['kind']) is types.DictType:
                    value=DV_PREFERENCE_TYPE[name]['kind'][value]
                c=0
                for i in self.listvalues[name]:
                    if i==value:
                        self.controls[name].SetSelection(c)
                    c=c+1
            else:
                self.controls[name].SetValue(value)
    def onOK(self,event):
        prefs={}
        for name,i in DV_PREFERENCE_TYPE.iteritems():
            if type(i['kind']) is types.DictType:
                prefs[name]=self.getListValue(name,i['strict'])
            elif i['kind'][0:3]=='int':
                prefs[name]=self.getListValue(name,i['strict'])
            elif i['kind']=='bool':
                if self.controls[name].GetValue():
                    prefs[name]='True'
                else:
                    prefs[name]='False'
            elif i['kind']=='dir':
                if os.path.lexists(self.controls[name].GetValue()):
                    if os.path.isdir(self.controls[name].GetValue()):
                        prefs[name]=self.controls[name].GetValue()
            elif i['kind'][0]=='%':
                prefs[name]=str(round(float(self.controls[name].GetValue())*float(i['kind'][1:])/100.0,5)) # This may be a float, but DamnConverter will ensure it's an int when converting
            self.parent.prefs.set(name,prefs[name])
        self.parent.prefs.save()
        self.Close(True)
    def onReset(self,event):
        l=event.GetEventObject()
        if l.GetSelection()==1: # DamnVid default
            for name,i in DV_PREFERENCE_TYPE.iteritems():
                if type(i['kind']) is types.DictType:
                    self.setListValue(name,i['strict'],i['default'])
                elif i['kind'][0:3]=='int':
                    self.setListValue(name,i['strict'],i['default'])
                elif i['kind']=='dir':
                    self.controls[name].SetValue(i['default'].replace('%CWD%',os.getcwd()).replace('/',OS_PATH_SEPARATOR))
                elif i['kind'][0]=='%':
                    self.controls[name].SetValue(int(100.0*float(i['default'])/float(i['kind'][1:])))
                elif i['kind']=='bool':
                    self.controls[name].SetValue(i['default']=='True')
        elif l.GetSelection()==2: # FFmpeg default
            for name,i in DV_PREFERENCE_TYPE.iteritems():
                if name[0:9]=='Encoding_':
                    if type(i['kind']) is types.DictType:
                        self.setListValue(name,i['strict'],'')
                    elif i['kind'][0:3]=='int':
                        self.setListValue(name,i['strict'],'')
                    elif i['kind'][0]=='%':
                        self.controls[name].SetValue(int(100.0))
        l.SetSelection(0)
    def onClose(self,event):
        self.Close(True)
class DamnWait(wx.Dialog): # Modal dialog that displays progress
    def __init__(self,parent,id,title,main):
        wx.Dialog.__init__(self,parent,id,title,size=(250,150),style=wx.CLOSE_BOX)
        self.parent=main
        panel=wx.Panel(self,-1)
        self.vbox=wx.BoxSizer(wx.VERTICAL)
        self.hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.gauge=wx.Gauge(panel,-1,size=(220,25))
        self.vbox.Add(self.gauge,1,wx.ALIGN_CENTRE)
        self.vbox.Add((0,10),0)
        self.text=wx.StaticText(panel,-1,'Converting...')
        self.vbox.Add(self.text,0,wx.ALIGN_CENTRE)
        self.vbox.Add((0,10),0)
        self.progress=wx.StaticText(panel,-1,'')
        self.vbox.Add(self.progress,0,wx.ALIGN_CENTRE)
        self.vbox.Add((0,10),0)
        self.close=wx.Button(panel,wx.ID_STOP)
        self.Bind(wx.EVT_BUTTON,self.onStop,id=wx.ID_STOP)
        self.vbox.Add(self.close,0,wx.ALIGN_CENTRE)
        self.hbox.Add(panel,1,wx.ALIGN_CENTRE)
        panel.SetSizer(self.vbox)
        self.SetSizer(self.hbox)
    def onStop(self,event):
        self.parent.thread.abortProcess()
class DamnConverter(thr.Thread): # The actual converter
    def __init__(self,i,parent):
        self.i=i
        self.parent=parent
        self.uri=self.getURI(parent.videos[i])
        thr.Thread.__init__(self)
    def getURI(self,uri):
        if uri[0:3]=='yt:':
            # YouTube video, must grab download ticket before continuing.
            html=urllib.urlopen('http://www.youtube.com/watch?v='+uri[3:])
            for i in html:
                res=REGEX_HTTP_YOUTUBE_TICKET_EXTRACT.search(i)
                if res:
                    return 'http://www.youtube.com/get_video?video_id='+uri[3:]+'&t='+res.group(3)+'&fmt=18' # If there's no match, ffmpeg will error by itself.
        elif uri[0:3]=='gv:':
            html=urllib.urlopen('http://video.google.com/videoplay?docid='+uri[3:])
            for i in html:
                res=REGEX_HTTP_GVIDEO_TICKET_EXTRACT.search(i)
                if res:
                    return res.group(1)
        elif uri[0:3]=='vh:':
            html=urllib.urlopen('http://www.veoh.com/rest/v2/execute.xml?method=veoh.video.findById&videoId='+REGEX_HTTP_VEOH_SUBID_EXTRACT.sub('\\1',uri[3:])+'&apiKey=54709C40-9415-B95B-A5C3-5802A4E91AF3') # Onoes it's an API key
            for i in html:
                res=REGEX_HTTP_VEOH_TICKET_EXTRACT.search(i)
                if res:
                    return res.group(1)
        return uri
    def cmd2str(self,cmd):
        s=''
        for i in cmd:
            if i.find(' ')!=-1 or i.find('&')!=-1 or i.find('|')!=-1:
                s+='"'+i+'" '
            else:
                s+=i+' '
        return s[0:len(s)-1]
    def run(self):
        self.parent.gauge1.SetValue(0.0)
        self.parent.gauge2.SetValue(100.0*float(self.parent.thisbatch-1)/len(self.parent.videos))
        self.parent.thisvideo.append(self.parent.videos[self.i])
        cmd=[DV_BIN_PATH+'ffmpeg.exe','-i',self.uri,'-y','-comment','Created by DamnVid '+DV_VERSION,'-deinterlace','-passlogfile',DV_TMP_PATH+'pass']
        for i in DV_PREFERENCE_ORDER:
            if i[0:9]=='Encoding_':
                pref=self.parent.prefs.get(i)
                if pref:
                    if type(DV_PREFERENCE_TYPE[i]['kind']) is types.StringType:
                        if DV_PREFERENCE_TYPE[i]['kind'][0]=='%':
                            pref=str(round(float(pref),0)) # Round
                    cmd.extend(['-'+i[9:],pref])
        self.filename=REGEX_FILE_CLEANUP_FILENAME.sub('',self.parent.meta[self.parent.videos[self.i]]['name'])
        vcodec=self.parent.prefs.get('Encoding_vcodec')
        if DV_FILE_EXT.has_key(vcodec):
            ext='.'+DV_FILE_EXT[vcodec]
        else:
            ext='.avi'
        if os.path.lexists(self.parent.prefs.get('Outdir')+self.filename+ext):
            c=2
            while os.path.lexists(self.parent.prefs.get('Outdir')+self.filename+' ('+str(c)+')'+ext):
                c=c+1
            self.filename=self.filename+' ('+str(c)+')'
        self.filename=self.filename+ext
        cmd.append(DV_TMP_PATH+self.filename)
        self.duration=None
        self.parent.SetStatusText('Converting '+self.parent.meta[self.parent.videos[self.i]]['fromfile']+' to '+self.filename+'...')
        self.process=subprocess.Popen(self.cmd2str(cmd),shell=False,stderr=subprocess.PIPE)
        self.abort=False
        curline=''
        self.curstep=0 # This is to prevent overparsing and slowing down by parsing EVERY line from stderr. Instead, only one line out of DV_LINE_PARSING_STEP (defined in the constants) will be parsed
        while self.process.poll()==None:
            c=self.process.stderr.read(1)
            curline+=c
            if c=="\r" or c=="\n":
                self.parseLine(curline)
                curline=''
        self.parent.gauge1.SetValue(100.0)
        self.parent.gauge2.SetValue(100.0*float(self.parent.thisbatch)/len(self.parent.videos))
        result=self.process.poll() # The process is complete, but .poll() still returns the process's return code
        time.sleep(.25) # Wait a bit
        self.grabberrun=False # That'll make the DamnConverterGrabber wake up just in case
        if result and os.path.lexists(self.parent.prefs.get('Outdir')+self.filename):
            os.remove(self.parent.prefs.get('Outdir')+self.filename) # Delete the output file if ffmpeg has been aborted and exitted with a bad return code
        for i in os.listdir(DV_TMP_PATH):
            if i[-4:].lower()=='.log':
                os.remove(DV_TMP_PATH+i)
            if i==self.filename:
                os.rename(DV_TMP_PATH+i,self.parent.prefs.get('Outdir')+i)
        if not result:
            self.parent.meta[self.parent.videos[self.i]]['status']='Success!'
            self.parent.list.SetStringItem(self.i,ID_COL_VIDSTAT,'Success!')
        else:
            self.parent.meta[self.parent.videos[self.i]]['status']='Failure.'
            self.parent.list.SetStringItem(self.i,ID_COL_VIDSTAT,'Failure.')
        self.parent.go(self.abort)
    def parseLine(self,line):
        if self.duration==None:
            res=REGEX_FFMPEG_DURATION_EXTRACT.search(line)
            if res:
                self.duration=int(res.group(1))*3600+int(res.group(2))*60+float(res.group(3))
        else:
            self.curstep=self.curstep+1
            if self.curstep==DV_LINE_PARSING_STEP:
                self.curstep=0
                res=REGEX_FFMPEG_TIME_EXTRACT.search(line)
                if res:
                    self.parent.gauge1.SetValue(float(res.group(1))/self.duration*100.0)
                    self.parent.gauge2.SetValue(float(self.parent.thisbatch+float(res.group(1))/self.duration)/float(len(self.parent.videos))*100.0)
    def abortProcess(self): # FIXME, I tried stdin.write('q') but seems not to be working?
        self.abort=True # This prevents the converter from going to the next file
        if os.name=='nt':
            subprocess.Popen('TASKKILL /PID '+str(self.process.pid)+' /F').wait()
        elif os.name=='mac':
            subprocess.Popen('kill -SIGTERM '+str(self.process.pid)).wait() # Untested, from http://www.cs.cmu.edu/~benhdj/Mac/unix.html but with SIGTERM instead of SIGSTOP
        else:
            os.kill(self.process.pid,signal.SIGTERM)
        time.sleep(.5) # Wait a bit, let the files get unlocked
        try:
            os.remove(self.parent.prefs.get('Outdir')+self.filename)
        except:
            pass # Maybe the file wasn't created yet
class MainFrame(wx.Frame): # The main window
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,wx.ID_ANY,title,size=(780,580),style=wx.DEFAULT_FRAME_STYLE)
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
        vidmenu.Append(ID_MENU_PREFERENCES,'Prerences','Opens DamnVid\'s preferences, allowing you to customize its settings.')
        self.Bind(wx.EVT_MENU,self.onPrefs,id=ID_MENU_PREFERENCES)
        vidmenu.Append(ID_MENU_OUTDIR,'Output directory','Opens DamnVid\'s output directory, where all the videos are saved.')
        self.Bind(wx.EVT_MENU,self.onOpenOutDir,id=ID_MENU_OUTDIR)
        halpmenu=wx.Menu()
        halpmenu.Append(ID_MENU_HALP,'DamnVid &Help','Opens DamnVid\'s help.')
        self.Bind(wx.EVT_MENU,self.onHalp,id=ID_MENU_HALP)
        halpmenu.AppendSeparator()
        halpmenu.Append(ID_MENU_ABOUT,'&About DamnVid '+DV_VERSION+'...','Displays information about DamnVid.')
        self.Bind(wx.EVT_MENU,self.onAboutDV,id=ID_MENU_ABOUT)
        self.menubar=wx.MenuBar()
        self.menubar.Append(filemenu,'&File')
        self.menubar.Append(vidmenu,'&DamnVid')
        self.menubar.Append(halpmenu,'&Help')
        self.SetMenuBar(self.menubar)
        vbox=wx.BoxSizer(wx.VERTICAL)
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(vbox)
        vbox.Add(hbox,1,wx.EXPAND)
        panel1=wx.Panel(self,-1)
        hbox2=wx.BoxSizer(wx.HORIZONTAL)
        panel1.SetSizer(hbox2)
        self.list=DamnList(panel1,window=self)
        self.list.InsertColumn(ID_COL_VIDNAME,'Name')
        self.list.SetColumnWidth(ID_COL_VIDNAME,width=120)
        self.list.InsertColumn(ID_COL_VIDPATH,'Path')
        self.list.SetColumnWidth(ID_COL_VIDPATH,wx.LIST_AUTOSIZE)
        self.list.InsertColumn(ID_COL_VIDSTAT,'Status')
        self.list.SetColumnWidth(ID_COL_VIDSTAT,width=80)
        self.list.Bind(wx.EVT_KEY_DOWN,self.onListKeyDown)
        il=wx.ImageList(16,16,True)
        self.ID_ICON_LOCAL=il.Add(wx.Bitmap(DV_IMAGES_PATH+'video.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_ONLINE=il.Add(wx.Bitmap(DV_IMAGES_PATH+'online.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_YOUTUBE=il.Add(wx.Bitmap(DV_IMAGES_PATH+'youtube.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_GVIDEO=il.Add(wx.Bitmap(DV_IMAGES_PATH+'googlevideo.png',wx.BITMAP_TYPE_PNG))
        self.ID_ICON_VEOH=il.Add(wx.Bitmap(DV_IMAGES_PATH+'veoh.png',wx.BITMAP_TYPE_PNG))
        self.list.AssignImageList(il,wx.IMAGE_LIST_SMALL)
        self.list.SetDropTarget(DamnDropHandler(self))
        self.list.Bind(wx.EVT_RIGHT_DOWN,self.list.onRightClick)
        tmppanel=wx.Panel(self,-1)
        tmpsizer=wx.BoxSizer(wx.HORIZONTAL)
        tmppanel.SetSizer(tmpsizer)
        tmptxt=wx.StaticText(tmppanel,-1,' ')
        tmpsizer.Add(tmptxt,1,wx.EXPAND|wx.ALL)
        hbox2.Add(self.list,1,wx.EXPAND|wx.ALL)
        hbox.Add(panel1,1,wx.EXPAND)
        hbox.Add(tmppanel,0,wx.EXPAND)
        panel2=wx.Panel(self,-1)
        sizer2=wx.BoxSizer(wx.VERTICAL)
        panel2.SetSizer(sizer2)
        self.addByFile=wx.Button(panel2,-1,'Add Files')
        sizer2.Add(self.addByFile,0)
        self.Bind(wx.EVT_BUTTON,self.onAddFile,self.addByFile)
        self.addByURL=wx.Button(panel2,-1,'Add URL')
        sizer2.Add(self.addByURL,0)
        self.Bind(wx.EVT_BUTTON,self.onAddURL,self.addByURL)
        self.delSelection=wx.Button(panel2,-1,'Remove')
        sizer2.Add(self.delSelection,0)
        self.Bind(wx.EVT_BUTTON,self.onDelSelection,self.delSelection)
        self.delAll=wx.Button(panel2,-1,'Remove all')
        sizer2.Add(self.delAll,0)
        self.Bind(wx.EVT_BUTTON,self.onDelAll,self.delAll)
        self.gobutton1=wx.Button(panel2,-1,'Let\'s go!')
        sizer2.Add(self.gobutton1,0)
        self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton1)
        hbox.Add(panel2,0,wx.EXPAND)
        grid=wx.FlexGridSizer(2,4)
        bottompanel=wx.Panel(self,-1)
        bottompanel.SetSizer(grid)
        vbox.Add((5,0))
        vbox.Add(bottompanel,0,wx.EXPAND)
        grid.Add(wx.StaticText(bottompanel,-1,'Current video:'),0)
        self.gauge1=wx.Gauge(bottompanel,-1)
        grid.Add(self.gauge1,1,wx.EXPAND)
        self.gobutton2=wx.Button(bottompanel,-1,'Let\'s go!')
        self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton2)
        grid.Add(wx.StaticText(bottompanel,-1,''),0)
        grid.Add(self.gobutton2,0)
        grid.Add(wx.StaticText(bottompanel,-1,'Total progress:'),0)
        self.gauge2=wx.Gauge(bottompanel,-1)
        grid.Add(self.gauge2,1,wx.EXPAND)
        self.stopbutton=wx.Button(bottompanel,-1,'Stop')
        self.stopbutton.Disable()
        self.Bind(wx.EVT_BUTTON,self.onStop,self.stopbutton)
        grid.Add(wx.StaticText(bottompanel,-1,''),0)
        grid.Add(self.stopbutton,0)
        grid.AddGrowableCol(1,1) # Make the second column (progress bars) growable
        self.videos=[]
        self.thisbatch=0
        self.thisvideo=[]
        self.meta={}
        self.prefs=DamnVidPrefs()
        self.converting=-1
        self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
    def onExit(self,event):
        self.Close(True)
    def onListKeyDown(self,event):
        if (event.GetKeyCode()==8 or event.GetKeyCode()==127) and self.list.GetSelectedItemCount(): # Backspace or delete, but only when there's at least one selected video
            self.onDelSelection(None)
    def onAddFile(self,event):
        dlg=wx.FileDialog(self,'Choose a damn video.',os.getcwd(),'','All files|*.*|AVI files (*.avi)|*.avi|MPEG Videos (*.mpg)|*.mpg|QuickTime movies (*.mov)|*.mov|Flash Video (*.flv)|*.flv|Windows Media Videos (*.wmv)|*.wmv',wx.OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal()==wx.ID_OK:
            self.addVid(dlg.GetPaths())
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
        if dlg.ShowModal()==wx.ID_OK:
            self.addVid([dlg.GetValue()])
        dlg.Destroy()
    def validURI(self,uri):
        if REGEX_HTTP_GENERIC.match(uri):
            if REGEX_HTTP_YOUTUBE.match(uri):
                return 'YouTube Video'
            else:
                # Add elif's
                return 'Online video' # Not necessarily true, but ffmpeg will tell
        elif os.path.lexists(uri):
            return 'Local file'
        return None
    def getVidName(self,uri):
        if uri[0:3]=='yt:':
            try:
                html=urllib.urlopen('http://www.youtube.com/watch?v='+uri[3:])
                for i in html:
                    res=REGEX_HTTP_YOUTUBE_TITLE_EXTRACT.search(i)
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
        elif uri[0:3]=='gv:':
            try:
                html=urllib.urlopen('http://video.google.com/videoplay?docid='+uri[3:])
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
                        self.addValid({'name':name,'fromfile':name,'dirname':'http://www.youtube.com/watch?v='+match.group(1),'uri':uri,'status':'Pending.','icon':self.ID_ICON_YOUTUBE})
                    #elif REGEX_HTTP_GVIDEO.search(uri):
                        #match=REGEX_HTTP_GVIDEO.search(uri)
                        #uri='gv:'+match.group(1)
                        #name=self.getVidName(uri)
                        #self.addValid({'name':name,'fromfile':name,'dirname':'http://video.google.com/videoplay?docid='+match.group(1),'uri':uri,'status':'Pending.','icon':self.ID_ICON_GVIDEO})
                    elif REGEX_HTTP_VEOH.search(uri):
                        html=urllib.urlopen(uri) # Gotta download it right there instead of downloading it twice with the getVidName function
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
                            self.addValid({'name':name,'fromfile':name,'dirname':'http://www.veoh.com/videos/'+Id,'uri':uri,'status':'Pending.','icon':self.ID_ICON_VEOH})
                        else:
                            self.SetStatusText('Couldn\'t detect Veoh video.')
                    else:
                        name=REGEX_HTTP_EXTRACT_FILENAME.sub('',uri)
                        self.addValid({'name':name,'fromfile':name,'dirname':REGEX_HTTP_EXTRACT_DIRNAME.sub('\\1/',uri),'uri':uri,'status':'Pending.','icon':self.ID_ICON_ONLINE})
                else:
                    # It's a file
                    if os.path.isdir(uri):
                        if self.prefs.get('DirRecursion')=='True':
                            for i in os.listdir(uri):
                                self.addVid([uri+OS_PATH_SEPARATOR+i]) # This is recursive; if i is a directory, this block will be executed for it too
                        else:
                            if len(uris)==1: # Only one dir, so an alert here is tolerable
                                dlg=wx.MessageDialog(None,'This is a directory, but recursion is disabled in the preferences. Please enable it if you want DamnVid to go through directories.','Recursion is disabled.',wx.OK|wx.ICON_EXCLAMATION)
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
                                dlg.ShowModal()
                                dlg.Destroy()
                        else:
                            self.addValid({'name':filename[0:filename.rfind('.')],'fromfile':filename,'uri':uri,'dirname':os.path.dirname(uri),'status':'Pending.','icon':self.ID_ICON_LOCAL})
            else:
                if len(uris)==1: # There's only one URI, so an alert here is tolerable
                    dlg=wx.MessageDialog(None,'This is not a valid video!','Invalid video',wx.ICON_EXCLAMATION|wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                self.SetStatusText('Skipped '+uri+' (invalid video).')
    def addValid(self,meta):
        curvid=len(self.videos)
        self.list.InsertStringItem(curvid,meta['name'])
        self.list.SetStringItem(curvid,ID_COL_VIDPATH,meta['dirname'])
        self.list.SetStringItem(curvid,ID_COL_VIDSTAT,meta['status'])
        self.list.SetItemImage(curvid,meta['icon'],meta['icon'])
        self.videos.append(meta['uri'])
        self.meta[meta['uri']]=meta
        self.SetStatusText('Added '+meta['name']+'.')
    def go(self,result,aborted=False):
        self.converting=-1
        for i in range(len(self.videos)):
            if self.videos[i] not in self.thisvideo:
                self.converting=i
                break
        if self.converting!=-1 and not aborted:
            # Let's go for the actual conversion...
            self.meta[self.videos[self.converting]]['status']='Converting...'
            self.list.SetStringItem(self.converting,ID_COL_VIDSTAT,'Converting...')
            self.thisbatch=self.thisbatch+1
            self.thread=DamnConverter(i=self.converting,parent=self)
            self.thread.start()
        else:
            self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
            if self.thisbatch:
                dlg=wx.MessageDialog(None,str(self.thisbatch)+' video(s) was/were processed.\r\nWant to open the output directory?','Done!',wx.YES_NO|wx.ICON_INFORMATION)
            else:
                dlg=wx.MessageDialog(None,'No videos were processed.','Aborted',wx.OK|wx.ICON_INFORMATION)
            if dlg.ShowModal()==wx.ID_YES:
                self.onOpenOutDir(None)
            self.converting=-1
            self.stopbutton.Disable()
            self.gobutton1.Enable()
            self.gobutton2.Enable()
            self.gauge1.SetValue(0.0)
            self.gauge2.SetValue(0.0)
    def onGo(self,event):
        if not len(self.videos):
            dlg=wx.MessageDialog(None,'Put some videos in the list first!','No videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.converting!=-1:
            dlg=wx.MessageDialog(None,'DamnVid '+DV_VERSION+' is already converting!','Already converting!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            success=0
            for i in self.videos:
                if self.meta[i]['status']=='Success!':
                    success=success+1
            if success==len(self.videos):
                dlg=wx.MessageDialog(None,'All videos in the list have already been processed!','Already done',wx.OK|wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.thisbatch=0
                self.thisvideo=[]
                self.stopbutton.Enable()
                self.gobutton1.Disable()
                self.gobutton2.Disable()
                self.go(None)
    def onStop(self,event):
        self.thread.abortProcess()
    def invertVids(self,i1,i2):
        tmp=self.videos[i1]
        self.videos[i1]=self.videos[i2]
        self.videos[i2]=tmp
        tmp=self.list.IsSelected(i2)
        self.list.Select(i2,on=self.list.IsSelected(i1))
        self.list.Select(i1,on=tmp)
        self.list.invertItems(i1,i2)
        if i1==self.converting:
            self.thread.i=i2
            self.converting=i2
        elif i2==self.converting:
            self.thread.i=i1
            self.converting=i1
    def onMoveUp(self,event):
        for i in self.list.getAllSelectedItems():
            self.invertVids(i,i-1)
    def onMoveDown(self,event):
        for i in reversed(self.list.getAllSelectedItems()):
            self.invertVids(i,i+1)
    def onPrefs(self,event):
        prefs=DamnVidPrefEditor(None,-1,'DamnVid '+DV_VERSION+' preferences',main=self)
        prefs.ShowModal()
        prefs.Destroy()
    def onOpenOutDir(self,event):
        if os.name=='nt':
            os.system('explorer.exe "'+self.prefs.get('Outdir').replace('%CWD%',os.getcwd()).replace('/',OS_PATH_SEPARATOR)+'"')
        else:
            pass # Halp here?
    def onHalp(self,event):
        pass
    def onAboutDV(self,event):
        pass
    def onDelSelection(self,event):
        num=self.list.GetSelectedItemCount()
        if num:
            items=[]
            i=0
            keepgoing=True
            items.append(self.list.GetFirstSelected())
            while keepgoing:
                item=self.list.GetNextSelected(items[i])
                if item==-1:
                    keepgoing=False
                else:
                    i=i+1
                    items.append(item)
            for i in reversed(items): # Sequence MUST be reversed, otherwise the first items get deleted first, which changes the indexes of the following items
                self.list.DeleteItem(i)
                self.videos.pop(i)
                if i<self.converting:
                    self.converting=self.converting-1
                    self.thread.i=self.thread.i-1
        else:
            dlg=wx.MessageDialog(None,'You must select some videos from the list first!','Select some videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
    def onDelAll(self,event):
        dlg=wx.MessageDialog(None,'Are you sure? (This will not delete any files, it will just remove them from the list.)','Confirmation',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if dlg.ShowModal()==wx.ID_YES:
            if self.converting!=-1:
                self.onStop(None) # Stop conversion if it's in progress
            self.list.DeleteAllItems()
            del self.videos
            self.videos=[]
        dlg.Destroy()
class DamnVid(wx.App):
    def OnInit(self):
        frame=MainFrame(None,-1,'DamnVid '+DV_VERSION+' by WindPower')
        frame.Show(True)
        frame.Centre()
        return True
app=DamnVid(0)
app.MainLoop()
