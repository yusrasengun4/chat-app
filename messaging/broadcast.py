# messaging/broadcast.py
from database.queries import save_message, get_broadcast_messages
from flask_socketio import emit
from datetime import datetime

class BroadcastChat:
    @staticmethod
    def send_message(data, sender):
        message_text = data.get('message') or data.get('content')

        message_id = save_message(
            sender_id=sender['id'],
            message_content=message_text,
            message_type='broadcast'
        )
        
        if not message_id:
            print("⚠️ Broadcast mesaj DB'ye kaydedilemedi")
        
        emit('receive_message', {
            'sender': sender['username'],
            'sender_id': sender['id'],
            'message': message_text,
            'content': message_text,
            'type': 'broadcast'
        }, broadcast=True)

        return {'success': True, 'message_id': message_id}
    
    @staticmethod
    def load_history(limit=50):
        """Mesaj geçmişini DB’den getirir"""
        return get_broadcast_messages(limit)