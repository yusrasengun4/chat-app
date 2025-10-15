Chat-app/
├── app.py                          # Ana uygulama (sadece başlatma)
├── config.py                    # Yapılandırma ayarları
|--extensions.py                      #socketIo tek bir yerden bağlanıldı
├── requirements.txt                # Bağımlılıklar
├── database/                       # Veritabanı modülü
│   ├── __init__.py
│   ├── db_manager.py              # Veritabanı bağlantısı
│   ├── models.py                  # Tablo yapıları
│   └── queries.py                 # SQL sorguları
├── auth/                          # Kimlik doğrulama modülü
│   ├── __init__.py
│   ├── routes.py                  # /login, /register route'ları
│   └──decorators.py                  
├── messaging/                          # Mesajlaşma modülü
│   ├── __init__.py
│   ├── broadcast.py               # 📢 Herkese mesaj
│   ├── groups.py                  # 👥 Grup mesajlaşma
│   ├── private.py                 # 💬 Özel mesajlaşma
│   └── socket_handler.py           # WebSocket olayları
│
├── api/                           # REST API endpoint'leri
│   ├── __init__.py
│   ├── users.py                   # Kullanıcı API'leri
│   ├── groups.py                  # Grup API'leri
│   └── messages.py                # Mesaj API'leri
│----core/
|   |--__init__.py
|    |---tcp_server.py    #mevcut  TCP sunucu
|    |---protocol.py       #mesaj protokolü 
├── clients/                           # istemci uygulamaları
│   ├── __init__.py
│   ├── terminal_client.py                   # Kullanıcı API'leri
│   ├── gui_client.py                  # Grup API'leri
├── templates/                     # HTML şablonları (tek sayfa varsa)
│   └── base.html
│   └──login.html
│   └──chat.html
│   └──register.html
├── static/                        # Frontend dosyaları
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └──chat.js
│   ├── gui_client.py                  # Grup API'leri
├── scripts/                     # HTML şablonları (tek sayfa varsa)
│   └── start_all.bat
│   └──start_server.bat
 │   └──start_web.bat
 │   └──start_client.bat
