@echo off
echo ====================================================
echo          Stark Gesture Controller Installer         
echo ====================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ALERT] Python was not found on your system.
    echo Launching python.org in your browser...
    echo.
    echo CRITICAL STEP: When installing Python, you MUST check the 
    echo box at the bottom that says "Add Python to PATH".
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b
)

set "TARGET_DIR=%USERPROFILE%\StarkGestureController"
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%"
)

copy /Y "gesture_controller.py" "%TARGET_DIR%\"
copy /Y "run_app.bat" "%TARGET_DIR%\"

echo Installing packages (PySide6, OpenCV, MediaPipe, PyAutoGUI)...
python -m pip install --upgrade pip
pip install PySide6 opencv-python mediapipe pyautogui

echo.
echo ====================================================
echo  Installation Complete! Ready to launch via run_app.bat
echo ====================================================
pause
