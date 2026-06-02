@echo off
title ExamSense Starter

echo ==========================================
echo Pornesc backend-ul Django...
echo ==========================================
start "ExamSense Backend" cmd /k "cd /d D:\ExamSense\core && D:\ExamSense\venv\Scripts\activate && python manage.py runserver"

timeout /t 3 /nobreak > nul

echo.
echo ==========================================
echo Pornesc frontend-ul Vite...
echo ==========================================
start "ExamSense Frontend" cmd /k "cd /d D:\ExamSense\core\examsense-frontend && npm run dev"

timeout /t 5 /nobreak > nul

echo.
echo ==========================================
echo Deschid aplicatia in browser...
echo ==========================================
start http://localhost:5173

exit