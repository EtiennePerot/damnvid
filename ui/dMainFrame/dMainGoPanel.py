# -*- coding: utf-8 -*-
from ..dUI import *

def DamnMainStopButton(panel=None, parent=None):
	stopbutton = wx.Button(panel, -1, DV.l('Stop'))
	stopbutton.Disable()
	if parent is not None:
		panel.Bind(wx.EVT_BUTTON, parent.onStop, stopbutton)
	return stopbutton

class DamnMainGoPanel(wx.Panel):
	def __init__(self, parent):
		Damnlog('Initializing DamnMainGoPanel.')
		wx.Panel.__init__(self, parent, -1)
		self.parent = parent
		hboxwrapper4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4 = wx.BoxSizer(wx.VERTICAL)
		hboxwrapper4.Add(hbox4)
		hboxwrapper4.Add((0, DV.border_padding))
		self.SetSizer(hboxwrapper4)
		parent.stopbutton = DamnMainStopButton(panel=self, parent=parent)
		for button in (parent.addByFile, parent.addByURL, parent.btnRename, parent.btnMoveUp, parent.btnMoveDown, parent.deletebutton, parent.gobutton1, parent.stopbutton, parent.btnSearch):
			button.SetMinSize((parent.getNiceDimensions()[0], button.GetSizeTuple()[1]))
		parent.gauge1.SetMaxSize((-1, parent.stopbutton.GetSizeTuple()[1]))
		parent.profiledropdown.SetMinSize(parent.getNiceDimensions())
		parent.profiledropdown.Bind(wx.EVT_CHOICE, parent.onChangeProfileDropdown)
		parent.profilepanel.Show()
		hbox4.Add(parent.stopbutton)
		hbox4.Add((0, DV.border_padding))
		#vbox.Add((0,DV.border_padding))
		Damnlog('DamnMainGoPanel initialized.')
