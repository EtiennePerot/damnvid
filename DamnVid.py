import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import os
import re
import subprocess
import time
try:
    import threading as thr
except ImportError:
    import dummy_threading as thr
# Begin constants
OS_PATH_SEPARATOR='\\'
DV_VERSION='1.0'
DV_CONF_FILE='conf/conf.ini'.replace('/',OS_PATH_SEPARATOR)
DV_IMAGES_PATH='img/'.replace('/',OS_PATH_SEPARATOR)
DV_BIN_PATH='exe/'.replace('/',OS_PATH_SEPARATOR)
DV_LOG_PATH='log/'.replace('/',OS_PATH_SEPARATOR)
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
}
# Begin ID constants
ID_MENU_EXIT=101
ID_MENU_ADD_FILE=102
ID_MENU_ADD_URL=103
ID_MENU_GO=104
ID_MENU_PREFERENCES=105
ID_MENU_OUTDIR=106
ID_MENU_HALP=107
ID_MENU_ABOUT=109
ID_BUTTON_ADD_FILE=120
ID_BUTTON_ADD_URL=121
ID_BUTTON_DEL_SELECTION=122
ID_BUTTON_DEL_ALL=123
ID_BUTTON_GO=124
ID_COL_VIDNAME=0
ID_COL_VIDTYPE=1
ID_COL_VIDSTAT=2
ID_COL_VIDPATH=3
# End constants
class DropHandler(wx.FileDropTarget):
    def __init__(self,window):
        wx.FileDropTarget.__init__(self)
        self.window=window
    def OnDropFiles(self,x,y,filenames):
        self.window.addVid(filenames)
class TehList(wx.ListCtrl,ListCtrlAutoWidthMixin):
    def __init__(self,parent):
        wx.ListCtrl.__init__(self,parent,-1,style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
class DamnVidPrefs():
    def __init__(self):
        self.conf={}
        f=open(DV_CONF_FILE)
        for i in re.finditer('(?m)^([_\\w]+)=(.*)$',f.read()):
            self.conf[i.group(1)]=i.group(2).replace('%CWD%',os.getcwd()).strip()
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
            f.write("\r\n"+i+'='+str(self.conf[i]).replace(os.getcwd(),'%CWD%'))
        f.close()
class DamnVidPrefEditor(wx.Dialog):
    def __init__(self,parent,id,title):
        wx.Dialog.__init__(self,parent,id,title)
    def onOK(self,event):
        pass
    def onCancel(self,event):
        pass
class DamnWait(wx.Dialog):
    def __init__(self,parent,id,title):
        wx.Dialog.__init__(self,parent,id,title,size=(250,150),style=wx.CLOSE_BOX)
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
        wx.EVT_BUTTON(self,wx.ID_STOP,self.onStop)
        self.vbox.Add(self.close,0,wx.ALIGN_CENTRE)
        self.hbox.Add(panel,1,wx.ALIGN_CENTRE)
        panel.SetSizer(self.vbox)
        self.SetSizer(self.hbox)
    def onStop(self,event):
        pass
class DamnConverter(thr.Thread):
    def __init__(self,i,parent):
        self.i=i
        self.parent=parent
        self.uri=parent.videos[i]
        thr.Thread.__init__(self)
    def run(self):
        cmd=[DV_BIN_PATH+'ffmpeg.exe','-i',self.uri,'-y','-comment','Created by DamnVid '+DV_VERSION,'-deinterlace','-passlogfile',DV_LOG_PATH+'pass']
        options=('vcodec','b','g','acodec','ab','ar','r','bt','maxrate','minrate','bufsize','pass','ac','vol')
        for i in options:
            pref=self.parent.prefs.get('Encoding_'+i)
            if pref:
                cmd.extend(['-'+i,pref])
        filename=self.parent.meta[self.parent.videos[self.i]]['name']
        vcodec=self.parent.prefs.get('Encoding_vcodec')
        if DV_FILE_EXT.has_key(vcodec):
            filename=filename+'.'+DV_FILE_EXT[vcodec]
        else:
            filename=filename+'.avi'
        cmd.append(self.parent.prefs.get('Outdir')+filename)
        self.parent.SetStatusText('Converting '+self.parent.meta[self.parent.videos[self.i]]['fromfile']+' to '+filename+'...')
        self.parent.wait.gauge.SetValue(float(self.i+1)/float(len(self.parent.videos))*100)
        self.parent.wait.progress.SetLabel(str(self.i+1)+'/'+str(len(self.parent.videos)))
        self.parent.wait.vbox.Layout()
        self.parent.wait.hbox.Layout()
        self.process=subprocess.Popen(cmd,shell=True)
        result=self.process.wait()
        time.sleep(0.5)
        for i in os.listdir(DV_LOG_PATH):
            if i[-4:].lower()=='.log':
                os.unlink(DV_LOG_PATH+i)
        self.parent.go(self.i,result)
class MainFrame(wx.Frame):
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
        hbox=wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(hbox)
        panel1=wx.Panel(self,-1)
        hbox2=wx.BoxSizer(wx.HORIZONTAL)
        panel1.SetSizer(hbox2)
        self.list=TehList(panel1)
        self.list.InsertColumn(ID_COL_VIDNAME,'Name')
        self.list.SetColumnWidth(ID_COL_VIDNAME,width=120)
        self.list.InsertColumn(ID_COL_VIDTYPE,'Type')
        self.list.SetColumnWidth(ID_COL_VIDTYPE,width=80)
        self.list.InsertColumn(ID_COL_VIDPATH,'Path')
        self.list.SetColumnWidth(ID_COL_VIDPATH,wx.LIST_AUTOSIZE)
        self.list.InsertColumn(ID_COL_VIDSTAT,'Status')
        self.list.SetColumnWidth(ID_COL_VIDSTAT,width=80)
        il=wx.ImageList(16,16,True)
        self.ID_ICON_LOCAL=il.Add(wx.Bitmap(DV_IMAGES_PATH+'video.png',wx.BITMAP_TYPE_PNG))
        self.list.AssignImageList(il,wx.IMAGE_LIST_SMALL)
        self.list.SetDropTarget(DropHandler(self))
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
        self.addByFile=wx.Button(panel2,ID_BUTTON_ADD_FILE,'Add Files')
        sizer2.Add(self.addByFile,0)
        self.Bind(wx.EVT_BUTTON,self.onAddFile,id=ID_BUTTON_ADD_FILE)
        self.addByURL=wx.Button(panel2,ID_BUTTON_ADD_URL,'Add URL')
        sizer2.Add(self.addByURL,0)
        self.Bind(wx.EVT_BUTTON,self.onAddURL,id=ID_BUTTON_ADD_URL)
        self.delSelection=wx.Button(panel2,ID_BUTTON_DEL_SELECTION,'Remove')
        sizer2.Add(self.delSelection,0)
        self.Bind(wx.EVT_BUTTON,self.onDelSelection,id=ID_BUTTON_DEL_SELECTION)
        self.delAll=wx.Button(panel2,ID_BUTTON_DEL_ALL,'Remove all')
        sizer2.Add(self.delAll,0)
        self.Bind(wx.EVT_BUTTON,self.onDelAll,id=ID_BUTTON_DEL_ALL)
        self.letsgo=wx.Button(panel2,ID_BUTTON_GO,'Let\'s go!')
        sizer2.Add(self.letsgo,0)
        self.Bind(wx.EVT_BUTTON,self.onGo,id=ID_BUTTON_GO)
        hbox.Add(panel2,0,wx.EXPAND)
        self.videos=[]
        self.meta={}
        self.prefs=DamnVidPrefs()
        self.converting=False
        self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
    def onExit(self,event):
        self.Close(True)
    def onAddFile(self,event):
        dlg=wx.FileDialog(self,'Choose a damn video.',os.getcwd(),'','All files|*.*|AVI files (*.avi)|*.avi|MPEG Videos (*.mpg)|*.mpg|QuickTime movies (*.mov)|*.mov|Flash Video (*.flv)|*.flv|Windows Media Videos (*.wmv)|*.wmv',wx.OPEN|wx.FD_MULTIPLE)
        if dlg.ShowModal()==wx.ID_OK:
            self.addVid(dlg.GetPaths())
        dlg.Destroy()
    def onAddURL(self,event):
        dlg=wx.TextEntryDialog(self,'Enter the URL of the video you wish to download.','Enter URL.')
        self.addVid([dlg.GetValue()])
        dlg.Destroy()
    def validURI(uri):
        if re.match('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/;\w]*)?$',uri,re.IGNORECASE):
            
        elif os.path.lexists(uri):
            return 'Local file'
        return None
    def addVid(self,uris):
        for uri in uris:
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
                    self.list.InsertStringItem(len(self.videos),filename)
                    self.list.SetStringItem(len(self.videos),ID_COL_VIDTYPE,'Local file')
                    self.list.SetStringItem(len(self.videos),ID_COL_VIDPATH,os.path.dirname(uri))
                    self.list.SetStringItem(len(self.videos),ID_COL_VIDSTAT,'Pending.')
                    self.list.SetItemImage(len(self.videos),self.ID_ICON_LOCAL,self.ID_ICON_LOCAL)
                    self.videos.append(uri)
                    self.meta[uri]={'name':filename[0:filename.rfind('.')],'fromfile':filename,'uri':uri,'dirname':os.path.dirname(uri),'status':'Pending.'}
                    self.SetStatusText('Added '+filename+'.')
    def go(self,i,result):
        if result is not None:
            if not result:
                self.meta[self.videos[i]]['status']='Success!'
                self.list.SetStringItem(i,ID_COL_VIDSTAT,'Success!')
            else:
                self.meta[self.videos[i]]['status']='Failure.'
                self.list.SetStringItem(i,ID_COL_VIDSTAT,'Failure.')
        i=i+1 # Next~
        if len(self.videos)>i:
            # Let's go for the actual conversion...
            if self.meta[self.videos[i]]=='Success!':
                self.go(i,0)
            else:
                self.meta[self.videos[i]]['status']='Converting...'
                self.list.SetStringItem(i,ID_COL_VIDSTAT,'Converting...')
                self.converting=True
                thread=DamnConverter(i=i,parent=self)
                thread.start()
        else:
            self.converting=False
            self.SetStatusText('DamnVid '+DV_VERSION+', waiting for instructions.')
            success=0
            failure=0
            for i in self.videos:
                if self.meta[i]['status']=='Success!':
                    success=success+1
                elif self.meta[i]['status']=='Failure.':
                    failure=failure+1
            dlg=wx.MessageDialog(None,'All videos were processed.\r\nResults:\r\n\r\nFiles: '+str(len(self.videos))+'\r\nSuccess: '+str(success)+' file(s)\r\nFailure: '+str(failure)+' file(s)\r\nDamnVid '+DV_VERSION+' is '+str(round(float(success)/float(len(self.videos))*100,2))+'% successful.\r\n\r\nWant to open the output directory?','Done!',wx.YES_NO|wx.ICON_INFORMATION)
            if dlg.ShowModal()==wx.ID_YES:
                self.onOpenOutDir(None)
            self.wait.Close(True)
    def onGo(self,event):
        if not len(self.videos):
            dlg=wx.MessageDialog(None,'Put some videos in the list first!','No videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            self.go(-1,None)
            self.wait=DamnWait(None,-1,'Converting, please wait...')
            self.wait.ShowModal()
            self.wait.Destroy()
    def onPrefs(self,event):
        pass
    def onOpenOutDir(self,event):
        os.system('explorer.exe "'+self.prefs.get('Outdir').replace('/',OS_PATH_SEPARATOR)+'"')
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
        else:
            dlg=wx.MessageDialog(None,'You must select some videos from the list first!','Select some videos!',wx.ICON_EXCLAMATION|wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
    def onDelAll(self,event):
        dlg=wx.MessageDialog(None,'Are you sure? (This will not delete any files, it will just remove them from the list.)','Confirmation',wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if dlg.ShowModal()==wx.ID_YES:
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
