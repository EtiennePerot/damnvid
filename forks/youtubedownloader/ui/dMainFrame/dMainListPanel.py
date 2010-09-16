# -*- coding: utf-8 -*-
from ..dUI import *
from .orig_dMainListPanel import DamnMainListPanel as orig_DamnMainListPanel
from .orig_dMainSidePanel import buildProfileDropDown as orig_buildProfileDropDown

class DamnMainListPanel(orig_DamnMainListPanel):
	def initList(self):
		self.quickAddURLText = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER)
		self.quickAddURLText.Bind(wx.EVT_TEXT_ENTER, self.onQuickAddURL)
		quickAddHbox = wx.BoxSizer(wx.HORIZONTAL)
		self.vbox1.Add(quickAddHbox, 0, wx.EXPAND)
		quickAddHbox.Add(self.quickAddURLText, 1, wx.EXPAND)
		quickAddHbox.Add((DV.border_padding*2, 0))
		quickAddHbox.Add(orig_buildProfileDropDown(self.parent, self, label=True), 0, wx.EXPAND) # Todo: Make dropdown appear
		orig_DamnMainListPanel.initList(self)
		self.quickAddURLText.SetFocus()
	def onQuickAddURL(self, event=None):
		value = DamnUnicode(self.quickAddURLText.GetValue())
		if not value:
			return
		self.parent.addVid([value], None)
		self.quickAddURLText.SetValue(u'')
		self.quickAddURLText.SetFocus(True)
