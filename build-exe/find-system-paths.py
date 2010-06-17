import os, sys

paths={
   'nsis': ['C:\Program Files\NSIS'],
   'python32': ['C:\Python25-x86', 'C:\Python26-x86', 'C:\Python25', 'C:\Python26'],
}

for k in paths.iterkeys():
   found = False
   for i in paths[k]:
      if os.path.exists(i):
         open(k+'-path.tmp', 'w').write(i)
         found = True
   if not found:
       print >> sys.stderr, 'Error: Could not find '+k+', please edit find-system-paths.py.'