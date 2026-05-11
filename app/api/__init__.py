# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import (User, ServiceOrder, SOSAlert, HealthRecord, Activity, 
                        ActivityRegistration, News, VolunteerServiceRecord)
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/user/info')
@login_required
def user_info():
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'real_name': current_user.real_name,
        'phone': current_user.phone,
        'role': current_user.role.name if current_user.role else None
    })

@api.route('/sos/trigger', methods=['POST'])
@login_required
def trigger_sos():
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    import random
    import string
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    alert_no = f'SOS{timestamp}{random_str}'
    
    data = request.get_json()
    alert = SOSAlert(
        alert_no=alert_no,
        elderly_id=current_user.id,
        longitude=data.get('longitude'),
        latitude=data.get('latitude'),
        address=data.get('address', ''),
        status='active'
    )
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'SOS警报已发送',
        'alert_id': alert.id,
        'alert_no': alert.alert_no
    })

@api.route('/sos/<int:alert_id>/respond', methods=['POST'])
@login_required
def respond_sos(alert_id):
    alert = SOSAlert.query.get_or_404(alert_id)
    
    if alert.status != 'active':
        return jsonify({'success': False, 'message': '该警报已处理'}), 400
    
    alert.responder_id = current_user.id
    alert.responded_at = datetime.utcnow()
    alert.status = 'responding'
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已响应警报'})

@api.route('/sos/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_sos(alert_id):
    alert = SOSAlert.query.get_or_404(alert_id)
    
    if alert.responder_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    data = request.get_json()
    alert.status = 'resolved'
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = data.get('notes', '')
    db.session.commit()
    
    return jsonify({'success': True, 'message': '警报已解除'})

@api.route('/health/record', methods=['POST'])
@login_required
def record_health():
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    data = request.get_json()
    record = HealthRecord(
        elderly_id=current_user.id,
        record_type=data.get('record_type'),
        systolic=data.get('systolic'),
        diastolic=data.get('diastolic'),
        blood_sugar=data.get('blood_sugar'),
        notes=data.get('notes', '')
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '健康数据已记录', 'record_id': record.id})

@api.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    order = ServiceOrder.query.get_or_404(order_id)
    
    if order.provider_id != current_user.id and order.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['accepted', 'in_progress', 'completed', 'cancelled']:
        order.status = new_status
        
        if new_status == 'accepted':
            order.accepted_at = datetime.utcnow()
        elif new_status == 'in_progress':
            order.arrived_at = datetime.utcnow()
            order.started_at = datetime.utcnow()
        elif new_status == 'completed':
            order.completed_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': '订单状态已更新'})
    
    return jsonify({'success': False, 'message': '无效的状态'}), 400

@api.route('/activities/<int:activity_id>/register', methods=['POST'])
@login_required
def register_activity_api(activity_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    
    existing = ActivityRegistration.query.filter_by(
        activity_id=activity_id, 
        elderly_id=current_user.id
    ).first()
    
    if existing:
        return jsonify({'success': False, 'message': '您已报名此活动'}), 400
    
    is_waitlist = activity.max_participants > 0 and activity.current_participants >= activity.max_participants
    
    registration = ActivityRegistration(
        activity_id=activity_id,
        elderly_id=current_user.id,
        is_waitlist=is_waitlist
    )
    db.session.add(registration)
    
    if not is_waitlist:
        activity.current_participants += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': '报名成功' + ('，您在候补名单中' if is_waitlist else ''),
        'is_waitlist': is_waitlist
    })

@api.route('/activities/<int:activity_id>/cancel', methods=['POST'])
@login_required
def cancel_activity_registration(activity_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    registration = ActivityRegistration.query.filter_by(
        activity_id=activity_id,
        elderly_id=current_user.id
    ).first_or_404()
    
    if not registration.is_waitlist:
        activity = registration.activity
        activity.current_participants -= 1
        
        waitlist = ActivityRegistration.query.filter_by(
            activity_id=activity_id,
            is_waitlist=True
        ).order_by(ActivityRegistration.registered_at).first()
        
        if waitlist:
            waitlist.is_waitlist = False
            activity.current_participants += 1
    
    registration.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已取消报名'})

@api.route('/stats/dashboard')
@login_required
def dashboard_stats():
    stats = {}
    
    if current_user.is_elderly():
        stats['pending_orders'] = ServiceOrder.query.filter_by(
            elderly_id=current_user.id, status='pending'
        ).count()
        stats['upcoming_activities'] = ActivityRegistration.query.filter_by(
            elderly_id=current_user.id, status='registered'
        ).join(Activity).filter(Activity.start_time > datetime.utcnow()).count()
    
    elif current_user.is_volunteer():
        profile = current_user.volunteer_profile
        stats['total_hours'] = profile.total_service_hours if profile else 0
        stats['total_points'] = profile.total_points if profile else 0
        stats['active_orders'] = ServiceOrder.query.filter_by(
            provider_id=current_user.id, status='in_progress'
        ).count()
    
    elif current_user.is_worker():
        stats['active_orders'] = ServiceOrder.query.filter_by(
            provider_id=current_user.id, status='in_progress'
        ).count()
        stats['completed_orders'] = ServiceOrder.query.filter_by(
            provider_id=current_user.id, status='completed'
        ).count()
    
    return jsonify(stats)

@api.route('/news/list')
def news_list():
    news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(10).all()
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'news_type': n.news_type,
        'published_at': n.published_at.isoformat() if n.published_at else None,
        'view_count': n.view_count
    } for n in news])

@api.route('/activities/list')
def activities_list():
    activities = Activity.query.filter(
        Activity.status == 'published',
        Activity.is_public == True,
        Activity.end_time > datetime.utcnow()
    ).order_by(Activity.start_time).limit(10).all()
    
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'activity_type': a.activity_type,
        'start_time': a.start_time.isoformat(),
        'end_time': a.end_time.isoformat(),
        'location': a.location,
        'max_participants': a.max_participants,
        'current_participants': a.current_participants
    } for a in activities])
