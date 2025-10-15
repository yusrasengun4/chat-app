"""
Veritabanı Tablo Yapıları
Tüm tabloların CREATE TABLE komutları
"""


def create_tables(conn):
    """
    Tüm veritabanı tablolarını oluşturur
    
    Args:
        conn: SQLite veritabanı bağlantısı
    
    Tablolar:
    1. users - Kullanıcı bilgileri
    2. groups - Grup bilgileri
    3. group_members - Grup üyelikleri
    4. messages - Mesaj kayıtları
    """
    cursor = conn.cursor()
    
    # ============= KULLANICILAR TABLOSU =============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            is_online INTEGER DEFAULT 0,
            last_seen TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============= GRUPLAR TABLOSU =============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # ============= GRUP ÜYELERİ TABLOSU =============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(group_id, user_id)
        )
    ''')
    
    # ============= MESAJLAR TABLOSU =============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            group_id INTEGER,
            message_content TEXT NOT NULL,
            message_hash TEXT NOT NULL,
            message_type TEXT NOT NULL CHECK(message_type IN ('private', 'group', 'broadcast')),
            status TEXT DEFAULT 'sent' CHECK(status IN ('sent', 'delivered', 'read')),
            is_offline INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivered_at TIMESTAMP,
            read_at TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
        )
    ''')
    
    # ============= İNDEXLER (Performans İçin) =============
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_group ON messages(group_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_members_user ON group_members(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id)')
    
    conn.commit()
    print("✅ Veritabanı tabloları oluşturuldu")
