# auth/decorators.py
from functools import wraps
from flask import session, jsonify, redirect, url_for, request  # request eklendi

def login_required(f):
    """Login kontrolü decorator'ı"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Giriş yapmanız gerekiyor'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Mevcut kullanıcıyı al"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'username': session['username']
        }
    return None


