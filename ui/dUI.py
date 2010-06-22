# -*- coding: utf-8 -*-
try:
	import wxversion
	try:
		wxversion.select('2.8')
	except:
		pass
except:
	pass
import wx
from dLocale import *
class Menubar(wx.MenuBar):
	def __init__(self, parent=None):
		self.parent = parent
		wx.MenuBar.__init__(self)
		filemenu = wx.Menu()
		menu_addfile = wx.MenuItem(filemenu, -1, DV.l('&Add files...'), DV.l('Adds damn videos from local files.'))
		filemenu.AppendItem(menu_addfile)
		self.parent.Bind(wx.EVT_MENU, self.parent.onAddFile, menu_addfile)
		menu_addurl = wx.MenuItem(filemenu, -1, DV.l('Add &URL...'), DV.l('Adds a damn video from a URL.'))
		filemenu.AppendItem(menu_addurl)
		self.parent.Bind(wx.EVT_MENU, self.parent.onAddURL, menu_addurl)
		menu_history = wx.MenuItem(filemenu, -1, DV.l('Video &history...'), DV.l('Opens DamnVid\'s video history.'))
		filemenu.AppendItem(menu_history)
		self.parent.Bind(wx.EVT_MENU, self.parent.onOpenHistory, menu_history)
		filemenu.AppendSeparator()
		filemenu.Append(wx.ID_EXIT, DV.l('E&xit'), DV.l('Terminates DamnVid.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onExit, id=wx.ID_EXIT)
		vidmenu = wx.Menu()
		menu_letsgo = wx.MenuItem(vidmenu, -1, DV.l('Start'), DV.l('Processes all the videos in the list.'))
		vidmenu.AppendItem(menu_letsgo)
		self.parent.Bind(wx.EVT_MENU, self.parent.onGo, menu_letsgo)
		vidmenu.AppendSeparator()
		self.parent.prefmenuitem = vidmenu.Append(wx.ID_PREFERENCES, DV.l('Preferences'), DV.l('Opens DamnVid\'s preferences, allowing you to customize its settings.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onPrefs, id=wx.ID_PREFERENCES)
		halpmenu = wx.Menu()
		halpmenu.Append(wx.ID_HELP, DV.l('&Help'), DV.l('Opens DamnVid\'s help.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onHalp, id=wx.ID_HELP)
		menu_reportbug = wx.MenuItem(halpmenu, -1, DV.l('Report a bug'), DV.l('Submit a new bug report.'))
		halpmenu.AppendItem(menu_reportbug)
		self.parent.Bind(wx.EVT_MENU, self.parent.onReportBug, menu_reportbug)
		menu_checkupdates = wx.MenuItem(halpmenu, -1, DV.l('Check for updates...'), DV.l('Checks if a new version of DamnVid is available.'))
		halpmenu.AppendItem(menu_checkupdates)
		self.parent.Bind(wx.EVT_MENU, self.parent.onCheckUpdates, menu_checkupdates)
		halpmenu.AppendSeparator()
		halpmenu.Append(wx.ID_ABOUT, DV.l('&About DamnVid ') + DV.version + '...', DV.l('Displays information about DamnVid.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onAboutDV, id=wx.ID_ABOUT)
		self.Append(filemenu, DV.l('&File'))
		self.Append(vidmenu, DV.l('&DamnVid'))
		self.Append(halpmenu, DV.l('&Help'))