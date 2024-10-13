@echo off
REM Navigate to the directory where the virtual environment is located
cd /d "%~dp0"

REM Activate the virtual environment
call C:\Users\craps\OneDrive\Documents\GitHub\Sensehub-Windows\Face-Recognition\SenseHub\Scripts\activate

REM Run the Python script using python11
python11 main_app.py

REM Pause to keep the command prompt window open (optional)
pause
