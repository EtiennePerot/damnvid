@echo Packaging DamnVid for win32.
@echo ----------------------------
@cd ..
@echo Trying to delete old setup, if any.
@del /q DamnVid-setup*
@echo Finding Python installation.
@python build-exe\find-system-paths-win32.py
@set /p python= < python32-path.tmp
@echo Building list of required files.
@%python%\python -OO build-any\build-required-files.py
@echo Creating /package/ directory.
@mkdir package
@echo Switching to /package/ directory.
@cd package
@echo Compyling DamnVid.
@copy /Y ..\build-exe\msvcp90.dll %python%\msvcp90.dll
echo %python%\python -OO ..\build-exe\py2exe-win32.py py2exe
@%python%\python -OO ..\build-exe\py2exe-win32.py py2exe
@echo Running UPX --brute on compyled executable.
@echo upx --brute dist\DamnVid.exe
@echo Switching to /package/dist/ directory.
@cd dist
@copy /Y ..\..\build-exe\gdiplus.dll .\gdiplus.dll
@copy /Y ..\..\build-exe\msvcp71.dll .\msvcp71.dll
@copy /Y ..\..\build-exe\msvcr71.dll .\msvcr71.dll
@copy /Y ..\..\build-exe\unicows.dll .\unicows.dll
@echo Done compyling.
@if "%1" == "/nopause" goto end
@pause
:end
