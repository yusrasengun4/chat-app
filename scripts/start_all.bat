@echo off
echo ========================================
echo  TUM SISTEMI BASLATICI
echo ========================================
echo.

echo 1. TCP Sunucusu baslatiliyor...
start "TCP Sunucu" cmd /k "cd .. && python core/tcp_server.py"
echo.
echo 2 saniye bekleniyor...
timeout /t 2 /nobreak > nul
echo.

echo 2. Web Sunucusu baslatiliyor...
start "Web Sunucu" cmd /k "cd .. && python app.py"
echo.
echo 3 saniye bekleniyor...
timeout /t 3 /nobreak > nul
echo.

echo 3. Web arayuzu aciliyor...
start http://localhost:5000
echo.
echo ========================================
echo  SISTEM HAZIR!
echo ========================================
echo TCP Sunucusu: localhost:5000
echo Web Arayuzu: http://localhost:5000
echo.
echo Web arayuzunden TCP sunucusuna baglanin!
echo.
pause
