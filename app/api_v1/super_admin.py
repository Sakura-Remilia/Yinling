# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, Role, Community, ServiceCategory, News, PointProduct, AlertRule, SystemLog, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime

@api_v1.route('/super-admin/dashboard', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_super_admin_dashboard():
    """获取系统概览统计"""
    # 用户统计
    total_users = User.query.count()
    elderly_count = User.query.join(User.role).filter_by(name='elderly').count()
    volunteer_count = User.query.join(User.role).filter_by(name='volunteer').count()
    worker_count = User.query.join(User.role).filter_by(name='worker').count()

    # 社区统计
    total_communities = Community.query.count()

    # 活跃用户 (最近7天登录)
    from datetime import timedelta
    recent_date = datetime.now() - timedelta(days=7)
    active_users = User.query.filter(User.last_login >= recent_date).count() if hasattr(User, 'last_login') else 0

    return jsonify({
        'success': True,
        'data': {
            'total_users': total_users,
            'elderly_count': elderly_count,
            'volunteer_count': volunteer_count,
            'worker_count': worker_count,
            'total_communities': total_communities,
            'active_users': active_users
        }
    })

@api_v1.route('/super-admin/communities', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_communities():
    """获取社区列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    keyword = request.args.get('keyword', '')

    query = Community.query

    if keyword:
        query = query.filter(Community.name.ilike(f'%{keyword}%'))

    pagination = query.order_by(Community.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    communities = []
    for c in pagination.items:
        communities.append({
            'id': c.id,
            'name': c.name,
            'address': c.address,
            'parent_id': c.parent_id,
            'level': c.level,
            'user_count': User.query.filter_by(community_id=c.id).count(),
            'created_at': c.created_at.isoformat() if hasattr(c, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': communities,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/super-admin/communities', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_community():
    """创建社区"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': '社区名称不能为空'}), 400

    community = Community(
        name=data['name'],
        address=data.get('address', ''),
        parent_id=data.get('parent_id'),
        level=data.get('level', 1)
    )

    try:
        db.session.add(community)
        db.session.commit()
        return jsonify({'success': True, 'message': '社区创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/super-admin/communities/<int:community_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin')
def update_community(community_id):
    """更新社区"""
    community = Community.query.get_or_404(community_id)
    data = request.get_json()

    if 'name' in data:
        community.name = data['name']
    if 'address' in data:
        community.address = data['address']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '社区更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/super-admin/communities/<int:community_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_community(community_id):
    """删除社区"""
    community = Community.query.get_or_404(community_id)

    try:
        db.session.delete(community)
        db.session.commit()
        return jsonify({'success': True, 'message': '社区删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/super-admin/service-categories', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_service_categories():
    """获取服务分类列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = ServiceCategory.query.order_by(ServiceCategory.sort_order.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = []
    for c in pagination.items:
        categories.append({
            'id': c.id,
            'name': c.name,
            'description': c.description,
            'price_range': c.price_range,
            'is_free': c.is_free,
            'sort_order': c.sort_order,
            'is_active': c.is_active if hasattr(c, 'is_active') else True
        })

    return jsonify({
        'success': True,
        'data': categories,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/super-admin/service-categories', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_service_category():
    """创建服务分类"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': '分类名称不能为空'}), 400

    category = ServiceCategory(
        name=data['name'],
        description=data.get('description', ''),
        price_range=data.get('price_range', ''),
        is_free=data.get('is_free', False),
        sort_order=data.get('sort_order', 0)
    )

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify({'success': True, 'message': '分类创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/super-admin/service-categories/<int:category_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin')
def update_service_category(category_id):
    """更新服务分类"""
    category = ServiceCategory.query.get_or_404(category_id)
    data = request.get_json()

    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'price_range' in data:
        category.price_range = data['price_range']
    if 'is_free' in data:
        category.is_free = data['is_free']
    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '分类更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/super-admin/service-categories/<int:category_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_service_category(category_id):
    """删除服务分类"""
    category = ServiceCategory.query.get_or_404(category_id)

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': '分类删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/super-admin/news', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_news_list():
    """获取新闻列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = News.query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    news_list = []
    for n in pagination.items:
        news_list.append({
            'id': n.id,
            'title': n.title,
            'news_type': n.news_type,
            'author_name': n.author.real_name if hasattr(n, 'author') and n.author else '未知',
            'is_published': n.is_published,
            'created_at': n.created_at.isoformat() if hasattr(n, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': news_list,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/super-admin/news', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_news():
    """创建新闻"""
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({'success': False, 'message': '标题不能为空'}), 400

    news = News(
        title=data['title'],
        content=data.get('content', ''),
        news_type=data.get('news_type', 'notice'),
        author_id=request.current_user.id,
        community_id=None,  # 超级管理员创建的资讯属于平台级别
        is_published=data.get('is_published', True)
    )

    try:
        db.session.add(news)
        db.session.commit()
        return jsonify({'success': True, 'message': '新闻创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/super-admin/news/<int:news_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin')
def update_news(news_id):
    """更新新闻"""
    news = News.query.get_or_404(news_id)
    data = request.get_json()

    if 'title' in data:
        news.title = data['title']
    if 'content' in data:
        news.content = data['content']
    if 'news_type' in data:
        news.news_type = data['news_type']
    if 'is_published' in data:
        news.is_published = data['is_published']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '新闻更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/super-admin/news/<int:news_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_news(news_id):
    """删除新闻"""
    news = News.query.get_or_404(news_id)

    try:
        db.session.delete(news)
        db.session.commit()
        return jsonify({'success': True, 'message': '新闻删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/super-admin/point-products', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_point_products():
    """获取积分商品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = PointProduct.query.order_by(PointProduct.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    products = []
    for p in pagination.items:
        products.append({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'points_required': p.points_required,
            'stock': p.stock,
            'is_active': p.is_active,
            'image_url': p.image if hasattr(p, 'image') else None,
            'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None
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

@api_v1.route('/super-admin/point-products', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_point_product():
    """创建积分商品"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': '商品名称不能为空'}), 400

    product = PointProduct(
        name=data['name'],
        description=data.get('description', ''),
        points_required=data.get('points_required', 0),
        stock=data.get('stock', 0),
        is_active=True,
        image_url=data.get('image_url')
    )

    try:
        db.session.add(product)
        db.session.commit()
        return jsonify({'success': True, 'message': '商品创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/super-admin/point-products/<int:product_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin')
def update_point_product(product_id):
    """更新积分商品"""
    product = PointProduct.query.get_or_404(product_id)
    data = request.get_json()

    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'points_required' in data:
        product.points_required = data['points_required']
    if 'stock' in data:
        product.stock = data['stock']
    if 'is_active' in data:
        product.is_active = data['is_active']
    if 'image_url' in data:
        product.image_url = data['image_url']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '商品更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/super-admin/point-products/<int:product_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_point_product(product_id):
    """删除积分商品"""
    product = PointProduct.query.get_or_404(product_id)

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True, 'message': '商品删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/super-admin/alert-rules', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_alert_rules():
    """获取预警规则列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = AlertRule.query.order_by(AlertRule.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    rules = []
    for r in pagination.items:
        rules.append({
            'id': r.id,
            'name': r.name,
            'rule_type': r.rule_type,
            'threshold': r.threshold,
            'time_window_hours': r.time_window_hours,
            'notify_roles': r.notify_roles,
            'is_active': r.is_active,
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': rules,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })

@api_v1.route('/super-admin/alert-rules', methods=['POST'])
@jwt_required
@role_required('super_admin')
def create_alert_rule():
    """创建预警规则"""
    data = request.get_json()

    if not data or not data.get('name'):
        return jsonify({'success': False, 'message': '规则名称不能为空'}), 400

    rule = AlertRule(
        name=data['name'],
        rule_type=data.get('rule_type', 'sos_count'),
        threshold=data.get('threshold', 3),
        time_window_hours=data.get('time_window_hours', 24),
        notify_roles=data.get('notify_roles', ''),
        is_active=True
    )

    try:
        db.session.add(rule)
        db.session.commit()
        return jsonify({'success': True, 'message': '规则创建成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500

@api_v1.route('/super-admin/alert-rules/<int:rule_id>', methods=['PUT'])
@jwt_required
@role_required('super_admin')
def update_alert_rule(rule_id):
    """更新预警规则"""
    rule = AlertRule.query.get_or_404(rule_id)
    data = request.get_json()

    if 'name' in data:
        rule.name = data['name']
    if 'rule_type' in data:
        rule.rule_type = data['rule_type']
    if 'threshold' in data:
        rule.threshold = data['threshold']
    if 'time_window_hours' in data:
        rule.time_window_hours = data['time_window_hours']
    if 'notify_roles' in data:
        rule.notify_roles = data['notify_roles']
    if 'is_active' in data:
        rule.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '规则更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/super-admin/alert-rules/<int:rule_id>', methods=['DELETE'])
@jwt_required
@role_required('super_admin')
def delete_alert_rule(rule_id):
    """删除预警规则"""
    rule = AlertRule.query.get_or_404(rule_id)

    try:
        db.session.delete(rule)
        db.session.commit()
        return jsonify({'success': True, 'message': '规则删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/super-admin/logs', methods=['GET'])
@jwt_required
@role_required('super_admin')
def get_system_logs():
    """获取系统日志"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    module = request.args.get('module', None)

    query = SystemLog.query

    if module:
        query = query.filter_by(module=module)

    pagination = query.order_by(SystemLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    logs = []
    for log in pagination.items:
        logs.append({
            'id': log.id,
            'user_name': log.user.real_name if hasattr(log, 'user') and log.user else '系统',
            'action': log.action,
            'module': log.module,
            'ip_address': log.ip_address,
            'request_data': log.request_data,
            'created_at': log.created_at.isoformat() if hasattr(log, 'created_at') else None
        })

    return jsonify({
        'success': True,
        'data': logs,
        'meta': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'total_pages': pagination.pages
        }
    })