@echo off
title SolarAI Ban Pong Web Application
chcp 65001 >nul
echo ===================================================
echo   SolarAI Ban Pong - Decision Support System
echo   กำลังเริ่มต้นเซิร์ฟเวอร์ระบบวิเคราะห์พลังงานแสงอาทิตย์...
echo ===================================================
echo.
echo กำลังเปิดหน้าเว็บที่: http://127.0.0.1:5000
echo.

start "" "http://127.0.0.1:5000"
python app.py

pause
