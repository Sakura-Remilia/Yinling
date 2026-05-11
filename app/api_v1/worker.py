# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, WorkerProfile, ServiceOrder, ElderlyProfile, VisitRecord, FollowUpRecord, HealthRecord, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime

@api_v1.route('/worker/profile', methods=['GET'])
@jwt_required
@role_required('worker')
def get_worker_profile():
    """获取工作人员档案"""
    user = request.current_user
    profile = WorkerProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.id,
                'real_name': user.real_name,
                'work_type': '',
                'is_trained': False,
                'is_verified': False,
                'total_orders': 0,
                'rating': 0
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'user_id': user.id,
            'real_name': user.real_name,
            'work_type': profile.work_type,
            'is_trained': profile.is_trained,
            'is_verified': profile.is_verified,
            'total_orders': profile.total_orders,
            'rating': float(profile.rating) if profile.rating else 0
        }
    })

@api_v1.route('/worker/profile', methods=['PUT'])
@jwt_required
@role_required('worker')
def update_worker_profile():
    """更新工作人员档案"""
    user = request.current_user
    data = request.get_json()

    if 'work_type' in data:
        profile = WorkerProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = WorkerProfile(user_id=user.id)
            db.session.add(profile)
        profile.work_type = data['work_type']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '档案更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/worker/orders', methods=['GET'])
@jwt_required
@role_required('worker')
def get_worker_orders():
    """获取可接订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = ServiceOrder.query.filter(
        ServiceOrder.status == 'pending',
        ServiceOrder.provider_type == 'worker',
        ServiceOrder.provider_id.is_(None)
    )

    # 过滤当前社区
    if request.current_user.community_id:
        query = query.filter_by(community_id=request.current_user.community_id)

    pagination = query.order_by(ServiceOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    orders = []
    for order in pagination.items:
        orders.append({
            'id': order.id,
            'order_no': order.order_no,
            'service_name': order.category.name if hasattr(order, 'category') and order.category else '服务',
            'elderly_name': order.elderly.real_name if hasattr(order, 'elderly') and order.elderly else '匿名',
            'phone': order.elderly.phone if hasattr(order, 'elderly') and order.elderly else '',
            'address': order.address,
            'scheduled_time': order.scheduled_time.isoformat() if order.scheduled_time else None,
            'price': float(order.price) if order.price else 0,
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

@api_v1.route('/worker/orders/<int:order_id>/accept', methods=['POST'])
@jwt_required
@role_required('worker')
def accept_order(order_id):
    """接取订单"""
    user = request.current_user
    order = ServiceOrder.query.get_or_404(order_id)

    if order.status != 'pending':
        return jsonify({'success': False, 'message': '该订单已被接取'}), 400

    order.provider_id = user.id
    order.provider_type = 'worker'
    order.status = 'accepted'

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '接单成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'接单失败: {str(e)}'}), 500

@api_v1.route('/worker/my-orders', methods=['GET'])
@jwt_required
@role_required('worker')
def get_worker_my_orders():
    """获取我的订单列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)

    query = ServiceOrder.query.filter_by(provider_id=user.id, provider_type='worker')

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
            'service_name': order.category.name if hasattr(order, 'category') and order.category else '服务',
            'elderly_name': order.elderly.real_name if hasattr(order, 'elderly') and order.elderly else '匿名',
            'phone': order.elderly.phone if hasattr(order, 'elderly') and order.elderly else '',
            'address': order.address,
            'scheduled_time': order.scheduled_time.isoformat() if order.scheduled_time else None,
            'price': float(order.price) if order.price else 0,
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

@api_v1.route('/worker/orders/<int:order_id>/arrive', methods=['POST'])
@jwt_required
@role_required('worker')
def confirm_arrive(order_id):
    """确认到达"""
    user = request.current_user
    order = ServiceOrder.query.filter_by(id=order_id, provider_id=user.id).first_or_404()

    if order.status != 'accepted':
        return jsonify({'success': False, 'message': '当前状态不允许操作'}), 400

    order.status = 'in_progress'
    order.check_in_time = datetime.now()

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '已确认到达'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/worker/orders/<int:order_id>/complete', methods=['POST'])
@jwt_required
@role_required('worker')
def complete_order(order_id):
    """完成任务"""
    user = request.current_user
    order = ServiceOrder.query.filter_by(id=order_id, provider_id=user.id).first_or_404()
    data = request.get_json() or {}

    if order.status != 'in_progress':
        return jsonify({'success': False, 'message': '当前状态不允许完成'}), 400

    order.status = 'completed'
    order.check_out_time = datetime.now()
    if 'completion_notes' in data:
        order.completion_notes = data['completion_notes']

    # 更新工作人员统计
    profile = WorkerProfile.query.filter_by(user_id=user.id).first()
    if profile:
        profile.total_orders += 1

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '服务完成'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/worker/elderly', methods=['GET'])
@jwt_required
@role_required('worker', 'community_admin')
def get_worker_elderly_list():
    """获取老人列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = User.query.join(ElderlyProfile).filter(User.role.has(name='elderly'))

    # 权限控制：工作人员和社区管理员只能查看本社区老人
    if request.current_user.community_id:
        query = query.filter(User.community_id == request.current_user.community_id)

    if keyword:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{keyword}%'),
                User.real_name.ilike(f'%{keyword}%'),
                User.phone.ilike(f'%{keyword}%')
            )
        )

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    elderly_list = []
    for user in pagination.items:
        profile = ElderlyProfile.query.filter_by(user_id=user.id).first()
        elderly_list.append({
            'id': user.id,
            'real_name': user.real_name,
            'phone': user.phone,
            'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else None,
            'gender': profile.gender if profile else None,
            'health_status': profile.health_status if profile else None,
            'is_living_alone': profile.is_living_alone if profile else None
        })

    return jsonify({
        'success': True,
        'data': elderly_list,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/worker/elderly/<int:elderly_id>', methods=['GET'])
@jwt_required
@role_required('worker', 'community_admin')
def get_worker_elderly_detail(elderly_id):
    """获取老人详情"""
    user = User.query.get_or_404(elderly_id)
    profile = ElderlyProfile.query.filter_by(user_id=user.id).first()

    return jsonify({
        'success': True,
        'data': {
            'id': user.id,
            'real_name': user.real_name,
            'phone': user.phone,
            'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else None,
            'gender': profile.gender if profile else None,
            'emergency_contact': profile.emergency_contact if profile else None,
            'emergency_phone': profile.emergency_phone if profile else None,
            'health_status': profile.health_status if profile else None,
            'chronic_diseases': profile.chronic_diseases if profile else None,
            'is_living_alone': profile.is_living_alone if profile else None
        }
    })

@api_v1.route('/worker/visits', methods=['GET'])
@jwt_required
@role_required('worker')
def get_worker_visits():
    """获取走访记录列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = VisitRecord.query.filter_by(visitor_id=user.id).order_by(
        VisitRecord.scheduled_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    visits = []
    for v in pagination.items:
        visits.append({
            'id': v.id,
            'elderly_name': v.elderly.real_name if hasattr(v, 'elderly') and v.elderly else '匿名',
            'visit_type': v.visit_type,
            'scheduled_time': v.scheduled_time.isoformat() if v.scheduled_time else None,
            'actual_time': v.actual_time.isoformat() if v.actual_time else None,
            'status': v.status,
            'health_status': v.health_status,
            'needs': v.needs,
            'notes': v.notes,
            'created_at': v.created_at.isoformat() if hasattr(v, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': visits,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/worker/visits', methods=['POST'])
@jwt_required
@role_required('worker')
def create_visit():
    """创建走访任务"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    elderly_id = data.get('elderly_id')
    if not elderly_id:
        return jsonify({'success': False, 'message': '请选择老人'}), 400

    visit = VisitRecord(
        visitor_id=user.id,
        elderly_id=elderly_id,
        visit_type=data.get('visit_type', 'regular'),
        scheduled_time=datetime.strptime(data['scheduled_time'], '%Y-%m-%d %H:%M') if data.get('scheduled_time') else datetime.now(),
        health_status=data.get('health_status', ''),
        needs=data.get('needs', ''),
        notes=data.get('notes', ''),
        status='pending'
    )

    try:
        db.session.add(visit)
        db.session.commit()
        return jsonify({'success': True, 'message': '走访任务创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/worker/visits/<int:visit_id>/complete', methods=['POST'])
@jwt_required
@role_required('worker')
def complete_visit(visit_id):
    """完成走访（可同步创建健康记录）"""
    user = request.current_user
    visit = VisitRecord.query.filter_by(id=visit_id, visitor_id=user.id).first_or_404()
    data = request.get_json() or {}

    if 'health_status' in data:
        visit.health_status = data['health_status']
    if 'needs' in data:
        visit.needs = data['needs']
    if 'notes' in data:
        visit.notes = data['notes']

    # 更新走访状态为已完成
    visit.status = 'completed'
    visit.actual_time = datetime.now()

    # 如果提交了健康数据，同时创建健康记录
    health_record_id = None
    if data.get('create_health_record'):
        health_data = data.get('health_data', {})
        health_record = HealthRecord(
            elderly_id=visit.elderly_id,
            creator_id=user.id,
            record_type='visit_check',
            systolic=health_data.get('systolic'),
            diastolic=health_data.get('diastolic'),
            blood_sugar=health_data.get('blood_sugar'),
            heart_rate=health_data.get('heart_rate'),
            temperature=health_data.get('temperature'),
            record_date=datetime.now().date(),
            exam_summary=health_data.get('exam_summary', ''),
            notes=health_data.get('notes', '')
        )
        db.session.add(health_record)
        db.session.flush()  # 获取 health_record.id
        health_record_id = health_record.id

        # 检查是否需要创建预警
        _check_and_create_health_alert(visit.elderly_id, health_record)

    try:
        db.session.commit()
        result = {'success': True, 'message': '走访记录已提交'}
        if health_record_id:
            result['data'] = {'health_record_id': health_record_id}
        return jsonify(result)
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'提交失败: {str(e)}'}), 500


def _check_and_create_health_alert(elderly_id, health_record):
    """检查健康数据是否异常，创建预警通知（如果需要）"""
    from app.models import AlertRule, AlertNotification, User

    # 获取该老人的紧急联系人信息
    elderly = User.query.get(elderly_id)
    if not elderly:
        return

    abnormal_conditions = []

    # 检查血压
    if health_record.systolic and health_record.diastolic:
        if health_record.systolic > 180 or health_record.diastolic > 110:
            abnormal_conditions.append('高血压危象')
        elif health_record.systolic > 140 or health_record.diastolic > 90:
            abnormal_conditions.append('血压偏高')
        elif health_record.systolic < 90 or health_record.diastolic < 60:
            abnormal_conditions.append('血压偏低')

    # 检查血糖
    if health_record.blood_sugar:
        if health_record.blood_sugar > 13.9:
            abnormal_conditions.append('血糖严重偏高')
        elif health_record.blood_sugar > 7.0:
            abnormal_conditions.append('血糖偏高')
        elif health_record.blood_sugar < 3.9:
            abnormal_conditions.append('血糖偏低')

    # 如果有异常，创建预警通知
    if abnormal_conditions:
        alert = AlertNotification(
            rule_id=None,  # 系统自动创建，非规则触发
            user_id=elderly_id,
            title=f'健康数据异常预警',
            content=f'走访检查发现异常：{"、".join(abnormal_conditions)}。请及时关注老人健康状况。',
            is_read=False
        )
        db.session.add(alert)

@api_v1.route('/worker/follow-ups', methods=['GET'])
@jwt_required
@role_required('worker')
def get_worker_follow_ups():
    """获取回访记录列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = FollowUpRecord.query.filter_by(follower_id=user.id).order_by(
        FollowUpRecord.follow_up_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    follow_ups = []
    for f in pagination.items:
        follow_ups.append({
            'id': f.id,
            'order_id': f.order_id,
            'elderly_name': f.order.elderly.real_name if hasattr(f, 'order') and f.order and hasattr(f.order, 'elderly') and f.order.elderly else '匿名',
            'follow_up_time': f.follow_up_time.isoformat() if f.follow_up_time else None,
            'satisfaction_level': f.satisfaction_level,
            'feedback': f.feedback,
            'created_at': f.created_at.isoformat() if hasattr(f, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': follow_ups,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/worker/follow-ups', methods=['POST'])
@jwt_required
@role_required('worker')
def create_follow_up():
    """创建回访记录"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    follow_up = FollowUpRecord(
        follower_id=user.id,
        order_id=data.get('order_id'),
        follow_up_time=datetime.strptime(data['follow_up_time'], '%Y-%m-%d %H:%M:%S') if data.get('follow_up_time') else datetime.now(),
        satisfaction_level=data.get('satisfaction_level', 5),
        feedback=data.get('feedback', '')
    )

    try:
        db.session.add(follow_up)
        db.session.commit()
        return jsonify({'success': True, 'message': '回访记录创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

# ============== 老人健康档案管理接口 ==============

@api_v1.route('/worker/elderly/<int:elderly_id>/health-records', methods=['POST'])
@jwt_required
@role_required('worker')
def create_elderly_health_record(elderly_id):
    """为老人录入体检/健康数据"""
    user = request.current_user

    # 权限校验：只能为本社区老人录入
    elderly = User.query.get_or_404(elderly_id)
    if user.community_id != elderly.community_id:
        return jsonify({'success': False, 'message': '无权为该老人录入数据'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    record_type = data.get('record_type', 'physical_exam')

    record = HealthRecord(
        elderly_id=elderly_id,
        creator_id=user.id,
        record_type=record_type,
        systolic=data.get('systolic'),
        diastolic=data.get('diastolic'),
        blood_sugar=data.get('blood_sugar'),
        heart_rate=data.get('heart_rate'),
        temperature=data.get('temperature'),
        height=data.get('height'),
        weight=data.get('weight'),
        vision_left=data.get('vision_left'),
        vision_right=data.get('vision_right'),
        hearing=data.get('hearing'),
        blood_type=data.get('blood_type'),
        record_date=datetime.strptime(data['record_date'], '%Y-%m-%d').date() if data.get('record_date') else datetime.now().date(),
        exam_summary=data.get('exam_summary'),
        notes=data.get('notes')
    )

    try:
        db.session.add(record)
        db.session.flush()

        # 检查健康数据是否异常，创建预警（如需要）
        _check_and_create_health_alert(elderly_id, record)

        db.session.commit()
        return jsonify({'success': True, 'message': '健康记录录入成功', 'data': {'id': record.id}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'录入失败: {str(e)}'}), 500

@api_v1.route('/worker/elderly/<int:elderly_id>/health-records', methods=['GET'])
@jwt_required
@role_required('worker', 'community_admin')
def get_elderly_health_records(elderly_id):
    """获取老人健康记录列表"""
    user = request.current_user

    # 权限校验
    elderly = User.query.get_or_404(elderly_id)
    if user.role.name == 'worker' and user.community_id != elderly.community_id:
        return jsonify({'success': False, 'message': '无权查看该老人健康记录'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    record_type = request.args.get('type', None)

    query = HealthRecord.query.filter_by(elderly_id=elderly_id)
    if record_type:
        query = query.filter_by(record_type=record_type)

    pagination = query.order_by(HealthRecord.record_date.desc()).paginate(
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
            'height': r.height,
            'weight': r.weight,
            'vision_left': r.vision_left,
            'vision_right': r.vision_right,
            'hearing': r.hearing,
            'blood_type': r.blood_type,
            'exam_summary': r.exam_summary,
            'creator_name': r.creator.real_name if r.creator else None,
            'notes': r.notes,
            'created_at': r.created_at.isoformat() if r.created_at else None
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

@api_v1.route('/worker/elderly/<int:elderly_id>/health-stats', methods=['GET'])
@jwt_required
@role_required('worker', 'community_admin')
def get_elderly_health_stats(elderly_id):
    """获取老人健康数据统计"""
    user = request.current_user

    # 权限校验
    elderly = User.query.get_or_404(elderly_id)
    if user.role.name == 'worker' and user.community_id != elderly.community_id:
        return jsonify({'success': False, 'message': '无权查看该老人健康数据'}), 403

    # 获取最新一条记录
    latest_record = HealthRecord.query.filter_by(
        elderly_id=elderly_id
    ).order_by(HealthRecord.record_date.desc()).first()

    # 获取最近30天的记录统计
    from datetime import timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)

    recent_records = HealthRecord.query.filter(
        HealthRecord.elderly_id == elderly_id,
        HealthRecord.record_date >= thirty_days_ago.date()
    ).order_by(HealthRecord.record_date.asc()).all()

    # 统计血压情况
    bp_records = [r for r in recent_records if r.systolic and r.diastolic]
    bp_normal = sum(1 for r in bp_records if 90 <= r.systolic <= 140 and 60 <= r.diastolic <= 90)
    bp_abnormal = len(bp_records) - bp_normal

    # 统计血糖情况
    bs_records = [r for r in recent_records if r.blood_sugar]
    bs_normal = sum(1 for r in bs_records if 3.9 <= r.blood_sugar <= 6.1)
    bs_abnormal = len(bs_records) - bs_normal

    # 血压趋势
    bp_trend = []
    for r in bp_records[-7:]:  # 最近7次
        bp_trend.append({
            'date': r.record_date.isoformat() if r.record_date else None,
            'systolic': r.systolic,
            'diastolic': r.diastolic
        })

    # 血糖趋势
    bs_trend = []
    for r in bs_records[-7:]:  # 最近7次
        bs_trend.append({
            'date': r.record_date.isoformat() if r.record_date else None,
            'blood_sugar': r.blood_sugar
        })

    profile = ElderlyProfile.query.filter_by(user_id=elderly_id).first()

    return jsonify({
        'success': True,
        'data': {
            'elderly_id': elderly_id,
            'elderly_name': elderly.real_name,
            'latest_record': {
                'record_date': latest_record.record_date.isoformat() if latest_record and latest_record.record_date else None,
                'systolic': latest_record.systolic if latest_record else None,
                'diastolic': latest_record.diastolic if latest_record else None,
                'blood_sugar': latest_record.blood_sugar if latest_record else None,
                'heart_rate': latest_record.heart_rate if latest_record else None,
                'temperature': latest_record.temperature if latest_record else None,
                'height': latest_record.height if latest_record else None,
                'weight': latest_record.weight if latest_record else None,
                'blood_type': latest_record.blood_type if latest_record else None,
            } if latest_record else None,
            'profile': {
                'health_status': profile.health_status if profile else None,
                'chronic_diseases': profile.chronic_diseases if profile else None,
                'allergies': profile.allergies if profile else None,
                'medical_history': profile.medical_history if profile else None,
            } if profile else None,
            'stats_30days': {
                'total_records': len(recent_records),
                'bp_normal_count': bp_normal,
                'bp_abnormal_count': bp_abnormal,
                'bs_normal_count': bs_normal,
                'bs_abnormal_count': bs_abnormal,
            },
            'bp_trend': bp_trend,
            'bs_trend': bs_trend
        }
    })

@api_v1.route('/worker/elderly/<int:elderly_id>/health-records/<int:record_id>', methods=['PUT'])
@jwt_required
@role_required('worker')
def update_health_record(elderly_id, record_id):
    """更新老人健康记录"""
    user = request.current_user

    # 权限校验
    elderly = User.query.get_or_404(elderly_id)
    if user.community_id != elderly.community_id:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    record = HealthRecord.query.filter_by(id=record_id, elderly_id=elderly_id).first_or_404()

    # 只有记录创建者可以修改
    if record.creator_id != user.id:
        return jsonify({'success': False, 'message': '只能修改自己录入的记录'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    # 更新字段
    if 'systolic' in data:
        record.systolic = data['systolic']
    if 'diastolic' in data:
        record.diastolic = data['diastolic']
    if 'blood_sugar' in data:
        record.blood_sugar = data['blood_sugar']
    if 'heart_rate' in data:
        record.heart_rate = data['heart_rate']
    if 'temperature' in data:
        record.temperature = data['temperature']
    if 'height' in data:
        record.height = data['height']
    if 'weight' in data:
        record.weight = data['weight']
    if 'vision_left' in data:
        record.vision_left = data['vision_left']
    if 'vision_right' in data:
        record.vision_right = data['vision_right']
    if 'hearing' in data:
        record.hearing = data['hearing']
    if 'blood_type' in data:
        record.blood_type = data['blood_type']
    if 'exam_summary' in data:
        record.exam_summary = data['exam_summary']
    if 'notes' in data:
        record.notes = data['notes']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '记录更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/worker/elderly/<int:elderly_id>/health-records/<int:record_id>', methods=['DELETE'])
@jwt_required
@role_required('worker')
def delete_health_record(elderly_id, record_id):
    """删除老人健康记录"""
    user = request.current_user

    # 权限校验
    elderly = User.query.get_or_404(elderly_id)
    if user.community_id != elderly.community_id:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    record = HealthRecord.query.filter_by(id=record_id, elderly_id=elderly_id).first_or_404()

    # 只有记录创建者可以删除
    if record.creator_id != user.id:
        return jsonify({'success': False, 'message': '只能删除自己录入的记录'}), 403

    try:
        db.session.delete(record)
        db.session.commit()
        return jsonify({'success': True, 'message': '记录删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500