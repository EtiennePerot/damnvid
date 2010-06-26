# -*- coding: utf-8 -*-
from dCore import *
from dConstants import *
from dConfig import *
from dLog import *
from dWx import wx

def DamnFadeIn(frame):
	if not frame.CanSetTransparent() or not DV.prefs.get('splashscreen') == 'True':
		frame.Show()
		return
	frame.SetTransparent(0)
	frame.Show()
	frame.fadeTimer = wx.Timer(frame)
	frame.fadeCurrent = 0
	frame.fadeDelta = 1
	frame.fadeInterval = 4
	frame.fadeLagTolerance = 2
	frame.fadeObjective = 255
	frame.fadeTime = time.time() * 1000
	frame.fadeDestroy = False
	frame.Bind(wx.EVT_TIMER, DamnCurry(DamnFadeCycle, frame), frame.fadeTimer)
	frame.fadeTimer.Start(frame.fadeInterval)
def DamnFadeOut(frame, destroy=True):
	if not frame.CanSetTransparent() or not DV.prefs.get('splashscreen') == 'True':
		frame.Hide()
		if destroy:
			frame.Destroy()
		return
	frame.fadeTimer = wx.Timer(frame)
	frame.fadeCurrent = 255
	frame.fadeDelta = -1
	frame.fadeInterval = 4
	frame.fadeLagTolerance = 2
	frame.fadeObjective = 0
	frame.fadeTime = time.time() * 1000
	frame.fadeDestroy = destroy
	frame.Bind(wx.EVT_TIMER, DamnCurry(DamnFadeCycle, frame), frame.fadeTimer)
	frame.fadeTimer.Start(frame.fadeInterval)
def DamnFadeCycle(frame, event=None):
	try:
		frame.SetTransparent(frame.fadeCurrent)
	except:
		pass
	newTime = time.time() * 1000
	if newTime - frame.fadeTime > frame.fadeInterval * frame.fadeLagTolerance:
		frame.fadeDelta *= 2 # Increase fade delta to make up for machine slowness.
		frame.fadeLagTolerance *= 2
	frame.fadeTime = newTime
	frame.fadeCurrent += frame.fadeDelta
	if (frame.fadeDelta > 0 and frame.fadeCurrent >= frame.fadeObjective) or (frame.fadeDelta < 0 and frame.fadeCurrent <= frame.fadeObjective):
		try:
			frame.SetTransparent(frame.fadeObjective)
		except:
			pass
		frame.fadeTimer.Stop()
		if frame.fadeDestroy:
			frame.Destroy()
class DamnFrame(wx.Frame):
	def fadeIn(self):
		DamnFadeIn(self)
	def fadeOut(self, destroy=True):
		DamnFadeOut(self, destroy)

# Now load UI stuff
from dEvent import *
from dWidgets import *
from dPrefEditor import *
from dDoneDialog import *
from dAddURLDialog import *
from dAboutDialog import *
from dReportBug import *
from dBrowser import *
from dVideoHistory import *
from dMainFrame import *