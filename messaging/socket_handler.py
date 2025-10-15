"""
from flask import request
from flask_socketio import join_room, leave_room, disconnect
from extensions import socketio  # SocketIO burada tanımlandıysa
from messaging import BroadcastChat, GroupChat, PrivateChat
from auth.decorators import get_current_user
from flask_socketio import emit
online_users = {}  # user_id -> socket_id mapping


@socketio.on('connect')
def handle_connect():
    print(f"Yeni bağlantı: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in list(online_users.items()):
        if sid == request.sid:
            user_id = uid
            del online_users[uid]
            print(f"Kullanıcı {uid} offline oldu.")
            break

"""
"""
@socketio.on('send_broadcast')
def handle_broadcast(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401
    BroadcastChat.send_message(data, user)
"""
"""
@socketio.on('send_broadcast')
def handle_broadcast(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401

    message = data.get('message')

    # 🔥 Tüm kullanıcılara yayın yap
    emit('receive_message', {
        'sender': user['username'],
        'message': message,
        'type': 'broadcast'
    }, broadcast=True)

    print(f"[Broadcast] {user['username']}: {message}")


@socketio.on('send_group')
def handle_group_message(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401
    GroupChat.send_message(data, user)


@socketio.on('join_group')
def handle_join_group(data):
    user = get_current_user()
    group_id = data['group_id']
    join_room(group_id)
    print(f"{user['username']} gruba katıldı: {group_id}")


@socketio.on('leave_group')
def handle_leave_group(data):
    user = get_current_user()
    group_id = data['group_id']
    leave_room(group_id)
    print(f"{user['username']} gruptan ayrıldı: {group_id}")


@socketio.on('send_private')
def handle_private_message(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401
    PrivateChat.send_message(data, user, online_users)
"""
from flask import request
from flask_socketio import join_room, leave_room, emit
from extensions import socketio
from messaging import BroadcastChat, GroupChat, PrivateChat
from auth.decorators import get_current_user

online_users = {}  # user_id -> socket_id mapping


@socketio.on('connect')
def handle_connect():
    print(f"Yeni bağlantı: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in list(online_users.items()):
        if sid == request.sid:
            user_id = uid
            del online_users[uid]
            print(f"Kullanıcı {uid} offline oldu.")
            break


@socketio.on('send_broadcast')
def handle_broadcast(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401

    # Mesajı 'message' veya 'content' olarak al
    message = data.get('message') or data.get('content')
    if not message:
        emit('error', {'message': 'Mesaj içeriği boş'})
        return

    # 🔹 Burada BroadcastChat üzerinden gönder ve kaydet
    BroadcastChat.send_message({'message': message}, user)


@socketio.on('send_group')
def handle_group_message(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401
    
    # ✅ 'content' -> 'message' dönüşümü yap
    if 'content' in data and 'message' not in data:
        data['message'] = data['content']
    
    GroupChat.send_message(data, user)


@socketio.on('join_group')
def handle_join_group(data):
    user = get_current_user()
    group_id = data['group_id']
    join_room(group_id)
    print(f"{user['username']} gruba katıldı: {group_id}")


@socketio.on('leave_group')
def handle_leave_group(data):
    user = get_current_user()
    group_id = data['group_id']
    leave_room(group_id)
    print(f"{user['username']} gruptan ayrıldı: {group_id}")


@socketio.on('send_private')
def handle_private_message(data):
    user = get_current_user()
    if not user:
        return {'error': 'Kimlik doğrulaması başarısız'}, 401
    
    # ✅ 'content' -> 'message' dönüşümü yap
    if 'content' in data and 'message' not in data:
        data['message'] = data['content']
    
    PrivateChat.send_message(data, user, online_users)


@socketio.on('join')
def handle_join(username):
    """Kullanıcı online olduğunda"""
    user = get_current_user()
    if user:
        online_users[user['id']] = request.sid
        print(f"✅ {username} online oldu (SID: {request.sid})")


@socketio.on('join_room')
def handle_join_room(data):
    """Sohbet odasına katıl"""
    room_type = data.get('room_type')
    room_id = data.get('room_id')
    
    if room_type == 'group':
        join_room(f"group_{room_id}")
        print(f"📥 Grup odasına katıldı: group_{room_id}")
    elif room_type == 'private':
        join_room(f"private_{room_id}")
        print(f"📥 Özel sohbet odasına katıldı: private_{room_id}")