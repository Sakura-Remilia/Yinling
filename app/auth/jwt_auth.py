# -*- coding: utf-8 -*-
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

def generate_tokens(user):
    """生成access_token和refresh_token"""
    access_token = jwt.encode({
        'sub': user.id,
        'role': user.role.name if hasattr(user, 'role') else user.role_id,
        'username': user.username,
        'exp': datetime.utcnow() + timedelta(minutes=15),
        'iat': datetime.utcnow()
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    refresh_token = jwt.encode({
        'sub': user.id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    return access_token, refresh_token

def verify_token(token):
    """验证token并返回payload"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header:
            return jsonify({'success': False, 'message': '缺少认证令牌'}), 401

        try:
            token = auth_header.replace('Bearer ', '', 1)
        except Exception:
            return jsonify({'success': False, 'message': '无效的认证格式'}), 401

        if not token:
            return jsonify({'success': False, 'message': '缺少认证令牌'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'success': False, 'message': '令牌无效或已过期'}), 401

        from app.models import User
        current_user = User.query.get(payload['sub'])
        if not current_user:
            return jsonify({'success': False, 'message': '用户不存在'}), 401

        if hasattr(current_user, 'is_active') and not current_user.is_active:
            return jsonify({'success': False, 'message': '用户已被禁用'}), 401

        request.current_user = current_user
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'success': False, 'message': '未认证'}), 401

            user_role = request.current_user.role.name if hasattr(request.current_user, 'role') else None
            if user_role not in roles:
                return jsonify({'success': False, 'message': '无权访问'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        user = request.current_user
        if hasattr(user, 'role'):
            role_name = user.role.name
            if role_name not in ['super_admin', 'community_admin']:
                return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated