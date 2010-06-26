# -*- coding: utf-8 -*-
from dCore import *
from dWx import wx

DV.evt_progress = wx.NewEventType()
DV.evt_prog = wx.PyEventBinder(DV.evt_progress, 1)
class DamnProgressEvent(wx.PyCommandEvent):
	def __init__(self, eventtype, eventid, eventinfo):
		wx.PyCommandEvent.__init__(self, eventtype, eventid)
		self.info = eventinfo
	def GetInfo(self):
		return self.info
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return '<DamnProgressEvent holding: ' + DamnUnicode(self.info) + '>'
DV.evt_loading = wx.NewEventType()
DV.evt_load = wx.PyEventBinder(DV.evt_loading, 1)
class DamnLoadingEvent(wx.PyCommandEvent):
	def __init__(self, eventtype, eventid, eventinfo):
		wx.PyCommandEvent.__init__(self, eventtype, eventid)
		self.info = eventinfo
	def GetInfo(self):
		return self.info
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return '<DamnLoadingEvent holding: ' + DamnUnicode(self.info) + '>'
DV.evt_bugreporting = wx.NewEventType()
DV.evt_bugreport = wx.PyEventBinder(DV.evt_bugreporting, 1)
class DamnBugReportEvent(wx.PyCommandEvent):
	def __init__(self, eventtype, eventid, eventinfo):
		wx.PyCommandEvent.__init__(self, eventtype, eventid)
		self.info = eventinfo
	def GetInfo(self):
		return self.info
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return '<DamnBugReportEvent holding: ' + DamnUnicode(self.info) + '>'
def DamnPostEvent(target, event):
	if type(event) in (type([]), type(())):
		if event[0] == DV.evt_loading:
			event = DamnLoadingEvent(DV.evt_loading, -1, event[-1])
		elif event[0] == DV.evt_progress:
			event = DamnProgressEvent(DV.evt_progress, -1, event[-1])
		elif event[0] == DV.evt_bugreporting:
			event = DamnBugReportEvent(DV.evt_bugreporting, -1, event[-1])
	try:
		wx.PostEvent(target, event)
	except:
		Damnlog('!! Failed delivering event', event, 'to target', target)
DV.postEvent = DamnPostEvent
