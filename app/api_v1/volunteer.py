# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, VolunteerProfile, ServiceOrder, VolunteerServiceRecord, PointTransaction, PointProduct, PointExchange, ElderlyProfile, HealthRecord, MedicationReminder, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime

@api_v1.route('/volunteer/profile', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_volunteer_profile():
    """获取志愿者档案"""
    user = request.current_user
    profile = VolunteerProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.id,
                'real_name': user.real_name,
                'skills': '',
                'total_service_hours': 0,
                'total_points': 0,
                'is_verified': False
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'user_id': user.id,
            'real_name': user.real_name,
            'skills': profile.skills,
            'total_service_hours': profile.total_service_hours,
            'total_points': profile.total_points,
            'is_verified': profile.is_verified
        }
    })

@api_v1.route('/volunteer/profile', methods=['PUT'])
@jwt_required
@role_required('volunteer')
def update_volunteer_profile():
    """更新志愿者档案"""
    user = request.current_user
    profile = VolunteerProfile.query.filter_by(user_id=user.id).first()
    data = request.get_json()

    if not profile:
        profile = VolunteerProfile(user_id=user.id)
        db.session.add(profile)

    if 'skills' in data:
        profile.skills = data['skills']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '档案更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/volunteer/tasks', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_available_tasks():
    """获取可接任务列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ServiceOrder.query.filter(
        ServiceOrder.status == 'pending',
        ServiceOrder.provider_type == 'volunteer',
        ServiceOrder.provider_id.is_(None)
    )

    pagination = query.order_by(ServiceOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    tasks = []
    for order in pagination.items:
        tasks.append({
            'id': order.id,
            'order_no': order.order_no,
            'service_name': order.category.name if hasattr(order, 'category') and order.category else '志愿服务',
            'elderly_name': order.elderly.real_name if hasattr(order, 'elderly') and order.elderly else '匿名',
            'address': order.address,
            'scheduled_time': order.scheduled_time.isoformat() if order.scheduled_time else None,
            'status': order.status,
            'created_at': order.created_at.isoformat() if hasattr(order, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': tasks,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/volunteer/tasks/<int:task_id>/accept', methods=['POST'])
@jwt_required
@role_required('volunteer')
def accept_task(task_id):
    """接取任务"""
    user = request.current_user
    order = ServiceOrder.query.get_or_404(task_id)

    if order.status != 'pending':
        return jsonify({'success': False, 'message': '该任务已被接取'}), 400

    if order.provider_id:
        return jsonify({'success': False, 'message': '该任务已被其他志愿者接取'}), 400

    order.provider_id = user.id
    order.provider_type = 'volunteer'
    order.status = 'accepted'

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '任务接取成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'接取失败: {str(e)}'}), 500

@api_v1.route('/volunteer/orders', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_volunteer_orders():
    """获取我的订单列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)

    query = ServiceOrder.query.filter_by(provider_id=user.id, provider_type='volunteer')

    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(ServiceOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    orders = []
    for order in pagination.items:
        orders.append({
            'id': order.id,
            'order_no': order.order_no,
            'service_name': order.category.name if hasattr(order, 'category') and order.category else '志愿服务',
            'elderly_name': order.elderly.real_name if hasattr(order, 'elderly') and order.elderly else '匿名',
            'address': order.address,
            'scheduled_time': order.scheduled_time.isoformat() if order.scheduled_time else None,
            'status': order.status,
            'created_at': order.created_at.isoformat() if hasattr(order, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': orders,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/volunteer/orders/<int:order_id>/checkin', methods=['POST'])
@jwt_required
@role_required('volunteer')
def volunteer_checkin(order_id):
    """志愿者签到"""
    user = request.current_user
    order = ServiceOrder.query.filter_by(id=order_id, provider_id=user.id).first_or_404()

    if order.status != 'accepted':
        return jsonify({'success': False, 'message': '当前状态不允许签到'}), 400

    order.status = 'in_progress'
    order.check_in_time = datetime.now()

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '签到成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'签到失败: {str(e)}'}), 500

@api_v1.route('/volunteer/orders/<int:order_id>/complete', methods=['POST'])
@jwt_required
@role_required('volunteer')
def volunteer_complete(order_id):
    """完成任务"""
    user = request.current_user
    order = ServiceOrder.query.filter_by(id=order_id, provider_id=user.id).first_or_404()
    data = request.get_json() or {}

    if order.status != 'in_progress':
        return jsonify({'success': False, 'message': '当前状态不允许完成'}), 400

    order.status = 'completed'
    order.check_out_time = datetime.now()

    # 计算服务时长并添加积分
    if order.check_in_time and order.check_out_time:
        duration = (order.check_out_time - order.check_in_time).seconds / 60
        points_earned = int(duration / 30) * 10  # 每30分钟10积分

        # 添加服务记录
        record = VolunteerServiceRecord(
            volunteer_id=user.id,
            order_id=order.id,
            duration_minutes=int(duration),
            points_earned=points_earned,
            start_time=order.check_in_time,
            end_time=order.check_out_time
        )
        db.session.add(record)

        # 更新志愿者积分
        profile = VolunteerProfile.query.filter_by(user_id=user.id).first()
        if profile:
            profile.total_service_hours += duration / 60
            profile.total_points += points_earned

        # 添加积分流水
        point_tx = PointTransaction(
            user_id=user.id,
            amount=points_earned,
            transaction_type='service_reward',
            balance_after=profile.total_points if profile else points_earned
        )
        db.session.add(point_tx)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '服务完成'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/volunteer/records', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_service_records():
    """获取服务记录"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = VolunteerServiceRecord.query.filter_by(volunteer_id=user.id).order_by(
        VolunteerServiceRecord.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    records = []
    for r in pagination.items:
        records.append({
            'id': r.id,
            'order_id': r.order_id,
            'duration_minutes': r.duration_minutes,
            'points_earned': r.points_earned,
            'check_in_time': r.check_in_time.isoformat() if r.check_in_time else None,
            'check_out_time': r.check_out_time.isoformat() if r.check_out_time else None,
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': records,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/volunteer/points', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_points_info():
    """获取积分信息"""
    user = request.current_user
    profile = VolunteerProfile.query.filter_by(user_id=user.id).first()

    return jsonify({
        'success': True,
        'data': {
            'total_points': profile.total_points if profile else 0,
            'total_service_hours': profile.total_service_hours if profile else 0
        }
    })

@api_v1.route('/volunteer/points/transactions', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_point_transactions():
    """获取积分明细"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = PointTransaction.query.filter_by(user_id=user.id).order_by(
        PointTransaction.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    transactions = []
    for tx in pagination.items:
        transactions.append({
            'id': tx.id,
            'amount': tx.amount,
            'transaction_type': tx.transaction_type,
            'balance_after': tx.balance_after,
            'created_at': tx.created_at.isoformat() if hasattr(tx, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': transactions,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/volunteer/points/products', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_exchangeable_products():
    """获取可兑换商品"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = PointProduct.query.filter_by(is_active=True).order_by(
        PointProduct.points_required.asc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    products = []
    for p in pagination.items:
        products.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'points_required': p.points_required,
            'stock': p.stock,
            'image_url': p.image_url
        })

    return jsonify({
        'success': True,
        'data': products,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/volunteer/points/exchange/<int:product_id>', methods=['POST'])
@jwt_required
@role_required('volunteer')
def exchange_product(product_id):
    """兑换商品"""
    user = request.current_user
    product = PointProduct.query.get_or_404(product_id)

    if not product.is_active:
        return jsonify({'success': False, 'message': '该商品已下架'}), 400

    if product.stock <= 0:
        return jsonify({'success': False, 'message': '库存不足'}), 400

    profile = VolunteerProfile.query.filter_by(user_id=user.id).first()
    if not profile or profile.total_points < product.points_required:
        return jsonify({'success': False, 'message': '积分不足'}), 400

    # 扣除积分
    profile.total_points -= product.points_required

    # 减少库存
    product.stock -= 1

    # 添加兑换记录
    exchange = PointExchange(
        user_id=user.id,
        product_id=product_id,
        points_used=product.points_required,
        status='pending'
    )
    db.session.add(exchange)

    # 添加积分流水
    point_tx = PointTransaction(
        user_id=user.id,
        amount=-product.points_required,
        transaction_type='exchange',
        balance_after=profile.total_points
    )
    db.session.add(point_tx)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '兑换成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'兑换失败: {str(e)}'}), 500

# ============== 老人护理信息查看接口 ==============

@api_v1.route('/volunteer/elderly/<int:elderly_id>/care-info', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_elderly_care_info(elderly_id):
    """获取老人护理注意事项（志愿者查看）"""
    user = request.current_user

    # 权限校验：志愿者只能查看自己有服务订单关联的老人
    has_order = ServiceOrder.query.filter_by(
        provider_id=user.id,
        provider_type='volunteer',
        elderly_id=elderly_id
    ).first()

    if not has_order:
        return jsonify({'success': False, 'message': '只能查看您服务过的老人信息'}), 403

    elderly = User.query.get_or_404(elderly_id)
    profile = ElderlyProfile.query.filter_by(user_id=elderly_id).first()

    # 获取老人最新的健康记录
    latest_health = HealthRecord.query.filter_by(
        elderly_id=elderly_id
    ).order_by(HealthRecord.record_date.desc()).first()

    # 获取该老人的用药提醒（志愿者可见）
    medications = MedicationReminder.query.filter_by(
        elderly_id=elderly_id,
        is_active=True
    ).all()

    return jsonify({
        'success': True,
        'data': {
            'elderly_id': elderly_id,
            'elderly_name': elderly.real_name,
            'elderly_phone': elderly.phone,
            'basic_info': {
                'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else None,
                'gender': profile.gender if profile else None,
                'health_status': profile.health_status if profile else None,
                'is_living_alone': profile.is_living_alone if profile else None,
            },
            'health_awareness': {
                'chronic_diseases': profile.chronic_diseases if profile else None,
                'allergies': profile.allergies if profile else None,
                'medical_history': profile.medical_history if profile else None,
                'emergency_contact': profile.emergency_contact if profile else None,
                'emergency_phone': profile.emergency_phone if profile else None,
            },
            'latest_health': {
                'record_date': latest_health.record_date.isoformat() if latest_health and latest_health.record_date else None,
                'systolic': latest_health.systolic if latest_health else None,
                'diastolic': latest_health.diastolic if latest_health else None,
                'blood_sugar': latest_health.blood_sugar if latest_health else None,
                'heart_rate': latest_health.heart_rate if latest_health else None,
            } if latest_health else None,
            'medications': [{
                'medication_name': m.medication_name,
                'dosage': m.dosage,
                'frequency': m.frequency,
                'reminder_times': m.reminder_times,
                'notes': m.notes
            } for m in medications]
        }
    })

@api_v1.route('/volunteer/elderly/<int:elderly_id>/health-records', methods=['GET'])
@jwt_required
@role_required('volunteer')
def get_volunteer_elderly_health_records(elderly_id):
    """获取老人健康记录（志愿者查看，仅限有服务关联）"""
    user = request.current_user

    # 权限校验
    has_order = ServiceOrder.query.filter_by(
        provider_id=user.id,
        provider_type='volunteer',
        elderly_id=elderly_id
    ).first()

    if not has_order:
        return jsonify({'success': False, 'message': '只能查看您服务过的老人健康记录'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = HealthRecord.query.filter_by(
        elderly_id=elderly_id
    ).order_by(HealthRecord.record_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    records = []
    for r in pagination.items:
        records.append({
            'id': r.id,
            'record_type': r.record_type,
            'record_date': r.record_date.isoformat() if r.record_date else None,
            'systolic': r.systolic,
            'diastolic': r.diastolic,
            'blood_sugar': r.blood_sugar,
            'heart_rate': r.heart_rate,
            'temperature': r.temperature,
            'exam_summary': r.exam_summary,
            'notes': r.notes
        })

    return jsonify({
        'success': True,
        'data': records,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })