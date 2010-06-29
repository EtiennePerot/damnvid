# -*- coding: utf-8 -*-
from dCore import *
from dLog import *
from dThread import *
import dSysInfo
import time
import random
import socket
import traceback
import cookielib
import gdata.youtube.service # YouTube service
import gdata.projecthosting.client # Google Code service
import BeautifulSoup
DV.blanksocket = socket.socket
DV.youtube_service = gdata.youtube.service.YouTubeService()
DV.youtube_service.ssl = False
DV.streamTimeout = 30.0
socket.setdefaulttimeout(DV.streamTimeout)
import urllib2
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
from dConfig import *
class DamnURLRequest(urllib2.Request):
	def __str__(self):
		return u'<DamnURLRequest of: ' + DamnUnicode(urllib2.Request.get_full_url(self)) + u'>'
	def __repr__(self):
		return self.__str__()
def DamnTimeoutStreamRead(stream, bytes=-1, timeout=None):
	if timeout is None:
		timeout = DV.streamTimeout
	t = DamnThreadedFunction(DamnCurry(stream.read, bytes), autostart=True)
	t.join(timeout)
	try:
		return t.getResult()
	except DamnThreadedFunctionNotDoneException:
		return None
class DamnResumableDownload:
	def __init__(self, req, data=None, resumeat=None, resumable=True, buffer=32768, autoopen=True, autofetch=True):
		Damnlog('DamnResumableDownload initiated with request', req, 'and data', data, '; Resumat at:', resumeat, '; Resumable:', resumable,'; Buffer size:', buffer, '; Auto-open:', autoopen,'; Auto-fetch:', autofetch)
		self.req = req
		self.url = req
		self.data = data
		self.resumable = resumable
		self.buffersize = buffer
		self.buffer = ''
		if type(req) in (type(''), type(u'')):
			req = DamnURLRequest(DamnUnicode(req))
		self.stream = None
		self.progress = 0
		if resumeat is not None:
			self.progress = resumeat
		self.fetchThread = None
		self.autofetch = autofetch
		self.hasTimeout = False
		if autoopen:
			self.open()
		if self.autofetch:
			self.spawnFetcher()
	def __str__(self):
		return u'<DamnResumableDownload of: ' + DamnUnicode(self.url) + u'>'
	def __repr__(self):
		return self.__str__()
	def open(self):
		Damnlog('DamnResumableDownload opening', self.url)
		if self.stream is not None:
			self.close()
		if self.progress > 0:
			self.req.add_header('Range', 'bytes=' + str(self.progress) + '-')
		try:
			self.stream = urllib2.urlopen(self.req)
			return self.stream
		except urllib2.URLError, e:
			Damnlog('! DamnResumableDownload failed opening with URLError', e, 'on', self.url)
			if hasattr(e, 'code'):
				Damnlog('!! DamnResumableDownload opening URLError has code', e.code, 'on', self.url,'; raising exception.')
				raise e
		except socket.timeout, e:
			Damnlog('! DamnResumableDownload failed opening with socket timeout error', e, 'on', self.url)
		except socket.error, e:
			Damnlog('! DamnResumableDownload failed opening with socket error', e, 'on', self.url)
		except Exception, e:
			Damnlog('! DamnResumableDownload failed opening with unknown error', e, 'on', self.url)
			self.hasTimeout = True
		time.sleep(DV.streamTimeout/2)
		self.open()
	def info(self):
		self.ensureOpen()
		return self.stream.info()
	def ensureOpen(self):
		if self.stream is None:
			self.open()
	def timeout(self):
		Damnlog('DamnResumableDownload timeout error for', self.url)
		self.hasTimeout = True
		self.close()
	def fetchBuffer(self):
		if self.hasTimeout:
			time.sleep(DV.streamTimeout/2) # Sleep for a bit before giving it another shot
		self.hasTimeout = False
		self.ensureOpen()
		try:
			c = DamnTimeoutStreamRead(self.stream, self.buffersize)
			if c is None:
				Damnlog('! DamnResumableDownload got None while trying to read stream of', self.url)
				self.hasTimeout = True
		except urllib2.URLError, e:
			Damnlog('! DamnResumableDownload failed reading with URLError', e, 'on', self.url)
			if hasattr(e, 'code'):
				Damnlog('!! DamnResumableDownload reading URLError has code', e.code, 'on', self.url,'; raising exception.')
				raise e
			self.hasTimeout = True
		except socket.timeout, e:
			Damnlog('! DamnResumableDownload failed reading with socket timeout error', e, 'on', self.url)
			self.hasTimeout = True
		except socket.error, e:
			Damnlog('! DamnResumableDownload failed reading with socket error', e, 'on', self.url)
			self.hasTimeout = True
		except Exception, e:
			Damnlog('! DamnResumableDownload failed reading with unknown error', e, 'on', self.url)
			self.hasTimeout = True
		if self.hasTimeout:
			self.close()
			return self.fetchBuffer()
		self.buffer += c
		self.progress += len(c)
	def spawnFetcher(self):
		self.fetchThread = DamnThreadedFunction(self.fetchBuffer, autostart=True)
	def joinFetcher(self):
		if self.fetchThread is not None:
			self.fetchThread.join()
			self.fetchThread = None
	def readBuffer(self):
		if self.fetchThread is None:
			self.spawnFetcher()
		self.joinFetcher()
		if self.autofetch and len(self.buffer) <= self.buffersize:
			self.spawnFetcher()
	def read(self, bytes=None):
		if bytes is None:
			bytes = -1
		if bytes == -1:
			buffer = ''
			i = self.read(self.buffersize)
			while len(i):
				buffer += i
				i = self.read(self.buffersize)
			return buffer
		if len(self.buffer) >= bytes: # If the buffer is rich enough
			buffer = self.buffer[:bytes]
			self.buffer = self.buffer[bytes:]
			return buffer
		oldBuffer = len(self.buffer)
		self.readBuffer()
		if oldBuffer < len(self.buffer): # There is still stuff left
			return self.read(bytes) # Then keep downloading
		buffer = self.buffer # Otherwise stream ended, just flush the buffer
		self.buffer = ''
		return buffer
	def readAll(self):
		Damnlog('DamnResumableDownload reading all for', self.url)
		return self.read(-1)
	def close(self):
		Damnlog('DamnResumableDownload closing', self.url)
		if self.stream is not None:
			try:
				self.stream.close()
			except:
				Damnlog('! DamnResumableDownload failed closing', self.url)
			self.stream = None
def DamnURLOpen(req, data=None, throwerror=False, autoresume=True, resumeat=None):
	Damnlog('DamnURLOpen called with request', req, '; data', data,'; Throw error?', throwerror, '; Autoresume?', autoresume)
	url = req
	if type(req) in (type(''), type(u'')):
		req = DamnURLRequest(DamnUnicode(req))
		Damnlog('Request was', url, '; request is now',req)
	try:
		if data is not None:
			pipe = DamnResumableDownload(req, data, resumable=autoresume, resumeat=resumeat)
		else:
			pipe = DamnResumableDownload(req, resumable=autoresume, resumeat=resumeat)
		Damnlog('DamnURLOpen successful, returning stream.')
		return pipe
	except IOError, err:
		if not hasattr(err, 'reason') and not hasattr(err, 'code'):
			Damnlog('DamnURLOpen on', url, 'failed with IOError but without reason or code.')
		else:
			try:
				Damnlog('DamnURLOpen on', url, 'failed with code', err.code, 'and reason', err.reason)
			except:
				try:
					Damnlog('DamnURLOpen on', url, 'failed with code', err.code, 'and no reason.')
				except:
					Damnlog('DamnURLOpen on', url, 'failed pretty badly.')
		if throwerror:
			raise err
		return None
	except Exception, e:
		if throwerror:
			Damnlog('DamnURLOpen failed on request',req,' with exception',e,'; throwing error because throwerror is True.')
			raise e
		Damnlog('DamnURLOpen failed on request',req,' with exception',e,'; returning None because throwerror is False.')
		return None
def DamnURLGetAll(req, data=None, onerror=None):
	Damnlog('DamnURLGetAll called with request', req,'and data', data,'; on error =', onerror)
	url = DamnURLOpen(req, data=data, throwerror=False)
	if url is None:
		Damnlog('DamnURLGetAll got None; returning onerror =', onerror)
		return DamnUnicode(onerror)
	content = DamnUnicode(url.read(-1))
	Damnlog('DamnURLGetAll successful; returning', len(content),'bytes of content.')
	return content
def DamnRTMPDump(req):
	pass # Todo
def DamnURLPicker(urls, urlonly=False, resumeat=None):
	tried = []
	if resumeat == 0:
		resumeat = None
	Damnlog('DamnURLPicker summoned. URLs:', urls, 'Resume at:', resumeat)
	for i in urls:
		i = DamnUnicode(i)
		if i not in tried:
			tried.append(i)
			try:
				pipe = DamnURLOpen(i, throwerror=True, resumeat=resumeat)
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
	Damnlog('DamnURLPicker returning None because no URLs are valid')
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
	trycount = 0
	for i in urls:
		if i not in tried:
			tried.append(i)
			trycount += 1
			try:
				handle = DamnURLOpen(i)
				size = int(handle.info()['Content-Length'])
				handle.close()
				maxlen.append(size)
				maxurl.append(i)
			except:
				maxlen.append(-trycount)
				maxurl.append(i)
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
class DamnDownloader(DamnThread): # Retrieves video by HTTP and feeds it back to ffmpeg via stdin
	def __init__(self, uri, pipe, copy=None):
		Damnlog('DamnDownloader spawned. URI:', uri, '; Pipe:', pipe)
		self.uri = uri
		self.pipe = pipe
		self.copy = copy
		DamnThread.__init__(self)
	def timeouterror(self):
		Damnlog('DamnDownloader timeout detection timer fired!')
		self.timeouted = True
		self.http.close()
	def go(self):
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
			tmptimer = DamnTimer(DV.streamTimeout, self.timeouterror)
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
class DamnStreamCopy(DamnThread):
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
		DamnThread.__init__(self)
	def start(self):
		if self.background:
			Damnlog('Starting stream copy in background thread.')
			DamnThread.start(self)
		else:
			Damnlog('Starting stream copy in current thread.')
			self.run()
	def go(self):
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
class DamnYouTubeService(DamnThread):
	def __init__(self, parent, query=None):
		self.parent = parent
		DamnThread.__init__(self)
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
			DV.postEvent(self.parent, (DV.evt_loading, -1, info))
		except:
			pass # Window might have been closed
	def returnResult(self, result, index=0):
		return self.postEvent({'index':index, 'query':self.queries[index], 'result':result})
	def getTempFile(self):
		name = DV.tmp_path + str(random.random()) + '.tmp'
		while os.path.exists(name):
			name = DV.tmp_path + str(random.random()) + '.tmp'
		return name
	def go(self):
		while self.queries is None:
			time.sleep(.025)
		try:
			self.parent.loadlevel += 1
		except:
			pass # Window might have been closed
		while len(self.queries):
			query = self.queries[0]
			if query[0] == 'feed':
				self.returnResult(DV.youtube_service.GetYouTubeVideoFeed(DamnUnicode(query[1]).encode('utf8')))
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
		self.postEvent({'query':('done',)}) # All done, service will be respawned if needed later
		try:
			self.parent.loadlevel -= 1
		except:
			pass # Window might have been closed
class DamnBugReporter(DamnThread):
	def __init__(self, desc, steps='', sysinfo=None, email='', parent=None):
		self.desc = desc
		self.steps = steps
		self.sysinfo = sysinfo
		if self.sysinfo is None:
			self.sysinfo = dSysInfo.DamnSysInfo()
		self.email = email
		self.parent = parent
		DamnThread.__init__(self)
	def postEvent(self, title=None, dialog=None, error=False, closedialog=True):
		info = {'title':title, 'dialog':dialog, 'error':error, 'closedialog':closedialog}
		Damnlog('Posting a bug report update event with info', info)
		if self.parent is None:
			Damnlog('Not posting anything, parent is none.')
			return
		try:
			DV.postEvent(self.parent, (DV.evt_bugreporting, -1, info))
		except:
			Damnlog('Posting event failed - Window was closed?')
	def go(self):
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
			http = DamnURLOpen(DamnURLRequest('http://pastehtml.com/upload/create?input_type=txt&result=address', urllib.urlencode({'txt':logdump.encode('utf8')})))
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
def DamnHtmlEntities(html):
	return DamnUnicode(BeautifulSoup.BeautifulStoneSoup(html, convertEntities=BeautifulSoup.BeautifulStoneSoup.HTML_ENTITIES)).replace(u'&amp;', u'&') # Because BeautifulSoup, as good as it is, puts &amp;badentity where &badentitity; are. Gotta convert that back.
