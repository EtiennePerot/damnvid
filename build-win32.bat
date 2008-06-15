@cd ..\bin\DamnVid
@python ..\..\DamnVid\setup-win32.py py2exe --package encodings
@Echo UPX --brute on the way
@cd dist
@upx --brute DamnVid.exe
@pause
@Echo NSIS on the way
@Echo Todo: NSIS packaging