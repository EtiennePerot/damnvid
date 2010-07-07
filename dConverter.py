# -*- coding: utf-8 -*-
from dCore import *
from dConstants import *
from dLog import *
from dThread import *
from dSpawn import *
from dTubes import *
import unicodedata
class DamnConverter(DamnThread): # The actual converter, dammit
	def __init__(self, parent):
		self.parent = parent
		self.sourceuri = parent.videos[parent.converting]
		self.outdir = None
		self.filename = None
		self.tmpfilename = None
		self.moduleextraargs = []
		Damnlog('DamnConverter initialized with parent', parent, '; Source URI:', self.sourceuri)
		DamnThread.__init__(self)
	def getURI(self, uri):
		if self.parent.meta[self.sourceuri].has_key('downloadgetter') and self.parent.meta[self.sourceuri].has_key('module'):
			if self.parent.meta[self.sourceuri]['module'] is not None:
				Damnlog('DamnConverter downloadgetter exists; calling it:', self.parent.meta[self.sourceuri]['downloadgetter'])
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
		prefix = DamnUnicode(REGEX_FILENAME_SANE_CHARACTERS.sub(u'', DamnUnicode(DamnUnicode(prefix).encode('ascii', 'ignore'))))
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
			info['progress'] = min(100.0, max(0.0, float(progress)))
		if statustext is not None:
			info['statustext'] = DamnUnicode(statustext)
		if status is not None:
			info['status'] = DamnUnicode(status)
		if dialog is not None:
			info['dialog'] = dialog
		if go is not None:
			info['go'] = go
		DV.postEvent(self.parent, (DV.evt_progress, -1, info))
	def go(self):
		Damnlog('DamnConverter started.')
		self.uris = self.getURI(self.sourceuri)
		self.abort = False
		Damnlog('DamnConverter URIs are', self.uris)
		if not self.abort:
			if True:
				if not len(self.uris):
					Damnlog('!! There are no URIs to download.')
					return
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
					self.outdir = self.outdir[:-1]
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
							total = int(src.info('Content-length'))
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
							progress = max(0.0, min(100.0, copied / total * 100.0))
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
				cmd = [DamnFindBinary(('ffmpeg-damnvid', 'ffmpeg' + os_exe_ext, 'ffmpeg')), '-i', '?DAMNVID_VIDEO_STREAM?', '-y', '-passlogfile', DV.tmp_path + 'pass']
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
				if DV.prefs.get('threads'):
					try:
						cmd.extend(['-threads',str(int(DV.prefs.get('threads')))])
					except:
						pass # Threads preference is probably not a number
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
				progress = max(0.0, min(100.0, float(float(res.group(1)) / self.duration / float(self.totalpasses) + float(float(self.passes - 1) / float(self.totalpasses))) * 100.0))
				DV.postEvent(self.parent, (DV.evt_progress, -1, {
					'progress': progress,
					'status': self.parent.meta[self.parent.videos[self.parent.converting]]['status'] + ' [' + str(int(progress)) + '%]'
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
					DamnSpawner('"' + DamnFindBinary('taskkill.exe') + '" /PID ' + str(self.process.pid) + ' /F').wait()
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
DV.converter = DamnConverter
