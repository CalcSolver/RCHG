@echo off
title Stark Engine Launcher
echo ====================================================
echo          Launching Stark Universal Engine...
echo ====================================================
echo.

if exist "gesture_controller.py" (
    python gesture_controller.py
) else if exist "%USERPROFILE%\StarkGestureController\gesture_controller.py" (
    python "%USERPROFILE%\StarkGestureController\gesture_controller.py"
) else (
    echo [ERROR] Run install.bat first before launching.
    pause
)
