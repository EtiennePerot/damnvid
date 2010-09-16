# -*- coding: utf-8 -*-
from ..dUI import *

def buildProfileDropDown(parent, panel, label=True):
	try:
		parent.profilepanel.Destroy() # Delete if it exists
	except:
		pass
	parent.profilepanel = wx.Panel(panel, -1)
	profilepanelsizer = wx.BoxSizer(wx.VERTICAL)
	parent.profilepanel.SetSizer(profilepanelsizer)
	if label:
		profilepanelsizer.Add(wx.StaticText(parent.profilepanel, -1, DV.l('Profile:')), 0, wx.ALIGN_CENTER)
		profilepanelsizer.Add((0, DV.control_vgap))
	parent.profiledropdown = wx.Choice(parent.profilepanel, -1, choices=[DV.l('(None)')])
	profilepanelsizer.Add(parent.profiledropdown, 0, wx.ALIGN_CENTER)
	return parent.profilepanel
class DamnMainSidePanel(wx.Panel):
	def __init__(self, parent):
		Damnlog('Initializing DamnMainSidePanel.')
		wx.Panel.__init__(self, parent, -1)
		vboxwrap2 = wx.BoxSizer(wx.HORIZONTAL)
		self.mainSizer = wx.BoxSizer(wx.VERTICAL)
		vboxwrap2.Add(self.mainSizer)
		vboxwrap2.Add((DV.border_padding, 0))
		self.mainSizer.Add((0, DV.border_padding))
		self.SetSizer(vboxwrap2)
		parent.droptarget = wx.animate.GIFAnimationCtrl(self, -1, DV.images_path + 'droptarget.gif')
		parent.droptarget.Bind(wx.EVT_LEFT_UP, parent.onDropTargetClick)
		self.mainSizer.Add(parent.droptarget, 0, wx.ALIGN_CENTER)
		parent.droptarget.SetDropTarget(DamnDropHandler(parent))
		# Extra forced gap here
		self.mainSizer.Add((0, DV.control_vgap + 4))
		parent.addByFile = wx.Button(self, -1, DV.l('Add Files'))
		self.mainSizer.Add(parent.addByFile, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onAddFile, parent.addByFile)
		parent.addByURL = wx.Button(self, -1, DV.l('Add URL'))
		self.mainSizer.Add(parent.addByURL, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onAddURL, parent.addByURL)
		parent.btnSearch = wx.Button(self, -1, DV.l('Search...'))
		self.mainSizer.Add(parent.btnSearch, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onSearch, parent.btnSearch)
		parent.btnRename = wx.Button(self, -1, DV.l('Rename'))
		self.mainSizer.Add(parent.btnRename, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onRename, parent.btnRename)
		self.mainSizer.Add(buildProfileDropDown(parent, self, label=True))
		self.niceHeight = parent.profiledropdown.GetSizeTuple()[1]
		parent.profilepanel.Hide()
		self.mainSizer.Add((0, DV.control_vgap))
		parent.btnMoveUp = wx.Button(self, -1, DV.l('Move up'))
		self.mainSizer.Add(parent.btnMoveUp, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onMoveUp, parent.btnMoveUp)
		parent.btnMoveDown = wx.Button(self, -1, DV.l('Move down'))
		self.mainSizer.Add(parent.btnMoveDown, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onMoveDown, parent.btnMoveDown)
		parent.deletebutton = wx.Button(self, -1, DV.l('Remove'))
		self.mainSizer.Add(parent.deletebutton, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.control_vgap))
		parent.Bind(wx.EVT_BUTTON, parent.onDelete, parent.deletebutton)
		parent.gobutton1 = wx.Button(self, -1, DV.l('Start'))
		self.mainSizer.Add(parent.gobutton1, 0, wx.ALIGN_CENTER)
		self.mainSizer.Add((0, DV.border_padding))
		parent.Bind(wx.EVT_BUTTON, parent.onGo, parent.gobutton1)
		dimensions = (self.getNiceWidth(), self.getNiceHeight())
		parent.setNiceDimensions(dimensions)
		Damnlog('DamnMainSidePanel initialized. Nice dimensions:', dimensions)
	def getNiceWidth(self):
		return self.mainSizer.GetMinSizeTuple()[0]
	def getNiceHeight(self):
		return self.niceHeight
