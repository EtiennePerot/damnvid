#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2008 Etienne Perot

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Uhm, yeah. I'm not really sure if I'm proud of this source code or not.
# I mean, some parts of the code are awesome, some parts are definitely not. I'm undecided.

# External Python modules required:
# - wx (with wx.animate and mixins)
# - GData (YouTube API, Google Code API)
# - BeautifulSoup (Malformed HTML parsing)
# - PyWin32 (Windows API calls) (only required on Windows)
# - Psyco (optional, speeds up execution)

print 'Starting up.'
print 'Importing core.'
from dCore import *
print 'Importing log.'
from dLog import *
print 'Importing system info.'
import dSysInfo
print 'Importing converter.'
from dConverter import *
print 'Importing wxPython.'
try:
	import wxversion
	try:
		wxversion.select('2.8')
	except:
		print 'Could not select version 2.8. Continuing anyway.'
except:
	print 'Could not import wxversion, continuing anyway.'
import wx # Oh my wx, it's wx.
import wx.animate # wx gif animations, oh my gif!
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin # Mixin for wx.ListrCtrl, to enable autowidth on columns
import wx.lib.stattext # Static texts that respond to mouse events
print 'Importing os.'
import os # Filesystem functions.
print 'Importing traceback.'
import traceback # Traces, yay.
print 'Importing regexes.'
import re # Regular expressions \o/
print 'Importing subprocess.'
import subprocess # Spawn sub-processes (ffmpeg, taskkill)
print 'Importing time.'
import time # Sleepin'
print 'Importing urllib.'
import urllib2 # Fetch data from the tubes, encode/decode URLs
import urllib # Sadly required as well, for its urlencode function
print 'Importing socks.'
import socks # SOCKS proxy client
print 'Importing socket.'
import socket # Used to override the default socket in case of a SOCKS proxy
print 'Importing cookielib.'
import cookielib # Cookie handling. Yum, warm, freshly-baked cookies.
print 'Importing signal.'
import signal # Process signals
print 'Importing webbrowser.'
import webbrowser # Open a page in default browser
print 'Importing random.'
import random # Generate temporary files
print 'Importing shutil.'
import shutil # Shell utilities (copyfile)
print 'Importing sys.'
import sys # System stuff
print 'Importing platform.'
import platform # Platform information
print 'Importing ConfigParser.'
import ConfigParser # INI file parsing and writing
print 'Importing base64.'
import base64 # Base64 encoding/decoding
print 'Importing gdata -> YouTube.'
import gdata.youtube.service # YouTube service
print 'Importing gdata -> Google Code.'
import gdata.projecthosting.client # Google Code service
print 'Importing xmlrpclib.'
import xmlrpclib # XML RPC server communication, used in modules
print 'Importing BeautifulSoup.'
import BeautifulSoup # Tag soup parsing! From http://www.crummy.com/software/BeautifulSoup/
print 'Importing unicodedata.'
import unicodedata # Unicode normalization
print 'Importing hashlib.'
import hashlib # MD5 hashes
print 'Importing tarfile.'
import tarfile # Tar/gz file reading/writing (used for modules)

DV.log = DamnLog(stderr='-q' not in sys.argv and '--quiet' not in sys.argv, flush=True) # Temporary logger until we are far enough to know where should the log file go
DV.sep = DamnUnicode(os.sep)
DV.curdir = DamnUnicode(os.path.dirname(os.path.abspath(sys.argv[0]))) + DV.sep
versionfile = DamnOpenFile(DV.curdir + 'version.damnvid', 'r')
DV.version = DamnUnicode(versionfile.readline().strip())
DV.argv = []
for i in sys.argv[1:]:
	DV.argv.append(DamnUnicode(i))
versionfile.close()
del versionfile
DV.url = u'http://code.google.com/p/damnvid/'
DV.url_halp = u'http://code.google.com/p/damnvid/wiki/Help'
DV.url_update = u'http://code.google.com/p/damnvid/wiki/CurrentVersion'
DV.url_download = u'http://code.google.com/p/damnvid/downloads/'
try:
	DamnExecFile(DV.curdir + u'conf' + DV.sep + u'overrides.damnvid', globs=globals())
except:
	pass # File is optional
DV.gui_ok = False
DV.streamTimeout = 30.0
DV.icon = None # This will be defined when DamnMainFrame is initialized
DV.icon2 = None
DV.icon16 = None
DV.globals = globals
DV.history_split = u'}/|\\{'
DV.my_videos_path = u''
DV.appdata_path = u''
DV.os = DamnUnicode(os.name)
DV.bit64 = False
if DV.os == 'posix' and sys.platform == 'darwin':
	DV.os = u'mac'
	DV.border_padding = 12
	DV.control_hgap = 10
	DV.control_vgap = 4
	DV.scroll_factor = 2
else:
	# Linux~
	DV.border_padding = 8
	DV.control_hgap = 8
	DV.control_vgap = 4
	DV.scroll_factor = 3
	if platform.architecture()[0] == '64bit':
		DV.bit64 = True
if DV.os == 'nt':
	import win32process, win32api
	# Need to determine the location of the "My Videos" and "Application Data" folder.
	import ctypes
	from ctypes import wintypes
	DV.my_videos_path = ctypes.create_string_buffer(wintypes.MAX_PATH)
	DV.appdata_path = ctypes.create_string_buffer(wintypes.MAX_PATH)
	ctypes.windll.shell32.SHGetFolderPathA(None, 0xE, None, 0, DV.my_videos_path)
	ctypes.windll.shell32.SHGetFolderPathA(None, 0x1A, None, 0, DV.appdata_path)
	DV.my_videos_path = DamnUnicode(DV.my_videos_path.value)
	DV.appdata_path = DamnUnicode(DV.appdata_path.value)
	del ctypes, wintypes
	# Do not delete win32process, it is used in the DamnSpawner class.
elif DV.os == 'mac':
	DV.my_videos_path = DamnUnicode(os.path.expanduser('~' + DV.sep + 'Movies'))
else:
	DV.my_videos_path = DamnUnicode(os.path.expanduser('~' + DV.sep + 'Videos'))
DV.my_videos_path = DamnOverridePath('--myvideos=', DV.my_videos_path)
DV.conf_file_location = {
	'nt':DamnUnicode(DV.appdata_path + DV.sep + 'DamnVid'),
	'posix':DamnUnicode('~' + DV.sep + '.damnvid'),
	'mac':DamnUnicode('~' + DV.sep + 'Library' + DV.sep + 'Preferences' + DV.sep + 'DamnVid')
}
if DV.os == 'posix' or DV.os == 'mac':
	DV.conf_file_location = DamnUnicode(os.path.expanduser(DV.conf_file_location[DV.os]))
	DV.appdata_path = os.path.dirname(DV.conf_file_location)
else:
	DV.conf_file_location = DamnUnicode(DV.conf_file_location[DV.os])
DV.conf_file_directory = DamnUnicode(DV.conf_file_location + DV.sep)
DV.actual_conf_file_directory = DV.conf_file_directory
if os.path.isdir(DV.curdir + u'portableConf'):
	DV.conf_file_directory = DV.curdir + u'portableConf' + DV.sep
DV.conf_file_directory = DamnOverridePath('--config=', DV.conf_file_directory)
if not os.path.exists(DV.conf_file_directory):
	try:
		os.makedirs(DV.conf_file_directory)
	except:
		DV.conf_file_directory = DV.actual_conf_file_directory
		try:
			os.makedirs(DV.conf_file_directory)
		except:
			Damnlog('Cannot create configuration directory!')
			pass
DV.conf_file = DamnUnicode(DV.conf_file_directory + 'damnvid.ini')
DV.log_file = DamnUnicode(DV.conf_file_directory + 'damnvid.log')
if os.path.exists(DV.log_file):
	try:
		os.remove(DV.log_file)
	except:
		DV.log_file = None
DV.log = DamnLog(DV.log_file, stderr=u'-q' not in DV.argv and u'--quiet' not in DV.argv, flush=u'--flush' in DV.argv)
if DV.bit64:
	Damnlog('DamnVid started in 64-bit mode on', sys.platform)
else:
	Damnlog('DamnVid started in 32-bit mode on', sys.platform)
Damnlog('Attempting to import Psyco.')
try:
	import psyco
	Damnlog('Psyco imported. Running it.')
	psyco.full()
	Damnlog('Psyco OK.')
except:
	Damnlog('Psyco error. Continuing anyway.')
Damnlog('System information:\n' + dSysInfo.DamnSysinfo() + '\n(End of system information)')
DV.first_run = False
DV.updated = False
if not os.path.exists(DV.conf_file):
	if not os.path.exists(os.path.dirname(DV.conf_file)):
		os.makedirs(os.path.dirname(DV.conf_file))
	shutil.copyfile(DV.curdir + u'conf' + DV.sep + u'conf.ini', DV.conf_file)
	lastversion = DamnOpenFile(DV.conf_file_directory + u'lastversion.damnvid', 'w')
	lastversion.write(DV.version)
	lastversion.close()
	del lastversion
	DV.first_run = True
else:
	if os.path.exists(DV.conf_file_directory + u'lastversion.damnvid'):
		lastversion = DamnOpenFile(DV.conf_file_directory + u'lastversion.damnvid', 'r')
		version = lastversion.readline().strip()
		lastversion.close()
		DV.updated = version != DV.version
		del version
	else:
		DV.updated = True
		lastversion = DamnOpenFile(DV.conf_file_directory + u'lastversion.damnvid', 'w')
		lastversion.write(DV.version.encode('utf8'))
		lastversion.close()
	del lastversion
DV.images_path = DamnUnicode(DV.curdir + u'img/'.replace(u'/', DV.sep))
Damnlog('Image path is', DV.images_path)
Damnlog('My videos path is', DV.my_videos_path)
DV.bin_paths = [DamnUnicode(DV.curdir + u'bin/'.replace(u'/', DV.sep))]
if os.environ.has_key('PATH'):
	DV.env_path = DamnUnicode(os.environ['PATH'])
	if len(DV.env_path):
		try:
			for i in DV.env_path.split(DamnUnicode(os.pathsep)):
				if len(i):
					DV.bin_paths.append(i)
		except:
			pass
else:
	DV.env_path = u''
for i in range(len(DV.bin_paths)):
	if DV.bin_paths[i][-1] != DV.sep:
		DV.bin_paths[i] += DV.sep
Damnlog('Bin paths are', DV.bin_paths)
DV.locale_path = DamnUnicode(DV.curdir + u'locale/'.replace(u'/', DV.sep))
Damnlog('Locale path is', DV.locale_path)
DV.tmp_path = DamnOverridePath('--temp=', DV.actual_conf_file_directory + u'temp/'.replace(u'/', DV.sep))
if not os.path.exists(DV.tmp_path):
	os.makedirs(DV.tmp_path)
Damnlog('Temp path is', DV.tmp_path)
if not os.path.exists(DV.tmp_path):
	Damnlog('Temp path does not exist - attempting to create it.')
	try:
		os.makedirs(DV.tmp_path)
		Damnlog('Temp path created successfully.')
	except:
		Damnlog('Could not create temp path, continuing anyway.')
DV.file_ext = {
	'avi':u'avi',
	'flv':u'flv',
	'mpeg1video':u'mpg',
	'mpeg2video':u'mpg',
	'mpegts':u'mpg',
	'mp4':u'mp4',
	'mov':u'mov',
	'ipod':u'mp4',
	'psp':u'mp4',
	'rm':u'rm',
	'matroska':u'mkv',
	'ogg':u'ogg',
	'vob':u'vob',
	'3gp':u'3gp',
	'3g2':u'3g2',
	'mp3':u'mp3',
	'mp2':u'mp2'
}
DV.file_ext_by_codec = {
	'rv10':u'rm',
	'rv20':u'rm',
	'flv':u'flv',
	'theora':u'ogg',
	'wmv1':u'wmv',
	'wmv2':u'wmv',
	'ac3':u'ac3',
	'vorbis':u'ogg',
	'wmav1':u'wma',
	'wmav2':u'wma'
} # Just in case the format isn't defined, fall back to DV.file_ext_by_codec. Otherwise, fall back to .avi (this is why only codecs that shouldn't get a .avi extension are listed here).
DV.codec_advanced_cl = {
	'mpeg4':[('g', '300'), ('cmp', '2'), ('subcmp', '2'), ('trellis', '2'), '+4mv'],
	'libx264':[('coder', '1'), '+loop', ('cmp', '+chroma'), ('partitions', '+parti4x4+partp8x8+partb8x8'), ('g', '250'), ('subq', '6'), ('me_range', '16'), ('keyint_min', '25'), ('sc_threshold', '40'), ('i_qfactor', '0.71'), ('b_strategy', '1')]
}
Damnlog('Init underway, starting to declare fancier stuff.')
print 'Importing constants.'
from dConstants import *
print 'Importing threading.'
from dThread import *
print 'Importing config.'
from dConfig import *
print 'Importing tubes.'
from dTubes import *
print 'Importing spawner.'
from dSpawn import *
print 'Importing loader.'
from dLoader import *
print 'Importing updater.'
from dUpdater import *
print 'Importing external UI.'
from ui import *
DV.oldclipboard = u''
DV.locale_warnings = []
DV.dumplocalewarnings = '--dump-locale-warnings' in DV.argv
if DV.dumplocalewarnings:
	DV.argv = [x for x in DV.argv if x != '--dump-locale-warnings']
if '-q' in DV.argv or '--flush':
	DV.argv = [x for x in DV.argv if x != '-q' and x != '--flush']
Damnlog('Loading initial config and modules.')
DamnLoadConfig(forcemodules=(DV.first_run or DV.updated))
from dLocale import *
DamnLocaleInit()
Damnlog('End init, begin declarations.')
class DamnVid(wx.App):
	def OnInit(self):
		showsplash = False
		if True:
			DV.prefs = DamnVidPrefs()
			DV.lang = DV.prefs.get('locale')
			DamnLoadCurrentLocale()
			if DV.prefs.get('splashscreen') == 'True':
				splash = DamnSplashScreen()
				clock = time.time()
				showsplash = True
		else:
			pass
		DamnURLOpener()
		self.frame = DamnMainFrame(None, -1, DV.l('DamnVid'))
		if showsplash:
			if True:
				while clock + .5 > time.time():
					time.sleep(.02) # Makes splashscreen stay at least half a second on screen, in case the loading was faster than that. I think it's a reasonable compromise between eyecandy and responsiveness/snappiness
				splash.fadeOut(True)
			else:
				Damnlog('Error while displaying splash screen.')
		self.frame.init2()
		self.frame.Show()
		self.frame.Raise()
		self.loadArgs(DV.argv)
		return True
	def loadArgs(self, args):
		if len(args):
			vids = []
			for i in args:
				if i[-15:].lower() == '.module.damnvid':
					DamnInstallModule(i)
				elif i[-8:].lower() != '.damnvid':
					DV.prefs.set('LastFileDir', os.path.dirname(i))
					vids.append(i)
			if len(vids):
				self.frame.addVid(vids)
	def MacReopenApp(self):
		self.GetTopWindow().Raise()
	def MacOpenFile(self, name):
		if type(name) is not type([]):
			name = [name]
		self.loadArgs(name)
def DamnMain():
	Damnlog('All done, starting wx app already.')
	app = DamnVid(0)
	DV.gui_ok = True
	Damnlog('App up, entering main loop.')
	app.MainLoop()
	Damnlog('Main loop ended, saving prefs.')
	DV.prefs.save()
	Damnlog('Trying to clean temp directory.')
	try:
		shutil.rmtree(DV.tmp_path)
		Damnlog('Cleaned temp directory.')
	except:
		Damnlog('Could not clean temp directory. Nothing fatal...')
	if DV.dumplocalewarnings:
		Damnlog('Starting locale warnings dump')
		try:
			f = DamnOpenFile('damnvid-locale-warnings.log', 'w')
			f.write(u'\n'.join(DV.locale_warnings).encode('utf8'))
			f.close()
			Damnlog('Successful locale warnings dump.')
		except:
			Damnlog('Failed to dump locale warnings.')
	DV.log.close()
# Let's do this.
DamnMain()
