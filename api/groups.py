from flask import Blueprint, request, jsonify
from auth.decorators import login_required, get_current_user
from database import (
    create_group,
    get_all_groups,
    get_group_by_id,
    get_user_groups,
    get_group_members,
    add_user_to_group,
    remove_user_from_group,
    is_user_in_group
)

# Blueprint oluştur
groups_api = Blueprint('groups_api', __name__)


@groups_api.route('/all', methods=['GET'])
@login_required
def get_groups():
    """
    Tüm grupları getir
    
    GET /api/groups/all
    
    Response:
        {
            "success": true,
            "groups": [
                {
                    "id": 1,
                    "group_name": "Genel Sohbet",
                    "description": "...",
                    "member_count": 10,
                    "created_at": "..."
                },
                ...
            ],
            "count": 5
        }
    """
    try:
        groups = get_all_groups()
        
        return jsonify({
            'success': True,
            'groups': groups,
            'count': len(groups)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/my-groups', methods=['GET'])
@login_required
def get_my_groups():
    """
    Mevcut kullanıcının gruplarını getir
    
    GET /api/groups/my-groups
    
    Response:
        {
            "success": true,
            "groups": [...],
            "count": 3
        }
    """
    try:
        current_user = get_current_user()
        groups = get_user_groups(current_user['id'])
        
        return jsonify({
            'success': True,
            'groups': groups,
            'count': len(groups)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/create', methods=['POST'])
@login_required
def create_new_group():
    """
    Yeni grup oluştur
    
    POST /api/groups/create
    Body: {
        "group_name": "Arkadaşlar",
        "description": "Arkadaş grubu"
    }
    
    Response:
        {
            "success": true,
            "group_id": 5,
            "message": "Grup oluşturuldu"
        }
    """
    try:
        data = request.get_json()
        group_name = data.get('group_name', '').strip()
        description = data.get('description', '').strip() or None
        
        if not group_name:
            return jsonify({
                'success': False,
                'error': 'Grup adı gerekli'
            }), 400
        
        if len(group_name) < 3:
            return jsonify({
                'success': False,
                'error': 'Grup adı en az 3 karakter olmalı'
            }), 400
        
        current_user = get_current_user()
        success, group_id = create_group(
            group_name=group_name,
            created_by=current_user['id'],
            description=description
        )
        
        if success:
            return jsonify({
                'success': True,
                'group_id': group_id,
                'message': f'"{group_name}" grubu oluşturuldu'
            })
        else:
            return jsonify({
                'success': False,
                'error': group_id  # Hata mesajı
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/<int:group_id>', methods=['GET'])
@login_required
def get_group_info(group_id):
    """
    Grup bilgilerini getir
    
    GET /api/groups/1
    
    Response:
        {
            "success": true,
            "group": {...},
            "members": [...]
        }
    """
    try:
        group = get_group_by_id(group_id)
        
        if not group:
            return jsonify({
                'success': False,
                'error': 'Grup bulunamadı'
            }), 404
        
        members = get_group_members(group_id)
        
        return jsonify({
            'success': True,
            'group': dict(group),
            'members': members,
            'member_count': len(members)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/<int:group_id>/join', methods=['POST'])
@login_required
def join_group(group_id):
    """
    Gruba katıl
    
    POST /api/groups/1/join
    
    Response:
        {
            "success": true,
            "message": "Gruba katıldınız"
        }
    """
    try:
        current_user = get_current_user()
        
        # Grup var mı kontrol et
        group = get_group_by_id(group_id)
        if not group:
            return jsonify({
                'success': False,
                'error': 'Grup bulunamadı'
            }), 404
        
        # Zaten üye mi kontrol et
        if is_user_in_group(current_user['id'], group_id):
            return jsonify({
                'success': False,
                'error': 'Zaten bu grubun üyesisiniz'
            }), 400
        
        # Gruba ekle
        success = add_user_to_group(group_id, current_user['id'])
        
        if success:
            return jsonify({
                'success': True,
                'message': f'"{group["group_name"]}" grubuna katıldınız'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Gruba katılınamadı'
            }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    """
    Gruptan ayrıl
    
    POST /api/groups/1/leave
    
    Response:
        {
            "success": true,
            "message": "Gruptan ayrıldınız"
        }
    """
    try:
        current_user = get_current_user()
        
        # Grup var mı kontrol et
        group = get_group_by_id(group_id)
        if not group:
            return jsonify({
                'success': False,
                'error': 'Grup bulunamadı'
            }), 404
        
        # Üye mi kontrol et
        if not is_user_in_group(current_user['id'], group_id):
            return jsonify({
                'success': False,
                'error': 'Bu grubun üyesi değilsiniz'
            }), 400
        
        # Gruptan çıkar
        remove_user_from_group(current_user['id'], group_id)
        
        return jsonify({
            'success': True,
            'message': f'"{group["group_name"]}" grubundan ayrıldınız'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@groups_api.route('/<int:group_id>/members', methods=['GET'])
@login_required
def get_members(group_id):
    """
    Grup üyelerini getir
    
    GET /api/groups/1/members
    
    Response:
        {
            "success": true,
            "members": [...],
            "count": 5
        }
    """
    try:
        # Grup var mı kontrol et
        group = get_group_by_id(group_id)
        if not group:
            return jsonify({
                'success': False,
                'error': 'Grup bulunamadı'
            }), 404
        
        members = get_group_members(group_id)
        
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
