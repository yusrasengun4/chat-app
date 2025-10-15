# auth/routes.py
from flask import Blueprint, request, jsonify, session, render_template
from database.queries import register_user, authenticate_user, set_user_online

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    success, user = authenticate_user(username, password)
    
    if success:
        session['user_id'] = user['id']
        session['username'] = user['username']
        set_user_online(user['id'], True)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Geçersiz kullanıcı adı veya şifre'
        }), 401
"""
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    success, result = register_user(username, password, email)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Kayıt başarılı!',
            'user_id': result
        })
    else:
        return jsonify({
            'success': False,
            'message': result
        }), 400
"""
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    success, result = register_user(username, password, email)
    
    if success:
        return jsonify({
            'success': True,
            'message': 'Kayıt başarılı!',
            'user_id': result
        })
    else:
        return jsonify({
            'success': False,
            'message': result
        }), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        set_user_online(session['user_id'], False)
        session.clear()
    
    return jsonify({'success': True})

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'username': session['username']
            }
        })
    return jsonify({'logged_in': False})