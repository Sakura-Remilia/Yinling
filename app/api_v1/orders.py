# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import ServiceOrder, ServiceCategory, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime
import random
import string

@api_v1.route('/orders', methods=['GET'])
@jwt_required
def get_orders():
    """获取订单列表 (根据角色过滤)"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', None)

    role_name = user.role.name if hasattr(user, 'role') else None

    if role_name == 'elderly':
        query = ServiceOrder.query.filter_by(elderly_id=user.id)
    elif role_name == 'volunteer' and user.role.name == 'volunteer':
        query = ServiceOrder.query.filter_by(provider_id=user.id, provider_type='volunteer')
    elif role_name == 'worker':
        query = ServiceOrder.query.filter_by(provider_id=user.id, provider_type='worker')
    elif role_name in ['community_admin', 'super_admin']:
        query = ServiceOrder.query
        if role_name == 'community_admin' and user.community_id:
            query = query.filter_by(community_id=user.community_id)
    else:
        query = ServiceOrder.query

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
            'phone': order.elderly.phone if hasattr(order, 'elderly') and order.elderly else '',
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

@api_v1.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required
def get_order_detail(order_id):
    """获取订单详情"""
    order = ServiceOrder.query.get_or_404(order_id)

    return jsonify({
        'success': True,
        'data': {
            'id': order.id,
            'order_no': order.order_no,
            'service_name': order.category.name if hasattr(order, 'category') and order.category else '服务',
            'elderly_name': order.elderly.real_name if hasattr(order, 'elderly') and order.elderly else '匿名',
            'elderly_phone': order.elderly.phone if hasattr(order, 'elderly') and order.elderly else '',
            'elderly_address': order.elderly.elderly_profile.address if hasattr(order.elderly, 'elderly_profile') and order.elderly.elderly_profile else order.address,
            'provider_name': order.provider.real_name if hasattr(order, 'provider') and order.provider else None,
            'provider_phone': order.provider.phone if hasattr(order, 'provider') and order.provider else None,
            'address': order.address,
            'scheduled_time': order.scheduled_time.isoformat() if order.scheduled_time else None,
            'price': float(order.price) if order.price else 0,
            'status': order.status,
            'notes': order.description,
            'completion_notes': order.completion_notes if order.completion_notes else None,
            'check_in_time': order.check_in_time.isoformat() if order.check_in_time else None,
            'check_out_time': order.check_out_time.isoformat() if order.check_out_time else None,
            'created_at': order.created_at.isoformat() if order.created_at else None
        }
    })

@api_v1.route('/orders', methods=['POST'])
@jwt_required
@role_required('elderly')
def create_order():
    """创建订单"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    category_id = data.get('category_id')
    if not category_id:
        return jsonify({'success': False, 'message': '请选择服务类别'}), 400

    # 生成订单号
    order_no = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(1000, 9999)}'

    order = ServiceOrder(
        order_no=order_no,
        elderly_id=user.id,
        category_id=category_id,
        community_id=user.community_id,
        address=data.get('address', ''),
        scheduled_time=datetime.strptime(data['scheduled_time'], '%Y-%m-%d %H:%M') if data.get('scheduled_time') else None,
        description=data.get('notes', ''),
        status='pending'
    )

    # 获取价格
    category = ServiceCategory.query.get(category_id)
    if category and not category.is_free:
        order.price = category.price_range.split('-')[0] if category.price_range else 0

    try:
        db.session.add(order)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {'id': order.id, 'order_no': order.order_no}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/orders/<int:order_id>/status', methods=['PUT'])
@jwt_required
def update_order_status(order_id):
    """更新订单状态"""
    order = ServiceOrder.query.get_or_404(order_id)
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({'success': False, 'message': '缺少status参数'}), 400

    new_status = data['status']
    user = request.current_user
    role_name = user.role.name if hasattr(user, 'role') else None

    # 权限检查
    if role_name == 'elderly' and order.elderly_id != user.id:
        return jsonify({'success': False, 'message': '无权修改该订单'}), 403

    if role_name in ['volunteer', 'worker'] and order.provider_id != user.id:
        return jsonify({'success': False, 'message': '无权修改该订单'}), 403

    valid_transitions = {
        'pending': ['accepted', 'cancelled'],
        'accepted': ['in_progress', 'cancelled'],
        'in_progress': ['completed', 'cancelled'],
        'completed': [],
        'cancelled': []
    }

    if new_status not in valid_transitions.get(order.status, []):
        return jsonify({'success': False, 'message': f'不允许的状态转换'}), 400

    order.status = new_status

    if new_status == 'in_progress':
        order.check_in_time = datetime.now()
    elif new_status == 'completed':
        order.check_out_time = datetime.now()
        if 'completion_notes' in data:
            order.completion_notes = data['completion_notes']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/orders/<int:order_id>/review', methods=['POST'])
@jwt_required
@role_required('elderly')
def review_order(order_id):
    """评价订单"""
    order = ServiceOrder.query.filter_by(id=order_id, elderly_id=request.current_user.id).first_or_404()
    data = request.get_json()

    if order.status != 'completed':
        return jsonify({'success': False, 'message': '只能评价已完成的订单'}), 400

    if hasattr(order, 'rating'):
        order.rating = data.get('rating', 5)
    if hasattr(order, 'review'):
        order.review = data.get('review', '')

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '评价成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'评价失败: {str(e)}'}), 500

@api_v1.route('/orders/categories', methods=['GET'])
def get_order_categories():
    """获取服务分类列表"""
    categories = ServiceCategory.query.filter(
        getattr(ServiceCategory, 'is_active', True) if hasattr(ServiceCategory, 'is_active') else True
    ).order_by(ServiceCategory.sort_order.asc()).all()

    data = []
    for c in categories:
        data.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'price_range': c.price_range,
            'is_free': c.is_free
        })

    return jsonify({'success': True, 'data': data})