from flask import Blueprint, request, jsonify
from auth.decorators import login_required, get_current_user
from database import (
    save_message,
    get_broadcast_messages,
    get_group_messages,
    get_private_messages,
    get_offline_messages,
    mark_message_delivered,
    mark_message_read,
    is_user_in_group
)

# Blueprint oluştur
messages_api = Blueprint('messages_api', __name__)


@messages_api.route('/broadcast', methods=['GET'])
@login_required
def get_broadcast_history():
    """
    Broadcast mesaj geçmişini getir
    
    GET /api/messages/broadcast?limit=50
    
    Response:
        {
            "success": true,
            "messages": [...],
            "count": 50
        }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        messages = get_broadcast_messages(limit)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messages_api.route('/group/<int:group_id>', methods=['GET'])
@login_required
def get_group_history(group_id):
    """
    Grup mesaj geçmişini getir
    
    GET /api/messages/group/1?limit=50
    
    Response:
        {
            "success": true,
            "messages": [...],
            "count": 50
        }
    """
    try:
        current_user = get_current_user()
        
        # Kullanıcı grupta mı kontrol et
        if not is_user_in_group(current_user['id'], group_id):
            return jsonify({
                'success': False,
                'error': 'Bu grubun üyesi değilsiniz'
            }), 403
        
        limit = request.args.get('limit', 50, type=int)
        messages = get_group_messages(group_id, limit)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messages_api.route('/private/<int:user_id>', methods=['GET'])
@login_required
def get_private_history(user_id):
    """
    Özel mesaj geçmişini getir
    
    GET /api/messages/private/2?limit=50
    
    Response:
        {
            "success": true,
            "messages": [...],
            "count": 50
        }
    """
    try:
        current_user = get_current_user()
        limit = request.args.get('limit', 50, type=int)
        
        messages = get_private_messages(current_user['id'], user_id, limit)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messages_api.route('/offline', methods=['GET'])
@login_required
def get_offline():
    """
    Çevrimdışı mesajları getir
    
    GET /api/messages/offline
    
    Response:
        {
            "success": true,
            "messages": [...],
            "count": 10
        }
    """
    try:
        current_user = get_current_user()
        messages = get_offline_messages(current_user['id'])
        
        # Mesajları teslim edildi olarak işaretle
        for msg in messages:
            mark_message_delivered(msg['id'])
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messages_api.route('/send', methods=['POST'])
@login_required
def send_message():
    """
    Mesaj gönder (broadcast, group, private)
    
    POST /api/messages/send
    Body: {
        "type": "broadcast",  // "broadcast", "group", "private"
        "content": "Merhaba",
        "group_id": 1,  // Sadece group için
        "receiver_id": 2  // Sadece private için
    }
    
    Response:
        {
            "success": true,
            "message_id": 123
        }
    """
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        message_type = data.get('type', '').lower()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Mesaj içeriği gerekli'
            }), 400
        
        if message_type not in ['broadcast', 'group', 'private']:
            return jsonify({
                'success': False,
                'error': 'Geçersiz mesaj tipi'
            }), 400
        
        # Mesaj tipine göre kaydet
        if message_type == 'broadcast':
            message_id = save_message(
                sender_id=current_user['id'],
                message_content=content,
                message_type='broadcast'
            )
        
        elif message_type == 'group':
            group_id = data.get('group_id')
            if not group_id:
                return jsonify({
                    'success': False,
                    'error': 'Grup ID gerekli'
                }), 400
            
            # Kullanıcı grupta mı kontrol et
            if not is_user_in_group(current_user['id'], group_id):
                return jsonify({
                    'success': False,
                    'error': 'Bu grubun üyesi değilsiniz'
                }), 403
            
            message_id = save_message(
                sender_id=current_user['id'],
                message_content=content,
                message_type='group',
                group_id=group_id
            )
        
        else:  # private
            receiver_id = data.get('receiver_id')
            if not receiver_id:
                return jsonify({
                    'success': False,
                    'error': 'Alıcı ID gerekli'
                }), 400
            
            message_id = save_message(
                sender_id=current_user['id'],
                message_content=content,
                message_type='private',
                receiver_id=receiver_id
            )
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'message': 'Mesaj gönderildi'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@messages_api.route('/<int:message_id>/read', methods=['POST'])
@login_required
def mark_read(message_id):
    """
    Mesajı okundu olarak işaretle
    
    POST /api/messages/123/read
    
    Response:
        {
            "success": true,
            "message": "Mesaj okundu olarak işaretlendi"
        }
    """
    try:
        mark_message_read(message_id)
        
        return jsonify({
            'success': True,
            'message': 'Mesaj okundu olarak işaretlendi'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500