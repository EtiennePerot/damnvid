# -*- coding: utf-8 -*-
from ..dUI import *

class DamnMainGaugePanel(wx.Panel):
	def __init__(self, parent):
		Damnlog('Initializing DamnMainGaugePanel.')
		wx.Panel.__init__(self, parent, -1)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add((DV.border_padding, 0))
		self.SetSizer(hbox3)
		hbox3.Add(wx.StaticText(self, -1, DV.l('Current video: ')), 0, wx.ALIGN_CENTER_VERTICAL)
		parent.gauge1 = wx.Gauge(self, -1)
		hbox3.Add(parent.gauge1, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		Damnlog('DamnMainGaugePanel initialized.')
