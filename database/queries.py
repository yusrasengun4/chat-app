"""
Veritabanı Sorguları
Tüm CRUD (Create, Read, Update, Delete) işlemleri
"""

import hashlib
from datetime import datetime
from .db_manager import get_db, execute_query


# =====================================================
# YARDIMCI FONKSİYONLAR
# =====================================================

def get_message_hash(message_content):
    """
    Mesaj içeriğini SHA256 ile hash'ler
    
    Args:
        message_content (str): Hash'lenecek mesaj
    
    Returns:
        str: 64 karakterlik hash değeri
    """
    return hashlib.sha256(message_content.encode()).hexdigest()


def hash_password(password):
    """
    Şifreyi SHA256 ile hash'ler
    
    Args:
        password (str): Kullanıcı şifresi
    
    Returns:
        str: Hash'lenmiş şifre
    """
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================
# KULLANICI İŞLEMLERİ
# =====================================================

def register_user(username, password, email=None):
    """
    Yeni kullanıcı kaydı oluşturur
    
    Args:
        username (str): Kullanıcı adı
        password (str): Şifre
        email (str, optional): Email adresi
    
    Returns:
        tuple: (başarılı mı?, kullanıcı_id veya hata mesajı)
    """
    try:
        password_hash = hash_password(password)
        
        query = '''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        '''
        user_id = execute_query(query, (username, password_hash, email))
        
        print(f"✅ Kullanıcı oluşturuldu: {username} (ID: {user_id})")
        return True, user_id
    
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return False, "Bu kullanıcı adı zaten kullanılıyor"
        return False, str(e)


def authenticate_user(username, password):
    """
    Kullanıcı giriş doğrulaması
    
    Args:
        username (str): Kullanıcı adı
        password (str): Şifre
    
    Returns:
        tuple: (başarılı mı?, kullanıcı bilgileri veya None)
    """
    password_hash = hash_password(password)
    
    query = '''
        SELECT * FROM users
        WHERE username = ? AND password_hash = ?
    '''
    user = execute_query(query, (username, password_hash), fetch=True)
    
    if user:
        # Kullanıcıyı online yap
        set_user_online(user['id'], True)
        print(f"✅ Giriş başarılı: {username}")
        return True, user
    
    return False, None


def get_user_by_id(user_id):
    """
    ID'ye göre kullanıcı bilgilerini getirir
    
    Args:
        user_id (int): Kullanıcı ID'si
    
    Returns:
        dict: Kullanıcı bilgileri veya None
    """
    query = 'SELECT * FROM users WHERE id = ?'
    return execute_query(query, (user_id,), fetch=True)


def get_user_by_username(username):
    """
    Kullanıcı adına göre bilgileri getirir
    
    Args:
        username (str): Kullanıcı adı
    
    Returns:
        dict: Kullanıcı bilgileri veya None
    """
    query = 'SELECT * FROM users WHERE username = ?'
    return execute_query(query, (username,), fetch=True)


def get_all_users():
    """
    Tüm kullanıcıları getirir
    
    Returns:
        list: Kullanıcı listesi
    """
    query = 'SELECT id, username, is_online, last_seen FROM users ORDER BY username'
    return execute_query(query, fetchall=True)


def set_user_online(user_id, is_online=True):
    """
    Kullanıcının çevrimiçi durumunu günceller
    
    Args:
        user_id (int): Kullanıcı ID'si
        is_online (bool): Çevrimiçi mi?
    """
    query = '''
        UPDATE users
        SET is_online = ?, last_seen = CURRENT_TIMESTAMP
        WHERE id = ?
    '''
    execute_query(query, (1 if is_online else 0, user_id))


def get_online_users():
    """
    Çevrimiçi kullanıcıları getirir
    
    Returns:
        list: Çevrimiçi kullanıcı listesi
    """
    query = 'SELECT id, username FROM users WHERE is_online = 1 ORDER BY username'
    return execute_query(query, fetchall=True)


# =====================================================
# GRUP İŞLEMLERİ
# =====================================================

def create_group(group_name, created_by, description=None):
    """
    Yeni grup oluşturur
    
    Args:
        group_name (str): Grup adı
        created_by (int): Oluşturan kullanıcının ID'si
        description (str, optional): Grup açıklaması
    
    Returns:
        tuple: (başarılı mı?, grup_id veya hata mesajı)
    """
    try:
        query = '''
            INSERT INTO groups (group_name, description, created_by)
            VALUES (?, ?, ?)
        '''
        group_id = execute_query(query, (group_name, description, created_by))
        
        # Oluşturanı gruba admin olarak ekle
        add_user_to_group(group_id, created_by, role='admin')
        
        print(f"✅ Grup oluşturuldu: {group_name} (ID: {group_id})")
        return True, group_id
    
    except Exception as e:
        if 'UNIQUE constraint failed' in str(e):
            return False, "Bu grup adı zaten kullanılıyor"
        return False, str(e)


def get_group_by_id(group_id):
    """
    ID'ye göre grup bilgilerini getirir
    
    Args:
        group_id (int): Grup ID'si
    
    Returns:
        dict: Grup bilgileri veya None
    """
    query = 'SELECT * FROM groups WHERE id = ?'
    return execute_query(query, (group_id,), fetch=True)


def get_all_groups():
    """
    Tüm grupları getirir
    
    Returns:
        list: Grup listesi
    """
    query = '''
        SELECT g.*, u.username as creator_name,
               COUNT(gm.user_id) as member_count
        FROM groups g
        LEFT JOIN users u ON g.created_by = u.id
        LEFT JOIN group_members gm ON g.id = gm.group_id
        GROUP BY g.id
        ORDER BY g.group_name
    '''
    return execute_query(query, fetchall=True)


def add_user_to_group(group_id, user_id, role='member'):
    """
    Kullanıcıyı gruba ekler
    
    Args:
        group_id (int): Grup ID'si
        user_id (int): Kullanıcı ID'si
        role (str): Rol ('admin' veya 'member')
    
    Returns:
        bool: Başarılı mı?
    """
    try:
        query = '''
            INSERT INTO group_members (group_id, user_id, role)
            VALUES (?, ?, ?)
        '''
        execute_query(query, (group_id, user_id, role))
        return True
    except:
        return False


def remove_user_from_group(group_id, user_id):
    """
    Kullanıcıyı gruptan çıkarır
    
    Args:
        group_id (int): Grup ID'si
        user_id (int): Kullanıcı ID'si
    """
    query = 'DELETE FROM group_members WHERE group_id = ? AND user_id = ?'
    execute_query(query, (group_id, user_id))


def get_group_members(group_id):
    """
    Grubun üyelerini getirir
    
    Args:
        group_id (int): Grup ID'si
    
    Returns:
        list: Üye listesi
    """
    query = '''
        SELECT u.id, u.username, gm.role, gm.joined_at
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = ?
        ORDER BY gm.role DESC, u.username
    '''
    return execute_query(query, (group_id,), fetchall=True)


def get_user_groups(user_id):
    """
    Kullanıcının üye olduğu grupları getirir
    
    Args:
        user_id (int): Kullanıcı ID'si
    
    Returns:
        list: Grup listesi
    """
    query = '''
        SELECT g.*, gm.role
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = ?
        ORDER BY g.group_name
    '''
    return execute_query(query, (user_id,), fetchall=True)


def is_user_in_group(user_id, group_id):
    """
    Kullanıcının grupta olup olmadığını kontrol eder
    
    Args:
        user_id (int): Kullanıcı ID'si
        group_id (int): Grup ID'si
    
    Returns:
        bool: Grupta mı?
    """
    query = 'SELECT 1 FROM group_members WHERE user_id = ? AND group_id = ?'
    result = execute_query(query, (user_id, group_id), fetch=True)
    return result is not None


# =====================================================
# MESAJ İŞLEMLERİ
# =====================================================
"""
def save_message(sender_id, message_content, message_type,
                 receiver_id=None, group_id=None, is_offline=False):
    """
"""
    Mesajı veritabanına kaydeder
    
    Args:
        sender_id (int): Gönderen kullanıcı ID'si
        message_content (str): Mesaj içeriği
        message_type (str): 'private', 'group', veya 'broadcast'
        receiver_id (int, optional): Alıcı kullanıcı ID'si
        group_id (int, optional): Grup ID'si
        is_offline (bool): Çevrimdışı mesaj mı?
    
    Returns:
        int: Mesaj ID'si
    """
"""
    message_hash = get_message_hash(message_content)
    
    query = '''
        INSERT INTO messages
        (sender_id, receiver_id, group_id, message_content,
         message_hash, message_type, is_offline)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    
    message_id = execute_query(
        query,
        (sender_id, receiver_id, group_id, message_content,
         message_hash, message_type, 1 if is_offline else 0)
    )
    
    return message_id

"""
def save_message(sender_id, message_content, message_type,
                 receiver_id=None, group_id=None, is_offline=False):
    """
    Mesajı veritabanına kaydeder
    """
    message_hash = get_message_hash(message_content)

    # Broadcast mesajı için receiver_id ve group_id null olabilir
    query = '''
        INSERT INTO messages
        (sender_id, receiver_id, group_id, message_content,
         message_hash, message_type, is_offline)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    try:
        message_id = execute_query(
            query,
            (
                sender_id,
                receiver_id if receiver_id else None,
                group_id if group_id else None,
                message_content,
                message_hash,
                message_type,
                1 if is_offline else 0
            )
        )
        return message_id
    except Exception as e:
        print("[DB ERROR] save_message:", e)
        return None

def get_messages_by_user(user_id, limit=100):
    """
    Kullanıcının tüm mesajlarını getirir
    
    Args:
        user_id (int): Kullanıcı ID'si
        limit (int): Maksimum mesaj sayısı
    
    Returns:
        list: Mesaj listesi
    """
    query = '''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.sender_id = ? OR m.receiver_id = ?
        ORDER BY m.created_at DESC
        LIMIT ?
    '''
    return execute_query(query, (user_id, user_id, limit), fetchall=True)


def get_group_messages(group_id, limit=50):
    """
    Grup mesajlarını getirir
    
    Args:
        group_id (int): Grup ID'si
        limit (int): Maksimum mesaj sayısı
    
    Returns:
        list: Mesaj listesi
    """
    query = '''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.group_id = ? AND m.message_type = 'group'
        ORDER BY m.created_at DESC
        LIMIT ?
    '''
    messages = execute_query(query, (group_id, limit), fetchall=True)
    return list(reversed(messages))  # Eski'den yeniye


def get_private_messages(user1_id, user2_id, limit=50):
    """
    İki kullanıcı arasındaki özel mesajları getirir
    
    Args:
        user1_id (int): Birinci kullanıcı ID'si
        user2_id (int): İkinci kullanıcı ID'si
        limit (int): Maksimum mesaj sayısı
    
    Returns:
        list: Mesaj listesi
    """
    query = '''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.message_type = 'private'
        AND ((m.sender_id = ? AND m.receiver_id = ?)
             OR (m.sender_id = ? AND m.receiver_id = ?))
        ORDER BY m.created_at DESC
        LIMIT ?
    '''
    messages = execute_query(
        query,
        (user1_id, user2_id, user2_id, user1_id, limit),
        fetchall=True
    )
    return list(reversed(messages))


def get_broadcast_messages(limit=50):
    """
    Broadcast mesajlarını getirir
    
    Args:
        limit (int): Maksimum mesaj sayısı
    
    Returns:
        list: Mesaj listesi
    """
    query = '''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.message_type = 'broadcast'
        ORDER BY m.created_at DESC
        LIMIT ?
    '''
    messages = execute_query(query, (limit,), fetchall=True)
    return list(reversed(messages))


def get_offline_messages(user_id):
    """
    Kullanıcının çevrimdışıyken gelen mesajlarını getirir
    
    Args:
        user_id (int): Kullanıcı ID'si
    
    Returns:
        list: Çevrimdışı mesaj listesi
    """
    query = '''
        SELECT m.*, u.username as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = ? AND m.is_offline = 1
        ORDER BY m.created_at
    '''
    return execute_query(query, (user_id,), fetchall=True)


def mark_message_delivered(message_id):
    """
    Mesajı 'teslim edildi' olarak işaretler
    
    Args:
        message_id (int): Mesaj ID'si
    """
    query = '''
        UPDATE messages
        SET status = 'delivered',
            delivered_at = CURRENT_TIMESTAMP,
            is_offline = 0
        WHERE id = ?
    '''
    execute_query(query, (message_id,))


def mark_message_read(message_id):
    """
    Mesajı 'okundu' olarak işaretler
    
    Args:
        message_id (int): Mesaj ID'si
    """
    query = '''
        UPDATE messages
        SET status = 'read',
            read_at = CURRENT_TIMESTAMP
        WHERE id = ?
    '''
    execute_query(query, (message_id,))
    
