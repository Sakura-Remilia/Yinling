# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import News, Activity, ServiceCategory, Community, CommunityAnnouncement
from app.auth.jwt_auth import jwt_required
from datetime import datetime

@api_v1.route('/public/news', methods=['GET'])
def get_public_news():
    """获取新闻列表 (公开)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    news_type = request.args.get('type', None)

    query = News.query.filter_by(is_published=True)

    if news_type:
        query = query.filter_by(news_type=news_type)

    pagination = query.order_by(News.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    news_list = []
    for n in pagination.items:
        news_list.append({
            'id': n.id,
            'title': n.title,
            'content': n.content[:200] + '...' if n.content and len(n.content) > 200 else n.content,
            'news_type': n.news_type,
            'author_name': n.author.real_name if n.author else '未知',
            'created_at': n.created_at.isoformat() if n.created_at else None
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

@api_v1.route('/public/news/<int:news_id>', methods=['GET'])
def get_public_news_detail(news_id):
    """获取新闻详情 (需登录且为老人角色才能查看完整内容)"""
    news = News.query.get_or_404(news_id)

    # 检查用户是否登录且为老人角色
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        # 未登录，返回部分内容提示登录
        return jsonify({
            'success': False,
            'message': '请先登录',
            'require_login': True
        }), 401

    # 验证token并检查角色
    from app.auth.jwt_auth import verify_token
    token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else ''
    payload = verify_token(token)
    if not payload:
        return jsonify({
            'success': False,
            'message': '登录已过期',
            'require_login': True
        }), 401

    # 检查是否为老人角色
    from app.models import User
    user = User.query.get(payload.get('user_id'))
    if not user or not user.is_elderly():
        return jsonify({
            'success': False,
            'message': '只有老人角色才能查看资讯详情',
            'require_elderly': True
        }), 403

    return jsonify({
        'success': True,
        'data': {
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'cover_image': news.cover_image,
            'news_type': news.news_type,
            'author_name': news.author.real_name if hasattr(news, 'author') and news.author else '未知',
            'created_at': news.created_at.isoformat() if hasattr(news, 'created_at') else None
        }
    })

@api_v1.route('/public/activities', methods=['GET'])
def get_public_activities():
    """获取活动列表 (公开)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Activity.query.filter_by(status='published').filter(
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

@api_v1.route('/public/service-categories', methods=['GET'])
def get_public_service_categories():
    """获取服务分类 (公开)"""
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

@api_v1.route('/public/communities', methods=['GET'])
def get_public_communities():
    """获取社区列表 (公开)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Community.query.order_by(Community.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    communities = []
    for c in pagination.items:
        communities.append({
            'id': c.id,
            'name': c.name,
            'address': c.address
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

@api_v1.route('/public/announcements', methods=['GET'])
def get_public_announcements():
    """获取社区公告列表 (公开)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    community_id = request.args.get('community_id', type=int)

    query = CommunityAnnouncement.query.filter_by(is_active=True)

    if community_id:
        query = query.filter_by(community_id=community_id)

    # 置顶的排前面，然后按时间倒序
    pagination = query.order_by(
        CommunityAnnouncement.is_pinned.desc(),
        CommunityAnnouncement.published_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    announcements = []
    for a in pagination.items:
        announcements.append({
            'id': a.id,
            'title': a.title,
            'content': a.content[:150] + '...' if a.content and len(a.content) > 150 else a.content,
            'cover_image': a.cover_image,
            'is_pinned': a.is_pinned,
            'community_name': a.community.name if a.community else '平台公告',
            'published_at': a.published_at.isoformat() if a.published_at else None,
            'created_at': a.created_at.isoformat() if a.created_at else None
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