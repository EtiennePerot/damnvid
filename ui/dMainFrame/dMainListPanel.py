# -*- coding: utf-8 -*-
from ..dUI import *

class DamnMainListPanel(wx.Panel):
	def __init__(self, parent):
		Damnlog('Initializing DamnMainListPanel.')
		self.parent = parent
		wx.Panel.__init__(self, self.parent, -1)
		self.vbox1 = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.vbox1)
		self.initList()
	def initList(self):
		dList = DamnList(self, window=self.parent)
		dList.InsertColumn(ID_COL_VIDNAME, DV.l('Video name'))
		dList.SetColumnWidth(ID_COL_VIDNAME, width=180)
		dList.InsertColumn(ID_COL_VIDPROFILE, DV.l('Encoding profile'))
		dList.SetColumnWidth(ID_COL_VIDPROFILE, width=120)
		dList.InsertColumn(ID_COL_VIDSTAT, DV.l('Status'))
		dList.SetColumnWidth(ID_COL_VIDSTAT, width=120)
		dList.InsertColumn(ID_COL_VIDPATH, DV.l('Source'))
		dList.SetColumnWidth(ID_COL_VIDPATH, wx.LIST_AUTOSIZE)
		dList.Bind(wx.EVT_KEY_DOWN, self.parent.onListKeyDown)
		dList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.parent.onListSelect)
		dList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.parent.onListSelect)
		DV.listicons.initWX()
		dList.AssignImageList(DV.listicons, wx.IMAGE_LIST_SMALL)
		dList.SetDropTarget(DamnDropHandler(self))
		dList.Bind(wx.EVT_RIGHT_DOWN, dList.onRightClick)
		self.vbox1.Add(dList, 1, wx.EXPAND)
		self.parent.list = dList
		Damnlog('DamnMainListPanel is up.')
