# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, ElderlyProfile, VolunteerProfile, WorkerProfile, CommunityAdminProfile, ServiceOrder, SOSAlert, Activity, Community, Role, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime, timedelta

@api_v1.route('/community-admin/dashboard', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_dashboard_stats():
    """获取仪表盘统计"""
    user = request.current_user

    # 统计老人数量
    elderly_count = User.query.join(User.role).filter(
        User.community_id == user.community_id,
        Role.name == 'elderly'
    ).count()

    # 独居老人数量
    living_alone_count = ElderlyProfile.query.join(User).filter(
        User.community_id == user.community_id,
        ElderlyProfile.is_living_alone == True
    ).count()

    # SOS待处理数量（通过老人关联社区）
    pending_sos = SOSAlert.query.join(
        User, SOSAlert.elderly_id == User.id
    ).filter(
        User.community_id == user.community_id,
        SOSAlert.status.in_(['pending', 'responding'])
    ).count()

    # 今日新订单
    today_orders = ServiceOrder.query.filter(
        ServiceOrder.community_id == user.community_id,
        ServiceOrder.created_at >= datetime.now().replace(hour=0, minute=0, second=0)
    ).count()

    # 进行中订单
    in_progress_orders = ServiceOrder.query.filter_by(
        community_id=user.community_id,
        status='in_progress'
    ).count()

    return jsonify({
        'success': True,
        'data': {
            'elderly_count': elderly_count,
            'living_alone_count': living_alone_count,
            'pending_sos': pending_sos,
            'today_orders': today_orders,
            'in_progress_orders': in_progress_orders
        }
    })

@api_v1.route('/community-admin/elderly', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_elderly_list():
    """获取老人列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = User.query.filter_by(community_id=user.community_id).join(User.role).filter_by(name='elderly')

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
    for u in pagination.items:
        profile = ElderlyProfile.query.filter_by(user_id=u.id).first()
        elderly_list.append({
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name,
            'phone': u.phone,
            'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else None,
            'gender': profile.gender if profile else None,
            'health_status': profile.health_status if profile else None,
            'is_living_alone': profile.is_living_alone if profile else None,
            'is_active': u.is_active if hasattr(u, 'is_active') else True
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

@api_v1.route('/community-admin/volunteers', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_volunteers():
    """获取志愿者列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = User.query.filter_by(community_id=request.current_user.community_id).join(User.role).filter_by(name='volunteer')

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

    volunteers = []
    for u in pagination.items:
        profile = VolunteerProfile.query.filter_by(user_id=u.id).first()
        volunteers.append({
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name,
            'phone': u.phone,
            'skills': profile.skills if profile else '',
            'total_service_hours': profile.total_service_hours if profile else 0,
            'total_points': profile.total_points if profile else 0,
            'is_verified': profile.is_verified if profile else False,
            'is_active': u.is_active if hasattr(u, 'is_active') else True
        })

    return jsonify({
        'success': True,
        'data': volunteers,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/community-admin/volunteers/<int:volunteer_id>/verify', methods=['POST'])
@jwt_required
@role_required('community_admin')
def verify_volunteer(volunteer_id):
    """审核志愿者"""
    volunteer = User.query.filter_by(id=volunteer_id, community_id=request.current_user.community_id).first_or_404()
    profile = VolunteerProfile.query.filter_by(user_id=volunteer.id).first()

    if profile:
        profile.is_verified = True

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '审核通过'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/community-admin/workers', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_workers():
    """获取工作人员列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = User.query.filter_by(community_id=request.current_user.community_id).join(User.role).filter_by(name='worker')

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

    workers = []
    for u in pagination.items:
        profile = WorkerProfile.query.filter_by(user_id=u.id).first()
        workers.append({
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name,
            'phone': u.phone,
            'work_type': profile.work_type if profile else '',
            'is_trained': profile.is_trained if profile else False,
            'is_verified': profile.is_verified if profile else False,
            'total_orders': profile.total_orders if profile else 0,
            'rating': float(profile.rating) if profile and profile.rating else 0,
            'is_active': u.is_active if hasattr(u, 'is_active') else True
        })

    return jsonify({
        'success': True,
        'data': workers,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/community-admin/workers/<int:worker_id>/verify', methods=['POST'])
@jwt_required
@role_required('community_admin')
def verify_worker(worker_id):
    """审核工作人员"""
    worker = User.query.filter_by(id=worker_id, community_id=request.current_user.community_id).first_or_404()
    profile = WorkerProfile.query.filter_by(user_id=worker.id).first()

    if profile:
        profile.is_verified = True

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '审核通过'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/community-admin/workers/<int:worker_id>/train', methods=['POST'])
@jwt_required
@role_required('community_admin')
def mark_worker_trained(worker_id):
    """标记培训完成"""
    worker = User.query.filter_by(id=worker_id, community_id=request.current_user.community_id).first_or_404()
    profile = WorkerProfile.query.filter_by(user_id=worker.id).first()

    if profile:
        profile.is_trained = True

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '已标记培训完成'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@api_v1.route('/community-admin/orders', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_orders():
    """获取订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)

    query = ServiceOrder.query.filter_by(community_id=request.current_user.community_id)

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
            'provider_name': order.provider.real_name if hasattr(order, 'provider') and order.provider else None,
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

@api_v1.route('/community-admin/sos', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_sos_list():
    """获取SOS警报列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)

    query = SOSAlert.query.join(
        User, SOSAlert.elderly_id == User.id
    ).filter(User.community_id == request.current_user.community_id)

    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(SOSAlert.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    alerts = []
    for alert in pagination.items:
        alerts.append({
            'id': alert.id,
            'alert_no': alert.alert_no,
            'elderly_name': alert.elderly.real_name if hasattr(alert, 'elderly') and alert.elderly else '匿名',
            'elderly_phone': alert.elderly.phone if hasattr(alert, 'elderly') and alert.elderly else '',
            'location': alert.location,
            'status': alert.status,
            'responder_name': alert.responder.real_name if hasattr(alert, 'responder') and alert.responder else None,
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

@api_v1.route('/community-admin/activities', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_activities():
    """获取活动列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Activity.query.filter_by(community_id=request.current_user.community_id).order_by(
        Activity.start_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    activities = []
    for a in pagination.items:
        activities.append({
            'id': a.id,
            'title': a.title,
            'start_time': a.start_time.isoformat() if a.start_time else None,
            'end_time': a.end_time.isoformat() if a.end_time else None,
            'location': a.location,
            'max_participants': a.max_participants,
            'current_participants': a.current_participants if a.current_participants else 0,
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None
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

@api_v1.route('/community-admin/activities', methods=['POST'])
@jwt_required
@role_required('community_admin')
def create_activity():
    """创建活动"""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    activity = Activity(
        community_id=request.current_user.community_id,
        title=data.get('title', ''),
        description=data.get('description', ''),
        start_time=datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M') if data.get('start_time') else None,
        end_time=datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M') if data.get('end_time') else None,
        location=data.get('location', ''),
        max_participants=data.get('max_participants', 0),
        status='published'
    )

    try:
        db.session.add(activity)
        db.session.commit()
        return jsonify({'success': True, 'message': '活动创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/community-admin/activities/<int:activity_id>', methods=['PUT'])
@jwt_required
@role_required('community_admin')
def update_activity(activity_id):
    """更新活动"""
    activity = Activity.query.filter_by(id=activity_id, community_id=request.current_user.community_id).first_or_404()
    data = request.get_json()

    if 'title' in data:
        activity.title = data['title']
    if 'description' in data:
        activity.description = data['description']
    if 'start_time' in data:
        activity.start_time = datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M')
    if 'end_time' in data:
        activity.end_time = datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M')
    if 'location' in data:
        activity.location = data['location']
    if 'max_participants' in data:
        activity.max_participants = data['max_participants']
    if 'status' in data:
        activity.status = data['status']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '活动更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/community-admin/accounts', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_accounts():
    """获取账号列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role', None)
    keyword = request.args.get('keyword', '')

    query = User.query.filter_by(community_id=request.current_user.community_id)
    # 排除系统管理员账户
    query = query.join(Role).filter(Role.name != 'super_admin')

    if role:
        query = query.join(User.role).filter_by(name=role)

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

    accounts = []
    for u in pagination.items:
        accounts.append({
            'id': u.id,
            'username': u.username,
            'real_name': u.real_name,
            'phone': u.phone,
            'role': u.role.name if hasattr(u, 'role') else None,
            'is_active': u.is_active if hasattr(u, 'is_active') else True,
            'created_at': u.created_at.isoformat() if hasattr(u, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': accounts,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/community-admin/alerts', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_alerts():
    """获取预警通知列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    from app.models import AlertNotification
    pagination = AlertNotification.query.filter_by(user_id=request.current_user.id).order_by(
        AlertNotification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    alerts = []
    for a in pagination.items:
        alerts.append({
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'is_read': a.is_read,
            'created_at': a.created_at.isoformat() if hasattr(a, 'created_at') else None
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

# ============== 社区老人健康统计接口 ==============

@api_v1.route('/community-admin/elderly/health-stats', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_community_health_stats():
    """获取本社区老人健康统计"""
    from app.models import HealthRecord

    # 获取本社区所有老人
    elderly_users = User.query.filter_by(
        community_id=request.current_user.community_id
    ).join(User.role).filter_by(name='elderly').all()

    total_elderly = len(elderly_users)

    # 统计有健康问题的老人
    with_chronic = 0
    with_hypertension = 0
    with_diabetes = 0
    recent_check_count = 0

    thirty_days_ago = datetime.now() - timedelta(days=30)

    for elderly in elderly_users:
        profile = ElderlyProfile.query.filter_by(user_id=elderly.id).first()

        # 慢性病统计
        if profile and profile.chronic_diseases:
            with_chronic += 1
            if '高血压' in profile.chronic_diseases or '血压' in profile.chronic_diseases:
                with_hypertension += 1
            if '糖尿病' in profile.chronic_diseases or '血糖' in profile.chronic_diseases:
                with_diabetes += 1

        # 30天内有健康检查记录的老人数
        recent_check = HealthRecord.query.filter(
            HealthRecord.elderly_id == elderly.id,
            HealthRecord.record_date >= thirty_days_ago.date()
        ).first()
        if recent_check:
            recent_check_count += 1

    return jsonify({
        'success': True,
        'data': {
            'total_elderly': total_elderly,
            'with_chronic_count': with_chronic,
            'with_hypertension_count': with_hypertension,
            'with_diabetes_count': with_diabetes,
            'recent_check_count': recent_check_count,
            'recent_check_rate': round(recent_check_count / total_elderly * 100, 1) if total_elderly > 0 else 0
        }
    })

@api_v1.route('/community-admin/elderly/<int:elderly_id>/health-stats', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_elderly_health_stats(elderly_id):
    """获取指定老人健康统计（社区管理员查看）"""
    from app.models import HealthRecord

    # 权限校验
    elderly = User.query.filter_by(
        id=elderly_id,
        community_id=request.current_user.community_id
    ).first_or_404()

    # 获取最新一条记录
    latest_record = HealthRecord.query.filter_by(
        elderly_id=elderly_id
    ).order_by(HealthRecord.record_date.desc()).first()

    # 获取最近30天的记录
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_records = HealthRecord.query.filter(
        HealthRecord.elderly_id == elderly_id,
        HealthRecord.record_date >= thirty_days_ago.date()
    ).order_by(HealthRecord.record_date.asc()).all()

    # 统计血压情况
    bp_records = [r for r in recent_records if r.systolic and r.diastolic]
    bp_abnormal = sum(1 for r in bp_records if r.systolic > 140 or r.diastolic > 90 or r.systolic < 90 or r.diastolic < 60)

    # 统计血糖情况
    bs_records = [r for r in recent_records if r.blood_sugar]
    bs_abnormal = sum(1 for r in bs_records if r.blood_sugar > 7.0 or r.blood_sugar < 3.9)

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
            } if latest_record else None,
            'profile': {
                'health_status': profile.health_status if profile else None,
                'chronic_diseases': profile.chronic_diseases if profile else None,
                'allergies': profile.allergies if profile else None,
            } if profile else None,
            'stats_30days': {
                'total_records': len(recent_records),
                'bp_abnormal_count': bp_abnormal,
                'bs_abnormal_count': bs_abnormal,
            }
        }
    })

# ============= 社区公告管理 =============

@api_v1.route('/community-admin/announcements', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_announcements():
    """获取公告列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = CommunityAnnouncement.query.filter_by(community_id=user.community_id)

    pagination = query.order_by(
        CommunityAnnouncement.is_pinned.desc(),
        CommunityAnnouncement.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    announcements = []
    for a in pagination.items:
        announcements.append({
            'id': a.id,
            'title': a.title,
            'content': a.content[:100] + '...' if a.content and len(a.content) > 100 else a.content,
            'cover_image': a.cover_image,
            'is_pinned': a.is_pinned,
            'is_active': a.is_active,
            'published_at': a.published_at.isoformat() if a.published_at else None,
            'created_at': a.created_at.isoformat() if hasattr(a, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': announcements,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/community-admin/announcements', methods=['POST'])
@jwt_required
@role_required('community_admin')
def create_ca_announcement():
    """创建公告"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': '标题不能为空'}), 400

    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'message': '内容不能为空'}), 400

    announcement = CommunityAnnouncement(
        title=title,
        content=content,
        cover_image=data.get('cover_image', ''),
        community_id=user.community_id,
        publisher_id=user.id,
        is_pinned=data.get('is_pinned', False),
        is_active=data.get('is_active', True),
        published_at=datetime.now()
    )

    try:
        db.session.add(announcement)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '公告创建成功',
            'data': {'id': announcement.id}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/community-admin/announcements/<int:announcement_id>', methods=['GET'])
@jwt_required
@role_required('community_admin')
def get_ca_announcement_detail(announcement_id):
    """获取公告详情"""
    user = request.current_user
    announcement = CommunityAnnouncement.query.filter_by(
        id=announcement_id,
        community_id=user.community_id
    ).first_or_404()

    return jsonify({
        'success': True,
        'data': {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'cover_image': announcement.cover_image,
            'is_pinned': announcement.is_pinned,
            'is_active': announcement.is_active,
            'published_at': announcement.published_at.isoformat() if announcement.published_at else None,
            'created_at': announcement.created_at.isoformat() if hasattr(announcement, 'created_at') else None
        }
    })

@api_v1.route('/community-admin/announcements/<int:announcement_id>', methods=['PUT'])
@jwt_required
@role_required('community_admin')
def update_ca_announcement(announcement_id):
    """更新公告"""
    user = request.current_user
    announcement = CommunityAnnouncement.query.filter_by(
        id=announcement_id,
        community_id=user.community_id
    ).first_or_404()

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'cover_image' in data:
        announcement.cover_image = data['cover_image']
    if 'is_pinned' in data:
        announcement.is_pinned = data['is_pinned']
    if 'is_active' in data:
        announcement.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '公告更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/community-admin/announcements/<int:announcement_id>', methods=['DELETE'])
@jwt_required
@role_required('community_admin')
def delete_ca_announcement(announcement_id):
    """删除公告"""
    user = request.current_user
    announcement = CommunityAnnouncement.query.filter_by(
        id=announcement_id,
        community_id=user.community_id
    ).first_or_404()

    try:
        db.session.delete(announcement)
        db.session.commit()
        return jsonify({'success': True, 'message': '公告删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500