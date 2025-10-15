"""
Database modülü
Veritabanı işlemleri için gerekli fonksiyonları içerir
"""

from .db_manager import get_db, init_db, close_db
from .models import create_tables
from .queries import (
    # Kullanıcı işlemleri
    register_user,
    authenticate_user,
    get_user_by_id,
    get_user_by_username,
    get_all_users,
    get_online_users,
    set_user_online,
    # Grup işlemleri
    create_group,
    get_group_by_id,
    get_all_groups,
    add_user_to_group,
    remove_user_from_group,
    get_group_members,
    get_user_groups,
    is_user_in_group,
    
    # Mesaj işlemleri
    save_message,
    get_messages_by_user,
    get_group_messages,
    get_private_messages,
    get_broadcast_messages,
    get_offline_messages,
    mark_message_delivered,
    mark_message_read
)

__all__ = [
    'get_db', 'init_db', 'close_db',
    'create_tables',
    'register_user', 'authenticate_user', 'get_user_by_id',
    'get_user_by_username', 'get_all_users','get_online_users','set_user_online',
    'create_group', 'get_group_by_id', 'get_all_groups',
    'add_user_to_group', 'remove_user_from_group',
    'get_group_members', 'get_user_groups', 'is_user_in_group',
    'save_message', 'get_messages_by_user', 'get_group_messages',
    'get_private_messages', 'get_broadcast_messages',
    'get_offline_messages', 'mark_message_delivered', 'mark_message_read'
]
