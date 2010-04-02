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
# - GData (YouTube API)
# - BeautifulSoup (Malformed HTML parsing)
# - PyWin32 (Windows API calls) (only required on Windows)
# - Psyco (optional, speeds up execution)

print 'Starting up.'
import wx # Oh my wx, it's wx.
import wx.animate # wx gif animations, oh my gif!
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin # Mixin for wx.ListrCtrl, to enable autowidth on columns
import wx.lib.stattext # Static texts that respond to mouse events
import os # Filesystem functions.
import traceback # Traces, yay.
import re # Regular expressions \o/
import subprocess # Spawn sub-processes (ffmpeg, taskkill)
import time # Sleepin'
import urllib2 # Fetch data from the tubes, encode/decode URLs
import urllib # Sadly required as well, for its urlencode function
import socket # Used to override the default socket in case of a SOCKS proxy
import cookielib # Cookie handling. Yum, warm, freshly-baked cookies.
import signal # Process signals
import webbrowser # Open a page in default browser
import random # Generate temporary files
import shutil # Shell utilities (copyfile)
import sys # System stuff
import platform # Platform information
import ConfigParser # INI file parsing and writing
import base64 # Base64 encoding/decoding
import gdata.youtube.service # YouTube service
import gdata.projecthosting.client # Google Code service
import xmlrpclib # XML RPC server communication, used in modules
import BeautifulSoup # Tag soup parsing! From http://www.crummy.com/software/BeautifulSoup/
import unicodedata # Unicode normalization
import hashlib # MD5 hashes
import tarfile # Tar/gz file reading/writing (used for modules)
import threading as thr # Threads
import socks # SOCKS proxies
print 'Imports done.'

# Yeah, declaring this very early
def DamnUnicode(s):
    if type(s) is type(u''):
        return s
    if type(s) is type(''):
        try:
            return unicode(s)
        except:
            try:
                return unicode(s.decode('utf8'))
            except:
                try:
                    return unicode(s.decode('windows-1252')) # Windows file paths with accents and weird characters
                except:
                    return unicode(s, errors='ignore')
    try:
        return unicode(s)
    except:
        return s
def DamnOpenFile(f, m):
    f = DamnUnicode(f)
    try:
        return open(f, m)
    except:
        try:
            return open(f.encode('utf8'), m)
        except:
            try:
                return open(f.encode('windows-1252'), m)
            except:
                return open(f.encode('utf8', 'ignore'), m)
# Begin constants
class DamnEmpty:
    pass
DV = DamnEmpty() # The only global variable out there... not
DV.sep = DamnUnicode(os.sep)
DV.curdir = DamnUnicode(os.path.dirname(os.path.abspath(sys.argv[0]))) + DV.sep
versionfile = DamnOpenFile(DV.curdir + 'version.damnvid', 'r')
DV.version = DamnUnicode(versionfile.readline().strip())
DV.argv = sys.argv[1:]
versionfile.close()
del versionfile
DV.blanksocket = socket.socket
DV.url = u'http://code.google.com/p/damnvid/'
DV.url_halp = u'http://code.google.com/p/damnvid/wiki/Help'
DV.url_update = u'http://code.google.com/p/damnvid/wiki/CurrentVersion'
DV.url_download = u'http://code.google.com/p/damnvid/downloads/'
DV.gui_ok = False
DV.streamTimeout = 30.0
DV.icon = None # This will be defined when DamnMainFrame is initialized
DV.icon2 = None
DV.icon16 = None
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
for i in DV.argv:
    if DamnUnicode(i)[:9].lower() == u'--config=':
        DV.conf_file_directory = DamnUnicode(i)[9:]
        if DV.conf_file_directory[-1:] != DV.conf_file_directory:
            DV.conf_file_directory += DV.sep
        DV.argv = [x for x in DV.argv if DamnUnicode(x)[:9] != u'--config=']
        break
if not os.path.exists(DV.conf_file_directory):
    try:
        os.makedirs(DV.conf_file_directory)
    except:
        DV.conf_file_directory = DV.actual_conf_file_directory
        try:
            os.makedirs(DV.conf_file_directory)
        except:
            print 'Cannot create configuration directory!'
            pass
DV.conf_file = DamnUnicode(DV.conf_file_directory + 'damnvid.ini')
DV.log_file = DamnUnicode(DV.conf_file_directory + 'damnvid.log')
if os.path.exists(DV.log_file):
    try:
        os.remove(DV.log_file)
    except:
        DV.log_file = None
class DamnLog:
    def __init__(self):
        self.time = 0
        try:
            if not os.path.exists(DV.appdata_path):
                self.makedirs(DV.appdata_path)
            self.stream = DamnOpenFile(DV.log_file, 'w')
            self.stream.write((self.getPrefix() + u'Log opened.').encode('utf8'))
        except:
            self.stream = None
            try:
                print 'Warning: No log stream!'
                traceback.print_exc()
            except:
                pass
    def getPrefix(self):
        t = int(time.time())
        if self.time != t:
            self.time = t
            return u'[' + DamnUnicode(time.strftime('%H:%M:%S')) + u'] '
        return u''
    def log(self, message):
        s = u'\r\n' + self.getPrefix() + DamnUnicode(message.strip())
        if DV.log_to_stdout:
            try:
                print s,
            except:
                try:
                    print s.encode('utf8', errors='ignore'),
                except:
                    print 'Cannot echo log string; invalid characters and/or non-tolerant output?'
            if DV.log_stdout_flush:
                sys.stdout.flush()
        if self.stream is not None:
            try:
                return self.stream.write(s)
            except:
                try:
                    return self.stream.write(s.encode('utf8'))
                except:
                    pass
    def flush(self):
        try:
            self.stream.flush()
        except:
            pass
        try:
            os.fsync(self.stream)
        except:
            pass
    def close(self):
        self.log('Closing log.')
        try:
            self.stream.close()
        except:
            pass
DV.log_to_stdout = '-q' not in sys.argv[1:]
DV.log_stdout_flush = '--flush' in sys.argv[1:]
DV.log = DamnLog()
def Damnlog(*args):
    s = []
    for i in args:
        if type(i) is type(''):
            s.append(DamnUnicode(i))
        elif type(i) is type(u''):
            s.append(i)
        else:
            s.append(DamnUnicode(i))
    return DV.log.log(' '.join(s))
def DamnlogException(typ, value, tb):
    try:
        Damnlog('!!',u'\n'.join(traceback.format_exception(typ, value, tb)))
    except:
        pass
try:
    sys.excepthook = DamnlogException
except:
    pass
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
def DamnSysinfo():
    try:
        sysinfo = u'DamnVid version: ' + DV.version + u'\nDamnVid mode: '
        if DV.bit64:
            sysinfo += u'64-bit'
        else:
            sysinfo += u'32-bit'
        sysinfo += u'\nDamnVid arguments: '
        if len(sys.argv[1:]):
            sysinfo += DamnUnicode(' '.join(sys.argv[1:]))
        else:
            sysinfo += u'(None)'
        sysinfo += u'\nMachine name: '
        if len(platform.node()):
            sysinfo += DamnUnicode(platform.node())
        else:
            sysinfo += u'Unknown'
        sysinfo += u'\nPlatform: '
        if len(platform.platform()):
            sysinfo += DamnUnicode(platform.platform())
        else:
            sysinfo += u'Unknown platform'
        if len(platform.release()):
            sysinfo += u' / ' + DamnUnicode(platform.release())
        else:
            sysinfo += u' / Unknown release'
        sysinfo += u'\nArchitecture: ' + DamnUnicode(' '.join(platform.architecture()))
        if len(platform.machine()):
            sysinfo += u' / ' + DamnUnicode(platform.machine())
        else:
            sysinfo += u' / Unknown machine type'
        return DamnUnicode(sysinfo)
    except:
        return u'System information collection failed.'
Damnlog('System information:\n' + DamnSysinfo() + '\n(End of system information)')
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
DV.bin_path = DamnUnicode(DV.curdir + u'bin/'.replace(u'/', DV.sep))
Damnlog('Bin path is', DV.bin_path)
DV.locale_path = DamnUnicode(DV.curdir + u'locale/'.replace(u'/', DV.sep))
Damnlog('Locale path is', DV.locale_path)
DV.tmp_path = DamnUnicode(DV.actual_conf_file_directory + u'temp/'.replace(u'/', DV.sep))
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
DV.youtube_service = gdata.youtube.service.YouTubeService()
Damnlog('Init underway, starting to declare fancier stuff.')
def DamnExecFile(f):
    try:
        execfile(DamnUnicode(f))
    except:
        try:
            execfile(DamnUnicode(f).encode('utf8'))
        except:
            try:
                execfile(DamnUnicode(f).encode('windows-1252'))
            except:
                pass
class DamnCookieJar(cookielib.CookieJar):
    def _cookie_from_cookie_tuple(self, tup, request): # Work-around for cookielib bug with non-integer cookie versions (*ahem* @ Apple)
        name, value, standard, rest = tup
        standard["version"]= 1
        cookielib.CookieJar._cookie_from_cookie_tuple(self, tup, request)
def DamnURLOpener():
    global urllib2
    Damnlog('Reloading proxy settings.')
    if DV.prefs is None:
        Damnlog('Prefs uninitialized, reloading them.')
        DV.prefs = DamnVidPrefs()
    Damnlog('Building damn cookie jar.')
    DV.cookiejar = DamnCookieJar()
    newSocket = DV.blanksocket
    proxy = DV.prefs.gets('damnvid-proxy', 'proxy')
    Damnlog('Proxy preference is', proxy)
    if proxy == 'none':
        proxyhandle = urllib2.ProxyHandler({}) # Empty dictionary = no proxy
        Damnlog('Proxy is none, set handle to', proxyhandle)
    elif proxy == 'http':
        proxy = {
            'http':DV.prefs.gets('damnvid-proxy','http_proxy'),
            'https':DV.prefs.gets('damnvid-proxy','https_proxy')
        }
        Damnlog('HTTP/HTTPS proxy addresses are', proxy)
        try:
            proxy['http'] += ':'+int(DV.prefs.gets('damnvid-proxy','http_port'))
            Damnlog('HTTP Proxy port is a valid integer.')
        except:
            Damnlog('HTTP Proxy port is not a valid integer.')
        try:
            proxy['https'] += ':'+int(DV.prefs.gets('damnvid-proxy','https_port'))
            Damnlog('HTTPS Proxy port is a valid integer.')
        except:
            Damnlog('HTTPS Proxy port is not a valid integer.')
        proxyhandle = urllib2.ProxyHandler(proxy)
        Damnlog('Proxy is', proxy, '; set handle to', proxyhandle)
    elif proxy == 'socks4' or proxy == 'socks5':
        Damnlog('Proxy is SOCKS-type.')
        proxyhandle = urllib2.ProxyHandler({})
        if proxy == 'socks4':
            Damnlog('It\'s a SOCKS4 proxy.')
            proxytype = socks.PROXY_TYPE_SOCKS4
        else:
            proxytype = socks.PROXY_TYPE_SOCKS5
            Damnlog('It\'s a SOCKS5 proxy.')
        address = DV.prefs.gets('damnvid-proxy','socks_proxy')
        Damnlog('SOCKS proxy address is', address)
        try:
            socks.setdefaultproxy(proxytype, address, int(DV.prefs.gets('damnvid-proxy','socks_port')))
            Damnlog('SOCKS proxy port is a valid integer.')
        except:
            socks.setdefaultproxy(proxytype, address)
            Damnlog('SOCKS proxy port is not a valid integer.')
        newSocket = socks.socksocket
    else:
        proxyhandle = urllib2.ProxyHandler()
        Damnlog('Using system settings, set proxy handle to', proxy)
    Damnlog('Reloading urllib2, setting socket to', newSocket)
    del urllib2
    socket.socket = newSocket
    import urllib2
    Damnlog('Building new URL opener.')
    DV.urllib2_urlopener = urllib2.build_opener(proxyhandle, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPCookieProcessor(DV.cookiejar))
    DV.urllib2_urlopener.addheaders = [('User-agent', 'DamnVid/' + DV.version)]
    Damnlog('URL opener built with user-agent', 'DamnVid/' + DV.version,'; installing as default.')
    urllib2.install_opener(DV.urllib2_urlopener)
    Damnlog('URL opener installed, proxy settings loaded.')
    return DV.urllib2_urlopener
class DamnIconList(wx.ImageList): # An imagelist with dictionary-like association, not stupid IDs, and graceful failure. Can also be initialized with delay.
    def __init__(self, width=16, height=16, mask=True, initialCount=0, fail=None, initNow=False):
        self.list = {}
        self.args = (width, height, mask, initialCount)
        self.init = False
        self.fail = fail
        self.width = width
        self.height = height
        self.rawbitmaps = {}
        if initNow:
            self.initWX()
    def initWX(self):
        wx.ImageList.__init__(self, self.args[0], self.args[1], self.args[2], self.args[3])
        self.init = True
        self.resetList(self.list)
    def add(self, bitmap, handle=None):
        Damnlog('Adding', bitmap, 'to icon list, with handle', handle)
        while handle is None or handle in self.list.keys():
            Damnlog('!Icon conflict found with handle', handle)
            handle = hashlib.md5(str(random.random()) + str(random.random())).hexdigest()
        if self.init:
            if type(bitmap) in (type(''), type(u'')):
                bitmap = wx.Bitmap(bitmap)
            self.list[handle] = self.Add(bitmap)
            self.rawbitmaps[handle] = bitmap
        else:
            self.list[handle] = bitmap
        return handle
    def getRawBitmap(self, handle):
        if type(handle) not in (type(''), type(u'')):
            for k in self.list.iterkeys():
                if self.list[k] == handle:
                    handle = k
        return self.rawbitmaps[handle]
    def get(self, handle):
        if not self.init:
            return
        if type(handle) in (type(''), type(u'')):
            if handle in self.list.keys():
                handle = self.list[handle]
            else:
                handle = self.blankid
        return handle
    def getBitmap(self, handle):
        return self.GetBitmap(self.get(handle))
    def resetList(self, items={}):
        self.list = {}
        if self.init:
            self.RemoveAll()
            if self.fail is None:
                blank = wx.EmptyBitmap(self.width, self.height)
            else:
                blank = wx.Bitmap(self.fail)
            self.blankid = self.Add(blank)
        for i in items.keys():
            self.add(items[i], i)
DV.listicons = DamnIconList(16, 16, fail=DV.images_path + 'video.png')
def DamnGetListIcon(icon):
    return DV.listicons.get(icon)
def DamnInstallModule(module):
    Damnlog('Attempting to install module', module)
    if not os.path.exists(module):
        return 'nofile'
    if not tarfile.is_tarfile(module):
        return 'nomodule'
    mod = tarfile.open(module, 'r')
    files = mod.getnames()
    if not len(files):
        return 'nomodule'
    if files[0].find('/') in (-1, 0):
        return 'nomodule'
    prefix = files[0][0:files[0].find('/') + 1]
    for i in files:
        if i.find('/') in (-1, 0):
            return 'nomodule'
        if i[0:i.find('/') + 1] != prefix:
            return 'nomodule'
    if os.path.exists(DV.modules_path + prefix):
        if os.path.isdir(DV.modules_path + prefix):
            shutil.rmtree(DV.modules_path + prefix)
        else:
            os.remove(DV.modules_path + prefix)
    mod.extractall(DV.modules_path)
    try:
        DV.prefs.rems('damnvid-module-' + prefix[0:-1]) # Reset module preferences when installing it.
        DV.prefs.save()
    except:
        Damnlog('Resetting module preferences for module', module, '(probably not installed or left default before)')
    DamnLoadModule(DV.modules_path + prefix[0:-1])
    Damnlog('Success installing module', module)
    return 'success'
def DamnIterModules(keys=True): # Lawl, this spells "DamnIt"
    mods = DV.modules.keys()
    mods.sort()
    if keys:
        return mods
    ret = []
    for i in mods:
        ret.append(DV.modules[i])
    return ret
def DamnRegisterModule(module):
    Damnlog('Attempting to register module', module)
    DV.modules[module['name']] = module
    DV.modulesstorage[module['name']] = {}
    if module.has_key('register'):
        module['class'].register = {}
        if module['register'].has_key('listicons'):
            module['class'].register['listicons'] = {}
            for icon in module['register']['listicons'].iterkeys():
                DV.listicons.add(DV.modules_path + module['name'] + DV.sep + module['register']['listicons'][icon], icon)
    if module.has_key('preferences'):
        for pref in module['preferences'].iterkeys():
            DV.preferences['damnvid-module-' + module['name'] + ':' + pref] = module['preferences'][pref]
            DV.defaultprefs['damnvid-module-' + module['name'] + ':' + pref] = module['preferences'][pref]['default']
            if module['preferences'][pref]['kind'] == 'dir':
                DV.path_prefs.append('damnvid-module-' + module['name'] + ':' + pref)
        if module.has_key('preferences_order'):
            DV.preference_order['damnvid-module-' + module['name']] = module['preferences_order']
        else:
            DV.preference_order['damnvid-module-' + module['name']] = module['preferences'].keys()
    Damnlog('Module registered:', module)
def DamnGetAlternateModule(uri):
    Damnlog('Got request to get new module for URI:', uri)
    urlgrabber = DamnVideoLoader(None, [uri], feedback=False, allownonmodules=False)
    urlgrabber.start()
    time.sleep(.1)
    while not urlgrabber.done:
        time.sleep(.05)
    res = urlgrabber.result
    urlgrabber.done = False
    if res is None:
        Damnlog('No module found for URI:',uri,'; DamnGetAlternateModule returning None.')
        return None
    Damnlog('Module found for URI:',uri,'; returning', res['module'])
    return res['module']
class DamnVideoModule:
    def __init__(self, uri):
        self.name = 'generic'
        self.uri = uri
        self.link = None
        self.id = None
        self.valid = None
        self.title = None
        self.ticket = None
        self.ticketdate = 0
        self.regex = {
            'title':DV.generic_title_extract
        }
    def isUp(self):
        return True
    def validURI(self):
        return not not self.valid
    def getLink(self):
        return DamnUnicode(self.link)
    def getURI(self):
        return DamnUnicode(self.uri)
    def getID(self):
        return self.id
    def getStorage(self):
        return DV.modulesstorage[self.name]
    def getTitle(self):
        if self.title is None:
            html = DamnURLOpen(self.link)
            total = ''
            for i in html:
                total += i
            res = self.regex['title'].search(total)
            if res:
                self.title = DamnHtmlEntities(res.group(1))
        if self.title is not None:
            return DamnUnicode(self.title)
        return DV.l('Unknown title')
    def getIcon(self):
        return DamnGetListIcon(self.name)
    def pref(self, pref, value=None):
        if value is None:
            return DV.prefs.getm(self.name, pref)
        return DV.prefs.setm(self.name, pref, value)
    def newTicket(self, ticket):
        self.ticket = ticket
        self.ticketdate = time.time()
    def getProfile(self):
        return self.pref('profile')
    def getOutdir(self):
        return self.pref('outdir')
    def renewTicket(self):
        if self.ticket is None:
            self.newTicket(self.uri)
    def getDownload(self):
        self.renewTicket()
        return self.ticket
    def getFFmpegArgs(self):
        return []
    def getDownloadGetter(self):
        return self.getDownload
    def addVid(self, parent):
        parent.addValid(self.getVidObject())
    def getVidObject(self):
        obj = {'name':DamnUnicode(self.getTitle()), 'profile':self.getProfile(), 'profilemodified':False, 'fromfile':DamnUnicode(self.getTitle()), 'dirname':DamnUnicode(self.getLink()), 'uri':DamnUnicode(self.getID()), 'status':DV.l('Pending.'), 'icon':self.getIcon(), 'module':self, 'downloadgetter':self.getDownloadGetter()}
        Damnlog('Module', self.name, 'returning video object:', obj)
        return obj
class DamnModuleUpdateCheck(thr.Thread):
    def __init__(self, parent, modules, byevent=True):
        Damnlog('Spawned module update checker for modules', modules, 'by event:', byevent)
        self.parent = parent
        if type(modules) is not type([]):
            modules = [modules]
        self.modules = modules
        self.done = {}
        self.downloaded = []
        self.byevent = byevent
        thr.Thread.__init__(self)
    def postEvent(self, module, result):
        info = {'module':module, 'result':result}
        Damnlog('Update checker sending event:', info, 'by event:', self.byevent)
        if self.byevent:
            wx.PostEvent(self.parent, DamnLoadingEvent(DV.evt_loading, -1, info))
        else:
            self.parent.onLoad(info)
    def run(self):
        for module in self.modules:
            if not module['about'].has_key('url'):
                self.postEvent(module, 'cannot')
            elif module['about']['url'] not in self.downloaded:
                self.downloaded.append(module['about']['url'])
                try:
                    http = DamnURLOpen(module['about']['url'])
                    checkingfor = [module]
                    for module2 in self.modules:
                        if module2['about'].has_key('url'):
                            if module2['about']['url'] == module['about']['url'] and module2 not in checkingfor:
                                checkingfor.append(module2)
                    html = ''
                    for i in http:
                        html += i
                except:
                    html = ''
                for module2 in checkingfor:
                    res = re.search('<tt>' + re.escape(module2['name']) + '</tt>.*?Latest\s+version\s*:\s*<tt>([^<>]+)</tt>.*?Available\s+at\s*:\s*<a href="([^"]+)"', html, re.IGNORECASE)
                    if not res:
                        self.postEvent(module2, 'error')
                    else:
                        vers = DamnHtmlEntities(res.group(1))
                        if DamnVersionCompare(vers,DamnUnicode(module2['version']))==1:
                            url = DamnHtmlEntities(res.group(2)).strip()
                            if not REGEX_HTTP_GENERIC.match(url):
                                self.postEvent(module2, 'error')
                            else:
                                try:
                                    http = DamnURLOpen(url)
                                    tmpname = DamnTempFile()
                                    tmp = DamnOpenFile(tmpname, 'wb')
                                    for i in http:
                                        tmp.write(i)
                                    tmp.close()
                                    http.close()
                                    DamnInstallModule(tmpname)
                                    self.postEvent(module2, (vers, url))
                                except:
                                    self.postEvent(module2, 'error')
                        else:
                            self.postEvent(module2, 'uptodate')
def DamnSpawner(cmd, shell=False, stderr=None, stdout=None, stdin=None, cwd=None):
    if cwd is None:
        cwd = DV.curdir
    cwd = DamnUnicode(cwd)
    if type(cmd) in (type(''), type(u'')):
        cmd = DamnUnicode(cmd)
    if DV.os == 'nt':
        if type(cmd) in (type([]), type(())):
            tempcmd = []
            for i in cmd:
                tempcmd.append(DamnUnicode(i).encode('windows-1252'))
            Damnlog('Spawning subprocess on NT:', tempcmd)
            return subprocess.Popen(tempcmd, shell=shell, creationflags=win32process.CREATE_NO_WINDOW, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=cwd.encode('windows-1252'), executable=None, bufsize=128) # Yes, ALL std's must be PIPEd, otherwise it doesn't work on win32 (see http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions)
        else:
            Damnlog('Spawning subprocess on NT:', cmd)
            return subprocess.Popen(cmd.encode('windows-1252'), shell=shell, creationflags=win32process.CREATE_NO_WINDOW, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=cwd.encode('windows-1252'), executable=None, bufsize=128)
    else:
        Damnlog('Spawning subprocess on UNIX:', cmd)
        return subprocess.Popen(cmd, shell=shell, stderr=stderr, stdout=stdout, stdin=stdin, cwd=cwd, executable=None, bufsize=128) # Must specify bufsize, or it might be too big to actually get any data (happened to me on Ubuntu)
def DamnVersionCompare(v1, v2): # Returns 1 if v1 is newer, 0 if equal, -1 if v2 is newer.
    v1 = v1.split('.')
    v2 = v2.split('.')
    for i in range(len(v1)):
        if len(v2) <= i:
            return 1
        if v1[i] != v2[i]:
            return 2 * int(v1[i] > v2[i]) - 1
    if len(v1) != len(v2):
        return 2 * (len(v1) > len(v2)) - 1
    return 0
class DamnVidUpdater(thr.Thread):
    def __init__(self, parent, verbose=False, main=True, modules=True):
        Damnlog('Spawned main updater thread')
        self.parent = parent
        self.todo = {'main':main, 'modules':modules}
        self.info = {'main':None, 'modules':{}, 'verbose':verbose}
        thr.Thread.__init__(self)
    def postEvent(self):
        Damnlog('Main updated thread sending event', self.info)
        wx.PostEvent(self.parent, DamnLoadingEvent(DV.evt_loading, -1, {'updateinfo':self.info}))
    def onLoad(self, info):
        if not info.has_key('module'):
            return
        self.info['modules'][info['module']['name']] = info['result']
    def run(self):
        if self.todo['main']:
            regex = re.compile('<tt>([^<>]+)</tt>', re.IGNORECASE)
            try:
                html = DamnURLOpen(DV.url_update)
                for i in html:
                    if regex.search(i):
                        self.info['main'] = regex.search(i).group(1).strip()
            except:
                pass
        if self.todo['modules']:
            updater = DamnModuleUpdateCheck(self, DamnIterModules(False), False)
            updater.run() # Yes, run(), not start(), this way we're waiting for it to complete.
        self.postEvent()
def DamnLoadModule(module):
    for i in os.listdir(module):
        if not os.path.isdir(module + DV.sep + i) and i[-8:] == '.damnvid':
            DamnExecFile(module + DV.sep + i)
def DamnLoadConfig(forcemodules=False):
    Damnlog('Loading config.')
    DV.preferences = None
    DamnExecFile(DV.curdir + u'conf' + DV.sep + u'preferences.damnvid')
    DV.path_prefs = []
    DV.defaultprefs = {
    }
    for i in DV.preferences.iterkeys():
        if DV.preferences[i].has_key('default'):
            DV.defaultprefs[i] = DV.preferences[i]['default']
        else:
            DV.defaultprefs[i] = None
        if DV.preferences[i]['kind'] == 'dir':
            DV.path_prefs.append(i)
    DV.prefs = None # Will be loaded later
    # Load modules
    Damnlog('Loading modules.')
    DV.modules_path = DV.conf_file_directory + 'modules' + DV.sep
    if not os.path.exists(DV.modules_path):
        os.makedirs(DV.modules_path)
    DV.modules = {}
    DV.modulesstorage = {}
    DV.generic_title_extract = re.compile('<title>\s*([^<>]+?)\s*</title>', re.IGNORECASE)
    DV.listicons.resetList({
        'damnvid':DV.images_path + 'video.png',
        'generic':DV.images_path + 'online.png'
    })
    if forcemodules or '--rebuild-modules' in DV.argv:
        Damnlog('forcemodules is on; resetting modules.')
        shutil.rmtree(DV.modules_path)
        os.makedirs(DV.modules_path)
        if '--rebuild-modules' in DV.argv: # DEBUG ONLY; rebuilds all modules
            Damnlog('Careful, rebuilding all modules!')
            DV.argv = [x for x in DV.argv if x != '--rebuild-modules']
            for i in os.listdir('./'):
                if i[-15:] == '.module.damnvid':
                    os.remove(i)
            for i in os.listdir(DV.curdir + 'modules/'):
                if i[-15:] == '.module.damnvid':
                    os.remove(DV.curdir + 'modules/' + i)
            for i in os.listdir(DV.curdir + 'modules'):
                if os.path.isdir(DV.curdir + 'modules/' + i) and i.find('svn') == -1:
                    Damnlog('Building module ' + i)
                    DamnSpawner(['python', 'build-any/module-package.py', DV.curdir + 'modules/' + i ], cwd=DV.curdir).wait()
            for i in os.listdir(DV.curdir):
                if i[-15:] == '.module.damnvid':
                    os.rename(DV.curdir + i, DV.curdir + 'modules/' + i)
        for i in os.listdir(DV.curdir + 'modules'):
            if i[-15:] == '.module.damnvid':
                Damnlog('Installing', i)
                DamnInstallModule(DV.curdir + 'modules' + DV.sep + i)
    for i in os.listdir(DV.modules_path):
        if os.path.isdir(DV.modules_path + i):
            DamnLoadModule(DV.modules_path + i)
    # End load modules
DV.locale_warnings = []
DV.dumplocalewarnings = '--dump-locale-warnings' in DV.argv
if DV.dumplocalewarnings:
    DV.argv = [x for x in DV.argv if x != '--dump-locale-warnings']
if '-q' in DV.argv or '--flush':
    DV.argv = [x for x in DV.argv if x != '-q' and x != '--flush']
def DamnLocale(s, asunicode=True, warn=True):
    k = DamnUnicode(s)
    s = DamnUnicode(s)
    if DV.locale is None:
        Damnlog('Locale warning: Locale is None.')
        if asunicode:
            return s
        return k
    if not DV.locale['strings'].has_key(k):
        if warn and k not in DV.locale_warnings:
            DV.locale_warnings.append(k)
            Damnlog('Locale warning:', k, 'has no key for language', DV.lang)
        if asunicode:
            return s
        return k
    if asunicode:
        return DamnUnicode(DV.locale['strings'][k])
    return str(DV.locale['strings'][k].encode('ascii', 'ignore'))
def DamnLoadCurrentLocale():
    if DV.languages.has_key(DV.lang):
        DV.locale = DV.languages[DV.lang]
    else:
        DV.locale = None
Damnlog('Loading initial config and modules.')
DamnLoadConfig(forcemodules=(DV.first_run or DV.updated))
Damnlog('Loading locales.')
DV.languages = {}
DV.l = DamnLocale # Function shortcut
DV.locale = None
DV.lang = 'English' # Default, will be overriden later if needed.
for i in os.listdir(DV.locale_path):
    if i[-7:].lower() == '.locale':
        Damnlog('Loading locale', DV.locale_path + i)
        DamnExecFile(DV.locale_path + i)
DamnLoadCurrentLocale()
# Begin ID constants
ID_MENU_EXIT = wx.ID_EXIT
ID_MENU_PREFERENCES = wx.ID_PREFERENCES
ID_MENU_HALP = wx.ID_HELP
ID_MENU_ABOUT = wx.ID_ABOUT
ID_COL_VIDNAME = 0
ID_COL_VIDPROFILE = 1
ID_COL_VIDSTAT = 2
ID_COL_VIDPATH = 3
# Begin regex constants
REGEX_PATH_MULTI_SEPARATOR_CHECK = re.compile('/+')
REGEX_FFMPEG_DURATION_EXTRACT = re.compile('^\\s*Duration:\\s*(\\d+):(\\d\\d):([.\\d]+)', re.IGNORECASE)
REGEX_FFMPEG_TIME_EXTRACT = re.compile('time=([.\\d]+)', re.IGNORECASE)
REGEX_HTTP_GENERIC = re.compile('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}#\w]*)?$', re.IGNORECASE)
REGEX_HTTP_GENERIC_LOOSE = re.compile('https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}\w]*)?', re.IGNORECASE)
REGEX_HTTP_EXTRACT_FILENAME = re.compile('^.*/|[?#].*$')
REGEX_HTTP_EXTRACT_DIRNAME = re.compile('^([^?#]*)/.*?$')
REGEX_FILE_CLEANUP_FILENAME = re.compile('[\\/:?"|*<>]+')
REGEX_URI_EXTENSION_EXTRACT = re.compile('^(?:[^?|<>]+[/\\\\])?[^/\\\\|?<>#]+\\.(\\w{1,3})(?:$|[^/\\\\\\w].*?$)')
REGEX_HTTP_GENERIC_TITLE_EXTRACT = re.compile('<title>([^<>]+)</title>', re.IGNORECASE)
REGEX_THOUSAND_SEPARATORS = re.compile('(?<=[0-9])(?=(?:[0-9]{3})+(?![0-9]))')
# End regex constants
# End constants
Damnlog('End init, begin declarations.')
def DamnURLOpen(req, data=None, throwerror=False):
    Damnlog('DamnURLOpen called with request',req,'; data',data,'; Throw error?',throwerror)
    if type(req) in (type(''), type(u'')):
        req = urllib2.Request(DamnUnicode(req))
        Damnlog('Request was string; request is now',req)
    try:
        if data is not None:
            pipe = urllib2.urlopen(req, data)
        else:
            pipe = urllib2.urlopen(req)
        Damnlog('DamnURLOpen successful, returning stream.')
        return pipe
    except Exception, e:
        if throwerror:
            Damnlog('DamnURLOpen failed on request',req,' with exception',e,'; throwing error because throwerror is True.')
            raise e
        Damnlog('DamnURLOpen failed on request',req,' with exception',e,'; returning None because throwerror is False.')
        return None
def DamnRTMPDump(req):
    pass # Todo
def DamnURLPicker(urls, urlonly=False, resumeat=None):
    tried = []
    if resumeat == 0:
        resumeat = None
    Damnlog('DamnURLPicker summoned. URLs:', urls, 'Resume at:', resumeat)
    for i in urls:
        if i not in tried:
            tried.append(i)
            if resumeat is None:
                request = urllib2.Request(i)
            else:
                request = urllib2.Request(i, None, {'Range':'bytes=' + str(resumeat) + '-*'})
            try:
                pipe = DamnURLOpen(request, throwerror=True)
                if urlonly:
                    try:
                        pipe.close()
                    except:
                        pass
                    return i
                Damnlog('DamnURLPicker returning pipe stream for', i)
                return pipe
            except IOError, err:
                if not hasattr(err, 'reason') and not hasattr(err, 'code'):
                    Damnlog('DamnURLPicker returning none because of an IOError without reason or code')
                    return None
    Damnlog('DamnURLPicker returning none because no URLs are valid')
    return None
def DamnURLPickerBySize(urls, array=False):
    Damnlog('URL picker by size summoned. URLs:', urls)
    if len(urls) == 1:
        if array:
            return urls
        return urls[0]
    tried = []
    maxlen = []
    maxurl = []
    for i in urls:
        if i not in tried:
            tried.append(i)
            try:
                handle = DamnURLOpen(i)
                size = int(handle.info()['Content-Length'])
                handle.close()
                maxlen.append(size)
                maxurl.append(i)
            except:
                pass
    if not len(maxurl):
        return urls[0]
    maxlen2 = maxlen
    maxlen2.sort()
    maxlen2.reverse()
    assoc = []
    finalurls = []
    for i in maxlen2:
        for f in range(len(maxlen)):
            if i == maxlen[f] and f not in assoc:
                assoc.append(f)
                finalurls.append(maxurl[f])
    for i in tried:
        if i not in finalurls:
            finalurls.append(i)
    if array:
        return finalurls
    return finalurls[0]
def DamnTempFile():
    name = DV.tmp_path + DamnUnicode(random.random()) + '.tmp'
    while os.path.exists(name):
        name = DV.tmp_path + DamnUnicode(random.random()) + '.tmp'
    Damnlog('Temp file requested. Return:', name)
    return name
def DamnFriendlyDir(d):
    if DV.os == 'mac':
        myvids = DV.l('Movies')
    else:
        myvids = DV.l('My Videos')
    d = d.replace('?DAMNVID_MY_VIDEOS?', myvids)
    d = os.path.expanduser(d).replace(DV.my_videos_path, myvids).replace('/', DV.sep).replace('\\', DV.sep)
    while d[-1:] == DV.sep:
        d = d[0:-1]
    return d
def DamnHtmlEntities(html):
    return DamnUnicode(BeautifulSoup.BeautifulStoneSoup(html, convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)).replace(u'&amp;', u'&') # Because BeautifulSoup, as good as it is, puts &amp;badentity where &badentitity; are. Gotta convert that back.
DV.evt_progress = wx.NewEventType()
DV.evt_prog = wx.PyEventBinder(DV.evt_progress, 1)
class DamnProgressEvent(wx.PyCommandEvent):
    def __init__(self, eventtype, eventid, eventinfo):
        wx.PyCommandEvent.__init__(self, eventtype, eventid)
        self.info = eventinfo
    def GetInfo(self):
        return self.info
DV.evt_loading = wx.NewEventType()
DV.evt_load = wx.PyEventBinder(DV.evt_loading, 1)
class DamnLoadingEvent(wx.PyCommandEvent):
    def __init__(self, eventtype, eventid, eventinfo):
        wx.PyCommandEvent.__init__(self, eventtype, eventid)
        self.info = eventinfo
    def GetInfo(self):
        return self.info
DV.evt_bugreporting = wx.NewEventType()
DV.evt_bugreport = wx.PyEventBinder(DV.evt_bugreporting, 1)
class DamnBugReportEvent(wx.PyCommandEvent):
    def __init__(self, eventtype, eventid, eventinfo):
        wx.PyCommandEvent.__init__(self, eventtype, eventid)
        self.info = eventinfo
    def GetInfo(self):
        return self.info
class DamnDropHandler(wx.FileDropTarget): # Handles files dropped on the ListCtrl
    def __init__(self, parent):
        wx.FileDropTarget.__init__(self)
        self.parent = parent
    def OnDropFiles(self, x, y, filenames):
        self.parent.addVid(filenames)
class DamnCurry:
    # From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.pending = args[:]
        self.kwargs = kwargs
    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.func(*(self.pending + args), **kw)
class DamnTrayIcon(wx.TaskBarIcon):
    def __init__(self, parent):
        wx.TaskBarIcon.__init__(self)
        Damnlog('DamnTrayIcon initialized with parent window',parent)
        self.parent = parent
        self.parent.Iconize(True) # Releases system memory
        self.parent.Hide()
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.raiseParent)
        self.Bind(wx.EVT_TASKBAR_CLICK, self.onMenu)
        if DV.os == 'nt':
            self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.raiseParent)
        Damnlog('DamnTrayIcon ready.')
        self.timer = -1
        self.tooltip = DV.l('DamnVid')
        self.alternateIcons = False
        self.isDead = False
        self.icons = [DV.icon16]#, DV.icon2]
        self.iconindex = 0
        self.iconTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onAlternateIcon, self.iconTimer)
        self.iconTimer.Start(500)
        self.updateIcon()
    def setTooltip(self, tooltip):
        self.tooltip = DamnUnicode(tooltip)
        self.updateIcon()
    def onAlternateIcon(self, event=None):
        if self.alternateIcons:
            self.iconindex = (self.iconindex + 1) % len(self.icons)
            self.updateIcon()
    def startAlternate(self):
        self.iconindex = 0
        self.updateIcon()
        self.alternateIcons = True
    def stopAlternate(self):
        self.startAlternate()
        self.alternateIcons = False
    def updateIcon(self):
        self.SetIcon(self.icons[self.iconindex], self.tooltip)
    def raiseParent(self, event=None):
        if time.time() - self.timer < 0.1:
            return
        self.timer=time.time()
        Damnlog('DamnTrayIcon raiseParent method called.')
        self.parent.trayicon = None
        self.parent.Iconize(False)
        self.parent.Show(True)
        self.parent.Raise() # Bring to front
        Damnlog('DamnTrayIcon parent shown and raised, destroying self.')
        self.destroyTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.selfDestruct, self.destroyTimer)
        self.destroyTimer.Start(5)
    def selfDestruct(self, *args):
        Damnlog('DamnTrayIcon self-destructing.')
        if self.isDead:
            return
        self.isDead = True
        self.destroyTimer.Stop()
        self.iconTimer.Stop()
        self.Destroy()
    def onMenu(self, event=None):
        menu = wx.Menu()
        show = wx.MenuItem(menu, -1, DV.l('Show DamnVid'))
        menu.AppendItem(show)
        menu.Bind(wx.EVT_MENU, self.raiseParent, show)
        if self.parent.converting == -1:
            go = wx.MenuItem(menu, -1, DV.l('Let\'s go!'))
            menu.AppendItem(go)
            menu.Bind(wx.EVT_MENU, self.parent.onGo, go)
        else:
            stop = wx.MenuItem(menu, -1, DV.l('Stop'))
            menu.AppendItem(stop)
            menu.Bind(wx.EVT_MENU, self.parent.onStop, stop)
        exit = wx.MenuItem(menu, -1, DV.l('E&xit'))
        menu.AppendItem(exit)
        menu.Bind(wx.EVT_MENU, self.onClose, exit)
        self.PopupMenu(menu)
    def onClose(self, event=None):
        self.raiseParent()
        self.parent.onClose(event)
class DamnListContextMenu(wx.Menu): # Context menu when right-clicking on the DamnList
    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent
        self.items = self.parent.getAllSelectedItems()
        if len(self.items): # If there's at least one item selected
            rename = wx.MenuItem(self, -1, DV.l('Rename'))
            self.AppendItem(rename)
            if len(self.items) != 1:
                rename.Enable(False)
            else:
                if self.items[0] == self.parent.parent.converting:
                    rename.Enable(False)
            self.Bind(wx.EVT_MENU, self.parent.parent.onRename, rename)
            moveup = wx.MenuItem(self, -1, DV.l('Move up'))
            self.AppendItem(moveup)
            moveup.Enable(self.items[0] > 0)
            self.Bind(wx.EVT_MENU, self.parent.parent.onMoveUp, moveup)
            movedown = wx.MenuItem(self, -1, 'Move down')
            self.AppendItem(movedown)
            movedown.Enable(self.items[-1] < self.parent.GetItemCount() - 1)
            self.Bind(wx.EVT_MENU, self.parent.parent.onMoveDown, movedown)
            stop = wx.MenuItem(self, -1, DV.l('Stop'))
            self.AppendItem(stop)
            stop.Enable(self.parent.parent.converting in self.items)
            self.Bind(wx.EVT_MENU, self.parent.parent.onStop, stop)
            remove = wx.MenuItem(self, -1, DV.l('Remove from list'))
            self.AppendItem(remove)
            remove.Enable(self.parent.parent.converting not in self.items)
            self.Bind(wx.EVT_MENU, self.parent.parent.onDelSelection, remove)
            if self.parent.parent.converting not in self.items:
                onepending = False
                for i in self.items:
                    if self.parent.parent.meta[self.parent.parent.videos[i]]['status'] == DV.l('Pending.'):
                        onepending = True
                if not onepending:
                    resetstatus = wx.MenuItem(self, -1, DV.l('Reset status'))
                    self.Bind(wx.EVT_MENU,self.parent.parent.onResetStatus, resetstatus)
                    self.AppendItem(resetstatus)
                profile = wx.Menu()
                uniprofile = int(self.parent.parent.meta[self.parent.parent.videos[self.items[0]]]['profile'])
                for i in self.items:
                    if int(self.parent.parent.meta[self.parent.parent.videos[i]]['profile']) != uniprofile:
                        uniprofile = -2
                for i in range(-1, DV.prefs.profiles):
                    if uniprofile != -2:
                        prof = wx.MenuItem(self, -1, DV.l(DV.prefs.getp(i, 'name'), warn=False), kind=wx.ITEM_RADIO)
                        profile.AppendItem(prof) # Item has to be appended before being checked, otherwise error. Annoying code duplication.
                        prof.Check(i == uniprofile)
                    else:
                        prof = wx.MenuItem(self, -1, DV.l(DV.prefs.getp(i, 'name'), warn=False))
                        profile.AppendItem(prof)
                    self.Bind(wx.EVT_MENU, DamnCurry(self.parent.parent.onChangeProfile, i), prof)    # Of course, on one platform it's self.Bind...
                    profile.Bind(wx.EVT_MENU, DamnCurry(self.parent.parent.onChangeProfile, i), prof) # ... and on the other it's profile.Bind. *sigh*
                self.AppendMenu(-1, DV.l('Encoding profile'), profile)
            else:
                profile = wx.MenuItem(self, -1, 'Encoding profile')
                self.AppendItem(profile)
                profile.Enable(False)
        else: # Otherwise, display a different context menu
            addfile = wx.MenuItem(self, -1, DV.l('Add Files'))
            self.AppendItem(addfile)
            self.Bind(wx.EVT_MENU, self.parent.parent.onAddFile, addfile)
            addurl = wx.MenuItem(self, -1, DV.l('Add URL'))
            self.AppendItem(addurl)
            self.Bind(wx.EVT_MENU, self.parent.parent.onAddURL, addurl)
class DamnHyperlink(wx.HyperlinkCtrl):
    def __init__(self, parent, id, label, url, background=None):
        wx.HyperlinkCtrl.__init__(self, parent, id, label, url)
        if background is not None:
            self.SetBackgroundColour(background)
class DamnList(wx.ListCtrl, ListCtrlAutoWidthMixin): # The ListCtrl, which inherits from the Mixin
    def __init__(self, parent, window):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)
        self.parent = window # "parent" is the panel
    def onRightClick(self, event):
        p = self.HitTest(event.GetPosition())
        if p[0] != -1:
            if not self.IsSelected(p[0]):
                self.clearAllSelectedItems()
                self.Select(p[0], on=1) # Select pointed item
        else:
            self.clearAllSelectedItems()
        self.PopupMenu(DamnListContextMenu(self), event.GetPosition())
    def getAllSelectedItems(self):
        items = []
        i = self.GetFirstSelected()
        while i != -1:
            items.append(i)
            i = self.GetNextSelected(i)
        return items
    def clearAllSelectedItems(self):
        for i in self.getAllSelectedItems():
            self.Select(i, on=0)
    def invertItems(self, i1, i2):
        for i in range(self.GetColumnCount()):
            tmp = [self.GetItem(i1, i).GetText(), self.GetItem(i1, i).GetImage()]
            self.SetStringItem(i1, i, self.GetItem(i2, i).GetText(), self.GetItem(i2, i).GetImage())
            self.SetStringItem(i2, i, tmp[0], tmp[1])
class DamnAddURLDialog(wx.Dialog):
    def __init__(self, parent, default):
        self.parent = parent
        wx.Dialog.__init__(self, parent, -1, DV.l('Add videos by URL...'))
        absolutetopsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(absolutetopsizer)
        innertopsizer = wx.BoxSizer(wx.HORIZONTAL)
        innertopsizer2 = wx.BoxSizer(wx.VERTICAL)
        self.toppanel = wx.Panel(self, -1)
        absolutetopsizer.Add(self.toppanel, 1, wx.EXPAND)
        self.toppanel.SetSizer(innertopsizer)
        topsizer = wx.BoxSizer(wx.VERTICAL)
        innertopsizer.Add((DV.border_padding, 0))
        innertopsizer.Add(innertopsizer2, 1, wx.EXPAND)
        innertopsizer.Add((DV.border_padding, 0))
        innertopsizer2.Add((0, DV.border_padding))
        innertopsizer2.Add(topsizer, 1, wx.EXPAND)
        innertopsizer2.Add((0, DV.border_padding))
        # Finished paddings and stuff, now for the actual dialog construction
        topsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('Enter the URL of the video you wish to download.')))
        topsizer.Add((0, DV.control_vgap))
        urlboxsizer = wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(urlboxsizer, 0, wx.EXPAND)
        urllabel = wx.StaticText(self.toppanel, -1, DV.l('URL:'))
        urlboxsizer.Add(urllabel, 0, wx.ALIGN_CENTER_VERTICAL)
        urlboxsizer.Add((DV.control_hgap, 0))
        self.urlbox = wx.TextCtrl(self.toppanel, -1, default, style=wx.TE_PROCESS_ENTER)
        urlboxsizer.Add(self.urlbox, 1, wx.EXPAND)
        self.urlbox.Bind(wx.EVT_TEXT_ENTER, self.onAdd)
        self.urlbox.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        urlboxsizer.Add((DV.control_hgap, 0))
        self.addButton = wx.Button(self.toppanel, -1, '+')
        urlboxsizer.Add(self.addButton, 0)
        btnheight = self.addButton.GetSizeTuple()[1]
        self.addButton.SetMinSize((btnheight, btnheight)) # Makes the button have a 1:1 aspect ratio
        self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
        topsizer.Add((0, DV.control_vgap))
        autoconvertchecksizer = wx.BoxSizer(wx.HORIZONTAL)
        self.autoconvertcheck = wx.CheckBox(self.toppanel, -1, DV.l('Automatically download and convert right away'))
        self.autoconvertcheck.SetValue(DV.prefs.get('autoconvert') == 'True')
        self.autoconvertcheck.Bind(wx.EVT_CHECKBOX, self.onAutoconvertCheck)
        autoconvertchecksizer.Add((DV.control_hgap + urllabel.GetSizeTuple()[0], 0))
        autoconvertchecksizer.Add(self.autoconvertcheck)
        topsizer.Add(autoconvertchecksizer, 0, wx.EXPAND)
        topsizer.Add((0, DV.control_vgap))
        topsizer.Add(wx.StaticLine(self.toppanel, -1, style=wx.HORIZONTAL), 0, wx.EXPAND)
        topsizer.Add((0, DV.control_vgap))
        # Start building the bottom part, put sizers in place...
        bottomhorizontalsizer = wx.BoxSizer(wx.HORIZONTAL)
        topsizer.Add(bottomhorizontalsizer, 1, wx.EXPAND)
        bottomleftsizer = wx.BoxSizer(wx.VERTICAL)
        bottomhorizontalsizer.Add(bottomleftsizer, 1, wx.EXPAND | wx.ALIGN_TOP)
        bottomhorizontalsizer.Add((DV.control_hgap, 0))
        bottomhorizontalsizer.Add(wx.StaticLine(self.toppanel, -1, style=wx.VERTICAL), 0, wx.EXPAND | wx.ALIGN_TOP)
        bottomhorizontalsizer.Add((DV.control_hgap, 0))
        bottomrightsizer = wx.BoxSizer(wx.VERTICAL)
        bottomhorizontalsizer.Add(bottomrightsizer, 1, wx.EXPAND | wx.ALIGN_TOP)
        # Now start building the bottom-left part
        bottomleftsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('Go ahead, add some videos!')))
        bottomleftsizer.Add((0, DV.control_vgap))
        bottomleftsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('The following sites are supported:')))
        scrollinglist = wx.ScrolledWindow(self.toppanel, -1)
        scrollinglistsizer = wx.BoxSizer(wx.VERTICAL)
        scrollinglist.SetSizer(scrollinglistsizer)
        bottomleftsizer.Add(scrollinglist, 1, wx.EXPAND)
        for i in DamnIterModules(False):
            if i.has_key('sites'):
                for site in i['sites']:
                    scrollinglistsizer.Add((0, DV.control_vgap))
                    sitesizer = wx.BoxSizer(wx.HORIZONTAL)
                    scrollinglistsizer.Add(sitesizer)
                    sitesizer.Add(wx.StaticBitmap(scrollinglist, -1, wx.Bitmap(DV.modules_path + i['name'] + DV.sep + site['icon'])), 0, wx.ALIGN_CENTER_VERTICAL)
                    sitesizer.Add((DV.control_hgap, 0))
                    sitesizer.Add(DamnHyperlink(scrollinglist, -1, site['title'], site['url']), 0, wx.ALIGN_CENTER_VERTICAL)
        scrollinglist.SetMinSize((-1, 220))
        scrollinglist.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
        # Now start building the bottom-right part
        self.monitorcheck = wx.CheckBox(self.toppanel, -1, DV.l('Monitor clipboard for new URLs'))
        self.monitorcheck.Bind(wx.EVT_CHECKBOX, self.onMonitorCheck)
        self.monitorcheck.SetValue(DV.prefs.get('clipboard') == 'True')
        bottomrightsizer.Add(self.monitorcheck)
        bottomrightsizer.Add((0, DV.control_vgap))
        self.monitorlabel = wx.StaticText(self.toppanel, -1, '')
        bottomrightsizer.Add(self.monitorlabel)
        bottomrightsizer.Add((0, DV.control_vgap))
        self.monitorlabel2 = wx.StaticText(self.toppanel, -1, '')
        bottomrightsizer.Add(self.monitorlabel2)
        self.onMonitorCheck()
        bottomrightsizer.Add((0, DV.control_vgap))
        self.videolist = DamnList(self.toppanel, self)
        il = wx.ImageList(16, 16, True)
        for i in range(DV.listicons.GetImageCount()):
            il.Add(DV.listicons.GetBitmap(i))
        self.videolist.AssignImageList(il, wx.IMAGE_LIST_SMALL)
        bottomrightsizer.Add(self.videolist, 1, wx.EXPAND)
        self.videocolumn = self.videolist.InsertColumn(ID_COL_VIDNAME, DV.l('Videos'))
        # We're done! Final touches...
        self.videos = []
        self.SetClientSize(self.toppanel.GetBestSize())
        self.Center()
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown, self.toppanel)
        self.Bind(wx.EVT_CLOSE, self.onClose)
    def onAdd(self, event=None, val=None):
        if val is None:
            val = self.urlbox.GetValue()
            self.urlbox.SetValue('')
        message = None
        if not val:
            message = (DV.l('No URL entered'), DV.l('You must enter a URL!'))
        elif not self.parent.validURI(val):
            message = (DV.l('Invalid URL'), DV.l('This is not a valid URL!'))
        if message is not None:
            dlg = wx.MessageDialog(None, message[1], message[0], wx.OK | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.videolist.InsertStringItem(len(self.videos), val)
        self.videolist.SetItemImage(len(self.videos), DamnGetListIcon('generic'), DamnGetListIcon('generic'))
        self.videos.append(val)
        self.parent.addVid([val], DV.prefs.get('autoconvert') == 'True')
        self.urlbox.SetFocus()
    def update(self, original, name, icon):
        for i in range(len(self.videos)):
            if self.videos[i] == original:
                self.videolist.SetStringItem(i, self.videocolumn, name)
                self.videolist.SetItemImage(i, DamnGetListIcon(icon), DamnGetListIcon(icon))
    def onAutoconvertCheck(self, event=None):
        DV.prefs.set('autoconvert', str(self.autoconvertcheck.GetValue()))
    def onMonitorCheck(self, event=None):
        newpref = self.monitorcheck.GetValue()
        DV.prefs.set('clipboard', str(newpref))
        if newpref:
            self.monitorlabel.SetLabel(DV.l('Your clipboard is being monitored.'))
            self.monitorlabel2.SetLabel(DV.l('Simply copy a video URL and DamnVid will add it.'))
        else:
            self.monitorlabel.SetLabel(DV.l('Your clipboard is not being monitored.'))
            self.monitorlabel2.SetLabel(DV.l('Check the checkbox above if you want it to be monitored.'))
        self.monitorlabel.Wrap(180)
        self.monitorlabel2.Wrap(180)
        self.toppanel.Layout()
    def onKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL):
            self.onClose(event)
        else:
            event.Skip() # Let the event slide, otherwise the key press isn't even registered
    def onClose(self, event):
        DV.prefs.save() # Save eventually-changed-with-the-checkboxes prefs
        self.Destroy()
class DamnEEgg(wx.Dialog):
    def __init__(self, parent, id):
        wx.Dialog.__init__(self, parent, id, DV.l('Salute the Secret Stoat!'))
        topvbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topvbox)
        self.panel = wx.Panel(self, -1)
        topvbox.Add(self.panel, 1, wx.EXPAND)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(self.vbox)
        self.vbox.Add(wx.StaticBitmap(self.panel, -1, wx.Bitmap(DV.images_path + 'stoat.jpg')), 0, wx.ALIGN_CENTER)
        self.AddText(DV.l('DamnVid ') + DV.version + DV.l(' is *100% stoat-powered*, and *proud* of it.'), True)
        self.AddText(DV.l('*No stoats were harmed* (much) during DamnVid\'s development. Ya rly.'), True)
        self.vbox.Add((0, 5))
        self.AddText(DV.l('Praise the *Secret Stoat* and all it stands for: *WIN*.'), True)
        self.vbox.Add((0, 5))
        self.AddText(DV.l('Definitions of *WIN* on the Web:'), True)
        self.vbox.Add((0, 5))
        self.AddText(DV.l('- be the winner in a contest or competition; be victorious; "He won the Gold Medal in skating"; "Our home team won"; "Win the game"'))
        self.AddText(DV.l('- acquire: win something through one\'s efforts; "I acquired a passing knowledge of Chinese"; "Gain an understanding of international finance"'))
        self.AddText(DV.l('- gain: obtain advantages, such as points, etc.; "The home team was gaining ground"'))
        self.AddText(DV.l('- a victory (as in a race or other competition); "he was happy to get the win"'))
        self.AddText(DV.l('- winnings: something won (especially money)'))
        self.AddText(DV.l('- succeed: attain success or reach a desired goal; "The enterprise succeeded"; "We succeeded in getting tickets to the show"; "she struggled to overcome her handicap and won"'))
        btn = wx.Button(self.panel, -1, DV.l('Secret Stoat!'))
        self.vbox.Add(btn, 0, wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.onBtn, btn)
        self.SetClientSize(self.panel.GetBestSize())
        self.Center()
    def AddText(self, s, center=False):
        strings = ['']
        for i in s:
            if i == '*':
                strings.append('')
            else:
                strings[-1] += i
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        bold = False
        sysfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        normfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), sysfont.GetWeight())
        boldfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), wx.FONTWEIGHT_BOLD)
        for i in strings:
            t = wx.StaticText(self.panel, -1, i)
            t.Wrap(500)
            if bold:
                t.SetFont(boldfont)
            else:
                t.SetFont(normfont)
            bold = not bold
            hbox.Add(t)
        if center:
            self.vbox.Add(hbox, 0, wx.ALIGN_CENTER)
        else:
            self.vbox.Add(hbox, 0)
    def onBtn(self, event):
        self.Close(True)
class DamnBugReporter(thr.Thread):
    def __init__(self, desc, steps='', sysinfo='', email='', parent=None):
        self.desc = desc
        self.steps = steps
        self.sysinfo = sysinfo
        self.email = email
        self.parent = parent
        thr.Thread.__init__(self)
    def postEvent(self, title=None, dialog=None, error=False, closedialog=True):
        info = {'title':title, 'dialog':dialog, 'error':error, 'closedialog':closedialog}
        Damnlog('Posting a bug report update event with info', info)
        if self.parent is None:
            Damnlog('Not posting anything, parent is none.')
            return
        try:
            wx.PostEvent(self.parent, DamnBugReportEvent(DV.evt_bugreporting, -1, info))
        except:
            Damnlog('Posting event failed - Window was closed?')
    def run(self):
        Damnlog('Bug reporter thread launched.')
        if not len(self.desc):
            Damnlog('Bug reporter not sending anything - bug description is empty.')
            self.postEvent(DV.l('Empty bug description field'), DV.l('You must enter a bug description.'), error=True, closedialog=False)
            return
        Damnlog('Ready to submit bug.')
        Damnlog('Initiating Google Code API object.')
        api = gdata.projecthosting.client.ProjectHostingClient()
        Damnlog('Logging in with damnvid-user@gmail.com credentials')
        try:
            api.client_login('damnvid.user@gmail.com', 'damnviduser', source='DamnVid ' + DV.version, service='code') # OMG! Raw password!
        except:
            Damnlog('Could not log in to Google Code (Invalid connection?)', traceback.format_exc())
            self.postEvent(DV.l('Error while connecting'), DV.l('Could not connect to Google Code. Please make sure that your Internet connection is active and that no firewall is blocking DamnVid.'), error=True, closedialog=False)
            return
        summary = u'Bug: ' + self.desc + u'\n\nSteps:\n' + self.steps + u'\n\n' + self.sysinfo + u'\n\n'
        if len(self.email):
            summary += u'Email: ' + self.email.replace(u'@', u' (at) ').replace(u'.', u' (dot) ').replace(u'+', u' (plus) ').replace(u'-', u' (minus) ') + u'\n\n'
        try:
            Damnlog('Starting log dump, flusing.')
            DV.log.flush()
            Damnlog('Flushed, dumping...')
            logdump = ''
            f = DamnOpenFile(DV.log_file, 'r')
            for i in f:
                logdump += i
            f.close()
            logdump = DamnUnicode(logdump.strip())
            Damnlog('Log dump done, uploading to pastebin.')
            http = DamnURLOpen(urllib2.Request('http://pastehtml.com/upload/create?input_type=txt&result=address', urllib.urlencode({'txt':logdump.encode('utf8')})))
            pasteurl = http.read(-1)
            http.close()
            Damnlog('Uploaded to', pasteurl)
            summary += u'damnvid.log: ' + DamnUnicode(pasteurl)
        except:
            summary += u'(Could not upload the contents of damnvid.log)'
            Damnlog('Impossible to send contents of damnvid.log!')
        Damnlog('Login successful, submitting issue...')
        try:
            api.add_issue('damnvid', self.desc.encode('utf8', 'ignore'), summary.encode('utf8', 'ignore'), 'windypower', status='New', labels=['Type-Defect', 'Priority-Medium'])
        except:
            Damnlog('Issue submission failed.', traceback.format_exc())
            self.postEvent(DV.l('Error while submitting issue'), DV.l('Could not submit bug report to Google Code. Please make sure that your Internet connection is active and that no firewall is blocking DamnVid.'), error=True, closedialog=False)
            return
        Damnlog('Issue submission successful.')
        self.postEvent(DV.l('Success'), DV.l('Bug report submitted successfully. Thanks!'), error=False, closedialog=True)
class DamnReportBug(wx.Dialog):
    def __init__(self, parent, id, main):
        Damnlog('Opening bug report form.')
        self.parent = main
        wx.Dialog.__init__(self, parent, id, DV.l('Report a bug'))
        Damnlog('Building UI of bug dialog.')
        topvbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topvbox)
        panel = wx.Panel(self, -1)
        panelvbox = wx.BoxSizer(wx.VERTICAL)
        topvbox.Add(panel, 1, wx.EXPAND)
        panel.SetSizer(panelvbox)
        panelvbox.Add((0, DV.border_padding))
        panelhbox = wx.BoxSizer(wx.HORIZONTAL)
        panelvbox.Add(panelhbox)
        panelvbox.Add((0, DV.border_padding))
        panelhbox.Add((DV.border_padding, 0))
        panelbox = wx.BoxSizer(wx.VERTICAL)
        panelhbox.Add(panelbox)
        panelhbox.Add((DV.border_padding, 0))
        formtitle = wx.StaticText(panel, -1, DV.l('Report a bug'))
        formtitle.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        panelbox.Add(formtitle)
        panelbox.Add(wx.StaticText(panel, -1, DV.l('Thanks for taking the time to report a bug.')))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('Please fill the form below to complete your bug report.')))
        panelbox.Add((0, DV.border_padding))
        panelbox.Add(wx.StaticLine(self, -1))
        panelbox.Add((0, DV.border_padding))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('Short description of the problem:')))
        self.description = wx.TextCtrl(panel, -1)
        panelbox.Add(self.description, 0, wx.EXPAND)
        panelbox.Add((0, 2 * DV.border_padding))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('What steps did you take for the problem to happen?')))
        self.steps = wx.TextCtrl(panel, -1, value='1. \n2. \n3. ', style=wx.TE_MULTILINE)
        panelbox.Add(self.steps, 0, wx.EXPAND)
        panelbox.Add(wx.StaticText(panel, -1, DV.l('(If you tried to download a video, please include its URL.)')))
        panelbox.Add((0, 2 * DV.border_padding))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('System information:')))
        sysinfo = DamnSysinfo()
        if sysinfo != u'System information collection failed.':
            sysinfo = u'-- Auto-collected system information --\n' + sysinfo + u'\n-- End of auto-collected system information --'
        self.sysinfo = wx.TextCtrl(panel, -1, value=sysinfo, style=wx.TE_MULTILINE)
        panelbox.Add(self.sysinfo, 0, wx.EXPAND)
        panelbox.Add((0, 2 * DV.border_padding))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('Email-address (Optional):')))
        self.email = wx.TextCtrl(panel, -1)
        panelbox.Add(self.email, 0, wx.EXPAND)
        panelbox.Add(wx.StaticText(panel, -1, DV.l('(You will be notified at this address when there is progress about this bug.)')))
        panelbox.Add((0, 2 * DV.border_padding))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('In addition to this information, DamnVid\'s log file will also be sent.')))
        panelbox.Add(wx.StaticText(panel, -1, DV.l('This file is located here: ') + DamnUnicode(DV.log_file)))
        panelbox.Add((0, 2 * DV.border_padding))
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        panelbox.Add(buttonsizer, 0, wx.ALIGN_RIGHT)
        self.loading = wx.animate.GIFAnimationCtrl(panel, -1, DV.images_path + 'bugreportload.gif')
        self.send = wx.Button(panel, -1, DV.l('Send'))
        self.Bind(wx.EVT_BUTTON, self.onSend, self.send)
        buttonsizer.Add(self.loading)
        buttonsizer.Add(self.send)
        self.loading.Hide()
        buttonsizer.Add((DV.border_padding, 0))
        closebutton = wx.Button(panel, -1, DV.l('Cancel'))
        self.Bind(wx.EVT_BUTTON, self.onCancel, closebutton)
        buttonsizer.Add(closebutton)
        self.Bind(DV.evt_bugreport, self.onReportUpdate)
        Damnlog('UI built, centering report bug dialog.')
        self.SetClientSize(panel.GetBestSize())
        self.Center()
        Damnlog('Report bug dialog ready to be shown.')
    def onCancel(self, event=None):
        self.Close(True)
    def onReportUpdate(self, event):
        info = event.GetInfo()
        Damnlog('Bug report update event fired with info:', info)
        self.send.Show()
        self.loading.Stop()
        self.loading.Hide()
        self.Layout()
        if info['error']:
            icon = wx.ICON_ERROR
        else:
            icon = wx.ICON_INFORMATION
        dlg = wx.MessageDialog(None, info['dialog'], info['title'], wx.OK | icon)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
        if info['closedialog']:
            Damnlog('Closing bug report dialog as requested by event,')
            self.onCancel()
    def onSend(self, event):
        Damnlog('Send bug report button clicked.')
        self.send.Hide()
        self.loading.Show()
        self.loading.Play()
        self.Layout()
        desc = DamnUnicode(self.description.GetValue())
        email = DamnUnicode(self.email.GetValue())
        sysinfo = DamnUnicode(self.sysinfo.GetValue())
        steps = DamnUnicode(self.steps.GetValue())
        Damnlog('Spawning DamnBugReporter with information: \n\tDescription: ' + desc + u'\n\tSystem info: ' + sysinfo + '\n\tSteps:\n' + steps + u'\n\tEmail: ', email)
        DamnBugReporter(desc, steps, sysinfo, email, parent=self).start()
        Damnlog('DamnBugReporter spawned and launched.')
def DamnOpenFileManager(directory, *args):
    if directory is not None:
        directory = DamnUnicode(directory)
    Damnlog('Opening default file manager at directory', directory)
    if DV.os == 'nt':
        DamnSpawner([u'explorer.exe', u'/e,', DamnUnicode(directory)])
    elif DV.os == 'mac':
        DamnSpawner([u'open', DamnUnicode(directory)])
    else:
        DamnSpawner([u'xdg-open', DamnUnicode(directory)])
def DamnLaunchFile(f, *args):
    f = DamnUnicode(f)
    if DV.os == 'nt':
        DamnSpawner([u'cmd', u'/c', u'start ' + DamnUnicode(win32api.GetShortPathName(f)).replace(u'"', u'\\"')])
    else:
        DamnOpenFileManager(f) # Hax! It works because 'open' or 'xdg-open' do not only open directories.
class DamnDoneDialog(wx.Dialog):
    def __init__(self, content, aborted=False, main=None):
        Damnlog('Done dialog opening with parameters content =', content, '; aborted?', aborted)
        dirs = []
        files = {}
        icons = {}
        for i in content:
            if i[1] not in dirs:
                dirs.append(i[1])
                files[i[1]] = []
            files[i[1]].append(i[0])
            icons[i[1] + i[0]] = i[2]
        dirs.sort()
        for i in dirs:
            files[i].sort()
        Damnlog('Done dialog parsed content; dirs =', dirs, '; files =', files)
        self.parent = main
        title = 'Processing done.'
        if aborted:
            title = 'Processing aborted.'
        wx.Dialog.__init__(self, None, -1, DV.l(title))
        absbox1 = wx.BoxSizer(wx.VERTICAL)
        absbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(absbox1)
        absbox1.Add((0, DV.border_padding))
        absbox1.Add(absbox2)
        absbox1.Add((0, DV.border_padding))
        topvbox = wx.BoxSizer(wx.VERTICAL)
        absbox2.Add((DV.border_padding, 0))
        absbox2.Add(topvbox)
        absbox2.Add((DV.border_padding, 0))
        panel = wx.Panel(self, -1)
        topvbox.Add(panel, 1, wx.EXPAND)
        mainvbox = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(mainvbox)
        self.underlined = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.underlined.SetUnderlined(True)
        # Build UI
        Damnlog('Building center UI of done dialog.')
        if aborted:
            title = wx.StaticText(panel, -1, DV.l('Video conversion aborted.'))
            title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        else:
            title = wx.StaticText(panel, -1, DV.l('Video conversion successful.'))
            title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        mainvbox.Add(title)
        mainvbox.Add((0, DV.border_padding * 2))
        if len(content):
            Damnlog('There is content, so we\'re gonna build tree.')
            mainvbox.Add(wx.StaticText(panel, -1, DV.l('The following videos have been processed:')))
            foldericon = wx.Bitmap(DV.images_path + 'foldermovie.png')
            for d in dirs:
                Damnlog('Building videos list for directory', d)
                tmpvbox = wx.BoxSizer(wx.VERTICAL)
                mainvbox.Add(tmpvbox)
                tmphbox = wx.BoxSizer(wx.HORIZONTAL)
                tmpvbox.Add(tmphbox)
                tmphbox.Add(self.bindAndCursor(wx.StaticBitmap(panel, -1, foldericon), launchdir=d), 0, wx.ALIGN_CENTER_VERTICAL)
                tmphbox.Add((DV.border_padding / 2, 0))
                tmphbox.Add(self.makeLabel(panel, d, launchdir=d))
                tmpinnerhbox = wx.BoxSizer(wx.HORIZONTAL)
                tmpvbox.Add(tmpinnerhbox)
                tmpinnerhbox.Add((foldericon.GetWidth() + DV.border_padding, 0))
                tmpinnervbox = wx.BoxSizer(wx.VERTICAL)
                tmpinnerhbox.Add(tmpinnervbox, 1)
                for f in files[d]:
                    tmphbox2 = wx.BoxSizer(wx.HORIZONTAL)
                    tmpinnervbox.Add(tmphbox2)
                    tmphbox2.Add(self.bindAndCursor(wx.StaticBitmap(panel, -1, DV.listicons.getRawBitmap(icons[d + f])), launchfile=d + f), 0, wx.ALIGN_CENTER_VERTICAL)
                    tmphbox2.Add((DV.border_padding / 2, 0))
                    tmphbox2.Add(self.makeLabel(panel, f, launchfile=d + f))
                mainvbox.Add((0, DV.border_padding))
        else:
            Damnlog('There\'s no content, so we\'re not gonna build much.')
            mainvbox.Add(wx.StaticText(panel, -1, DV.l('No videos were processed.')))
            mainvbox.Add((0, DV.border_padding))
        mainvbox.Add((0, DV.border_padding)) # Again!
        okhbox = wx.BoxSizer(wx.HORIZONTAL)
        mainvbox.Add(okhbox, 0, wx.ALIGN_RIGHT)
        okButton = wx.Button(panel, wx.ID_OK, DV.l('OK'))
        okhbox.Add(okButton)
        self.Bind(wx.EVT_BUTTON, self.onOK, okButton)
        Damnlog('Finished building done dialog UI, displaying it.')
        # Finished building UI
        self.SetClientSize(self.GetBestSize())
        self.Center()
        Damnlog('Done dialog displayed and centered.')
    def makeLabel(self, panel, text, launchdir=None, launchfile=None):
        Damnlog('Making label with text', text, 'launchdir =', launchdir, '; launchfile =', launchfile)
        label = wx.lib.stattext.GenStaticText(panel, -1, DamnUnicode(text))
        label.SetFont(self.underlined)
        return self.bindAndCursor(label, launchdir=launchdir, launchfile=launchfile)
    def bindAndCursor(self, element, launchdir=None, launchfile=None):
        Damnlog('Binding', element, 'to display hand cursor, and launchdir =', launchdir, '; launchfile =', launchfile)
        element.Bind(wx.EVT_ENTER_WINDOW, DamnCurry(self.handCursor, element))
        element.Bind(wx.EVT_LEAVE_WINDOW, DamnCurry(self.normalCursor, element))
        if launchfile is not None:
            element.Bind(wx.EVT_LEFT_UP, DamnCurry(DamnLaunchFile, launchfile))
        elif launchdir is not None:
            element.Bind(wx.EVT_LEFT_UP, DamnCurry(DamnOpenFileManager, launchdir))
        return element
    def handCursor(self, element, event):
        Damnlog('Displaying hand cursor due to event', event, 'over element', element)
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        element.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
    def normalCursor(self, element, event):
        Damnlog('Displaying normal cursor due to event', event, 'over element', element)
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        element.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
    def onOK(self, event):
        self.Close(True)
class DamnAboutDamnVid(wx.Dialog):
    def __init__(self, parent, id, main):
        self.parent = main
        wx.Dialog.__init__(self, parent, id, DV.l('About DamnVid ') + DV.version)
        absbox1 = wx.BoxSizer(wx.VERTICAL)
        absbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(absbox1)
        absbox1.Add((0, DV.border_padding))
        absbox1.Add(absbox2)
        absbox1.Add((0, DV.border_padding))
        topvbox = wx.BoxSizer(wx.VERTICAL)
        absbox2.Add((DV.border_padding, 0))
        absbox2.Add(topvbox)
        absbox2.Add((DV.border_padding, 0))
        panel = wx.Panel(self, -1)
        topvbox.Add(panel, 1, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(hbox)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(vbox1, 0, wx.EXPAND)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(vbox2, 1, wx.EXPAND)
        icon = wx.StaticBitmap(panel, -1, wx.Bitmap(DV.images_path + 'icon256.png'))
        icon.Bind(wx.EVT_LEFT_DCLICK, self.eEgg)
        vbox1.Add(icon, 1, wx.ALIGN_CENTER)
        title = wx.StaticText(panel, -1, DV.l('DamnVid ') + DV.version)
        title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox2.Add(title)
        vbox2.Add((0, DV.border_padding * 2))
        author = wx.StaticText(panel, -1, DV.l('By Etienne Perot'))
        author.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        vbox2.Add(author)
        vbox2.Add((0, DV.border_padding * 2))
        vbox2.Add(DamnHyperlink(panel, -1, DV.url, DV.url))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('Contributors:')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- Tatara (Linux compatibility/packaging)')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- Palmer (Graphics)')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- Benoit Philippe (Testing)')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('Special thanks to:')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- The FFmpeg team')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- Every stoat on the planet')))
        vbox2.Add(wx.StaticText(panel, -1, DV.l('- You!')))
        for l in DV.languages.iterkeys():
            if DV.lang == l and DV.languages[l].has_key('author'):
                vbox2.Add((0, DV.border_padding))
                vbox2.Add(wx.StaticText(panel, -1, DV.l('Translation:')))
                vbox2.Add(wx.StaticText(panel, -1, DamnUnicode(DV.languages[l]['author'])))
        vbox2.Add((0, DV.border_padding * 2))
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox2.Add(hbox2, 0, wx.ALIGN_RIGHT)
        okButton = wx.Button(panel, -1, DV.l('OK'))
        self.Bind(wx.EVT_BUTTON, self.onOK, okButton)
        hbox2.Add(okButton)
        self.SetClientSize(self.GetBestSize())
        self.Layout()
        self.Center()
    def eEgg(self, event):
        dlg = DamnEEgg(None, -1)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def onOK(self, event):
        self.Close(True)
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
class DamnSplashScreen(wx.SplashScreen):
    def __init__(self):
        wx.SplashScreen.__init__(self, wx.Bitmap(DV.images_path + 'splashscreen.png', wx.BITMAP_TYPE_PNG), wx.SPLASH_CENTRE_ON_SCREEN | wx.STAY_ON_TOP, 10000, None)
        self.fadeIn()
    def fadeIn(self):
        DamnFadeIn(self)
    def fadeOut(self, destroy=True):
        DamnFadeOut(self, destroy)
class DamnVidPrefs: # Preference manager (backend, not GUI)
    def __init__(self):
        self.conf = {}
        f = DamnOpenFile(DV.conf_file, 'r')
        self.ini = ConfigParser.SafeConfigParser()
        self.ini.readfp(f)
        f.close()
        self.profiles = 0
        for i in self.ini.sections():
            if i[0:16] == 'damnvid-profile-':
                self.profiles = self.profiles + 1
    def expandPath(self, value):
        value = REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/', value.replace(DV.sep, '/').replace('?DAMNVID_MY_VIDEOS?', DV.my_videos_path.replace(DV.sep, '/'))).replace('/', DV.sep)
        if value[-1:] != DV.sep:
            value += DV.sep
        return value
    def reducePath(self, value):
        value = REGEX_PATH_MULTI_SEPARATOR_CHECK.sub('/', value.replace(DV.sep, '/').replace(DV.my_videos_path.replace(DV.sep, '/'), '?DAMNVID_MY_VIDEOS?')).replace(DV.sep, '/')
        if value[-1:] != '/':
            value += '/'
        return value
    def gets(self, section, name):
        name = name.lower()
        shortsection = section
        if shortsection[0:16] == 'damnvid-profile-':
            shortsection = 'damnvid-profile'
        if self.ini.has_section(section):
            if self.ini.has_option(section, name):
                value = DamnUnicode(self.ini.get(section, name))
            elif DV.defaultprefs.has_key(shortsection + ':' + name):
                value = DamnUnicode(DV.defaultprefs[shortsection + ':' + name])
                self.sets(section, name, value)
            else:
                value = u''
            if shortsection + ':' + name in DV.path_prefs:
                value = DamnUnicode(self.expandPath(value))
            return value
        if DV.defaultprefs.has_key(section + ':' + name):
            value = DamnUnicode(DV.defaultprefs[section + ':' + name])
            self.ini.add_section(section)
            self.sets(section, name, value)
            return DamnUnicode(self.gets(section, name))
        print 'No such pref:', section + ':' + name
    def sets(self, section, name, value):
        name = name.lower()
        value = DamnUnicode(value)
        if self.ini.has_section(section):
            if section + ':' + name in DV.path_prefs:
                value = self.reducePath(value)
            return self.ini.set(section, name, value.encode('utf8'))
        else:
            print 'No such section:', section
    def rems(self, section, name=None):
        try:
            if name is None:
                self.ini.remove_section(section)
            else:
                self.ini.remove_option(section, name)
        except:
            print 'No such section/option'
    def lists(self, section):
        prefs = []
        if DV.preference_order.has_key(section):
            prefs.extend(DV.preference_order[section])
        if self.ini.has_section(section):
            for i in self.ini.options(section):
                if i not in prefs:
                    prefs.append(i)
        if len(prefs):
            return prefs
        print 'No such section.'
    def listsections(self):
        return self.ini.sections()
    def get(self, name):
        return self.gets('damnvid', name)
    def set(self, name, value):
        return self.sets('damnvid', name, value)
    def getp(self, profile, name):
        if int(profile) == -1:
            if name.lower() == 'name':
                return DV.l('(Do not encode)')
            if name.lower() == 'outdir':
                return self.get('defaultoutdir')
        return self.gets('damnvid-profile-' + str(profile), name)
    def setp(self, profile, name, value):
        return self.sets('damnvid-profile-' + str(profile), name, value)
    def listp(self, profile):
        return self.lists('damnvid-profile-' + str(profile))
    def getm(self, module, name):
        return self.gets('damnvid-module-' + module, name)
    def setm(self, module, name, value):
        return self.sets('damnvid-module-' + module, name, value)
    def addp(self):
        self.ini.add_section('damnvid-profile-' + str(self.profiles))
        for i in DV.defaultprefs.iterkeys():
            if i[0:16] == 'damnvid-profile:':
                self.setp(self.profiles, i[16:], DamnUnicode(DV.defaultprefs[i]))
        self.profiles += 1
    def remp(self, profile):
        if self.profiles > 1:
            for i in DV.preferences.iterkeys():
                section, option = (i[0:i.find(':')], i[i.find(':') + 1:])
                if DV.preferences[i]['kind'] == 'profile':
                    if int(self.gets(section, option)) == int(profile):
                        self.ini.set(section, option, '0') # Fall back to default profile
                    elif int(self.gets(section, option)) > int(profile):
                        self.ini.set(section, option, str(int(self.gets(section, option)) - 1))
            for i in DamnIterModules():
                for j in DV.modules[i]['preferences'].iterkeys():
                    if DV.modules[i]['preferences'][j]['kind'] == 'profile':
                        if int(self.getm(DV.modules[i]['name'], j)) == int(profile):
                            self.setm(DV.modules[i]['name'], j, '0') # Fall back to default profile
                        elif int(self.getm(DV.modules[i]['name'], j)) > int(profile):
                            self.setm(DV.modules[i]['name'], j, str(int(self.getm(DV.modules[i]['name'], j)) - 1))
            for i in range(profile, self.profiles - 1):
                for j in self.ini.options('damnvid-profile-' + str(i)):
                    self.ini.remove_option('damnvid-profile-' + str(i), j)
                for j in self.ini.options('damnvid-profile-' + str(i + 1)):
                    self.ini.set('damnvid-profile-' + str(i), j, self.ini.get('damnvid-profile-' + str(i + 1), j))
            self.profiles -= 1
            self.ini.remove_section('damnvid-profile-' + str(self.profiles))
            return self.profiles
        return None
    def geta(self, section, name):
        array = eval(base64.b64decode(self.gets(section, name)))
        unicodearray = []
        for i in array:
            unicodearray.append(DamnUnicode(i))
        return unicodearray
    def seta(self, section, name, value):
        return self.sets(section, name, base64.b64encode(DamnUnicode(value)))
    def save(self):
        f = DamnOpenFile(DV.conf_file, 'w')
        self.ini.write(f)
        f.close()
        DamnURLOpener()
class DamnBrowseDirButton(wx.Button): # "Browse..." button for directories
    def __init__(self, parent, id, label, control, title, callback):
        self.filefield = control
        self.title = title
        self.callback = callback
        wx.Button.__init__(self, parent, id, label)
    def onBrowse(self, event):
        dlg = wx.DirDialog(self, self.title, self.filefield.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        dlg.SetIcon(DV.icon)
        path = None
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.filefield.SetValue(path)
        dlg.Destroy()
        if path != None:
            self.callback(self, path)
class DamnYouTubeService(thr.Thread):
    def __init__(self, parent, query=None):
        self.parent = parent
        thr.Thread.__init__(self)
        if query is None:
            self.queries = None
        else:
            self.queries = [query]
    def query(self, query):
        if self.queries is None:
            self.queries = [query]
        else:
            self.queries.append(query)
    def stillAlive(self):
        return True
    def postEvent(self, info):
        info['self'] = self
        try:
            wx.PostEvent(self.parent, DamnLoadingEvent(DV.evt_loading, -1, info))
        except:
            pass # Window might have been closed
    def returnResult(self, result, index=0):
        return self.postEvent({'index':index, 'query':self.queries[index], 'result':result})
    def getTempFile(self):
        name = DV.tmp_path + str(random.random()) + '.tmp'
        while os.path.exists(name):
            name = DV.tmp_path + str(random.random()) + '.tmp'
        return name
    def run(self):
        while self.queries is None:
            time.sleep(.025)
        try:
            self.parent.loadlevel += 1
        except:
            pass # Window might have been closed
        while len(self.queries):
            query = self.queries[0]
            if query[0] == 'feed':
                self.returnResult(DV.youtube_service.GetYouTubeVideoFeed(query[1]))
            elif query[0] == 'image':
                http = DamnURLOpen(query[1])
                tmpf = self.getTempFile()
                tmpfstream = DamnOpenFile(tmpf, 'wb')
                for i in http.readlines():
                    tmpfstream.write(i)
                http.close()
                tmpfstream.close()
                self.returnResult(tmpf)
            self.queries.pop(0)
            if not len(self.queries):
                time.sleep(.5) # Hang around for a moment, wait for work
        self.postEvent({'query':('done',)})
        try:
            self.parent.loadlevel -= 1
        except:
            pass # Window might have been closed
class DamnVidBrowser(wx.Dialog):
    def __init__(self, parent):
        Damnlog('Opening new YouTube browser dialog.')
        self.parent = parent
        wx.Dialog.__init__(self, parent, -1, DV.l('Search for videos...'))
        topsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(topsizer)
        self.toppanel = wx.Panel(self, -1)
        topsizer.Add(self.toppanel, 1, wx.EXPAND)
        topvbox = wx.BoxSizer(wx.VERTICAL)
        tophbox = wx.BoxSizer(wx.HORIZONTAL)
        self.toppanel.SetSizer(tophbox)
        tophbox.Add((DV.border_padding, 0))
        tophbox.Add(topvbox, 1, wx.EXPAND)
        tophbox.Add((DV.border_padding, 0))
        topvbox.Add((0, DV.border_padding))
        searchhbox = wx.BoxSizer(wx.HORIZONTAL)
        topvbox.Add(searchhbox, 0, wx.EXPAND)
        searchhbox.Add(wx.StaticText(self.toppanel, -1, DV.l('Search:')), 0, wx.ALIGN_CENTER_VERTICAL)
        searchhbox.Add((DV.control_hgap, 0))
        self.standardchoices = {
            'most_popular':DV.l('Most popular'),
            'most_viewed':DV.l('Most viewed'),
            'top_rated':DV.l('Top rated'),
            'recently_featured':DV.l('Recently featured'),
            'most_recent':DV.l('Most recent'),
            'most_discussed':DV.l('Most discussed'),
            'top_favorites':DV.l('Top favorites'),
            'most_linked':DV.l('Most linked'),
            'most_responded':DV.l('Most responded')
        }
        self.searchbox = wx.SearchCtrl(self.toppanel, -1, '', style=wx.TE_PROCESS_ENTER)
        self.searchbox.SetSearchMenuBitmap(wx.Bitmap(DV.images_path + 'searchctrl.png'))
        self.searchbox.Bind(wx.EVT_TEXT_ENTER, self.search)
        searchhbox.Add(self.searchbox, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        self.searchbutton = wx.animate.GIFAnimationCtrl(self.toppanel, -1, DV.images_path + 'search.gif')
        self.searchbutton.Bind(wx.EVT_LEFT_DOWN, self.search)
        searchhbox.Add((DV.control_hgap, 0))
        searchhbox.Add(self.searchbutton, 0, wx.ALIGN_CENTER_VERTICAL)
        self.scrollpanel = wx.ScrolledWindow(self.toppanel, -1, size=(360, 270 + 3 * DV.control_vgap))
        self.scrollpanel.SetMinSize((360, 270 + 3 * DV.control_vgap))
        self.scrollpanel.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
        scrollpanelsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.scrollpanel.SetSizer(scrollpanelsizer)
        self.resultpanel = wx.Panel(self.scrollpanel, -1)
        scrollpanelsizer.Add(self.resultpanel, 1, wx.EXPAND)
        self.resultsizer = wx.BoxSizer(wx.VERTICAL)
        self.resultpanel.SetSizer(self.resultsizer)
        topvbox.Add((0, DV.control_vgap))
        topvbox.Add(self.scrollpanel, 1, wx.EXPAND)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(DV.evt_load, self.onLoad)
        self.buildSearchbox()
        self.loadlevel = 0
        self.results = []
        self.displayedurls = []
        self.resultctrls = []
        self.service = None
        self.scrollpanel.Hide()
        self.waitingpanel = wx.Panel(self.toppanel, -1, size=(360, 270 + 3 * DV.control_vgap))
        waitingsizer = wx.BoxSizer(wx.VERTICAL)
        self.waitingpanel.SetSizer(waitingsizer)
        waitingsizer.Add((0, int(DV.control_vgap * 1.5)))
        waitingsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        waitingsizer.Add(waitingsizer2)
        waitingsizer2.Add((DV.control_hgap, 0))
        topvbox.Add(self.waitingpanel)
        self.searchingimg = wx.StaticBitmap(self.waitingpanel, -1, wx.Bitmap(DV.images_path + 'searchpanel.png'))
        waitingsizer2.Add(self.searchingimg)
        Damnlog('YouTube browser dialog has been built. Populating.')
        defaultsearch = DV.prefs.gets('damnvid-search', 'default_search')
        if defaultsearch and DV.prefs.gets('damnvid-search', 'doinitialsearch') == 'True':
            self.search(search=defaultsearch)
        else:
            pass
        topvbox.Add((0, DV.control_vgap))
        self.downloadAll = wx.Button(self.toppanel, -1, DV.l('Download all'))
        self.downloadAll.Bind(wx.EVT_BUTTON, self.onDownloadAll)
        topvbox.Add(self.downloadAll, 0, wx.ALIGN_RIGHT)
        topvbox.Add((0, DV.border_padding))
        self.SetClientSize(self.GetBestSize())
        self.Center()
        Damnlog('YouTube browser dialog init complete.')
    def cleanString(self, s):
        return DamnHtmlEntities(s)
    def getService(self):
        if self.service is None:
            self.service = DamnYouTubeService(self)
            self.service.start()
        else:
            try:
                if self.service.stillAlive():
                    return self.service
            except:
                self.service = None
                return self.getService()
        return self.service
    def search(self, event=None, search=u''):
        Damnlog('YouTube browser is now searching for', search, 'from event', event)
        self.scrollpanel.Hide()
        self.waitingpanel.Show()
        self.toppanel.Layout()
        if not search:
            search = self.searchbox.GetValue()
        if not search:
            return
        search=DamnUnicode(search)
        self.searchbutton.LoadFile(DV.images_path + 'searching.gif')
        self.searchbutton.Play()
        Damnlog('YouTube browser interface updated and ready for search, resolving API query.')
        prefix = 'http://gdata.youtube.com/feeds/api/videos?racy=include&orderby=viewCount&vq='
        isstandard = False
        for i in self.standardchoices.keys():
            if DV.l(self.standardchoices[i], warn=False) == search:
                isstandard = True
                search = i
        if search in self.standardchoices.keys():
            Damnlog('Query is a standard choice:', search)
            prefix = 'http://gdata.youtube.com/feeds/api/standardfeeds/'
            searchlabel = self.standardchoices[search]
        else:
            Damnlog('Query is not a standard choice. Updating query history.')
            history = DV.prefs.geta('damnvid-search', 'history')
            if search not in history:
                history.append(search)
                while len(history) > int(DV.prefs.gets('damnvid-search', 'history_length')):
                    history.pop(0)
            DV.prefs.seta('damnvid-search', 'history', history)
            searchlabel = search
        self.searchbox.SetValue(searchlabel)
        Damnlog('Youtube browser API prefix is', prefix)
        self.buildSearchbox()
        Damnlog('YouTube browser search box populating complete, beginning actual search for', search,'at URL:',prefix + urllib2.quote(search))
        self.getService().query(('feed', prefix + urllib2.quote(search)))
        Damnlog('YouTube browser search results for', search, 'are in, destroying interface.')
        for i in self.resultctrls:
            i.Destroy()
        self.resultctrls = []
        self.scrollpanel.AdjustScrollbars()
        self.resultsizer.Clear(True)
        self.displayedurls = []
    def onLoad(self, event):
        info = event.GetInfo()
        Damnlog('onLoad event on YouTube browser. Event data:', info)
        if info['query'][0] == 'feed':
            results = info['result']
            boldfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            boldfont.SetWeight(wx.FONTWEIGHT_BOLD)
            tmpscrollbar = wx.ScrollBar(self.resultpanel, -1, style=wx.SB_VERTICAL)
            panelwidth = self.scrollpanel.GetSizeTuple()[0] - tmpscrollbar.GetSizeTuple()[0]
            tmpscrollbar.Destroy()
            del tmpscrollbar
            self.resultpanel.DestroyChildren()
            self.resultpanel.Layout()
            for i in range(len(results.entry)):
                tmpvbox = wx.BoxSizer(wx.VERTICAL)
                tmpsizer = wx.BoxSizer(wx.HORIZONTAL)
                tmpvbox.Add((0, DV.border_padding))
                tmpvbox.Add(tmpsizer)
                tmppanel = wx.Panel(self.resultpanel, -1, style=wx.SIMPLE_BORDER)
                self.resultctrls.append(tmppanel)
                tmppanel.SetBackgroundColour(wx.WHITE)
                tmppanel.SetMinSize((panelwidth, -1))
                self.resultsizer.Add(tmppanel)
                tmppanel.SetSizer(tmpvbox)
                tmpsizer.Add((DV.border_padding, 0))
                thumb = wx.animate.GIFAnimationCtrl(tmppanel, -1, DV.images_path + 'thumbnail.gif')
                self.getService().query(('image', results.entry[i].media.thumbnail[0].url, thumb))
                tmpsizer.Add(thumb)
                thumb.Play()
                tmpsizer.Add((DV.control_hgap, 0))
                infobox = wx.BoxSizer(wx.VERTICAL)
                tmpsizer.Add(infobox, 1, wx.EXPAND)
                title = DamnHyperlink(tmppanel, -1, self.cleanString(results.entry[i].media.title.text), self.cleanString(results.entry[i].media.player.url), wx.WHITE)
                infobox.Add(title)
                #infobox.Add((0,DV.control_vgap))
                desc = self.makeDescPanel(results.entry[i].media.description.text, tmppanel, panelwidth - 2 * DV.border_padding)
                tmpvbox.Add(desc, 0, wx.EXPAND)
                desc.Hide()
                videoinfo = wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(videoinfo)
                #infobox.Add((0,DV.control_vgap))
                tmplabel = wx.StaticText(tmppanel, -1, results.entry[i].media.category[0].text)
                tmplabel.SetFont(boldfont)
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel = wx.StaticText(tmppanel, -1, ', ')
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel = wx.StaticText(tmppanel, -1, self.sec2time(results.entry[i].media.duration.seconds))
                tmplabel.SetFont(boldfont)
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                tmplabel = wx.StaticText(tmppanel, -1, '.')
                tmplabel.SetForegroundColour(wx.BLACK)
                videoinfo.Add(tmplabel)
                statistics = wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(statistics)
                infobox.Add((0, DV.control_vgap))
                statistics2 = wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(statistics2)
                try:
                    viewcount = wx.StaticText(tmppanel, -1, self.numFormat(results.entry[i].statistics.view_count))
                except:
                    viewcount = wx.StaticText(tmppanel, -1, self.numFormat(0))
                viewcount.SetFont(boldfont)
                viewcount.SetForegroundColour(wx.BLACK)
                statistics.Add(viewcount)
                tmplabel = wx.StaticText(tmppanel, -1, DV.l(' views.'))
                tmplabel.SetForegroundColour(wx.BLACK)
                statistics.Add(tmplabel)
                tmplabel = wx.StaticText(tmppanel, -1, DV.l('Rating: '))
                tmplabel.SetForegroundColour(wx.BLACK)
                statistics2.Add(tmplabel, 0, wx.ALIGN_CENTER_VERTICAL)
                if results.entry[i].rating is None:
                    tmplabel = wx.StaticText(tmppanel, -1, DV.l('(None)'))
                    tmplabel.SetForegroundColour(wx.BLACK)
                    statistics2.Add(tmplabel, 0, wx.ALIGN_CENTER_VERTICAL)
                else:
                    statistics2.Add(wx.StaticBitmap(tmppanel, -1, wx.Bitmap(DV.images_path + 'stars_' + str(int(round(float(results.entry[i].rating.average), 0))) + '.png')), 0, wx.ALIGN_CENTER_VERTICAL)
                infobox.Add((0, DV.control_vgap))
                buttonrow = wx.BoxSizer(wx.HORIZONTAL)
                infobox.Add(buttonrow)
                btnDesc = wx.Button(tmppanel, -1, DV.l('Description'))
                buttonrow.Add(btnDesc)
                buttonrow.Add((DV.control_hgap, 0))
                btnDesc.Bind(wx.EVT_BUTTON, DamnCurry(self.onDescButton, desc, tmppanel))
                btnDownload = wx.Button(tmppanel, -1, DV.l('Download'))
                btnDownload.Bind(wx.EVT_BUTTON, DamnCurry(self.onDownload, results.entry[i].media.player.url))
                self.displayedurls.append(results.entry[i].media.player.url)
                buttonrow.Add(btnDownload)
                tmpsizer.Add((DV.border_padding, 0))
                tmpvbox.Add((0, DV.border_padding))
                if i + 1 != len(results.entry):
                    self.resultsizer.Add((0, DV.control_vgap))
                    self.resultsizer.Add(wx.StaticLine(tmppanel, -1), 0, wx.EXPAND)
                    self.resultsizer.Add((0, DV.control_vgap))
            self.waitingpanel.Hide()
            self.scrollpanel.Show()
            self.resultpanel.Fit()
            self.scrollpanel.AdjustScrollbars()
            self.resultpanel.Layout()
            self.toppanel.Layout()
        elif info['query'][0] == 'image':
            try:
                ctrl = info['query'][2]
                ctrl.Stop()
                ctrl.SetInactiveBitmap(wx.Bitmap(info['result']))
            except:
                pass
            try:
                os.remove(info['result'])
            except:
                pass
        elif info['query'][0] == 'done':
            try:
                self.service = None
                self.searchbutton.Stop()
                self.searchbutton.LoadFile(DV.images_path + 'search.gif')
            except:
                pass
    def buildSearchbox(self):
        Damnlog('Building search box on YouTube browser dialog.')
        val = self.searchbox.GetValue().strip().lower()
        Damnlog('Clean search box value is', val, '; Destroying boxmenu.')
        boxmenu = wx.Menu('')
        history = DV.prefs.geta('damnvid-search', 'history')
        Damnlog('Rebuilding history menu. History data:', history)
        if len(history):
            history.reverse() # Recent entries appear on top
            for i in history:
                item = wx.MenuItem(boxmenu, -1, i, kind=wx.ITEM_RADIO)
                boxmenu.AppendItem(item) # Once again, item has to be appended before being checked
                item.Check(i.lower() == val)
                boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
                self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
            item = wx.MenuItem(boxmenu, -1, DV.l('(Clear search history)'), kind=wx.ITEM_RADIO) # Ironic, but necessary to put this one as a radio, otherwise wx guesses that the menu is actually two separated radio menus
            boxmenu.AppendItem(item)
            boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, None), item)
            self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, None), item)
        Damnlog('History menu rebuilt, will now add standard choices.')
        for i in self.standardchoices.iterkeys():
            item = wx.MenuItem(boxmenu, -1, self.standardchoices[i], kind=wx.ITEM_RADIO)
            boxmenu.AppendItem(item)
            item.Check(i == val or self.standardchoices[i].lower() == val)
            boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
            self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
        Damnlog('History menu built, assigning it to search box.')
        self.searchbox.SetMenu(boxmenu)
    def onSearchMenu(self, query, event):
        Damnlog('YouTube browser dialog received onSearchmenu event. Query is', query)
        if query is None: # Clear history
            DV.prefs.seta('damnvid-search', 'history', [])
            DV.prefs.save()
            Damnlog('Query is none, deleted history, rebuilding search box.')
            self.buildSearchbox()
        else:
            self.searchbox.SetValue(query)
            Damnlog('Query is not none, set searchbox value, starting search.')
            self.search()
    def makeDescPanel(self, desc, parent, width):
        desc = self.cleanString(desc)
        panel = wx.Panel(parent, -1)
        panel.SetBackgroundColour(wx.WHITE)
        wrapper = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, DV.control_vgap))
        wrapper.Add((DV.border_padding, 0))
        wrapper.Add(sizer)
        wrapper.Add((DV.border_padding, 0))
        panel.SetSizer(wrapper)
        descfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        descfont.SetWeight(wx.FONTWEIGHT_BOLD)
        txt = wx.StaticText(panel, -1, DV.l('Description:'))
        txt.SetFont(descfont)
        txt.SetForegroundColour(wx.BLACK)
        sizer.Add(txt)
        descs = []
        lastindex = 0
        urls = []
        curmatch = 1
        for link in REGEX_HTTP_GENERIC_LOOSE.finditer(desc):
            before = desc[lastindex:link.start()].strip()
            if before:
                descs.extend((before, link.group()))
            else:
                descs.append(link.group())
                curmatch -= 1
            urls.append(curmatch)
            lastindex = link.end()
            curmatch += 2
        if not len(descs):
            descs = [desc]
        for i in range(len(descs)):
            if i in urls:
                link = DamnHyperlink(panel, -1, descs[i], descs[i], wx.WHITE)
                sizer.Add(link)
            else:
                txt = wx.StaticText(panel, -1, descs[i])
                txt.SetForegroundColour(wx.BLACK)
                txt.Wrap(width)
                sizer.Add(txt)
        return panel
    def sec2time(self, sec):
        t = (0, 0, int(sec))
        t = (t[0], (t[2] - t[2] % 60) / 60, t[2] % 60)
        t = (str((t[1] - t[1] % 60) / 60), str(t[1] % 60), str(t[2]))
        if t[0] == '0':
            return t[1] + ':' + self.numFormat(t[2], True)
        return t[0] + ':' + self.numFormat(t[1], True) + ':' + self.numFormat(t[2], True)
    def numFormat(self, num, doublezero=False):
        num = REGEX_THOUSAND_SEPARATORS.sub(',', str(num))
        if doublezero and len(num) == 1:
            num = '0' + num
        return num
    def onDownload(self, url, event):
        self.parent.addVid([url], DV.prefs.get('autoconvert') == 'True')
    def onDownloadAll(self, event):
        self.parent.addVid(self.displayedurls, DV.prefs.get('autoconvert') == 'True')
    def onDescButton(self, ctrl, panel, event):
        position = self.scrollpanel.GetViewStart()
        ctrl.Show(not ctrl.IsShown())
        panel.Fit()
        panel.Layout()
        self.resultpanel.Fit()
        self.scrollpanel.AdjustScrollbars()
        self.scrollpanel.Scroll(position[0], position[1])
    def onClose(self, event=None):
        self.parent.searchopen = False
        DV.prefs.save() # Saves search history
        self.Destroy()
class DamnVidPrefEditor(wx.Dialog): # Preference dialog (not manager)
    def __init__(self, parent, id, title, main):
        # Dialog init
        wx.Dialog.__init__(self, parent, id, title)
        self.parent = main
        DV.prefs.save() # Save just in case, we're gonna modify stuff!
        self.toppanel = wx.Panel(self, -1)
        self.bestsize = [0, 0]
        self.defaultvalue = DV.l('(default)')
        # Top part of the toppanel
        self.topsizer = wx.BoxSizer(wx.VERTICAL)
        self.topsizer.Add((0, DV.border_padding))
        self.uppersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.uppersizer.Add((DV.border_padding, 0))
        self.topsizer.Add(self.uppersizer, 1, wx.EXPAND)
        # -> Left part of the upperpanel
        self.upperleftpanel = wx.Panel(self.toppanel, -1)
        self.uppersizer.Add(self.upperleftpanel, 0)
        self.uppersizer.Add((DV.control_hgap, 0))
        self.upperleftsizer = wx.BoxSizer(wx.VERTICAL)
        self.tree = wx.TreeCtrl(self.upperleftpanel, -1, size=(260, 280), style=wx.TR_LINES_AT_ROOT | wx.TR_HAS_BUTTONS | wx.TR_FULL_ROW_HIGHLIGHT)
        self.upperleftsizer.Add(self.tree, 1, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.control_vgap))
        self.buildTree()
        self.addProfileButton = wx.Button(self.upperleftpanel, -1, DV.l('Add profile'))
        self.upperleftsizer.Add(self.addProfileButton, 0, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.control_vgap))
        self.deleteProfileButton = wx.Button(self.upperleftpanel, -1, DV.l('Delete profile'))
        self.upperleftsizer.Add(self.deleteProfileButton, 0, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.control_vgap))
        self.importButton = wx.Button(self.upperleftpanel, -1, DV.l('Import preferences'))
        self.upperleftsizer.Add(self.importButton, 0, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.control_vgap))
        self.exportButton = wx.Button(self.upperleftpanel, -1, DV.l('Export preferences'))
        self.upperleftsizer.Add(self.exportButton, 0, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.control_vgap))
        self.resetButton = wx.Button(self.upperleftpanel, -1, DV.l('Reset all'))
        self.upperleftsizer.Add(self.resetButton, 0, wx.EXPAND)
        self.upperleftsizer.Add((0, DV.border_padding))
        self.upperleftpanel.SetSizer(self.upperleftsizer)
        # -> Right part of the upperpanel
        self.upperrightpanel = wx.Panel(self.toppanel, -1)
        self.uppersizer.Add(self.upperrightpanel, 1, wx.EXPAND)
        self.prefpanelabel = wx.StaticBox(self.upperrightpanel, -1, '')
        self.upperrightsizer = wx.StaticBoxSizer(self.prefpanelabel, wx.VERTICAL)
        # -> -> Preference pane creation
        self.prefpane = wx.Panel(self.upperrightpanel, -1)
        self.prefpanesizer = wx.GridBagSizer(DV.control_vgap, DV.control_hgap) # Yes, it's vgap then hgap
        self.prefpane.SetSizer(self.prefpanesizer)
        # -> -> End preference pane creation
        self.upperrightsizer.Add(self.prefpane, 1, wx.EXPAND)
        self.uppersizer.Add((DV.border_padding, 0))
        self.upperrightpanel.SetSizer(self.upperrightsizer)
        self.topsizer.Add((0, DV.control_vgap))
        # Bottom part of the toppanel
        self.lowersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.topsizer.Add(self.lowersizer, 0, wx.EXPAND)
        self.lowersizer.AddStretchSpacer(1)
        self.okButton = wx.Button(self.toppanel, wx.ID_OK, DV.l('OK'))
        self.lowersizer.Add(self.okButton, 0, wx.ALIGN_RIGHT)
        self.lowersizer.Add((DV.control_hgap, 0))
        self.closeButton = wx.Button(self.toppanel, wx.ID_CLOSE, DV.l('Cancel'))
        self.lowersizer.Add(self.closeButton, 0, wx.ALIGN_RIGHT)
        self.lowersizer.Add((DV.border_padding, 0))
        self.topsizer.Add((0, DV.border_padding))
        # Final touches, binds, etc.
        self.toppanel.SetSizer(self.topsizer)
        self.Bind(wx.EVT_BUTTON, self.onAddProfile, self.addProfileButton)
        self.Bind(wx.EVT_BUTTON, self.onDeleteProfile, self.deleteProfileButton)
        self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.onImport, self.importButton)
        self.Bind(wx.EVT_BUTTON, self.onExport, self.exportButton)
        self.Bind(wx.EVT_BUTTON, self.onReset, self.resetButton)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChanged, self.tree)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown, self.toppanel)
        self.Bind(DV.evt_load, self.onLoad)
        self.toppanel.SetFocus()
        self.forceSelect(self.treeroot) # Will also resize the window on certain platforms since it fires the selection events, but not on Linux it seems, so...
        self.updatePrefPane('damnvid')
        self.Center()
    def buildTree(self):
        self.tree.DeleteAllItems()
        self.treeimages = wx.ImageList(16, 16, True)
        self.tree.AssignImageList(self.treeimages)
        self.treeroot = self.tree.AddRoot(DV.l('DamnVid Preferences'))
        self.tree.SetItemImage(self.treeroot, self.treeimages.Add(wx.Bitmap(DV.images_path + 'icon16.png')))
        self.proxyprefs = self.tree.AppendItem(self.treeroot, DV.l('Proxy'))
        self.tree.SetItemImage(self.proxyprefs, self.treeimages.Add(wx.Bitmap(DV.images_path + 'web-16.png')))
        self.searchprefs = self.tree.AppendItem(self.treeroot, DV.l('YouTube browser'))
        self.tree.SetItemImage(self.searchprefs, self.treeimages.Add(wx.Bitmap(DV.images_path + 'youtubebrowser.png')))
        self.modulelistitem = self.tree.AppendItem(self.treeroot, DV.l('Modules'))
        self.tree.SetItemImage(self.modulelistitem, self.treeimages.Add(wx.Bitmap(DV.images_path + 'modules.png')))
        self.modules = {}
        self.moduledescs = {}
        for i in DamnIterModules():
            self.modules[i] = self.tree.AppendItem(self.modulelistitem, DV.modules[i]['title'])
            self.tree.SetItemImage(self.modules[i], self.treeimages.Add(wx.Bitmap(DV.modules_path + DV.modules[i]['name'] + DV.sep + DV.modules[i]['icon']['small'])))
        self.profileroot = self.tree.AppendItem(self.treeroot, DV.l('Encoding profiles'))
        self.tree.SetItemImage(self.profileroot, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profiles.png')))
        self.profiles = []
        for i in range(DV.prefs.profiles):
            treeitem = self.tree.AppendItem(self.profileroot, DV.prefs.getp(i, 'name'))
            self.profiles.append(treeitem)
            self.tree.SetItemImage(treeitem, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profile.png')))
        self.tree.ExpandAll()
        self.forceSelect(self.treeroot)
    def forceSelect(self, item, event=None):
        self.tree.SelectItem(item, True)
    def onTreeSelectionChanged(self, event):
        item = event.GetItem()
        self.prefpanelabel.SetLabel(self.tree.GetItemText(item))
        if item == self.treeroot:
            self.updatePrefPane('damnvid')
        elif item == self.searchprefs:
            self.updatePrefPane('damnvid-search')
        elif item == self.proxyprefs:
            self.updatePrefPane('damnvid-proxy')
        elif item == self.modulelistitem:
            self.updatePrefPane('special:modules')
        elif item == self.profileroot:
            self.updatePrefPane('special:profileroot')
        elif item in self.profiles:
            self.updatePrefPane('damnvid-profile-' + str(self.profiles.index(item)))
        elif item in self.modules.values():
            for i in DamnIterModules():
                if self.modules[i] == item:
                    self.updatePrefPane('damnvid-module-' + i)
                    break
        else:
            self.updatePrefPane('special:error')
    def getLabel(self, panel, label, color='#000000', bold=False, hyperlink=None, background=None):
        if hyperlink is None:
            lbl = wx.StaticText(panel, -1, label)
        else:
            lbl = DamnHyperlink(panel, -1, label, hyperlink)
        lbl.SetBackgroundColour(wx.WHITE)
        if bold:
            sysfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            boldfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), wx.FONTWEIGHT_BOLD)
            lbl.SetFont(boldfont)
        if hyperlink is None and color is not None:
            lbl.SetForegroundColour(color)
        return lbl
    def buildModulePanel(self, parent, module, extended=False, buttons=True, withscrollbars=False):
        mod = DV.modules[module]
        tmppanel = wx.Panel(parent, -1, style=wx.SIMPLE_BORDER)
        tmppanel.SetBackgroundColour(wx.WHITE)
        panelwidth = parent.GetSizeTuple()[0]
        if withscrollbars:
            tmpscroll = wx.ScrollBar(tmppanel, -1, style=wx.SB_VERTICAL)
            panelwidth -= tmpscroll.GetSizeTuple()[0]
            tmpscroll.Destroy()
            del tmpscroll
        tmptop3sizer = wx.BoxSizer(wx.VERTICAL)
        tmppanel.SetSizer(tmptop3sizer)
        tmptop3sizer.Add((0, DV.border_padding))
        tmptop2sizer = wx.BoxSizer(wx.HORIZONTAL)
        tmptop3sizer.Add(tmptop2sizer, 1, wx.EXPAND)
        tmptop3sizer.Add((0, DV.border_padding))
        tmptop2sizer.Add((DV.border_padding, 0))
        tmptopsizer = wx.BoxSizer(wx.VERTICAL)
        tmptop2sizer.Add(tmptopsizer, 1, wx.EXPAND)
        tmptop2sizer.Add((DV.border_padding, 0))
        # Construct top row of the module item
        tehrow = wx.BoxSizer(wx.HORIZONTAL)
        tmptopsizer.Add(tehrow, 1, wx.EXPAND)
        tehrow.Add(wx.StaticBitmap(tmppanel, -1, wx.Bitmap(DV.modules_path + module + DV.sep + mod['icon']['large'])))
        tehrow.Add((DV.control_hgap, 0))
        rightcol = wx.BoxSizer(wx.VERTICAL)
        tehrow.Add(rightcol, 1, wx.EXPAND)
        toprow = wx.BoxSizer(wx.HORIZONTAL)
        rightcol.Add(toprow)
        if mod['about'].has_key('url'):
            toprow.Add(self.getLabel(tmppanel, mod['title'], hyperlink=mod['about']['url'], bold=True))
        else:
            toprow.Add(self.getLabel(tmppanel, mod['title'], bold=True))
        toprow.Add(self.getLabel(tmppanel, DV.l(' (version ')))
        toprow.Add(self.getLabel(tmppanel, mod['version'], bold=True))
        toprow.Add(self.getLabel(tmppanel, ')'))
        toprow.Add(self.getLabel(tmppanel, DV.l(' by '), color='#707070'))
        if mod['author'].has_key('url'):
            toprow.Add(self.getLabel(tmppanel, mod['author']['name'], hyperlink=mod['author']['url'], bold=True))
        else:
            toprow.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True))
        toprow.Add(self.getLabel(tmppanel, '.'))
        descwidth = parent.GetSizeTuple()[0] - 2 * DV.border_padding - 72 - DV.control_hgap
        if extended:
            rightcol.Add(self.getLabel(tmppanel, DV.l('Author:'), bold=True))
            authorsizer = wx.BoxSizer(wx.HORIZONTAL)
            rightcol.Add(authorsizer)
            authorsizer.Add((DV.control_hgap * 2, 0)) # Indent a bit
            if mod['author'].has_key('url'):
                authorsizer.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True, hyperlink=mod['author']['url']))
            else:
                authorsizer.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True))
            if mod['author'].has_key('email'):
                authorsizer.Add(self.getLabel(tmppanel, DV.l(' <'), color='#707070'))
                authorsizer.Add(self.getLabel(tmppanel, mod['author']['email'], hyperlink='mailto:' + mod['author']['email']))
                authorsizer.Add(self.getLabel(tmppanel, DV.l('>'), color='#707070'))
            desc = self.getLabel(tmppanel, mod['about']['long'])
        else:
            desc = self.getLabel(tmppanel, mod['about']['short'])
        desc.Wrap(descwidth)
        self.moduledescs[mod['name']] = (desc, descwidth)
        rightcol.Add((0, DV.control_vgap))
        rightcol.Add(desc)
        if buttons:
            rightcol.Add((0, DV.control_vgap))
            tmpbuttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            rightcol.Add(tmpbuttonsizer, 0, wx.ALIGN_RIGHT)
            config = wx.Button(tmppanel, -1, DV.l('Configure'))
            config.Bind(wx.EVT_BUTTON, DamnCurry(self.forceSelect, self.modules[module]))
            tmpbuttonsizer.Add(config)
            tmpbuttonsizer.Add((DV.control_hgap, 0))
            update = wx.Button(tmppanel, -1, DV.l('Update'))
            update.Bind(wx.EVT_BUTTON, DamnCurry(self.onModuleUpdate, module))
            tmpbuttonsizer.Add(update)
            tmpbuttonsizer.Add((DV.control_hgap, 0))
            uninstall = wx.Button(tmppanel, -1, DV.l('Uninstall'))
            uninstall.Bind(wx.EVT_BUTTON, DamnCurry(self.onModuleUninstall, module))
            tmpbuttonsizer.Add(uninstall)
        return tmppanel
    def updatePrefPane(self, pane):
        self.prefpanesizer.Clear(True) # Delete all controls in prefpane
        for i in range(self.prefpanesizer.GetCols()):
            try:
                self.prefpanesizer.RemoveGrowableCol(i)
            except:
                pass
        for i in range(self.prefpanesizer.GetRows()):
            try:
                self.prefpanesizer.RemoveGrowableRow(i)
            except:
                pass
        self.pane = pane
        if pane[0:8].lower() == 'special:':
            pane = pane[8:]
            if pane == 'profileroot':
                txt = wx.StaticText(self.prefpane, -1, DV.l('locale:damnvid-profile-explanation'))
                txt.Wrap(max(self.prefpane.GetSize()[0], 300))
                self.prefpanesizer.Add(txt, (0, 0), (1, 1))
            elif pane == 'error':
                txt = wx.StaticText(self.prefpane, -1, DV.l('Error!'))
                txt.Wrap(max(self.prefpane.GetSize()[0], 300))
                self.prefpanesizer.Add(txt, (0, 0), (1, 1))
            elif pane == 'modules':
                topsizer = wx.BoxSizer(wx.VERTICAL)
                self.prefpanesizer.Add(topsizer, (0, 0), (1, 1), wx.EXPAND)
                self.prefpanesizer.AddGrowableCol(0, 1)
                self.prefpanesizer.AddGrowableRow(0, 1)
                # Construct module list
                self.modulelist = wx.ScrolledWindow(self.prefpane, -1, size=(460, 3 * (72 + 2 * DV.border_padding)))
                self.modulelist.SetMinSize((460, 3 * (72 + 2 * DV.border_padding)))
                modlistsizer = wx.BoxSizer(wx.VERTICAL)
                self.modulelist.SetSizer(modlistsizer)
                topsizer.Add(self.modulelist, 1, wx.EXPAND)
                topsizer.Add((0, DV.control_vgap))
                buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
                topsizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT, border=1)
                if DV.os == 'mac':
                    topsizer.Add((0, 2)) # Annoying glitch with the buttons
                # Construct module list scrollable window
                for mod in DamnIterModules():
                    modlistsizer.Add(self.buildModulePanel(self.modulelist, mod, withscrollbars=True), 0, wx.EXPAND)
                self.modulelist.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
                # Construct buttons under module list
                install = wx.Button(self.prefpane, -1, DV.l('Install...'))
                install.Bind(wx.EVT_BUTTON, self.onModuleInstall)
                buttonsizer.Add(install)
                buttonsizer.Add((DV.control_hgap, 0))
                reset = wx.Button(self.prefpane, -1, DV.l('Reset all...'))
                reset.Bind(wx.EVT_BUTTON, self.onModuleAllReset)
                buttonsizer.Add(reset)
                buttonsizer.Add((DV.control_hgap, 0))
                update = wx.Button(self.prefpane, -1, DV.l('Check for updates'))
                update.Bind(wx.EVT_BUTTON, self.onModuleAllUpdate)
                buttonsizer.Add(update)
        else:
            prefprefix = pane
            profile = None
            module = None
            if prefprefix[0:16].lower() == 'damnvid-profile-':
                prefprefix = prefprefix[0:15]
                profile = int(pane[16:])
            elif prefprefix[0:15].lower() == 'damnvid-module-':
                module = prefprefix[15:]
            prefprefix += ':'
            self.controls = {}
            currentprefs = []
            maxheight = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
            maxwidth = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
            count = 0
            availprefs = DV.prefs.lists(pane)
            for i in DV.preference_order[prefprefix[0:-1]]:
                if prefprefix + i in DV.preferences.keys() and i in availprefs:
                    if not DV.preferences[prefprefix + i].has_key('noedit'):
                        currentprefs.append(prefprefix + i)
            for i in availprefs:
                if prefprefix + i in DV.preferences.keys():
                    desc = DV.preferences[prefprefix + i]
                    if not desc.has_key('noedit'):
                        if prefprefix + i not in currentprefs:
                            currentprefs.append(prefprefix + i)
                        maxheight[str(desc['type'])] += 1
                        maxwidth[str(desc['type'])] = max((maxwidth[str(desc['type'])], self.getPrefWidth(prefprefix + i)))
            maxwidth[str(DV.preference_type_profile)] = max((maxwidth[str(DV.preference_type_misc)], maxwidth[str(DV.preference_type_profile)], maxwidth[str(DV.preference_type_video)] + maxwidth[str(DV.preference_type_audio)]))
            maxwidth[str(DV.preference_type_misc)] = maxwidth[str(DV.preference_type_profile)]
            count = 0
            currentprefsinsection = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
            for i in currentprefs:
                shortprefname = i[i.find(':') + 1:]
                if profile == None:
                    val = DV.prefs.gets(pane, shortprefname)
                else:
                    val = DV.prefs.getp(profile, shortprefname)
                position = [int(module is not None), 0]
                if DV.preferences[i]['type'] == DV.preference_type_audio:
                    position[1] += maxwidth[str(DV.preference_type_video)]
                elif DV.preferences[i]['type'] == DV.preference_type_profile:
                    position[0] += max((maxheight[str(DV.preference_type_video)], maxheight[str(DV.preference_type_audio)]))
                elif DV.preferences[i]['type'] == DV.preference_type_misc:
                    position[0] += maxheight[str(DV.preference_type_profile)] + max((maxheight[str(DV.preference_type_video)], maxheight[str(DV.preference_type_audio)]))
                position[0] += currentprefsinsection[str(DV.preferences[i]['type'])]
                controlposition = (position[0], position[1] + 1)
                controlspan = (1, maxwidth[str(DV.preferences[i]['type'])] - 1)
                currentprefsinsection[str(DV.preferences[i]['type'])] += 1
                if DV.preferences[i]['kind'] != 'bool':
                    label = wx.StaticText(self.prefpane, -1, DV.l(DV.preferences[i]['name']) + ':')
                    self.prefpanesizer.Add(label, (position[0], position[1]), (1, 1), wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
                if type(DV.preferences[i]['kind']) is type({}):
                    choices = [self.defaultvalue]
                    for f in DV.preferences[i]['order']:
                        choices.append(DV.preferences[i]['kind'][f])
                    if not val:
                        val = self.defaultvalue
                    else:
                        if val in DV.preferences[i]['kind']:
                            val = DV.preferences[i]['kind'][val]
                    self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, val) # makeList takes care of the event binding
                    self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
                elif DV.preferences[i]['kind'][0] == '%':
                    self.controls[i] = self.makeSlider(self.prefpane, self.prefpanesizer, (controlposition, controlspan), int(100.0 * float(val) / float(str(DV.preferences[i]['kind'][1:]))), 0, 200)
                elif DV.preferences[i]['kind'] == 'bool':
                    if DV.preferences[i]['align']:
                        self.controls[i] = wx.CheckBox(self.prefpane, -1)
                        label = wx.StaticText(self.prefpane, -1, DV.l(DV.preferences[i]['name']))
                        label.Bind(wx.EVT_LEFT_UP, DamnCurry(self.onFakeCheckboxLabelClick, self.controls[i]))
                        self.prefpanesizer.Add(self.controls[i], (position[0], position[1]), (1, 1), wx.ALIGN_RIGHT)
                        self.prefpanesizer.Add(label, (position[0], position[1] + 1), (1, 1), wx.EXPAND)
                    else:
                        self.controls[i] = wx.CheckBox(self.prefpane, -1, DV.l(DV.preferences[i]['name']))
                        self.prefpanesizer.Add(self.controls[i], (position[0], position[1]), (1, maxwidth[str(DV.preferences[i]['type'])]), wx.EXPAND)
                    self.controls[i].SetValue(val == 'True')
                    self.Bind(wx.EVT_CHECKBOX, self.onPrefChange, self.controls[i])
                elif DV.preferences[i]['kind'][0:3] == 'int':
                    choices = [self.defaultvalue]
                    if DV.preferences[i]['kind'][0:5] == 'intk:':
                        for f in range(int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':') + 1:DV.preferences[i]['kind'].find('-')]), int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-') + 1:])):
                            choices.append(str(pow(2, f)) + 'k')
                        if not val:
                            val = self.defaultvalue
                        self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, val) # makeList takes care of the event binding
                        self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
                    elif DV.preferences[i]['kind'][0:4] == 'int:':
                        interval = (int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':') + 1:DV.preferences[i]['kind'].find('-')]), int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-') + 1:]))
                        if not val:
                            val = '0'
                        self.controls[i] = self.makeSlider(self.prefpane, self.prefpanesizer, (controlposition, controlspan), int(val), min(interval), max(interval))
                    elif DV.preferences[i]['kind'] == 'int':
                        if not val:
                            val = self.defaultvalue
                        self.controls[i] = self.makeList(False, [self.defaultvalue], self.prefpane, val)
                        self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
                elif DV.preferences[i]['kind'] == 'dir':
                    pathpanel = wx.Panel(self.prefpane, -1)
                    pathsizer = wx.BoxSizer(wx.HORIZONTAL)
                    pathpanel.SetSizer(pathsizer)
                    self.prefpanesizer.Add(pathpanel, controlposition, controlspan, wx.EXPAND)
                    self.controls[i] = wx.TextCtrl(pathpanel, -1, val)
                    self.Bind(wx.EVT_TEXT, self.onPrefChange, self.controls[i])
                    pathsizer.Add(self.controls[i], 1, wx.EXPAND)
                    pathsizer.Add((DV.control_hgap, 0))
                    browseButton = DamnBrowseDirButton(pathpanel, -1, DV.l('Browse...'), control=self.controls[i], title=DV.l('Select DamnVid\'s output directory.'), callback=self.onBrowseDir)
                    self.Bind(wx.EVT_BUTTON, browseButton.onBrowse, browseButton)
                    pathsizer.Add(browseButton, 0)
                elif DV.preferences[i]['kind'] == 'text':
                    self.controls[i] = wx.TextCtrl(self.prefpane, -1, val)
                    self.Bind(wx.EVT_TEXT, self.onPrefChange, self.controls[i])
                    self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
                elif DV.preferences[i]['kind'] == 'locale':
                    langs = []
                    c = 0
                    lang = 0
                    for l in DV.languages.iterkeys():
                        if DV.lang == l:
                            lang = c
                        c += 1
                        langs.append(DV.languages[l]['title']) # Eventually translate here, but I'm not sure. Maybe both translated and untranslated?
                    self.controls[i] = self.makeList(DV.preferences[i]['strict'], langs, self.prefpane, None, localize=False) # makeList takes care of the event binding
                    self.controls[i].SetSelection(lang)
                    self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
                elif DV.preferences[i]['kind'] == 'profile':
                    if DV.prefs.profiles:
                        choices = []
                        for p in range(-1, DV.prefs.profiles):
                            choices.append(DV.prefs.getp(p, 'name'))
                        self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, None) # makeList takes care of the event binding
                        self.controls[i].SetSelection(int(val) + 1) # +1 to compensate for -1 -> (Do not encode)
                    else:
                        self.controls[i] = wx.StaticText(self.prefpane, -1, DV.l('No encoding profiles found!'))
                    self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
                count = count + 1
            self.prefpanesizer.Layout()
            cols = self.prefpanesizer.GetCols()
            totalwidth = float(self.prefpanesizer.GetMinSize()[0] - (cols - 1) * self.prefpanesizer.GetHGap())
            splitwidth = round(totalwidth / float(cols) - .5)
            lastrow = self.prefpanesizer.GetRows()
            for i in range(cols):
                try:
                    self.prefpanesizer.AddGrowableCol(i)
                except:
                    pass
                curwidth = splitwidth
                if i == cols - 1:
                    curwidth += totalwidth - splitwidth * cols
                self.prefpanesizer.Add((int(curwidth), 0), (lastrow, i), (1, 1))
            if module is not None:
                self.prefpanesizer.Add(self.buildModulePanel(self.prefpane, module, extended=True, buttons=False), (0, 0), (1, self.prefpanesizer.GetCols()), wx.EXPAND)
        self.prefpanesizer.Layout() # Mandatory
        newsize = self.toppanel.GetBestSize()
        if newsize[0] > self.bestsize[0]:
            self.bestsize[0] = newsize[0]
        if newsize[1] > self.bestsize[1]:
            self.bestsize[1] = newsize[1]
        self.SetClientSize(newsize)
        self.SetClientSize(self.bestsize)
        self.Center()
    def getPrefWidth(self, pref):
        if type(DV.preferences[pref]['kind']) is type({}):
            return 2
        if DV.preferences[pref]['kind'][0:3] == 'int':
            return 2
        if DV.preferences[pref]['kind'] == 'profile':
            return 2
        if DV.preferences[pref]['kind'] == 'locale':
            return 2
        if DV.preferences[pref]['kind'][0] == '%':
            return 2
        if DV.preferences[pref]['kind'] == 'text':
            return 2
        if DV.preferences[pref]['kind'] == 'dir':
            return 2 # Label + Panel{TextCtrl + Button} = 2
        if DV.preferences[pref]['kind'] == 'bool':
            return 1
        return 0
    def onFakeCheckboxLabelClick(self, checkbox, event):
        checkbox.SetValue(not checkbox.IsChecked())
    def splitLongPref(self, pref):
        if pref.find(':') == -1:
            return pref
        return (pref[0:pref.find(':')], pref[pref.find(':') + 1:])
    def onPrefChange(self, event):
        Damnlog('Preference changed event caught.')
        name = None
        for i in self.controls.iterkeys():
            pref = self.splitLongPref(i)
            prefname = pref[1]
            if pref[0][0:16] == 'damnvid-profile-':
                genericpref = pref[0][0:15]
            else:
                genericpref = pref[0]
            genericpref += ':' + pref[1]
            val = None
            if type(DV.preferences[genericpref]['kind']) is type({}) or (DV.preferences[genericpref]['kind'][0:3] == 'int' and DV.preferences[genericpref]['kind'][0:4] != 'int:'):
                if DV.preferences[genericpref]['strict']:
                    val = self.controls[i].GetSelection()
                    if val:
                        val = DV.preferences[genericpref]['order'][val - 1]
                    else:
                        val = ''
                else:
                    val = self.controls[i].GetValue()
                    if val == self.defaultvalue or val == '(default)':
                        val = ''
                    elif type(DV.preferences[genericpref]['kind']) is type({}) and val in DV.preferences[genericpref]['kind'].values():
                        for j in DV.preferences[genericpref]['kind'].iterkeys():
                            if val == DV.preferences[genericpref]['kind'][j]:
                                val = j
            elif DV.preferences[genericpref]['kind'] == 'profile':
                val = self.controls[i].GetSelection() - 1
            elif DV.preferences[genericpref]['kind'] == 'locale':
                val = self.controls[i].GetString(self.controls[i].GetSelection())
                for loc in DV.languages.iterkeys():
                    if DV.languages[loc]['title'] == val:
                        val = loc
                        break
            elif DV.preferences[genericpref]['kind'][0:4] == 'int:':
                val = int(self.controls[i].GetValue())
            elif DV.preferences[genericpref]['kind'][0] == '%':
                val = float(float(self.controls[i].GetValue())*float(int(DV.preferences[genericpref]['kind'][1:])) / 100.0)
            elif DV.preferences[genericpref]['kind'] == 'dir' or DV.preferences[genericpref]['kind'] == 'text':
                val = self.controls[i].GetValue()
                if genericpref == 'damnvid-profile:name':
                    name = val
            elif DV.preferences[genericpref]['kind'] == 'bool':
                val = self.controls[i].IsChecked() # The str() representation takes care of True/False
            if val is not None:
                DV.prefs.sets(self.pane, prefname, DamnUnicode(val))
        if name != None and self.tree.GetSelection() != self.treeroot and self.tree.GetItemParent(self.tree.GetSelection()) == self.profileroot:
            self.tree.SetItemText(self.tree.GetSelection(), name)
            self.prefpanelabel.SetLabel(name)
    def onBrowseDir(self, button, path):
        for i in self.controls.iterkeys():
            if self.controls[i] == button.filefield:
                DV.prefs.sets(self.pane, self.splitLongPref(i)[1], path)
    def onAddProfile(self, event):
        DV.prefs.addp()
        prof = self.tree.AppendItem(self.profileroot, DV.prefs.getp(DV.prefs.profiles - 1, 'name'))
        self.tree.SetItemImage(prof, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profile.png')))
        self.profiles.append(prof)
        self.tree.SelectItem(self.profiles[-1], True)
    def onDeleteProfile(self, event):
        if self.tree.GetSelection() != self.treeroot and self.tree.GetItemParent(self.tree.GetSelection()) == self.profileroot:
            if len(self.profiles) > 1:
                profile = int(self.pane[16:])
                DV.prefs.remp(profile)
                curprofile = self.tree.GetSelection()
                if not profile:
                    # User is deleting first profile
                    newprofile = self.tree.GetNextSibling(curprofile)
                else:
                    # User is not deleting first profile, all right
                    newprofile = self.tree.GetPrevSibling(curprofile)
                self.profiles.remove(curprofile)
                try:
                    self.tree.SelectItem(newprofile)
                except:
                    self.tree.SelectItem(self.profileroot)
                self.tree.Delete(curprofile)
            else:
                dlg = wx.MessageDialog(None, DV.l('Cannot delete all encoding profiles!'), DV.l('Cannot delete all profiles'), wx.OK | wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg = wx.MessageDialog(None, DV.l('Please choose a profile to delete from the profile list.'), DV.l('No profile selected'), wx.OK | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onLoad(self, event):
        if self.tree.GetSelection() != self.modulelistitem:
            return
        info = event.GetInfo()
        mod = info['module']['name']
        modtitle = info['module']['title']
        desc = self.moduledescs[mod]
        if type(info['result']) is type(''):
            if info['result'] == 'error':
                desc[0].SetLabel(DV.l('There was an error while checking for updates to ') + modtitle + '.')
                desc[0].Wrap(desc[1])
            elif info['result'] == 'uptodate':
                desc[0].SetLabel(modtitle + DV.l(' is up-to-date.'))
                desc[0].Wrap(desc[1])
            elif info['result'] == 'cannot':
                desc[0].SetLabel(modtitle + DV.l(' has no update mechanism.'))
                desc[0].Wrap(desc[1])
        elif type(info['result']) is type(()):
            self.buildTree()
            self.forceSelect(self.modulelistitem)
            desc = self.moduledescs[mod]
            desc[0].SetLabel(modtitle + DV.l(' has been updated to version ') + str(info['result'][0]) + '.')
            desc[0].Wrap(desc[1])
        self.modulelist.Layout()
        self.modulelist.AdjustScrollbars()
    def onModuleUpdate(self, module=None, event=None):
        if not DV.modules.has_key(module):
            return
        module = DV.modules[module]
        desc = self.moduledescs[module['name']]
        if not module['about'].has_key('url'):
            desc[0].SetLabel(module['title'] + DV.l(' has no update mechanism.'))
            desc[0].Wrap(desc[1])
            return
        desc[0].SetLabel(DV.l('Checking for updates...'))
        desc[0].Wrap(desc[1])
        updatecheck = DamnModuleUpdateCheck(self, module)
        updatecheck.start()
    def onModuleAllUpdate(self, event):
        modlist = []
        for i in self.moduledescs.iterkeys():
            if DV.modules.has_key(i):
                modlist.append(DV.modules[i])
                self.moduledescs[i][0].SetLabel(DV.l('Checking for updates...'))
                self.moduledescs[i][0].Wrap(self.moduledescs[i][1])
        updatecheck = DamnModuleUpdateCheck(self, modlist)
        updatecheck.start()
    def onModuleAllReset(self, event):
        dlg = wx.MessageDialog(None, DV.l('Are you sure you want to reset all the default modules and their preferences?'), DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_YES:
            for i in DV.prefs.listsections():
                if i[0:15] == 'damnvid-module-':
                    DV.prefs.rems(i)
            DV.prefs.save()
            DamnLoadConfig(forcemodules=True)
            DV.prefs = DamnVidPrefs()
            self.buildTree()
            self.forceSelect(self.modulelistitem)
        dlg.Destroy()
    def onModuleInstall(self, event=None):
        dlg = wx.FileDialog(None, DV.l('Where is located the module to install?'), DV.prefs.get('lastmoduledir'), '', DV.l('locale:browse-damnvid-modules'), wx.FD_OPEN)
        dlg.SetIcon(DV.icon)
        result = None
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            DV.prefs.set('lastmoduledir', os.path.dirname(path))
            result = DamnInstallModule(path)
        dlg.Destroy()
        message = None
        if result is not None:
            if result == 'success':
                message = (DV.l('Success!'), DV.l('The module was successfully installed.'), wx.ICON_INFORMATION)
            elif result == 'nofile':
                message = (DV.l('Error'), DV.l('Error: Could not find the module file.'), wx.ICON_ERROR)
            elif result == 'nomodule':
                message = (DV.l('Error'), DV.l('Error: This file is not a valid DamnVid module.'), wx.ICON_ERROR)
            else:
                message = (DV.l('Error'), DV.l('Error: Unknown error while installing module.'), wx.ICON_ERROR)
        if message is not None:
            DamnLoadConfig()
            DV.prefs = DamnVidPrefs()
            self.buildTree()
            self.forceSelect(self.modulelistitem)
            dlg = wx.MessageDialog(None, message[1], message[0], message[2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onModuleUninstall(self, module=None, event=None):
        if not DV.modules.has_key(module):
            return
        dlg = wx.MessageDialog(None, DV.l('Are you sure you want to uninstall the module: ') + DV.modules[module]['title'] + '?', DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_YES:
            del DV.modules[module]
            try:
                shutil.rmtree(DV.modules_path + module)
            except:
                pass
            DV.prefs.rems('damnvid-module-' + module)
            self.buildTree()
            self.forceSelect(self.modulelistitem)
        dlg.Destroy()
    def makeList(self, strict, choices, panel, value, localize=True):
        choices2 = []
        for c in choices:
            if not localize or c == self.defaultvalue:
                choices2.append(c)
            else:
                choices2.append(DV.l(c))
        if strict:
            cont = wx.Choice(panel, -1, choices=choices2)
            if value == self.defaultvalue or value == '(default)':
                cont.SetSelection(0)
            else:
                for f in range(len(choices2)):
                    if choices[f] == value:
                        cont.SetSelection(f)
            self.Bind(wx.EVT_CHOICE, self.onPrefChange, cont)
        else:
            cont = wx.ComboBox(panel, -1, choices=choices, value=value)
            cont.SetValue(value) # Fixes bug on OS X where the value wouldn't be set if it's not one of the choices
            self.Bind(wx.EVT_TEXT, self.onPrefChange, cont)
        return cont
    def makeSlider(self, panel, sizer, position, value, minval, maxval):
        value = min((maxval, max((int(minval), int(value)))))
        tmppanel = wx.Panel(panel, -1)
        tmpsizer = wx.BoxSizer(wx.HORIZONTAL)
        tmppanel.SetSizer(tmpsizer)
        containersizer = wx.BoxSizer(wx.VERTICAL)
        tmpsizer.Add(containersizer, 7, wx.ALIGN_CENTER_VERTICAL)
        containersizer.Add((0, 1))
        slider = wx.Slider(tmppanel, -1, value=value, minValue=minval, maxValue=maxval, style=wx.SL_HORIZONTAL)
        containersizer.Add(slider, 1, wx.EXPAND)
        containersizer.Add((0, 1))
        tmplabel = wx.StaticText(tmppanel, -1, str(value))
        tmpsizer.Add(tmplabel, 1, wx.ALIGN_CENTER_VERTICAL)
        self.Bind(wx.EVT_SLIDER, DamnCurry(self.updateSlider, slider, tmplabel), slider)
        sizer.Add(tmppanel, position[0], position[1], wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        return slider
    def updateSlider(self, slider, label, event=None):
        label.SetLabel(str(slider.GetValue()))
        self.onPrefChange(event)
    def getListValue(self, name, strict):
        if strict:
            val = self.listvalues[name][self.controls[name].GetSelection()]
        else:
            val = self.controls[name].GetValue()
        if val == self.defaultvalue or val == '(default)':
            val = ''
        elif type(DV.preference_type[name]['kind']) is type({}):
            for key, i in DV.preference_type[name]['kind'].iteritems():
                if i == val or DV.l(i) == val:
                    return key
        return val
    def setListValue(self, name, strict, value):
        if not value:
            if strict:
                self.controls[name].SetSelection(0)
            else:
                self.controls[name].SetValue(self.defaultvalue)
        else:
            if strict:
                if type(DV.preference_type[name]['kind']) is type({}):
                    value = DV.l(DV.preference_type[name]['kind'][value])
                c = 0
                for i in self.listvalues[name]:
                    if i == value:
                        self.controls[name].SetSelection(c)
                    c = c + 1
            else:
                self.controls[name].SetValue(value)
    def onOK(self, event):
        DV.prefs.save()
        self.Close(True)
    def onReset(self, event):
        dlg = wx.MessageDialog(None, DV.l('All changes to DamnVid\'s configuration will be lost. Continue?'), DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_YES:
            dlg.Destroy()
            checkupdates = DV.prefs.get('checkforupdates')
            DV.prefs = None
            os.remove(DV.conf_file)
            shutil.copyfile(DV.curdir + 'conf' + DV.sep + 'conf.ini', DV.conf_file)
            DamnLoadConfig(forcemodules=True)
            DV.prefs = DamnVidPrefs()
            DV.prefs.set('checkforupdates', checkupdates)
            DV.prefs.save()
            self.buildTree()
            dlg = wx.MessageDialog(None, DV.l('DamnVid\'s configuration has been successfully reset.'), DV.l('Configuration reset'), wx.OK | wx.ICON_INFORMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
        dlg.Destroy()
    def onImport(self, event):
        dlg = wx.FileDialog(None, DV.l('Where is located the configuration file to import?'), DV.prefs.get('lastprefdir'), 'DamnVid-' + DV.version + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_OPEN)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_OK:
            self.tree.SelectItem(self.treeroot, True)
            path = dlg.GetPath()
            dlg.Destroy()
            DV.prefs.set('lastprefdir', path)
            f = DamnOpenFile(path, 'r')
            testprefs = ConfigParser.SafeConfigParser()
            allOK = False
            try:
                testprefs.readfp(f)
                f.close()
                allOK = True
            except:
                try:
                    f.close()
                except:
                    pass
                dlg = wx.MessageDialog(None, DV.l('Invalid configuration file.'), DV.l('Invalid file'), wx.OK | wx.ICON_ERROR)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            if allOK:
                keepgoing = True
                while keepgoing:
                    keepgoing = DV.prefs.remp(0) is not None
                for i in testprefs.sections():
                    try:
                        DV.prefs.ini.add_section(i)
                    except:
                        pass
                    for j in testprefs.options(i):
                        DV.prefs.sets(i, j, testprefs.get(i, j))
                self.parent.reopenprefs = True
                self.onOK(None)
        else:
            dlg.Destroy()
    def onExport(self, event):
        dlg = wx.FileDialog(None, DV.l('Where do you want to export DamnVid\'s configuration?'), DV.prefs.get('lastprefdir'), 'DamnVid-' + DV.version + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            DV.prefs.set('lastprefdir', path)
            f = DamnOpenFile(path, 'w')
            DV.prefs.ini.write(f)
            f.close()
        dlg.Destroy()
    def onKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL):
            self.onClose(event)
        elif event.GetKeyCode() in (wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN, wx.WXK_EXECUTE):
            self.onOK(event)
    def onClose(self, event):
        DV.prefs = DamnVidPrefs() # Reload from ini
        self.Close(True)
class DamnVideoLoader(thr.Thread):
    def __init__(self, parent, uris, thengo=False, feedback=True, allownonmodules=True):
        thr.Thread.__init__(self)
        self.uris = uris
        self.parent = parent
        self.thengo = thengo
        self.feedback = feedback
        self.done = False
        self.result = None
        self.allownonmodules = allownonmodules
        Damnlog('DamnVideoLoader spawned with parameters: parent =',parent,'; thengo?',thengo,'; feedback?',feedback,'; allow non-modules?',allownonmodules)
    def run(self):
        if self.feedback:
            self.parent.toggleLoading(True)
        self.vidLoop(self.uris)
        self.done = True
        if self.feedback:
            self.parent.toggleLoading(False)
        else:
            while self.done:
                time.sleep(.1)
    def postEvent(self, info):
        if self.feedback:
            wx.PostEvent(self.parent, DamnLoadingEvent(DV.evt_loading, -1, info))
    def getVidName(self, uri):
        return self.parent.getVidName(uri)
    def addValid(self, meta):
        meta['original'] = self.originaluri
        self.result = meta
        self.postEvent({'meta':meta, 'go':self.thengo})
    def SetStatusText(self, status):
        self.postEvent({'status':status})
    def showDialog(self, title, content, icon):
        self.postEvent({'dialog':(title, content, icon)})
    def vidLoop(self, uris):
        Damnlog('Starting vidLoop with URIs:',uris)
        for uri in uris:
            Damnlog('vidLoop considering URI:',uri)
            self.originaluri = uri
            bymodule = False
            for module in DamnIterModules(False):
                Damnlog('Trying module',module['class'],'for URI',uri)
                mod = module['class'](uri)
                if mod.validURI():
                    Damnlog('Module has been chosen for URI',uri,':',mod)
                    mod.addVid(self)
                    bymodule = True
                    break
            if not bymodule:
                Damnlog('No module found for URI:',uri)
                if not self.allownonmodules:
                    Damnlog('DamnVideoLoader exitting because no module was found and non-modules are not allowed.')
                    self.result = None
                    return
                if REGEX_HTTP_GENERIC.match(uri):
                    Damnlog('HTTP regex still matches URI:',uri)
                    name = self.getVidName(uri)
                    if name == DV.l('Unknown title'):
                        name = REGEX_HTTP_EXTRACT_FILENAME.sub('', uri)
                    self.addValid({'name':name, 'profile':DV.prefs.get('defaultwebprofile'), 'profilemodified':False, 'fromfile':name, 'dirname':REGEX_HTTP_EXTRACT_DIRNAME.sub('\\1/', uri), 'uri':uri, 'status':DV.l('Pending.'), 'icon':DamnGetListIcon('generic')})
                else:
                    # It's a file or a directory
                    if os.path.isdir(uri):
                        Damnlog('URI',uri,'is a directory.')
                        if DV.prefs.get('DirRecursion') == 'True':
                            for i in os.listdir(uri):
                                self.vidLoop([uri + DV.sep + i]) # This is recursive; if i is a directory, this block will be executed for it too
                        else:
                            if len(uris) == 1: # Only one dir, so an alert here is tolerable
                                self.showDialog(DV.l('Recursion is disabled.'), DV.l('This is a directory, but recursion is disabled in the preferences. Please enable it if you want DamnVid to go through directories.'), wx.OK | wx.ICON_EXCLAMATION)
                            else:
                                self.SetStatusText(DV.l('Skipped ') + uri + DV.l(' (directory recursion disabled).'))
                    else:
                        Damnlog('URI',uri,'is a file.')
                        filename = os.path.basename(uri)
                        if uri in self.parent.videos:
                            self.SetStatusText(DV.l('Skipped ') + filename + DV.l(' (already in list).'))
                            if len(uris) == 1: # There's only one file, so an alert here is tolerable
                                self.showDialog(DV.l('Duplicate found'), DV.l('This video is already in the list!'), wx.ICON_EXCLAMATION | wx.OK)
                        else:
                            self.addValid({'name':filename[0:filename.rfind('.')], 'profile':DV.prefs.get('defaultprofile'), 'profilemodified':False, 'fromfile':filename, 'uri':uri, 'dirname':os.path.dirname(uri), 'status':DV.l('Pending.'), 'icon':DamnGetListIcon('damnvid')})
class DamnConverter(thr.Thread): # The actual converter, dammit
    def __init__(self, parent):
        self.parent = parent
        self.sourceuri = parent.videos[parent.converting]
        self.outdir = None
        self.filename = None
        self.tmpfilename = None
        self.moduleextraargs = []
        thr.Thread.__init__(self)
    def getURI(self, uri):
        if self.parent.meta[self.sourceuri].has_key('downloadgetter') and self.parent.meta[self.sourceuri].has_key('module'):
            if self.parent.meta[self.sourceuri]['module'] is not None:
                uri = self.parent.meta[self.sourceuri]['downloadgetter']()
                self.moduleextraargs = self.parent.meta[self.sourceuri]['module'].getFFmpegArgs()
                if not self.parent.meta[self.sourceuri]['profilemodified']:
                    self.outdir = self.parent.meta[self.sourceuri]['module'].getOutdir()
                if type(uri) in (type(''), type(u'')):
                    uri = [uri]
                if uri is None:
                    Damnlog('URI is None!')
                    return [None]
                return uri
        return [uri]
    def cmd2str(self, cmd):
        s = []
        stream = DamnUnicode(self.stream)
        if self.stream != '-' and DV.os == 'nt':
            stream = DamnUnicode(win32api.GetShortPathName(self.stream))
        for i in cmd:
            s.append(i.replace('?DAMNVID_VIDEO_STREAM?', stream).replace('?DAMNVID_VIDEO_PASS?', str(self.passes)).replace('?DAMNVID_OUTPUT_FILE?', DV.tmp_path + self.tmpfilename))
        return s
    def gettmpfilename(self, path, prefix, ext):
        prefix = DamnUnicode(DamnUnicode(prefix).encode('ascii', 'ignore'))
        ext = DamnUnicode(ext)
        path = DamnUnicode(path)
        tmpfilename = prefix + u'-0' + ext
        tmpcount = 0
        while os.path.exists(path + tmpfilename):
            tmpcount += 1
            tmpfilename = prefix + u'-' + DamnUnicode(tmpcount) + ext
        f = DamnOpenFile(path + tmpfilename, 'wb')   # Just create the file
        f.close()
        Damnlog('Temp file name generated:', tmpfilename, 'In path:', path)
        return tmpfilename
    def getfinalfilename(self, path, prefix, ext):
        ext = DamnUnicode(ext)
        prefix = DamnUnicode(prefix)
        path = DamnUnicode(path)
        if not os.path.exists(path + prefix + ext):
            return prefix
        c = 2
        while os.path.exists(path + prefix + u' (' + DamnUnicode(c) + u')' + ext):
            c = c + 1
        return prefix + u' (' + DamnUnicode(c) + u')'
    def update(self, progress=None, statustext=None, status=None, dialog=None, go=None):
        info = {}
        if progress is not None:
            info['progress'] = float(progress)
        if statustext is not None:
            info['statustext'] = DamnUnicode(statustext)
        if status is not None:
            info['status'] = DamnUnicode(status)
        if dialog is not None:
            info['dialog'] = dialog
        if go is not None:
            info['go'] = go
        wx.PostEvent(self.parent, DamnProgressEvent(DV.evt_progress, -1, info))
    def run(self):
        self.uris = self.getURI(self.sourceuri)
        self.abort = False
        if not self.abort:
            if True:
                Damnlog('Conversion routine starting, URI is', self.uris[0])
                self.uri = self.uris[0]
                self.update(0)
                self.parent.thisvideo.append(self.parent.videos[self.parent.converting])
                self.filename = unicodedata.normalize('NFKD', DamnUnicode(REGEX_FILE_CLEANUP_FILENAME.sub('', self.parent.meta[self.parent.videos[self.parent.converting]]['name']))).encode('utf8', 'ignore').replace('/', '').replace('\\', '').strip() # Heck of a line!
                self.profile = int(self.parent.meta[self.parent.videos[self.parent.converting]]['profile'])
                if os.path.exists(self.uri):
                    Damnlog('We\'re dealing with a file stream here.')
                    self.stream = self.uri
                    if self.outdir is None:
                        self.outdir = DV.prefs.get('defaultoutdir')
                else:
                    Damnlog('We\'re dealing with a network stream here.')
                    self.stream = '-' # It's another stream, spawn a downloader thread to take care of it and pipe the content to ffmpeg via stdin
                    if self.outdir is None:
                        self.outdir = DV.prefs.get('defaultweboutdir')
                if self.outdir[-1:] == DV.sep:
                    self.outdir = self.outdir[0:-1]
                if not os.path.exists(self.outdir):
                    os.makedirs(self.outdir)
                elif not os.path.isdir(self.outdir):
                    os.remove(self.outdir)
                    os.makedirs(self.outdir)
                self.outdir = self.outdir + DV.sep
                Damnlog('Profile is', self.profile, '; Output directory is', self.outdir)
                if self.profile == -1: # Do not encode, just copy
                    Damnlog('We\'re in raw copy mode')
                    if True:
                        failed = False
                        if self.stream == '-': # Spawn a downloader
                            src = DamnURLPicker(self.uris)
                            total = int(src.info()['Content-Length'])
                            Damnlog('Total bytes:', total)
                            ext = 'avi'
                            try:
                                if src.info()['Content-Type'].lower().find('audio') != -1:
                                    ext = 'mp3'
                            except:
                                ext = 'avi'
                            try:
                                tmpuri = src.info()['Content-Disposition'][src.info()['Content-Disposition'].find('filename=') + 9:]
                            except:
                                tmpuri = 'Video.' + ext # And pray for the best!
                            Damnlog('Temp URI is', tmpuri)
                        else: # Just copy the file, lol
                            total = int(os.lstat(self.stream).st_size)
                            src = DamnOpenFile(self.stream, 'rb')
                            tmpuri = self.stream
                            Damnlog('Total is', total, '; Temp URI is', tmpuri)
                        if REGEX_URI_EXTENSION_EXTRACT.search(tmpuri):
                            ext = '.' + REGEX_URI_EXTENSION_EXTRACT.sub('\\1', tmpuri)
                        else:
                            ext = '.avi' # And pray for the best again!
                        self.filename = self.getfinalfilename(self.outdir, self.filename, ext)
                        Damnlog('Filename is', self.filename, '; opening local stream.')
                        dst = DamnOpenFile(self.outdir + self.filename + ext, 'wb')
                        Damnlog(self.outdir + self.filename + ext, 'opened.')
                        keepgoing = True
                        copied = 0.0
                        lasttime = 0.0
                        self.update(statustext=DV.l('Copying ') + DamnUnicode(self.parent.meta[self.parent.videos[self.parent.converting]]['name']) + DV.l('...'))
                        Damnlog('Starting raw download of stream', src)
                        while keepgoing and not self.abort:
                            i = src.read(4096)
                            if len(i):
                                dst.write(i)
                                copied += 4096.0
                            else:
                                copied = float(total)
                                keepgoing = False
                            progress = min((100.0, copied / total * 100.0))
                            nowtime = float(time.time())
                            if lasttime + .5 < nowtime or not keepgoing: # Do not send a progress update more than 2 times per second, otherwise the event queue can get overloaded. On some platforms, time() is an int, but that doesn't matter; the progress will be updated once a second instead of 2 times, which is still acceptable.
                                self.update(progress, status=self.parent.meta[self.parent.videos[self.parent.converting]]['status'] + ' [' + str(int(progress)) + '%]')
                                lasttime = nowtime
                        Damnlog('Done downloading!')
                    else:
                        Damnlog('Raw download failed. Aborted?', self.abort)
                        failed = True
                    self.grabberrun = False
                    if self.abort or failed:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status'] = DV.l('Failure.')
                        self.update(status=DV.l('Failure.'))
                    else:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status'] = DV.l('Success!')
                        self.update(status=DV.l('Success!'))
                        self.parent.resultlist.append((self.filename + ext, self.outdir, self.parent.meta[self.parent.videos[self.parent.converting]]['icon']))
                    self.update(go=self.abort)
                    return
                Damnlog('We\'re in on-the-fly conversion mode.')
                os_exe_ext = ''
                if DV.os == 'nt':
                    os_exe_ext = '.exe'
                elif DV.os == 'mac':
                    os_exe_ext = 'osx'
                if DV.bit64:
                    os_exe_ext = '64' + os_exe_ext
                self.passes = 1
                cmd = [DV.bin_path + 'ffmpeg' + os_exe_ext, '-i', '?DAMNVID_VIDEO_STREAM?', '-y', '-passlogfile', DV.tmp_path + 'pass']
                for i in DV.preferences.keys():
                    if i[0:25] == 'damnvid-profile:encoding_':
                        i = i[16:]
                        pref = DV.prefs.getp(self.profile, i)
                        if pref:
                            if type(DV.preferences['damnvid-profile:' + i]['kind']) in (type(''), type(u'')):
                                if DV.preferences['damnvid-profile:' + i]['kind'][0] == '%':
                                    pref = str(round(float(pref), 0)) # Round
                            if i == 'encoding_pass':
                                pref = '?DAMNVID_VIDEO_PASS?'
                            if i[9:] == 'b' and pref == 'sameq':
                                cmd.append('-sameq')
                            else:
                                cmd.extend(['-' + i[9:], pref])
                self.encodevideo = DamnUnicode(DV.prefs.getp(self.profile, 'video')) == u'True'
                self.encodeaudio = DamnUnicode(DV.prefs.getp(self.profile, 'audio')) == u'True'
                if self.encodevideo:
                    Damnlog('Encoding video.')
                else:
                    Damnlog('Not encoding video.')
                    cmd.append('-vn')
                if self.encodeaudio:
                    Damnlog('Encoding audio.')
                else:
                    Damnlog('Not encoding audio.')
                    cmd.append('-an')
                vidformat = DV.prefs.getp(self.profile, 'Encoding_f')
                self.vcodec = DV.prefs.getp(self.profile, 'Encoding_vcodec')
                self.acodec = DV.prefs.getp(self.profile, 'Encoding_acodec')
                self.totalpasses = DV.prefs.getp(self.profile, 'Encoding_pass')
                if not self.totalpasses:
                    self.totalpasses = 1
                else:
                    self.totalpasses = int(self.totalpasses)
                if vidformat and DV.file_ext.has_key(vidformat):
                    ext = '.' + DV.file_ext[vidformat]
                else:
                    if self.vcodec and self.encodevideo and DV.file_ext_by_codec.has_key(self.vcodec):
                        ext = '.' + DV.file_ext_by_codec[self.vcodec]
                    elif self.encodeaudio and not self.encodevideo:
                        if DV.file_ext_by_codec.has_key(self.acodec):
                            ext = '.' + DV.file_ext_by_codec[self.acodec]
                        else:
                            ext = '.mp3'
                    else:
                        ext = '.avi'
                flags = []
                if self.vcodec and DV.codec_advanced_cl.has_key(self.vcodec):
                    for o in DV.codec_advanced_cl[self.vcodec]:
                        if type(o) in (type(''), type(u'')):
                            if o not in flags: # If the flag is already there, don't add it again
                                flags.append(o)
                        else:
                            if '-' + o[0] not in cmd: # If the option is already there, don't overwrite it
                                cmd.extend(['-' + o[0], o[1]])
                if len(flags):
                    cmd.extend(['-flags', ''.join(flags)])
                self.filename = DamnUnicode(self.getfinalfilename(self.outdir, self.filename, ext))
                self.filenamenoext = self.filename
                self.tmpfilename = DamnUnicode(self.gettmpfilename(DV.tmp_path, self.filenamenoext, ext))
                cmd.append('?DAMNVID_OUTPUT_FILE?')
                if len(self.moduleextraargs):
                    cmd.extend(self.moduleextraargs)
                Damnlog('ffmpeg call has been generated:', cmd)
                self.filename = self.filenamenoext + ext
                self.duration = None
                self.update(statustext=DV.l('Converting ') + DamnUnicode(self.parent.meta[self.parent.videos[self.parent.converting]]['name']) + DV.l('...'))
                while int(self.passes) <= int(self.totalpasses) and not self.abort:
                    Damnlog('Starting pass', self.passes, 'out of', self.totalpasses)
                    if self.totalpasses != 1:
                        self.parent.meta[self.parent.videos[self.parent.converting]]['status'] = DV.l('Pass ') + str(self.passes) + '/' + str(self.totalpasses) + DV.l('...')
                        self.update(status=DV.l('Pass ') + str(self.passes) + '/' + str(self.totalpasses) + DV.l('...'))
                        if self.stream == '-':
                            if self.passes == 1:
                                self.tmppassfile = DV.tmp_path + self.gettmpfilename(DV.tmp_path, self.filenamenoext, ext)
                            else:
                                self.stream = self.tmppassfile
                        if self.passes != 1:
                            self.tmpfilename = self.gettmpfilename(DV.tmp_path, self.filenamenoext, ext)
                    self.process = DamnSpawner(self.cmd2str(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, cwd=os.path.dirname(DV.tmp_path))
                    if self.stream == '-':
                        if self.totalpasses != 1:
                            self.feeder = DamnDownloader(self.uris, self.process.stdin, self.tmppassfile)
                        else:
                            self.feeder = DamnDownloader(self.uris, self.process.stdin)
                        self.feeder.start()
                    curline = ''
                    Damnlog('Starting ffmpeg polling.')
                    while self.process.poll() == None and not self.abort:
                        c = self.process.stderr.read(1)
                        curline += c
                        if c == '\r' or c == '\n':
                            self.parseLine(curline)
                            curline = ''
                    Damnlog('Stopping ffmpeg polling. Abort?', self.abort)
                    try:
                        commun = self.process.communicate()
                        curline += commun
                        Damnlog('Grabbed additional ffmpeg stuff:', commun)
                    except:
                        Damnlog('Couldn\'t grab additional ffmpeg stuff.')
                    if curline:
                        self.parseLine(curline)
                    self.passes += 1
                Damnlog('And we\'re done converting!')
                self.update(100)
                result = self.process.poll() # The process is complete, but .poll() still returns the process's return code
                time.sleep(.25) # Wait a bit
                self.grabberrun = False # That'll make the DamnConverterGrabber wake up just in case
                if result and os.path.exists(DV.tmp_path + self.tmpfilename):
                    os.remove(DV.tmp_path + self.tmpfilename) # Delete the output file if ffmpeg has exitted with a bad return code
                Damnlog('All the routine completed successfully.')
            else:
                result = 1
                Damnlog('Error in main conversion routine.')
            Damnlog('Cleaning up after conversion.')
            for i in os.listdir(os.path.dirname(DV.tmp_path)):
                if i == self.tmpfilename and not result and not self.abort:
                    try:
                        os.rename(DV.tmp_path + i, self.outdir + self.filename)
                    except: # Maybe the file still isn't unlocked, it happens... Wait moar and retry
                        try:
                            time.sleep(2)
                            os.rename(DV.tmp_path + i, self.outdir + self.filename)
                        except: # Now this is really bad, alert the user
                            try: # Manual copy, might be needed if we're working on two different filesystems on a non-Windows platform
                                src = DamnOpenFile(DV.tmp_path + i, 'rb')
                                dst = DamnOpenFile(self.outdir + self.filename, 'wb')
                                for fileline in src.readlines():
                                    dst.write(fileline)
                                try: # Another try block in order to avoid raising the huge except block with the dialog
                                    src.close()
                                    dst.close()
                                    os.remove(DV.tmp_path + i)
                                except:
                                    pass
                            except:
                                self.update(dialog=(DV.l('Cannot move file!'), DV.l('locale:successfully-converted-file-but-ioerror') + '\n' + DV.tmp_path + i, wx.OK | wx.ICON_EXCLAMATION))
                else:
                    try:
                        os.remove(DV.tmp_path + i)
                    except:
                        pass
            Damnlog('End cleanup, returning. Result?', result, '; Abort?', self.abort)
            if not result and not self.abort:
                self.parent.meta[self.parent.videos[self.parent.converting]]['status'] = DV.l('Success!')
                self.parent.resultlist.append((self.filename, self.outdir, self.parent.meta[self.parent.videos[self.parent.converting]]['icon']))
                self.update(status=DV.l('Success!'), go=self.abort)
                return
            self.parent.meta[self.parent.videos[self.parent.converting]]['status'] = DV.l('Failure.')
            self.update(status=DV.l('Failure.'), go=self.abort)
    def parseLine(self, line):
        Damnlog('ffmpeg>', line)
        if self.duration == None:
            res = REGEX_FFMPEG_DURATION_EXTRACT.search(line)
            if res:
                self.duration = int(res.group(1)) * 3600 + int(res.group(2)) * 60 + float(res.group(3))
                if not self.duration:
                    self.duration = None
        else:
            res = REGEX_FFMPEG_TIME_EXTRACT.search(line)
            if res:
                wx.PostEvent(self.parent, DamnProgressEvent(DV.evt_progress, -1, {
                    'progress':min(100.0, float(float(res.group(1)) / self.duration / float(self.totalpasses) + float(float(self.passes - 1) / float(self.totalpasses))) * 100.0),
                    'status':self.parent.meta[self.parent.videos[self.parent.converting]]['status'] + ' [' + str(int(100.0 * float(res.group(1)) / self.duration)) + '%]'
                }))
    def abortProcess(self): # Cannot send "q" because it's not a shell'd subprocess. Got to kill ffmpeg.
        Damnlog('I\'m gonna kill dash nine, cause it\'s my time to shine.')
        self.abort = True # This prevents the converter from going to the next file
        try:
            killit = True
            if self.__dict__.has_key('profile'):
                if self.profile == -1:
                    killit = False
            Damnlog('Killing process?', killit)
            if killit:
                if DV.os == 'nt':
                    DamnSpawner('"' + DV.bin_path + 'taskkill.exe" /PID ' + str(self.process.pid) + ' /F').wait()
                elif DV.os == 'mac':
                    DamnSpawner('kill -SIGTERM ' + str(self.process.pid)).wait() # From http://www.cs.cmu.edu/~benhdj/Mac/unix.html but with SIGTERM instead of SIGSTOP
                else:
                    os.kill(self.process.pid, signal.SIGTERM)
                time.sleep(.5) # Wait a bit, let the files get unlocked
                try:
                    os.remove(self.outdir + self.tmpfilename)
                except:
                    pass # Maybe the file wasn't created yet
        except:
            Damnlog('Error while trying to stop encoding process.')
class DamnStreamCopy(thr.Thread):
    def __init__(self, s1, s2, buffer=1048576, background=True, closes1=True, closes2=True):
        Damnlog('DamnStreamCopy spawned, will rip', s1, 'to', s2, ' when started. Background?', background)
        self.s1 = s1
        if type(s1) in (type(u''), type('')):
            self.s1 = DamnOpenFile(DamnUnicode(s1), 'rb')
        self.s2 = s2
        if type(s2) in (type(u''), type('')):
            self.s2 = DamnOpenFile(DamnUnicode(s2), 'wb')
        self.background = background
        self.buffer = buffer
        self.closes1 = closes1
        self.closes2 = closes2
        thr.Thread.__init__(self)
    def start(self):
        if self.background:
            Damnlog('Starting stream copy in background thread.')
            thr.Thread.start(self)
        else:
            Damnlog('Starting stream copy in current thread.')
            self.run()
    def run(self):
        firstread = True
        firstwrite = True
        Damnlog('Stream copy: Begin')
        i = 'Let\'s go'
        while len(i):
            try:
                i = self.s1.read(self.buffer)
                if firstread:
                    Damnlog('Stream copy: first read successful, read', len(i), 'bytes.')
                    firstread = False
                try:
                    self.s2.write(i)
                    if firstwrite:
                        Damnlog('Stream copy: first write successful, wrote ', len(i), 'bytes.')
                        firstwrite = False
                except Exception, e:
                    Damnlog('Stream copy: failed to write', len(i), 'bytes to output stream:',e)
            except:
                Damnlog('Stream copy: Failed to read from input stream.')
        Damnlog('Stream copying done.')
        if self.closes1:
            try:
                self.s1.close()
            except:
                Damnlog('Stream copy: closing input stream failed.')
        if self.closes2:
            try:
                self.s2.close()
            except:
                Damnlog('Stream copy: closing output stream failed.')
class DamnDownloader(thr.Thread): # Retrieves video by HTTP and feeds it back to ffmpeg via stdin
    def __init__(self, uri, pipe, copy=None):
        Damnlog('DamnDownloader spawned. URI:', uri, '; Pipe:', pipe)
        self.uri = uri
        self.pipe = pipe
        self.copy = copy
        thr.Thread.__init__(self)
    def timeouterror(self):
        Damnlog('DamnDownloader timeout detection timer fired!')
        self.timeouted = True
        self.http.close()
    def run(self):
        self.amountwritten = 0
        self.timeouted = True
        Damnlog('DamnDownloader starting download for first time.')
        while self.timeouted:
            self.timeouted = False
            self.goDownload()
            Damnlog('DamnDownloader goDownload subroutine done. Total written is', self.amountwritten, 'bytes. Timeout?', self.timeouted)
    def goDownload(self):
        self.http = DamnURLPicker(self.uri, resumeat=self.amountwritten)
        if self.http == None:
            try:
                self.pipe.close() # This tells ffmpeg that it's the end of the stream
            except:
                pass
            return None
        writing = ''
        direct = False
        if self.copy != None:
            copystream = DamnOpenFile(self.copy, 'wb')
        i = 'letsgo'
        while len(i):
            tmptimer = thr.Timer(DV.streamTimeout, self.timeouterror)
            tmptimer.start()
            try:
                i = self.http.read(1024)
                tmptimer.cancel()
            except:
                Damnlog('DamnDownloader stream timeout from exception handler.')
                self.timeouted = True
                break
            if True:
                if direct:
                    self.pipe.write(i)
                    if self.copy != None:
                        copystream.write(i)
                else:
                    writing += i
                    if len(writing) > 102400: # Cache the first 100 KB and write them all at once (solves ffmpeg's "moov atom not found" problem)
                        self.pipe.write(writing)
                        if self.copy != None:
                            copystream.write(writing)
                        direct = True
                        del writing
            else:
                break
            self.amountwritten += len(i)
        if not direct:  # Video weighs less than 100 KB (!)
            try:
                self.pipe.write(writing)
                if self.copy != None:
                    copystream.write(writing)
            except:
                pass
        try:
            self.http.close()
        except:
            pass
        try:
            self.pipe.close() # This tells ffmpeg that it's the end of the stream
        except:
            pass
        try:
            copystream.close() # Might not be defined, but doesn't matter
        except:
            pass
class DamnMainFrame(DamnFrame): # The main window
    def __init__(self, parent, id, title):
        Damnlog('DamnMainFrame GUI building starting.')
        DamnFrame.__init__(self, parent, wx.ID_ANY, title, size=(780, 580), style=wx.DEFAULT_FRAME_STYLE)
        self.CreateStatusBar()
        filemenu = wx.Menu()
        menu_addfile = wx.MenuItem(filemenu, -1, DV.l('&Add files...'), DV.l('Adds damn videos from local files.'))
        filemenu.AppendItem(menu_addfile)
        self.Bind(wx.EVT_MENU, self.onAddFile, menu_addfile)
        menu_addurl = wx.MenuItem(filemenu, -1, DV.l('Add &URL...'), DV.l('Adds a damn video from a URL.'))
        filemenu.AppendItem(menu_addurl)
        self.Bind(wx.EVT_MENU, self.onAddURL, menu_addurl)
        self.historymenu = wx.Menu()
        filemenu.AppendMenu(-1, DV.l('Add from &history...'), self.historymenu, DV.l('Adds a damn video from the video history.'))
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_EXIT, DV.l('E&xit'), DV.l('Terminates DamnVid.'))
        self.Bind(wx.EVT_MENU, self.onExit, id=ID_MENU_EXIT)
        vidmenu = wx.Menu()
        menu_letsgo = wx.MenuItem(vidmenu, -1, DV.l('Let\'s &go!'), DV.l('Processes all the videos in the list.'))
        vidmenu.AppendItem(menu_letsgo)
        self.Bind(wx.EVT_MENU, self.onGo, menu_letsgo)
        vidmenu.AppendSeparator()
        self.prefmenuitem = vidmenu.Append(ID_MENU_PREFERENCES, DV.l('Preferences'), DV.l('Opens DamnVid\'s preferences, allowing you to customize its settings.'))
        self.Bind(wx.EVT_MENU, self.onPrefs, id=ID_MENU_PREFERENCES)
        halpmenu = wx.Menu()
        halpmenu.Append(ID_MENU_HALP, DV.l('&Help'), DV.l('Opens DamnVid\'s help.'))
        self.Bind(wx.EVT_MENU, self.onHalp, id=ID_MENU_HALP)
        menu_reportbug = wx.MenuItem(halpmenu, -1, DV.l('Report a bug'), DV.l('Submit a new bug report.'))
        halpmenu.AppendItem(menu_reportbug)
        self.Bind(wx.EVT_MENU, self.onReportBug, menu_reportbug)
        menu_checkupdates = wx.MenuItem(halpmenu, -1, DV.l('Check for updates...'), DV.l('Checks if a new version of DamnVid is available.'))
        halpmenu.AppendItem(menu_checkupdates)
        self.Bind(wx.EVT_MENU, self.onCheckUpdates, menu_checkupdates)
        halpmenu.AppendSeparator()
        halpmenu.Append(ID_MENU_ABOUT, DV.l('&About DamnVid ') + DV.version + '...', DV.l('Displays information about DamnVid.'))
        self.Bind(wx.EVT_MENU, self.onAboutDV, id=ID_MENU_ABOUT)
        self.menubar = wx.MenuBar()
        self.menubar.Append(filemenu, DV.l('&File'))
        self.menubar.Append(vidmenu, DV.l('&DamnVid'))
        self.menubar.Append(halpmenu, DV.l('&Help'))
        self.SetMenuBar(self.menubar)
        Damnlog('DamnMainFrame menu bar is up.')
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        #vbox.Add((0,DV.border_padding)) Actually, do NOT add a padding there, it looks better when stuck on the edge
        panel = wx.Panel(self, -1)
        vbox.Add(panel, 1, wx.EXPAND)
        grid = wx.FlexGridSizer(2, 2, 8, 8)
        panel1 = wx.Panel(panel, -1)
        grid.Add(panel1, 1, wx.EXPAND)
        panel2 = wx.Panel(panel, -1)
        grid.Add(panel2, 0, wx.EXPAND)
        panel3 = wx.Panel(panel, -1)
        grid.Add(panel3, 0, wx.EXPAND)
        panel4 = wx.Panel(panel, -1)
        grid.Add(panel4, 0, wx.EXPAND)
        panel.SetSizer(grid)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        #hbox1.Add((DV.border_padding,0)) Ditto
        panel1.SetSizer(hbox1)
        self.list = DamnList(panel1, window=self)
        self.list.InsertColumn(ID_COL_VIDNAME, DV.l('Video name'))
        self.list.SetColumnWidth(ID_COL_VIDNAME, width=180)
        self.list.InsertColumn(ID_COL_VIDPROFILE, DV.l('Encoding profile'))
        self.list.SetColumnWidth(ID_COL_VIDPROFILE, width=120)
        self.list.InsertColumn(ID_COL_VIDSTAT, DV.l('Status'))
        self.list.SetColumnWidth(ID_COL_VIDSTAT, width=120)
        self.list.InsertColumn(ID_COL_VIDPATH, DV.l('Source'))
        self.list.SetColumnWidth(ID_COL_VIDPATH, wx.LIST_AUTOSIZE)
        self.list.Bind(wx.EVT_KEY_DOWN, self.onListKeyDown)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelect)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSelect)
        DV.listicons.initWX()
        self.list.AssignImageList(DV.listicons, wx.IMAGE_LIST_SMALL)
        self.list.SetDropTarget(DamnDropHandler(self))
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.list.onRightClick)
        hbox1.Add(self.list, 1, wx.EXPAND)
        Damnlog('DamnMainFrame MainList is up.')
        vboxwrap2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        vboxwrap2.Add(sizer2)
        vboxwrap2.Add((DV.border_padding, 0))
        sizer2.Add((0, DV.border_padding))
        panel2.SetSizer(vboxwrap2)
        self.droptarget = wx.animate.GIFAnimationCtrl(panel2, -1, DV.images_path + 'droptarget.gif')
        self.droptarget.Bind(wx.EVT_LEFT_UP, self.onDropTargetClick)
        sizer2.Add(self.droptarget, 0, wx.ALIGN_CENTER)
        self.droptarget.SetDropTarget(DamnDropHandler(self))
        # Extra forced gap here
        sizer2.Add((0, DV.control_vgap + 4))
        self.addByFile = wx.Button(panel2, -1, DV.l('Add Files'))
        sizer2.Add(self.addByFile, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onAddFile, self.addByFile)
        self.addByURL = wx.Button(panel2, -1, DV.l('Add URL'))
        sizer2.Add(self.addByURL, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onAddURL, self.addByURL)
        self.btnSearch = wx.Button(panel2, -1, DV.l('Search...'))
        sizer2.Add(self.btnSearch, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onSearch, self.btnSearch)
        self.btnRename = wx.Button(panel2, -1, DV.l('Rename'))
        sizer2.Add(self.btnRename, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onRename, self.btnRename)
        self.profilepanel = wx.Panel(panel2, -1)
        profilepanelsizer = wx.BoxSizer(wx.VERTICAL)
        self.profilepanel.SetSizer(profilepanelsizer)
        profilepanelsizer.Add(wx.StaticText(self.profilepanel, -1, DV.l('Profile:')), 0, wx.ALIGN_CENTER)
        self.profiledropdown = wx.Choice(self.profilepanel, -1, choices=[DV.l('(None)')])
        profilepanelsizer.Add((0, DV.control_vgap))
        profilepanelsizer.Add(self.profiledropdown, 0, wx.ALIGN_CENTER)
        sizer2.Add(self.profilepanel)
        tmplistheight = self.profiledropdown.GetSizeTuple()[1]
        self.profilepanel.Hide()
        sizer2.Add((0, DV.control_vgap))
        self.btnMoveUp = wx.Button(panel2, -1, DV.l('Move up'))
        sizer2.Add(self.btnMoveUp, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onMoveUp, self.btnMoveUp)
        self.btnMoveDown = wx.Button(panel2, -1, DV.l('Move down'))
        sizer2.Add(self.btnMoveDown, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onMoveDown, self.btnMoveDown)
        self.deletebutton = wx.Button(panel2, -1, DV.l('Remove'))
        sizer2.Add(self.deletebutton, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.control_vgap))
        self.Bind(wx.EVT_BUTTON, self.onDelete, self.deletebutton)
        self.gobutton1 = wx.Button(panel2, -1, DV.l('Let\'s go!'))
        sizer2.Add(self.gobutton1, 0, wx.ALIGN_CENTER)
        sizer2.Add((0, DV.border_padding))
        buttonwidth = sizer2.GetMinSizeTuple()[0]
        self.Bind(wx.EVT_BUTTON, self.onGo, self.gobutton1)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3.Add((DV.border_padding, 0))
        panel3.SetSizer(hbox3)
        hbox3.Add(wx.StaticText(panel3, -1, DV.l('Current video: ')), 0, wx.ALIGN_CENTER_VERTICAL)
        self.gauge1 = wx.Gauge(panel3, -1)
        self.gauge1.SetSize((self.gauge1.GetSizeTuple()[0], hbox3.GetSizeTuple()[1]))
        hbox3.Add(self.gauge1, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
        #self.gobutton2=wx.Button(bottompanel,-1,'Let\'s go!')
        #self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton2)
        #grid.Add(wx.StaticText(bottompanel,-1,''),0)
        #grid.Add(self.gobutton2,0)
        #grid.Add(wx.StaticText(bottompanel,-1,'Total progress:'),0)
        #self.gauge2=wx.Gauge(bottompanel,-1)
        #grid.Add(self.gauge2,1,wx.EXPAND)
        hboxwrapper4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.VERTICAL)
        hboxwrapper4.Add(hbox4)
        hboxwrapper4.Add((0, DV.border_padding))
        panel4.SetSizer(hboxwrapper4)
        self.stopbutton = wx.Button(panel4, -1, DV.l('Stop'))
        for button in (self.addByFile, self.addByURL, self.btnRename, self.btnMoveUp, self.btnMoveDown, self.deletebutton, self.gobutton1, self.stopbutton, self.btnSearch):
            button.SetMinSize((buttonwidth, button.GetSizeTuple()[1]))
        self.profiledropdown.SetMinSize((buttonwidth, tmplistheight))
        self.profiledropdown.Bind(wx.EVT_CHOICE, self.onChangeProfileDropdown)
        self.profilepanel.Show()
        hbox4.Add(self.stopbutton)
        hbox4.Add((0, DV.border_padding))
        #vbox.Add((0,DV.border_padding)) Ditto
        self.stopbutton.Disable()
        self.Bind(wx.EVT_BUTTON, self.onStop, self.stopbutton)
        grid.AddGrowableRow(0, 1)
        grid.AddGrowableCol(0, 1)
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(DV.evt_prog, self.onProgress)
        self.Bind(DV.evt_load, self.onLoading)
        Damnlog('DamnMainFrame: All GUI is up.')
        self.clipboardtimer = wx.Timer(self, -1)
        self.clipboardtimer.Start(1000)
        self.Bind(wx.EVT_TIMER, self.onClipboardTimer, self.clipboardtimer)
        Damnlog('DaminMainFrame: Clipboard timer started.')
        DV.icon = wx.Icon(DV.images_path + 'icon.ico', wx.BITMAP_TYPE_ICO)
        #DV.icon2 = wx.Icon(DV.images_path + 'icon-alt.ico', wx.BITMAP_TYPE_ICO)
        DV.icon16 = wx.Icon(DV.images_path + 'icon16.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(DV.icon)
        Damnlog('DamnMainFrame: init stage 1 done.')
    def init2(self):
        Damnlog('Starting DamnMainFrame init stage 2.')
        if os.path.exists(DV.conf_file_directory + 'lastversion.damnvid'):
            lastversion = DamnOpenFile(DV.conf_file_directory + 'lastversion.damnvid', 'r')
            dvversion = lastversion.readline().strip()
            lastversion.close()
            del lastversion
            Damnlog('Version file found; version number read:',dvversion)
        else:
            dvversion = 'old' # This is not just an arbitrary erroneous value, it's actually handy in the concatenation on the wx.FileDialog line below
            Damnlog('No version file found.')
        Damnlog('Read version:',dvversion,';running version:',DV.version)
        if dvversion != DV.version: # Just updated to new version, ask what to do about the preferences
            #dlg = wx.MessageDialog(self, DV.l('DamnVid was updated to ') + DV.version + '.\n' + DV.l('locale:damnvid-updated-export-prefs'), DV.l('DamnVid was successfully updated'), wx.YES | wx.NO | wx.ICON_QUESTION)
            tmpprefs = DamnVidPrefs()
            try:
                checkupdates = tmpprefs.get('CheckForUpdates')
                locale = tmpprefs.get('locale')
            except:
                pass
            Damnlog('Check for updates preference is',checkupdates)
            if False: #dlg.ShowModal() == wx.ID_YES:
                dlg.Destroy()
                dlg = wx.FileDialog(self, DV.l('Where do you want to export DamnVid\'s configuration?'), tmpprefs.get('lastprefdir'), 'DamnVid-' + dvversion + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
                if dlg.ShowModal() == wx.ID_OK:
                    path = dlg.GetPath()
                    f = DamnOpenFile(path, 'w')
                    tmpprefs.ini.write(f)
                    f.close()
                dlg.Destroy()
            else:
                pass
            # Now, overwrite the preferences!
            del tmpprefs
            os.remove(DV.conf_file)
            shutil.copyfile(DV.curdir + 'conf' + DV.sep + 'conf.ini', DV.conf_file)
            lastversion = DamnOpenFile(DV.conf_file_directory + 'lastversion.damnvid', 'w')
            lastversion.write(DV.version.encode('utf8'))
            lastversion.close()
            del lastversion
            tmpprefs = DamnVidPrefs()
            try:
                tmpprefs.set('CheckForUpdates', checkupdates)
                tmpprefs.set('locale', locale)
            except:
                pass
            tmpprefs.save()
            del tmpprefs
        Damnlog('Local version check done, initializing DamnMainFrame properties.')
        self.videos = []
        self.clippedvideos = []
        self.resultlist = []
        self.thisbatch = 0
        self.thisvideo = []
        self.meta = {}
        DV.prefs = DamnVidPrefs()
        self.converting = -1
        self.isclosing = False
        self.searchopen = False
        self.addurl = None
        self.loadingvisible = 0
        self.trayicon = None
        self.onListSelect()
        Damnlog('DamnMainFrame properties OK, first run?',DV.first_run)
        if DV.first_run:
            dlg = wx.MessageDialog(self, DV.l('Welcome to DamnVid ') + DV.version + '!\n' + DV.l('Would you like DamnVid to check for updates every time it starts?'), DV.l('Welcome to DamnVid ') + DV.version + '!', wx.YES | wx.NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                DV.prefs.set('CheckForUpdates', 'True')
            else:
                DV.prefs.set('CheckForUpdates', 'False')
        if DV.prefs.get('CheckForUpdates') == 'True':
            Damnlog('DamnMainFrame checking for updates.')
            self.onCheckUpdates(None)
        self.SetStatusText(DV.l('DamnVid ready.'))
        windowpolicy = DV.prefs.get('windowpolicy')
        if not len(windowpolicy) or windowpolicy=='center':
            Damnlog('Window policy is centering.')
            self.Center()
        elif windowpolicy=='remember':
            Damnlog('Window policy is remember; trying to load saved window geometry.')
            lastx = DV.prefs.gets('damnvid-mainwindow','lastx')
            lasty = DV.prefs.gets('damnvid-mainwindow','lasty')
            lastw = DV.prefs.gets('damnvid-mainwindow','lastw')
            lasth = DV.prefs.gets('damnvid-mainwindow','lasth')
            lastresw = DV.prefs.gets('damnvid-mainwindow','lastresw')
            lastresh = DV.prefs.gets('damnvid-mainwindow','lastresh')
            allstuff=(lastx,lasty,lastw,lasth,lastresw,lastresh)
            Damnlog('Old window geometry information:',allstuff)
            allstuff2=[]
            for i in allstuff:
                try:
                    allstuff2.append(int(i))
                except:
                    allstuff2.append(-1)
            if -1 in allstuff2:
                Damnlog('Invalid information in old window geometry information; giving up on restoring window geometry.')
            else:
                try:
                    screen = wx.Display().GetGeometry()[2:]
                    if allstuff2[4] != screen[0] or allstuff2[5]!= screen[1]:
                        Damnlog('Resolution information is different:',allstuff2[4:5],'vs',screen,'(current); giving up on restoring window geometry.')
                    elif allstuff[0] < 0 or allstuff[0] + allstuff[2] >= lastresw or allstuff[1] < 0 or allstuff[1] + allstuff[3] >= lasth:
                        Damnlog('Window position is out of bounds; giving up.')
                    else:
                        Damnlog('All window geometry tests passed, attempting to restore window geometry.')
                        try:
                            self.SetSizeWH(allstuff2[2],allstuff2[3])
                            self.MoveXY(allstuff2[0],allstuff2[1])
                            Damnlog('Window geometry restored successfully.')
                        except:
                            Damnlog('Window manager refused to change window geometry.')
                except:
                    Damnlog('Could not get screen resolution; giving up on restoring window geometry.')
        else:
            Damnlog('Window policy is',windowpolicy,'; doing nothing.')
        self.buildHistoryMenu()
        Damnlog('DamnMainFrame: Main window all ready,')
    def onMinimize(self, event):
        Damnlog('DamnMainFrame iconize event fired. Is being minimized?', event.Iconized())
        if self.isclosing:
            Damnlog('DamnMainFrame being closed, not interfering.')
            return
        if not event.Iconized():
            Damnlog('DamnMainFrame being restored, doing nothing.')
            return
        if DV.prefs.get('minimizetotray')=='True':
            Damnlog('Minimize to tray preference is True, creating tray icon.')
            self.trayicon = DamnTrayIcon(self)
        else:
            Damnlog('Minimize to tray preference is False, doing nothing.')
    def onExit(self, event):
        self.Close(True)
    def onListSelect(self, event=None):
        sel = self.list.getAllSelectedItems()
        gotstuff = bool(len(sel))
        self.btnRename.Enable(len(sel) == 1)
        self.profiledropdown.Enable(gotstuff)
        if gotstuff:
            self.deletebutton.SetLabel(DV.l('Remove'))
            self.btnMoveUp.Enable(sel[0])
            self.btnMoveDown.Enable(sel[-1] != self.list.GetItemCount() - 1)
            choices = []
            uniprofile = int(self.meta[self.videos[sel[0]]]['profile'])
            for i in sel:
                if int(self.meta[self.videos[i]]['profile']) != uniprofile:
                    uniprofile = -2
            for p in range(-1, DV.prefs.profiles):
                choices.append(DV.l(DV.prefs.getp(p, 'name'), warn=False))
            if uniprofile == -2:
                choices.insert(0, DV.l('(Multiple)'))
            self.profiledropdown.SetItems(choices)
            if uniprofile == -2:
                self.profiledropdown.SetSelection(0)
            else:
                self.profiledropdown.SetSelection(uniprofile + 1)
        else:
            self.deletebutton.SetLabel(DV.l('Remove all'))
            self.btnMoveUp.Disable()
            self.btnMoveDown.Disable()
            self.profiledropdown.SetItems([DV.l('(None)')])
    def onListKeyDown(self, event):
        if (event.GetKeyCode() == 8 or event.GetKeyCode() == 127) and self.list.GetSelectedItemCount(): # Backspace or delete, but only when there's at least one selected video
            self.onDelSelection(None)
    def onAddFile(self, event):
        d = os.getcwd()
        if os.path.exists(DV.prefs.get('LastFileDir')):
            if os.path.isdir(DV.prefs.get('LastFileDir')):
                d = DV.prefs.get('LastFileDir')
        elif os.path.exists(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
            if os.path.isdir(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
                d = DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')
        dlg = wx.FileDialog(self, DV.l('Choose a damn video.'), d, '', DV.l('locale:browse-video-files'), wx.OPEN | wx.FD_MULTIPLE)
        dlg.SetIcon(DV.icon)
        if dlg.ShowModal() == wx.ID_OK:
            vids = dlg.GetPaths()
            DV.prefs.set('LastFileDir', os.path.dirname(vids[0]))
            DV.prefs.save()
            self.addVid(vids)
        dlg.Destroy()
    def onAddURL(self, event):
        Damnlog('onAddURL event fired:',event)
        default = ''
        try:
            if wx.TheClipboard.Open():
                dataobject = wx.TextDataObject()
                wx.TheClipboard.GetData(dataobject)
                default = dataobject.GetText()
                wx.TheClipboard.Close()
                Damnlog('Text scavenged from clipboard:',default)
                if not self.validURI(default):
                    default = '' # Only set that as default text if the clipboard's text content is not a URL
        except:
            default = ''
        try:
            wx.TheClipboard.Close() # In case there's been an error before the clipboard could be closed, try to close it now
        except:
            pass # There's probably wasn't any error, just pass
        self.addurl = DamnAddURLDialog(self, default)
        self.addurl.SetIcon(DV.icon)
        self.addurl.ShowModal()
        try:
            self.addurl.Destroy()
        except:
            pass # The addurl destroys itself, supposedly, and doing it again sometimes (sometimes!) generates errors.
        self.addurl = None
    def validURI(self, uri):
        if REGEX_HTTP_GENERIC.match(uri):
            for i in DamnIterModules(False):
                if i['class'](uri).validURI():
                    return 'Video site'
            return 'Online video' # Not necessarily true, but ffmpeg will tell
        elif os.path.exists(uri):
            return 'Local file'
        return None
    def getVidName(self, uri):
        try:
            html = DamnURLOpen(uri[3:])
            for i in html:
                res = REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
                if res:
                    return DamnHtmlEntities(res.group(1)).strip()
        except:
            pass # Can't grab this? Return Unknown title
        return DV.l('Unknown title')
    def onDropTargetClick(self, event):
        dlg = wx.MessageDialog(self, DV.l('This is a droptarget: You may drop video files and folders here (or in the big list as well).'), DV.l('DamnVid Droptarget'), wx.ICON_INFORMATION)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def toggleLoading(self, show):
        isvisible = self.loadingvisible > 0
        self.loadingvisible = max((0, self.loadingvisible + int(show) * 2 - 1))
        if (isvisible and not self.loadingvisible) or (not isvisible and self.loadingvisible):
            wx.PostEvent(self, DamnLoadingEvent(DV.evt_loading, -1, {'show':bool(self.loadingvisible)}))
    def onLoading(self, event):
        info = event.GetInfo()
        if info.has_key('show'):
            if info['show']:
                self.droptarget.LoadFile(DV.images_path + 'droptargetloading.gif')
                self.droptarget.Play()
            else:
                self.droptarget.Stop()
                self.droptarget.LoadFile(DV.images_path + 'droptarget.gif')
        if info.has_key('status'):
            self.SetStatusText(info['status'])
        if info.has_key('dialog'):
            dlg = wx.MessageDialog(self, info['dialog'][1], info['dialog'][0], info['dialog'][2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        if info.has_key('meta'):
            self.addValid(info['meta'])
        if info.has_key('go') and self.converting == -1:
            if info['go']:
                self.onGo()
        if info.has_key('updateinfo'):
            if info['updateinfo'].has_key('verbose'):
                verbose = info['updateinfo']['verbose']
            else:
                verbose = True
            if info['updateinfo'].has_key('main'):
                if info['updateinfo']['main'] is not None:
                    msg = None
                    if DamnVersionCompare(info['updateinfo']['main'], DV.version) == 1 and type(info['updateinfo']['main']) is type(''):
                        dlg = wx.MessageDialog(self, DV.l('A new version (') + info['updateinfo']['main'] + DV.l(') is available! You are running DamnVid ') + DV.version + '.\n' + DV.l('Want to go to the download page and download the update?'), DV.l('Update available!'), wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_INFORMATION)
                        dlg.SetIcon(DV.icon)
                        if dlg.ShowModal() == wx.ID_YES:
                            webbrowser.open(DV.url_download, 2)
                        dlg.Destroy()
                    elif verbose and type(info['updateinfo']['main']) is type(''):
                        if DV.version != info['updateinfo']['main']:
                            versionwarning = DV.l(' However, your version (') + DV.version + DV.l(') seems different than the latest version available online. Where would you get that?')
                        else:
                            versionwarning = ''
                        msg = (DV.l('DamnVid is up-to-date.'), DV.l('DamnVid is up-to-date! The latest version is ') + info['updateinfo']['main'] + '.' + versionwarning, wx.ICON_INFORMATION)
                    elif verbose:
                        msg = (DV.l('Error!'), DV.l('There was a problem while checking for updates. You are running DamnVid ') + DV.version + '.\n' + DV.l('Make sure you are connected to the Internet, and that no firewall is blocking DamnVid.'), wx.ICON_INFORMATION)
                    if msg is not None:
                        dlg = wx.MessageDialog(self, msg[1], msg[0], msg[2])
                        dlg.SetIcon(DV.icon)
                        dlg.ShowModal()
                        dlg.Destroy()
            if info['updateinfo'].has_key('modules'):
                msg = []
                for i in info['updateinfo']['modules'].iterkeys():
                    if type(info['updateinfo']['modules'][i]) is type(()):
                        msg.append((True, DV.modules[i]['title'] + DV.l(' was updated to version ') + info['updateinfo']['modules'][i][0] + '.'))
                    elif type(info['updateinfo']['modules'][i]) is type('') and verbose:
                        if info['updateinfo']['modules'][i] == 'error':
                            msg.append((False, DV.modules[i]['title'] + DV.l(' is up-to-date (version ') + DV.modules[i]['version'] + ').'))
                if len(msg):
                    msgs = []
                    for i in msg:
                        if i[0]:
                            msgs.append(i[1])
                    if not len(msg) and verbose:
                        msgs = msg
                    if len(msgs):
                        msg = DV.l('DamnVid also checked for updates to its modules.') + '\n'
                        for i in msgs:
                            msg += '\n' + i
                        dlg = wx.MessageDialog(self, msg, DV.l('Module updates'), wx.ICON_INFORMATION)
                        dlg.SetIcon(DV.icon)
                        dlg.ShowModal()
                        dlg.Destroy()
    def buildHistoryMenu(self):
        Damnlog('Clearing video history menu.')
        for i in self.historymenu.GetMenuItems():
            self.historymenu.DestroyItem(i)
        history = DV.prefs.geta('damnvid-videohistory','videos')
        histsize = int(DV.prefs.get('videohistorysize'))
        Damnlog('Video history is',history,'; history size is',histsize)
        if not histsize:
            Damnlog('Histize is zero, disabling feature.')
            self.historymenu.Append(-1, DV.l('Feature disabled'), DV.l('This feature is disabled because you set the history size to 0.'))
        else:
            Damnlog('Histsize is not 0, building history menu.')
            menuitems = []
            for i in range(min(histsize,len(history))):
                video = history[i].split(u'|')
                Damnlog('Creating history menu item for video',video)
                if len(video) != 2:
                    Damnlog('Size of video array is not 2; aborting.')
                    continue
                menuitems.append(wx.MenuItem(self.historymenu, -1, DamnUnicode(video[0]), DamnUnicode(video[1])))
                self.historymenu.Bind(wx.EVT_MENU, DamnCurry(self.onHistoryVideoMenu, video), menuitems[-1])
                self.Bind(wx.EVT_MENU, DamnCurry(self.onHistoryVideoMenu, video), menuitems[-1])
                self.historymenu.AppendItem(menuitems[-1])
            if len(history):
                self.historymenu.AppendSeparator()
                clearhistory = wx.MenuItem(self.historymenu, -1, DV.l('(Clear history)'), DV.l('Clears the video history.'))
                self.historymenu.AppendItem(clearhistory)
                self.historymenu.Bind(wx.EVT_MENU, self.clearHistory, clearhistory)
                self.Bind(wx.EVT_MENU, self.clearHistory, clearhistory)
            else:
                self.historymenu.Append(-1, DV.l('(Empty history)'), DV.l('The video history is empty.'))
            Damnlog('Done building video history menu.')
    def onHistoryVideoMenu(self, video, event=None):
        self.addVid([video[1]], DV.prefs.get('autoconvert') == 'True')
    def clearHistory(self, *args):
        DV.prefs.seta('damnvid-videohistory','videos',[])
        self.buildHistoryMenu()
    def addVid(self, uris, thengo=False):
        DamnVideoLoader(self, uris, thengo).start()
    def addTohistory(self, title, uri):
        uri = DamnUnicode(uri)
        title = DamnUnicode(title)
        Damnlog('Adding video to history:',title,'with URI',uri)
        history = DV.prefs.geta('damnvid-videohistory','videos')
        histsize = int(DV.prefs.get('videohistorysize'))
        if not histsize:
            Damnlog('Histsize is zero, not touching anything.')
            return
        for i in history:
            tempvideo = i.split(u'|')
            if len(tempvideo) != 2:
                Damnlog('Invalid entry in history:',i)
                continue
            if tempvideo[1].strip().lower() == uri.strip().lower():
                Damnlog('URI',uri,'is already in history, not adding it to history again.')
                return
        history.reverse()
        while len(history) >= histsize:
            history = history[1:]
        history.append(u'|'.join([DamnUnicode(title),DamnUnicode(uri)]))
        history.reverse()
        DV.prefs.seta('damnvid-videohistory','videos',history)
        Damnlog('Video added successfully, rebuilding history menu.')
        self.buildHistoryMenu()
    def addValid(self, meta):
        Damnlog('Adding video to DamnList with meta:',meta)
        self.addTohistory(meta['name'], meta['original'])
        curvid = len(self.videos)
        self.list.InsertStringItem(curvid, meta['name'])
        self.list.SetStringItem(curvid, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(meta['profile'], 'name')))
        self.list.SetStringItem(curvid, ID_COL_VIDPATH, meta['dirname'])
        self.list.SetStringItem(curvid, ID_COL_VIDSTAT, meta['status'])
        self.list.SetItemImage(curvid, meta['icon'], meta['icon'])
        self.videos.append(meta['uri'])
        self.meta[meta['uri']] = meta
        self.SetStatusText(DV.l('Added ') + meta['name'] + '.')
        if self.addurl is not None:
            self.addurl.update(meta['original'], meta['name'], meta['icon'])
        self.onListSelect()
    def onProgress(self, event):
        info = event.GetInfo()
        if info.has_key('progress'):
            self.gauge1.SetValue(info['progress'])
        if info.has_key('statustext'):
            self.SetStatusText(info['statustext'])
        if info.has_key('status'):
            self.list.SetStringItem(self.converting, ID_COL_VIDSTAT, info['status'])
            if self.trayicon is not None:
                self.trayicon.setTooltip(DamnUnicode(self.meta[self.videos[self.converting]]['name'])+u': '+info['status'])
        if info.has_key('dialog'):
            dlg = wx.MessageDialog(self, info['dialog'][0], info['dialog'][1], info['dialog'][2])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        if info.has_key('go'):
            self.go(info['go'])
    def go(self, aborted=False):
        self.converting = -1
        for i in range(len(self.videos)):
            if self.videos[i] not in self.thisvideo and self.meta[self.videos[i]]['status'] != DV.l('Success!'):
                self.converting = i
                break
        if self.converting != -1 and not aborted: # Let's go for the actual conversion...
            self.meta[self.videos[self.converting]]['status'] = DV.l('In progress...')
            self.list.SetStringItem(self.converting, ID_COL_VIDSTAT, DV.l('In progress...'))
            self.thisbatch = self.thisbatch + 1
            self.thread = DamnConverter(parent=self)
            if self.trayicon is not None:
                self.trayicon.startAlternate()
            self.thread.start()
        else:
            if self.trayicon is not None:
                self.trayicon.stopAlternate()
            if not self.isclosing:
                self.SetStatusText(DV.l('DamnVid, waiting for instructions.'))
                dlg = DamnDoneDialog(content=self.resultlist, aborted=aborted, main=self)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
                self.converting = -1
                self.stopbutton.Disable()
                self.gobutton1.Enable()
                self.gauge1.SetValue(0.0)
    def onGo(self, event=None):
        if not len(self.videos):
            dlg = wx.MessageDialog(None, DV.l('Put some videos in the list first!'), DV.l('No videos!'), wx.ICON_EXCLAMATION | wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        elif self.converting != -1:
            dlg = wx.MessageDialog(None, DV.l('DamnVid is already converting!'), DV.l('Already converting!'), wx.ICON_EXCLAMATION | wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            success = 0
            for i in self.videos:
                if self.meta[i]['status'] == DV.l('Success!'):
                    success = success + 1
            if success == len(self.videos):
                dlg = wx.MessageDialog(None, DV.l('All videos in the list have already been processed!'), DV.l('Already done'), wx.OK | wx.ICON_INFORMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.thisbatch = 0
                self.thisvideo = []
                self.resultlist = []
                self.stopbutton.Enable()
                self.gobutton1.Disable()
                self.go()
    def onStop(self, event):
        self.thread.abortProcess()
    def onRename(self, event):
        item = self.list.getAllSelectedItems()
        if len(item) > 1:
            dlg = wx.MessageDialog(None, DV.l('You can only rename one video at a time.'), DV.l('Multiple videos selected.'), wx.ICON_EXCLAMATION | wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        elif not len(item):
            dlg = wx.MessageDialog(None, DV.l('Select a video in order to rename it.'), DV.l('No videos selected'), wx.ICON_EXCLAMATION | wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            item = item[0]
            dlg = wx.TextEntryDialog(None, DV.l('Enter the new name for "') + self.meta[self.videos[item]]['name'] + '".', DV.l('Rename'), self.meta[self.videos[item]]['name'])
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            self.meta[self.videos[item]]['name'] = dlg.GetValue()
            self.list.SetStringItem(item, ID_COL_VIDNAME, dlg.GetValue())
            dlg.Destroy()
    def onSearch(self, event):
        if not self.searchopen:
            self.searchopen = True
            self.searchdialog = DamnVidBrowser(self)
            self.searchdialog.Show()
        else:
            self.searchdialog.Raise()
    def invertVids(self, i1, i2):
        tmp = self.videos[i1]
        self.videos[i1] = self.videos[i2]
        self.videos[i2] = tmp
        tmp = self.list.IsSelected(i2)
        self.list.Select(i2, on=self.list.IsSelected(i1))
        self.list.Select(i1, on=tmp)
        self.list.invertItems(i1, i2)
        if i1 == self.converting:
            self.converting = i2
        elif i2 == self.converting:
            self.converting = i1
        self.onListSelect()
    def onMoveUp(self, event):
        items = self.list.getAllSelectedItems()
        if len(items):
            if items[0]:
                for i in items:
                    self.invertVids(i, i - 1)
            else:
                dlg = wx.MessageDialog(None, DV.l('You\'ve selected the first item in the list, which cannot be moved further up!'), DV.l('Invalid selection'), wx.OK | wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg = wx.MessageDialog(None, DV.l('Select some videos in the list first.'), DV.l('No videos selected!'), wx.OK | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        self.onListSelect()
    def onMoveDown(self, event):
        items = self.list.getAllSelectedItems()
        if len(items):
            if items[-1] < self.list.GetItemCount() - 1:
                for i in reversed(self.list.getAllSelectedItems()):
                    self.invertVids(i, i + 1)
            else:
                dlg = wx.MessageDialog(None, DV.l('You\'ve selected the last item in the list, which cannot be moved further down!'), DV.l('Invalid selection'), wx.OK | wx.ICON_EXCLAMATION)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            dlg = wx.MessageDialog(None, DV.l('Select some videos in the list first.'), DV.l('No videos selected!'), wx.OK | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
        self.onListSelect()
    def onChangeProfileDropdown(self, event):
        sel = self.profiledropdown.GetCurrentSelection()
        if self.profiledropdown.GetItems()[0] == '(Multiple)':
            sel = sel - 1
        if sel != -1:
            self.onChangeProfile(sel - 1, event)
    def onChangeProfile(self, profile, event):
        items = self.list.getAllSelectedItems()
        for i in items:
            if self.meta[self.videos[i]]['profile'] != profile:
                self.meta[self.videos[i]]['profile'] = profile
                self.meta[self.videos[i]]['profilemodified'] = True
                self.list.SetStringItem(i, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(profile, 'name')))
        self.onListSelect()
    def onResetStatus(self, event=None):
        items = self.list.getAllSelectedItems()
        for i in items:
            self.meta[self.videos[i]]['status'] = DV.l('Pending.')
            self.list.SetStringItem(i, ID_COL_VIDSTAT, DV.l('Pending.'))
    def onPrefs(self, event):
        self.reopenprefs = False
        prefs = DamnVidPrefEditor(self, -1, DV.l('DamnVid preferences'), main=self)
        prefs.ShowModal()
        prefs.Destroy()
        if self.reopenprefs:
            self.onPrefs(event)
        else:
            for i in range(len(self.videos)):
                if self.meta[self.videos[i]]['profile'] >= DV.prefs.profiles or not self.meta[self.videos[i]]['profilemodified']:
                    # Yes, using icons as source identifiers, why not? Lol
                    if self.meta[self.videos[i]].has_key('module'):
                        self.meta[self.videos[i]]['profile'] = self.meta[self.videos[i]]['module'].getProfile()
                    elif self.meta[self.videos[i]]['icon'] == DamnGetListIcon('damnvid'):
                        self.meta[self.videos[i]]['profile'] = DV.prefs.get('defaultprofile')
                    elif self.meta[self.videos[i]]['icon'] == DamnGetListIcon('generic'):
                        self.meta[self.videos[i]]['profile'] = DV.prefs.get('defaultwebprofile')
                self.list.SetStringItem(i, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(self.meta[self.videos[i]]['profile'], 'name')))
        try:
            del self.reopenprefs
        except:
            pass
        self.buildHistoryMenu() # In case history size changed
        self.onListSelect()
    def onOpenOutDir(self, event):
        if DV.os == 'nt':
            os.system('explorer.exe "' + DV.prefs.get('outdir') + '"')
        else:
            pass # Halp here?
    def onHalp(self, event):
        webbrowser.open(DV.url_halp, 2)
    def onReportBug(self, event):
        dlg = DamnReportBug(None, -1, main=self)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def onCheckUpdates(self, event=None):
        updater = DamnVidUpdater(self, verbose=event is not None)
        updater.start()
    def onAboutDV(self, event):
        dlg = DamnAboutDamnVid(None, -1, main=self)
        dlg.SetIcon(DV.icon)
        dlg.ShowModal()
        dlg.Destroy()
    def delVid(self, i):
        self.list.DeleteItem(i)
        for vid in range(len(self.thisvideo)):
            if self.thisvideo[vid] == self.videos[i]:
                self.thisvideo.pop(vid)
                self.thisbatch = self.thisbatch - 1
        del self.meta[self.videos[i]]
        self.videos.pop(i)
        if self.converting > i:
            self.converting = self.converting - 1
    def onDelete(self, event):
        if len(self.list.getAllSelectedItems()):
            self.onDelSelection(event)
        else:
            self.onDelAll(event)
    def confirmDeletion(self):
        if DV.prefs.get('warnremove')!='True':
            return True
        dlg = wx.MessageDialog(None, DV.l('Are you sure? (This will not delete any files, it will just remove them from the list.)'), DV.l('Confirmation'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        dlg.SetIcon(DV.icon)
        return dlg.ShowModal() == wx.ID_YES
    def onDelSelection(self, event):
        items = self.list.getAllSelectedItems()
        if len(items):
            if self.converting in items:
                dlg = wx.MessageDialog(None, DV.l('Stop the video conversion before deleting the video being converted.'), DV.l('Cannot delete this video'), wx.ICON_EXCLAMATION | wx.OK)
                dlg.SetIcon(DV.icon)
                dlg.ShowModal()
                dlg.Destroy()
            elif self.confirmDeletion():
                for i in reversed(items): # Sequence MUST be reversed, otherwise the first items get deleted first, which changes the indexes of the following items
                    self.delVid(i)
            self.onListSelect()
        else:
            dlg = wx.MessageDialog(None, DV.l('You must select some videos from the list first!'), DV.l('Select some videos!'), wx.ICON_EXCLAMATION | wx.OK)
            dlg.SetIcon(DV.icon)
            dlg.ShowModal()
            dlg.Destroy()
    def onDelAll(self, event):
        if len(self.videos):
            if self.confirmDeletion():
                if self.converting != -1:
                    self.onStop(None) # Stop conversion if it's in progress
                self.list.DeleteAllItems()
                self.videos = []
                self.thisvideo = []
                self.thisbatch = 0
                self.meta = {}
        else:
            dlg = wx.MessageDialog(None, DV.l('Add some videos in the list first.'), DV.l('No videos!'), wx.OK | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            dlg.Destroy()
    def onResize(self, event):
        self.Layout()
    def onClipboardTimer(self, event):
        self.clipboardtimer.Stop()
        try:
            if DV.gui_ok and DV.prefs.get('clipboard') == 'True':
                if wx.TheClipboard.Open():
                    dataobject = wx.TextDataObject()
                    wx.TheClipboard.GetData(dataobject)
                    clip = dataobject.GetText()
                    wx.TheClipboard.Close()
                    if self.validURI(clip) == 'Video site' and clip not in self.clippedvideos:
                        self.clippedvideos.append(clip)
                        if self.addurl is not None:
                            self.addurl.onAdd(val=clip)
                        else:
                            self.addVid([clip], DV.prefs.get('autoconvert') == 'True')
        except:
            pass # The clipboard might not get opened properly, or the prefs object might not exist yet. Just silently pass, gonna catch up at next timer event.
        try:
            wx.TheClipboard.Close() # Try to close it, just in case it's left open.
        except:
            pass
        try:
            self.clipboardtimer.Start(1000)
        except:
            pass # Sometimes the timer can still live while DamnMainFrame is closed, and if EVT_TIMER is then raised, error!
    def onClose(self, event):
        Damnlog('Main window onClose event fired. Converting?', self.converting, '; Is already closing?', self.isclosing)
        if self.converting != -1:
            dlg = wx.MessageDialog(None, DV.l('DamnVid is currently converting a video! Closing DamnVid will cause it to abort the conversion.') + '\r\n' + DV.l('Continue?'), DV.l('Conversion in progress'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            dlg.SetIcon(DV.icon)
            if dlg.ShowModal() == wx.ID_YES:
                Damnlog('User forced shutdown!')
                self.shutdown()
        else:
            self.shutdown()
    def shutdown(self):
        Damnlog('Main window got shutdown() call')
        try:
            Damnlog('Attempting to get window position/size information.')
            position = self.GetPositionTuple()
            size = self.GetSize()
            screen = wx.Display().GetGeometry()[2:]
            Damnlog('Position is',position,'; size is',size,'; resolution is',screen)
            DV.prefs.sets('damnvid-mainwindow','lastx',position[0])
            DV.prefs.sets('damnvid-mainwindow','lasty',position[1])
            DV.prefs.sets('damnvid-mainwindow','lastw',size[0])
            DV.prefs.sets('damnvid-mainwindow','lasth',size[1])
            DV.prefs.sets('damnvid-mainwindow','lastresw',screen[0])
            DV.prefs.sets('damnvid-mainwindow','lastresh',screen[1])
        except:
            Damnlog('Error while trying to grab position/size information.')
        self.isclosing = True
        self.clipboardtimer.Stop()
        self.Destroy()
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
    DV.log.close()
    if DV.dumplocalewarnings:
        Damnlog('Starting locale warnings dump')
        try:
            f = DamnOpenFile('damnvid-locale-warnings.log', 'w')
            f.write(u'\n'.join(DV.locale_warnings).encode('utf8'))
            f.close()
            Damnlog('Successful locale warnings dump.')
        except:
            Damnlog('Failed to dump locale warnings.')
try:
    DamnMain()
except:
    try:
        Damnlog('Error in DamnMain!', traceback.format_exc())
    except:
        pass # Epic fail
# Done!
