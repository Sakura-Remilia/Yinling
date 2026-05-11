# -*- coding: utf-8 -*-
from flask import request, jsonify, current_app
from app.api_v1 import api_v1
from app.models import SOSAlert, User, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime
import random
import string

@api_v1.route('/sos/trigger', methods=['POST'])
@jwt_required
@role_required('elderly')
def trigger_sos():
    """触发SOS警报"""
    user = request.current_user
    data = request.get_json() or {}

    # 生成警报编号
    alert_no = f'SOS{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(1000, 9999)}'

    alert = SOSAlert(
        alert_no=alert_no,
        elderly_id=user.id,
        community_id=user.community_id,
        address=data.get('address', ''),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        status='pending'
    )

    try:
        db.session.add(alert)
        db.session.commit()

        # 触发WebSocket通知 (如果可用)
        try:
            from app import socketio
            if socketio:
                socketio.emit('new_sos_alert', {
                    'alert_id': alert.id,
                    'alert_no': alert.alert_no,
                    'elderly_name': user.real_name,
                    'elderly_phone': user.phone,
                    'address': alert.address,
                    'community_id': alert.community_id,
                    'created_at': alert.created_at.isoformat()
                }, room=f'community_{alert.community_id}')
        except Exception:
            pass  # WebSocket未初始化，静默忽略

        return jsonify({
            'success': True,
            'message': 'SOS警报已发送',
            'data': {'alert_id': alert.id, 'alert_no': alert.alert_no}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500

@api_v1.route('/sos/my-alerts', methods=['GET'])
@jwt_required
@role_required('elderly')
def get_my_alerts():
    """获取我的SOS警报"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = SOSAlert.query.filter_by(elderly_id=user.id).order_by(
        SOSAlert.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    alerts = []
    for alert in pagination.items:
        alerts.append({
            'id': alert.id,
            'alert_no': alert.alert_no,
            'address': alert.address,
            'status': alert.status,
            'responder_name': alert.responder.real_name if hasattr(alert, 'responder') and alert.responder else None,
            'resolved_at': alert.resolved_at.isoformat() if hasattr(alert, 'resolved_at') and alert.resolved_at else None,
            'created_at': alert.created_at.isoformat() if hasattr(alert, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': alerts,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/sos/<int:alert_id>', methods=['GET'])
@jwt_required
def get_sos_detail(alert_id):
    """获取SOS警报详情"""
    alert = SOSAlert.query.get_or_404(alert_id)

    return jsonify({
        'success': True,
        'data': {
            'id': alert.id,
            'alert_no': alert.alert_no,
            'elderly_name': alert.elderly.real_name if hasattr(alert, 'elderly') and alert.elderly else '匿名',
            'elderly_phone': alert.elderly.phone if hasattr(alert, 'elderly') and alert.elderly else '',
            'address': alert.address,
            'latitude': alert.latitude,
            'longitude': alert.longitude,
            'status': alert.status,
            'responder_name': alert.responder.real_name if hasattr(alert, 'responder') and alert.responder else None,
            'resolved_at': alert.resolved_at.isoformat() if hasattr(alert, 'resolved_at') and alert.resolved_at else None,
            'created_at': alert.created_at.isoformat() if hasattr(alert, 'created_at') else None
        }
    })

@api_v1.route('/sos/<int:alert_id>/respond', methods=['POST'])
@jwt_required
@role_required('worker', 'community_admin', 'volunteer')
def respond_sos(alert_id):
    """响应SOS警报"""
    user = request.current_user
    alert = SOSAlert.query.get_or_404(alert_id)

    if alert.status != 'pending':
        return jsonify({'success': False, 'message': '该警报已被响应'}), 400

    alert.responder_id = user.id
    alert.status = 'responding'

    try:
        db.session.commit()

        # 通知老人
        try:
            from app import socketio
            if socketio:
                socketio.emit('sos_responded', {
                    'alert_id': alert.id,
                    'responder_name': user.real_name
                }, room=f'user_{alert.elderly_id}')
        except Exception:
            pass

        return jsonify({'success': True, 'message': '已响应SOS警报'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'响应失败: {str(e)}'}), 500

@api_v1.route('/sos/<int:alert_id>/resolve', methods=['POST'])
@jwt_required
@role_required('worker', 'community_admin', 'volunteer')
def resolve_sos(alert_id):
    """解除SOS警报"""
    alert = SOSAlert.query.get_or_404(alert_id)
    data = request.get_json() or {}

    if alert.status not in ['pending', 'responding']:
        return jsonify({'success': False, 'message': '该警报已解除'}), 400

    alert.status = 'resolved'
    alert.resolved_at = datetime.now()
    alert.resolution_notes = data.get('notes', '')

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'SOS警报已解除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'解除失败: {str(e)}'}), 500

@api_v1.route('/sos/<int:alert_id>/cancel', methods=['POST'])
@jwt_required
@role_required('elderly')
def cancel_sos(alert_id):
    """取消SOS警报"""
    alert = SOSAlert.query.filter_by(id=alert_id, elderly_id=request.current_user.id).first_or_404()

    if alert.status == 'resolved':
        return jsonify({'success': False, 'message': '该警报已解除，无法取消'}), 400

    alert.status = 'cancelled'

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'SOS警报已取消'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'取消失败: {str(e)}'}), 500