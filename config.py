# config.py
import os
from pathlib import Path

class Config:
    """Uygulama yapılandırması"""
    BASE_DIR = Path(__file__).parent
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'
    DEBUG = True
    
    # Database
    DB_FILE = BASE_DIR / 'messaging.db'
    
    # TCP Server
    TCP_HOST = '0.0.0.0'
    TCP_PORT = 9999
    
    # Web Server
    WEB_HOST = '0.0.0.0'
    WEB_PORT = 5000
    
    # SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 saat