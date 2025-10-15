@echo off
echo ============================================
echo GUVENLI MESAJLASMA - TCP SUNUCUSU
echo ============================================
echo.
echo Sunucu baslatiliyor...
echo.
echo Diger bilgisayarlar bu IP ile baglanabilir:
ipconfig | findstr "IPv4"
echo.
echo Port: 5000
echo.

:: Proje köküne geç
cd ..

:: TCP sunucuyu çalıştır
python core/tcp_server.py

pause
