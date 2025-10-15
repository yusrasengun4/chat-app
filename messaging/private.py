# messaging/private.py
from database.queries import save_message, get_private_messages
from flask_socketio import emit
from datetime import datetime

class PrivateChat:
    @staticmethod
    def send_message(data, sender, online_users):
        """Özel mesaj gönder"""
        target_id = data['target_id']
        """
        message_id = save_message(
            sender_id=sender['id'],
            sender_username=sender['username'],
            message=data['message'],
            message_type='private',
            target_id=target_id
        )
        """
        message_id = save_message(
    sender_id=sender['id'],
    message_content=data['message'],   # içerik
    message_type='private',
    receiver_id=target_id              # alıcı ID
)
        message_data = {
            'id': message_id,
            'sender': sender['username'],
            'sender_id': sender['id'],
            'message': data['message'],
            'type': 'private',
            'target_id': target_id,
            'timestamp': datetime.now().isoformat()
        }
        
        # Gönderene de göster
        emit('new_message', {**message_data, 'is_own': True})
        
        # Alıcıya gönder (online ise)
        target_socket = online_users.get(target_id)
        if target_socket:
            emit('new_message', {**message_data, 'is_own': False}, room=target_socket)
        
        return {'success': True, 'message_id': message_id}