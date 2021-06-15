@echo off
cd %~dp0
reg query "HKCU\Software\Python\PythonCore\3.9\InstallPath"1> NUL 2>&1
if errorlevel 1 goto errorNoPython
rem "how hard can this be" - famous last words
FOR /F "tokens=2* skip=2" %%a in ('reg query "HKCU\Software\Python\PythonCore\3.9\InstallPath" /v "ExecutablePath"') do SET python=%%b
:runServer
if exist Scripts\ (
    .\Scripts\activate.bat
    python server.py
) else (
    %python% -m venv .\
    .\Scripts\activate.bat
    pip install -r requirements.txt 
    python server.py
)

:errorNoPython
echo.
echo Error^: Python not installed
reg Query "HKLM\Hardware\Description\System\CentralProcessor\0" | find /i "x86" > NUL && set OSBITS=32BIT || set OSBITS=64BIT
if %OSBITS%==32BIT (
    curl https://www.python.org/ftp/python/3.9.5/python-3.9.5.exe --output python-3.9.5.exe > NUL
    python-3.9.5.exe 
    goto runServer
)
if %OSBITS%==64BIT (
    curl https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe --output python-3.9.5-amd64.exe > NUL
    python-3.9.5-amd64.exe
    goto runServer
) 
