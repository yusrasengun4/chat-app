@echo off
echo ============================================
echo  WEB SUNUCU BASLATICI
echo ============================================
echo.
echo Web arayuzu baslatiliyor...
echo TCP sunucusu: localhost:5000
echo Web arayuzu: http://localhost:5000
echo.
echo NOT: Once TCP sunucusunu baslatmaniz gerekir!
echo.

:: Proje köküne geç
cd ..

:: Web sunucuyu çalıştır
python app.py

pause
