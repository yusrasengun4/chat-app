"""
Veritabanı Bağlantı Yöneticisi
SQLite bağlantılarını yönetir
"""

import sqlite3
from pathlib import Path
import threading

# Veritabanı dosyası yolu
DB_FILE = Path(__file__).parent.parent / 'messaging.db'

# Thread-safe bağlantı yönetimi için
_local = threading.local()


def get_db():
    """
    Thread-safe SQLite veritabanı bağlantısı döndürür
    
    Returns:
        sqlite3.Connection: Veritabanı bağlantı nesnesi
    
    Özellikler:
    - Her thread için ayrı bağlantı oluşturur
    - Row factory ile dict benzeri erişim sağlar
    - Otomatik bağlantı yönetimi
    """
    if not hasattr(_local, 'connection') or _local.connection is None:
        _local.connection = sqlite3.connect(
            DB_FILE,
            check_same_thread=False,
            timeout=10.0  # Timeout 10 saniye
        )
        # Row'ları dict gibi kullanabilmek için
        _local.connection.row_factory = sqlite3.Row
        # Foreign key kontrollerini aktif et
        _local.connection.execute('PRAGMA foreign_keys = ON')
    
    return _local.connection


def close_db():
    """
    Mevcut thread'in veritabanı bağlantısını kapatır
    
    Kullanım:
    - Uygulama kapanırken
    - Uzun süre kullanılmayacak bağlantılar için
    """
    if hasattr(_local, 'connection') and _local.connection is not None:
        _local.connection.close()
        _local.connection = None


def init_db():
    """
    Veritabanını başlatır ve tabloları oluşturur
    
    Bu fonksiyon:
    1. Veritabanı dosyasını oluşturur (yoksa)
    2. Tüm tabloları oluşturur
    3. Foreign key kontrollerini aktif eder
    """
    from .models import create_tables
    
    print("🔧 Veritabanı başlatılıyor...")
    
    # Veritabanı bağlantısı al
    conn = get_db()
    
    # Tabloları oluştur
    create_tables(conn)
    
    print(f"✅ Veritabanı hazır: {DB_FILE}")


def execute_query(query, params=None, fetch=False, fetchall=False, commit=True):
    """
    Güvenli SQL sorgu yürütme fonksiyonu
    
    Args:
        query (str): SQL sorgusu
        params (tuple): Sorgu parametreleri (SQL injection koruması)
        fetch (bool): Tek satır döndür
        fetchall (bool): Tüm satırları döndür
        commit (bool): Değişiklikleri kaydet
    
    Returns:
        list/dict/int: Sorgu sonucu veya lastrowid
    """
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if commit:
            conn.commit()
        
        if fetch:
            result = cursor.fetchone()
            return dict(result) if result else None
        elif fetchall:
            return [dict(row) for row in cursor.fetchall()]
        else:
            return cursor.lastrowid
    
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Veritabanı hatası: {e}")
        raise
    finally:
        cursor.close()

