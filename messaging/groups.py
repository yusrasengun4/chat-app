# messaging/groups.py
from database.queries import (
    save_message, get_group_messages, is_user_in_group
)
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
"""
class GroupChat:
    @staticmethod
    def send_message(data, sender):
        
        group_id = data['group_id']
        
        # Kullanıcı grupta mı kontrol et
        if not is_user_in_group(sender['id'], group_id):
            return {'success': False, 'error': 'Bu grubun üyesi değilsiniz'}
        
        message_id = save_message(
            sender_id=sender['id'],
           # sender_username=sender['username'],
            message=data['message'],
            message_type='group',
            target_id=group_id
        )
        
        emit('new_message', {
            'id': message_id,
            'sender': sender['username'],
            'sender_id': sender['id'],
            'message': data['message'],
            'type': 'group',
            'group_id': group_id,
            'timestamp': datetime.now().isoformat()
        }, room=f'group_{group_id}')
        
        return {'success': True, 'message_id': message_id}
    """
class GroupChat:
    @staticmethod
    def send_message(data, sender):
        group_id = data['group_id']

        # 🔹 Burada sadece save_message'ın desteklediği parametreleri gönder
        message_id = save_message(
    sender_id=sender['id'],
    message_content=data['message'],   # ⚡ message_content olmalı
    message_type='group',
    group_id=group_id                  # ⚡ target_id yerine group_id
)
        emit('receive_message', {
    'id': message_id,
    'sender': sender['username'],
    'sender_id': sender['id'],
    'message': data['message'],   # backend mesaj
    'content': data['message'],   # frontend ile uyumlu
    'type': 'group',
    'group_id': group_id,
    'timestamp': datetime.now().isoformat()
}, room=f"group_{group_id}")
        return {'success': True, 'message_id': message_id}
    @staticmethod
    def join_group_room(user_id, group_id, socket_id):
        """Kullanıcıyı grup odasına ekle"""
        if is_user_in_group(user_id, group_id):
            join_room(f'group_{group_id}', sid=socket_id)
            return True
        return False
    
    @staticmethod
    def leave_group_room(user_id, group_id, socket_id):
        """Kullanıcıyı grup odasından çıkar"""
        leave_room(f'group_{group_id}', sid=socket_id)
    
    @staticmethod
    def load_history(group_id, limit=50):
        """Grup mesaj geçmişini yükle"""
        return get_group_messages(group_id, limit)