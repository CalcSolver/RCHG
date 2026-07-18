@echo off
echo ====================================================
echo          Stark Gesture Controller Installer         
echo ====================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your System PATH.
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b
)

:: 2. Create application directory inside the user's home profile dynamically
set "TARGET_DIR=%USERPROFILE%\StarkGestureController"
if not exist "%TARGET_DIR%" (
    echo Creating installation directory at %TARGET_DIR%...
    mkdir "%TARGET_DIR%"
)

:: 3. Copy script files to the user directory
echo Copying application files...
copy /Y "gesture_controller.py" "%TARGET_DIR%\"

:: 4. Install required machine learning and UI libraries
echo Installing required dependencies (PySide6, OpenCV, MediaPipe, PyAutoGUI)...
python -m pip install --upgrade pip
pip install PySide6 opencv-python mediapipe pyautogui

echo.
echo ====================================================
echo  Installation Complete! 
echo  Your files are located at: %TARGET_DIR%
echo  To run the app, type: python "%TARGET_DIR%\gesture_controller.py"
echo ====================================================
pause