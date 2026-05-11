# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import Activity, ActivityRegistration, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime

@api_v1.route('/activities', methods=['GET'])
def get_activities():
    """获取活动列表 (公开)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', 'published')

    query = Activity.query

    if status:
        query = query.filter_by(status=status)

    pagination = query.filter(
        Activity.start_time >= datetime.now()
    ).order_by(Activity.start_time.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    activities = []
    for a in pagination.items:
        activities.append({
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'start_time': a.start_time.isoformat() if a.start_time else None,
            'end_time': a.end_time.isoformat() if a.end_time else None,
            'location': a.location,
            'max_participants': a.max_participants,
            'registered_count': getattr(a, 'registered_count', 0),
            'community_name': a.community.name if hasattr(a, 'community') and a.community else '平台活动'
        })

    return jsonify({
        'success': True,
        'data': activities,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/activities/<int:activity_id>', methods=['GET'])
def get_activity_detail(activity_id):
    """获取活动详情"""
    activity = Activity.query.get_or_404(activity_id)

    return jsonify({
        'success': True,
        'data': {
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'start_time': activity.start_time.isoformat() if activity.start_time else None,
            'end_time': activity.end_time.isoformat() if activity.end_time else None,
            'location': activity.location,
            'max_participants': activity.max_participants,
            'registered_count': getattr(activity, 'registered_count', 0),
            'community_name': activity.community.name if hasattr(activity, 'community') and activity.community else '平台活动',
            'status': activity.status
        }
    })

@api_v1.route('/activities/<int:activity_id>/register', methods=['POST'])
@jwt_required
@role_required('elderly')
def register_activity(activity_id):
    """报名活动"""
    user = request.current_user
    activity = Activity.query.get_or_404(activity_id)

    if activity.status != 'published':
        return jsonify({'success': False, 'message': '活动未开始报名'}), 400

    if activity.max_participants > 0:
        registered_count = ActivityRegistration.query.filter_by(activity_id=activity_id).count()
        if registered_count >= activity.max_participants:
            return jsonify({'success': False, 'message': '报名已满'}), 400

    # 检查是否已报名
    existing = ActivityRegistration.query.filter_by(
        activity_id=activity_id,
        elderly_id=user.id
    ).first()

    if existing:
        return jsonify({'success': False, 'message': '您已报名该活动'}), 400

    registration = ActivityRegistration(
        activity_id=activity_id,
        elderly_id=user.id,
        is_attended=False
    )

    try:
        db.session.add(registration)
        # 更新报名数量
        if hasattr(activity, 'registered_count'):
            activity.registered_count = ActivityRegistration.query.filter_by(activity_id=activity_id).count() + 1
        db.session.commit()
        return jsonify({'success': True, 'message': '报名成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'报名失败: {str(e)}'}), 500

@api_v1.route('/activities/<int:activity_id>/cancel', methods=['POST'])
@jwt_required
@role_required('elderly')
def cancel_registration(activity_id):
    """取消报名"""
    user = request.current_user

    registration = ActivityRegistration.query.filter_by(
        activity_id=activity_id,
        elderly_id=user.id
    ).first()

    if not registration:
        return jsonify({'success': False, 'message': '您未报名该活动'}), 400

    try:
        db.session.delete(registration)
        activity = Activity.query.get(activity_id)
        if activity and hasattr(activity, 'registered_count'):
            activity.registered_count = max(0, activity.registered_count - 1)
        db.session.commit()
        return jsonify({'success': True, 'message': '取消报名成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500

@api_v1.route('/activities/my-registrations', methods=['GET'])
@jwt_required
@role_required('elderly')
def get_my_registrations():
    """获取我的报名"""
    user = request.current_user

    registrations = ActivityRegistration.query.filter_by(elderly_id=user.id).order_by(
        ActivityRegistration.created_at.desc()
    ).all()

    data = []
    for reg in registrations:
        activity = reg.activity
        if activity:
            data.append({
                'id': reg.id,
                'activity_id': activity.id,
                'title': activity.title,
                'start_time': activity.start_time.isoformat() if activity.start_time else None,
                'location': activity.location,
                'is_attended': reg.is_attended,
                'registered_at': reg.created_at.isoformat() if hasattr(reg, 'created_at') else None
            })

    return jsonify({'success': True, 'data': data})