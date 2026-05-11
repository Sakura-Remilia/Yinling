# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, Role, db
from app.auth.jwt_auth import generate_tokens, verify_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@api_v1.route('/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    if hasattr(user, 'is_active') and not user.is_active:
        return jsonify({'success': False, 'message': '账号已被禁用'}), 401

    # 验证密码
    if not check_password_hash(user.password_hash, password):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

    # 生成tokens
    access_token, refresh_token = generate_tokens(user)

    return jsonify({
        'success': True,
        'message': '登录成功',
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'phone': user.phone,
                'role': user.role.name if hasattr(user, 'role') else None,
                'avatar': user.avatar if hasattr(user, 'avatar') else None,
                'community_id': user.community_id if hasattr(user, 'community_id') else None
            }
        }
    })

@api_v1.route('/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')
    real_name = data.get('real_name', '').strip()
    phone = data.get('phone', '').strip()
    role_name = data.get('role', 'elderly')

    # 验证必填字段
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': '密码长度至少6位'}), 400

    # 检查用户名是否存在
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400

    # 获取角色
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'success': False, 'message': '无效的角色'}), 400

    # 创建用户
    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        real_name=real_name or username,
        phone=phone,
        role_id=role.id
    )

    try:
        db.session.add(user)
        db.session.commit()

        access_token, refresh_token = generate_tokens(user)

        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'real_name': user.real_name,
                    'phone': user.phone,
                    'role': role.name,
                    'avatar': None
                }
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@api_v1.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """刷新access_token"""
    data = request.get_json()
    if not data or 'refresh_token' not in data:
        return jsonify({'success': False, 'message': '缺少refresh_token'}), 400

    payload = verify_token(data['refresh_token'])
    if not payload:
        return jsonify({'success': False, 'message': 'refresh_token无效或已过期'}), 401

    user = User.query.get(payload['sub'])
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 401

    if hasattr(user, 'is_active') and not user.is_active:
        return jsonify({'success': False, 'message': '账号已被禁用'}), 401

    access_token, refresh_token = generate_tokens(user)

    return jsonify({
        'success': True,
        'data': {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    })

@api_v1.route('/auth/user', methods=['GET'])
@jwt_required
def get_current_user():
    """获取当前用户信息"""
    user = request.current_user

    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'username': user.username,
            'real_name': user.real_name,
            'phone': user.phone,
            'email': user.email if hasattr(user, 'email') else None,
            'role': user.role.name if hasattr(user, 'role') else None,
            'avatar': user.avatar if hasattr(user, 'avatar') else None,
            'community_id': user.community_id if hasattr(user, 'community_id') else None,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
    })

@api_v1.route('/auth/profile', methods=['PUT'])
@jwt_required
def update_profile():
    """更新个人资料"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    # 更新允许的字段
    if 'real_name' in data:
        user.real_name = data['real_name'].strip()
    if 'phone' in data:
        user.phone = data['phone'].strip()
    if 'email' in data and data['email']:
        user.email = data['email'].strip()

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '资料更新成功',
            'data': {
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'phone': user.phone,
                'email': getattr(user, 'email', None),
                'role': user.role.name if hasattr(user, 'role') else None,
                'avatar': getattr(user, 'avatar', None)
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/auth/password', methods=['PUT'])
@jwt_required
def change_password():
    """修改密码"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': '原密码和新密码不能为空'}), 400

    if not check_password_hash(user.password_hash, old_password):
        return jsonify({'success': False, 'message': '原密码错误'}), 400

    if len(new_password) < 6:
        return jsonify({'success': False, 'message': '新密码长度至少6位'}), 400

    user.password_hash = generate_password_hash(new_password)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '密码修改成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'修改失败: {str(e)}'}), 500

@api_v1.route('/auth/logout', methods=['POST'])
@jwt_required
def logout():
    """登出 (前端删除token即可)"""
    return jsonify({'success': True, 'message': '登出成功'})