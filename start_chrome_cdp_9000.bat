@echo off
title Chrome CDP 9000
echo ===================================================
echo Starting Google Chrome with CDP on port 9000...
echo Remote Debugging URL: http://localhost:9000
echo ===================================================

set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" (
    set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)
if not exist "%CHROME_PATH%" (
    set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

echo Using Chrome at: %CHROME_PATH%

start "" "%CHROME_PATH%" --remote-debugging-port=9000 --remote-allow-origins=* --user-data-dir="%LOCALAPPDATA%\Google\Chrome\CDP_Profile_9000" --no-first-run --no-default-browser-check

echo Chrome has been launched with remote debugging on port 9000.
timeout /t 3 >nul
