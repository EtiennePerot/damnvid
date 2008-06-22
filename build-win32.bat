@echo Packaging DamnVid for win32.
@echo ----------------------------
@echo Trying to delete old setup, if any.
@del /q DamnVid-setup.exe
@echo Creating /package/ directory.
@mkdir package
@echo Switching to /package/ directory.
@cd package
@echo Compyling DamnVid.
@python ..\py2exe-win32.py py2exe --package encodings
@pause
@echo Running UPX --brute on compyled executable.
@upx --brute dist\DamnVid.exe
@echo Switching to /package/dist/ directory.
@cd dist
@echo Packaging with NSIS.
@"C:\Program Files\NSIS\makensis.exe" -V4 -NOCD ..\..\NSIS-win32.nsi
@echo Switching back to root directory.
@cd ..\..
@echo DamnVid packaged. Cleaning up.
@rmdir package /s /q
@echo All done.
@pause