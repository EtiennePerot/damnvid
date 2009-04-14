import os
import shutil

while not os.path.lexists('./DamnVid.py'):
    os.chdir('./../')
deletables=['COPYING','DamnVid.exe.manifest','required-files.txt','package']
for i in deletables:
    if os.path.lexists(i):
        if os.path.isdir(i):
            shutil.rmtree(i)
        else:
            os.remove(i)
