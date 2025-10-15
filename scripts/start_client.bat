@echo off
echo ============================================
echo GUVENLI MESAJLASMA - TERMINAL ISTEMCISI
echo ============================================
echo.
echo Terminal istemcisi baslatiliyor...
echo.
echo NOT: Web arayuzunu kullanmaniz onerilir!
echo Web: http://localhost:5000
echo.

:: Proje köküne geç
cd ..

:: Terminal istemciyi çalıştır
python clients/terminal_client.py

pause
