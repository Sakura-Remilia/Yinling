# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, Role, Community, db
from app.auth.jwt_auth import jwt_required, role_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@api_v1.route('/users', methods=['GET'])
@jwt_required
@role_required('super_admin', 'community_admin')
def get_users():
    """获取用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', None)
    keyword = request.args.get('keyword', '')
    community_id = request.args.get('community_id', None, type=int)
    is_active = request.args.get('is_active', None)

    query = User.query

    # 权限过滤：社区管理员只能看本社区用户，且不能看到系统管理员
    current_user = request.current_user
    if current_user.role.name == 'community_admin':
        query = query.filter_by(community_id=current_user.community_id)
        # 排除系统管理员账户
        query = query.join(Role).filter(Role.name != 'super_admin')
    elif community_id:
        query = query.filter_by(community_id=community_id)

    if role:
        query = query.join(Role).filter(Role.name == role)

    if keyword:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{keyword}%'),
                User.real_name.ilike(f'%{keyword}%'),
                User.phone.ilike(f'%{keyword}%')
            )
        )

    if is_active is not None:
        query = query.filter_by(is_active=is_active)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = []
    for user in pagination.items:
        users.append({
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'phone': user.phone,
            'email': getattr(user, 'email', None),
            'role': user.role.name if hasattr(user, 'role') else None,
            'role_id': user.role_id,
            'avatar': getattr(user, 'avatar', None),
            'community_id': user.community_id,
            'is_active': getattr(user, 'is_active', True),
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': users,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/users/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get_or_404(user_id)

    # 权限检查
    current_user = request.current_user
    if current_user.role.name not in ['super_admin', 'community_admin'] and current_user.id != user_id:
        return jsonify({'success': False, 'message': '无权查看该用户'}), 403

    if current_user.role.name == 'community_admin' and user.community_id != current_user.community_id:
        return jsonify({'success': False, 'message': '无权查看该用户'}), 403

    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'phone': user.phone,
            'email': getattr(user, 'email', None),
            'role': user.role.name if hasattr(user, 'role') else None,
            'role_id': user.role_id,
            'avatar': getattr(user, 'avatar', None),
            'community_id': user.community_id,
            'is_active': getattr(user, 'is_active', True),
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
    })

@api_v1.route('/users', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_user():
    """创建用户 (仅超级管理员)"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    role_name = data.get('role', 'elderly')
    community_id = data.get('community_id', None)

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6位'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'success': False, 'message': '无效的角色'}), 400

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        real_name=real_name or username,
        phone=phone,
        email=email if email else None,
        role_id=role.id,
        community_id=community_id
    )

    try:
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'phone': user.phone,
                'role': role.name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin', 'community_admin')
def update_user(user_id):
    """更新用户"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    current_user = request.current_user

    # 权限检查
    if current_user.role.name == 'community_admin':
        if user.community_id != current_user.community_id:
            return jsonify({'success': False, 'message': '无权修改该用户'}), 403
        # 社区管理员不能修改角色
        if 'role' in data or 'role_id' in data:
            return jsonify({'success': False, 'message': '无权修改用户角色'}), 403

    # 更新字段
    if 'real_name' in data:
        user.real_name = data['real_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()
    if 'email' in data:
        user.email = data['email'].strip() if data['email'] else None
    if 'community_id' in data and current_user.role.name == 'super_admin':
        user.community_id = data['community_id']
    if 'role' in data and current_user.role.name == 'super_admin':
        role = Role.query.filter_by(name=data['role']).first()
        if role:
            user.role_id = role.id

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用户更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'phone': user.phone,
                'role': user.role.name if hasattr(user, 'role') else None
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/users/<int:user_id>/toggle-active', methods=['PUT'])
@jwt_required
@role_required('super_admin', 'community_admin')
def toggle_user_active(user_id):
    """启用/禁用用户"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data or 'is_active' not in data:
        return jsonify({'success': False, 'message': '缺少is_active参数'}), 400

    current_user = request.current_user

    # 权限检查
    if current_user.role.name == 'community_admin':
        if user.community_id != current_user.community_id:
            return jsonify({'success': False, 'message': '无权修改该用户'}), 403

    # 不能禁用自己
    if current_user.id == user_id:
        return jsonify({'success': False, 'message': '不能禁用自己的账号'}), 400

    if hasattr(user, 'is_active'):
        user.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f"用户{'禁用' if not data['is_active'] else '启用'}成功"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/users/<int:user_id>/reset-password', methods=['PUT'])
@jwt_required
@role_required('super_admin', 'community_admin')
def reset_user_password(user_id):
    """重置用户密码"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if not data or 'new_password' not in data:
        return jsonify({'success': False, 'message': '缺少new_password参数'}), 400

    new_password = data['new_password']
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6位'}), 400

    current_user = request.current_user

    # 权限检查
    if current_user.role.name == 'community_admin':
        if user.community_id != current_user.community_id:
            return jsonify({'success': False, 'message': '无权重置该用户密码'}), 403

    user.password_hash = generate_password_hash(new_password)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '密码重置成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'重置失败: {str(e)}'}), 500

@api_v1.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_user(user_id):
    """删除用户 (仅超级管理员)"""
    user = User.query.get_or_404(user_id)

    # 不能删除自己
    if request.current_user.id == user_id:
        return jsonify({'success': False, 'message': '不能删除自己的账号'}), 400

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500