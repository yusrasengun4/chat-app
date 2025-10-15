from flask import Blueprint, request, jsonify
from auth.decorators import login_required, get_current_user
from database import (
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    get_online_users,
    set_user_online
)

# Blueprint oluştur
users_api = Blueprint('users_api', __name__)


@users_api.route('/all', methods=['GET'])
@login_required
def get_users():
    """
    Tüm kullanıcıları getir
    
    GET /api/users/all
    
    Response:
        {
            "success": true,
            "users": [
                {
                    "id": 1,
                    "username": "ahmet",
                    "is_online": 1,
                    "last_seen": "2024-01-01 12:00:00"
                },
                ...
            ],
            "count": 10
        }
    """
    try:
        users = get_all_users()
        
        # Şifre hash'lerini çıkar (güvenlik)
        safe_users = []
        for user in users:
            safe_users.append({
                'id': user['id'],
                'username': user['username'],
                'is_online': user.get('is_online', 0),
                'last_seen': user.get('last_seen')
            })
        
        return jsonify({
            'success': True,
            'users': safe_users,
            'count': len(safe_users)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_api.route('/online', methods=['GET'])
@login_required
def get_users_online():
    """
    Çevrimiçi kullanıcıları getir
    
    GET /api/users/online
    
    Response:
        {
            "success": true,
            "users": [...],
            "count": 5
        }
    """
    try:
        users = get_online_users()
        
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_api.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def get_user_profile(user_id):
    """
    Kullanıcı profili getir
    
    GET /api/users/profile/1
    
    Response:
        {
            "success": true,
            "user": {
                "id": 1,
                "username": "ahmet",
                "email": "ahmet@example.com",
                "is_online": 1,
                "created_at": "2024-01-01 10:00:00"
            }
        }
    """
    try:
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Kullanıcı bulunamadı'
            }), 404
        
        # Şifre hash'ini çıkar
        safe_user = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email'),
            'is_online': user.get('is_online', 0),
            'last_seen': user.get('last_seen'),
            'created_at': user.get('created_at')
        }
        
        return jsonify({
            'success': True,
            'user': safe_user
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_api.route('/search', methods=['POST'])
@login_required
def search_users():
    """
    Kullanıcı ara
    
    POST /api/users/search
    Body: {"query": "ahmet"}
    
    Response:
        {
            "success": true,
            "users": [...],
            "count": 3
        }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip().lower()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Arama sorgusu gerekli'
            }), 400
        
        # Tüm kullanıcıları al ve filtrele
        all_users = get_all_users()
        
        filtered_users = [
            user for user in all_users
            if query in user['username'].lower()
        ]
        
        return jsonify({
            'success': True,
            'users': filtered_users,
            'count': len(filtered_users)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@users_api.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """
    Mevcut kullanıcının bilgilerini getir
    
    GET /api/users/me
    
    Response:
        {
            "success": true,
            "user": {...}
        }
    """
    try:
        current_user = get_current_user()
        user = get_user_by_username(current_user['username'])
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Kullanıcı bulunamadı'
            }), 404
        
        safe_user = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email'),
            'is_online': user.get('is_online', 0),
            'created_at': user.get('created_at')
        }
        
        return jsonify({
            'success': True,
            'user': safe_user
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

