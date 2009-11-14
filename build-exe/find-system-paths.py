import os, sys

paths={
	'nsis':['C:\Program Files\NSIS','C:\Program Files (x86)\NSIS'],
	'python32':['C:\Python26-x86'],
	'python64':['C:\Python26','C:\Python26-x64']
}
for k in paths.iterkeys():
	for i in paths[k]:
		if os.path.exists(i):
			open(k+'-path.tmp','w').write(i)
			continue
	print >> sys.stderr, 'Error: Could not find '+k+', please edit find-system-paths.py.'
