# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (User, Role, Community, ServiceCategory, News, SystemLog,
                        PointProduct, AlertRule, ServiceOrder, VolunteerServiceRecord, CommunityAnnouncement)
from datetime import datetime
from sqlalchemy import func
import json

super_admin = Blueprint('super_admin', __name__)

@super_admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    total_users = User.query.count()
    total_communities = Community.query.count()
    total_orders = ServiceOrder.query.count()
    total_service_hours = db.session.query(func.sum(VolunteerServiceRecord.duration_minutes)).scalar() or 0
    
    users_by_role = db.session.query(Role.name, func.count(User.id)).join(User).group_by(Role.id).all()
    
    return render_template('super_admin/dashboard.html',
                         total_users=total_users,
                         total_communities=total_communities,
                         total_orders=total_orders,
                         total_service_hours=total_service_hours,
                         users_by_role=users_by_role)

@super_admin.route('/communities')
@login_required
def communities():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    communities = Community.query.order_by(Community.created_at.desc()).all()
    return render_template('super_admin/communities.html', communities=communities)

@super_admin.route('/communities/create', methods=['GET', 'POST'])
@login_required
def create_community():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        community = Community(
            name=request.form.get('name'),
            address=request.form.get('address'),
            contact_phone=request.form.get('contact_phone'),
            description=request.form.get('description'),
            parent_id=request.form.get('parent_id', type=int),
            level=request.form.get('level', type=int, default=1)
        )
        db.session.add(community)
        db.session.commit()
        flash('社区已创建', 'success')
        return redirect(url_for('super_admin.communities'))
    
    parent_communities = Community.query.filter_by(level=1).all()
    return render_template('super_admin/create_community.html', parent_communities=parent_communities)

@super_admin.route('/communities/<int:community_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_community(community_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    community = Community.query.get_or_404(community_id)
    
    if request.method == 'POST':
        community.name = request.form.get('name')
        community.address = request.form.get('address')
        community.contact_phone = request.form.get('contact_phone')
        community.description = request.form.get('description')
        db.session.commit()
        flash('社区信息已更新', 'success')
        return redirect(url_for('super_admin.communities'))
    
    parent_communities = Community.query.filter(Community.id != community_id, Community.level == 1).all()
    return render_template('super_admin/edit_community.html', community=community, parent_communities=parent_communities)

@super_admin.route('/users')
@login_required
def users():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    role_id = request.args.get('role', type=int)
    community_id = request.args.get('community', type=int)
    
    query = User.query
    if role_id:
        query = query.filter_by(role_id=role_id)
    if community_id:
        query = query.filter_by(community_id=community_id)
    
    users = query.order_by(User.created_at.desc()).all()
    roles = Role.query.all()
    communities = Community.query.all()
    
    return render_template('super_admin/users.html', users=users, roles=roles, communities=communities)

@super_admin.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('super_admin.create_user'))
        
        user = User(
            username=username,
            real_name=request.form.get('real_name'),
            phone=request.form.get('phone'),
            email=request.form.get('email', ''),
            role_id=request.form.get('role_id', type=int),
            community_id=request.form.get('community_id', type=int)
        )
        user.password = request.form.get('password', '123456')
        db.session.add(user)
        db.session.commit()
        flash('用户已创建', 'success')
        return redirect(url_for('super_admin.users'))
    
    roles = Role.query.all()
    communities = Community.query.all()
    return render_template('super_admin/create_user.html', roles=roles, communities=communities)

@super_admin.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.real_name = request.form.get('real_name')
        user.phone = request.form.get('phone')
        user.email = request.form.get('email')
        user.role_id = request.form.get('role_id', type=int)
        user.community_id = request.form.get('community_id', type=int)
        user.is_active = request.form.get('is_active') == 'on'
        
        new_password = request.form.get('new_password')
        if new_password:
            user.password = new_password
        
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('super_admin.users'))
    
    roles = Role.query.all()
    communities = Community.query.all()
    return render_template('super_admin/edit_user.html', user=user, roles=roles, communities=communities)

@super_admin.route('/service-categories')
@login_required
def service_categories():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    categories = ServiceCategory.query.order_by(ServiceCategory.sort_order).all()
    return render_template('super_admin/service_categories.html', categories=categories)

@super_admin.route('/service-categories/create', methods=['GET', 'POST'])
@login_required
def create_service_category():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        category = ServiceCategory(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price_range=request.form.get('price_range'),
            is_free=request.form.get('is_free') == 'on',
            sort_order=request.form.get('sort_order', type=int, default=0)
        )
        db.session.add(category)
        db.session.commit()
        flash('服务类别已创建', 'success')
        return redirect(url_for('super_admin.service_categories'))
    
    return render_template('super_admin/create_service_category.html')

@super_admin.route('/service-categories/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service_category(category_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    category = ServiceCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        category.price_range = request.form.get('price_range')
        category.is_free = request.form.get('is_free') == 'on'
        category.sort_order = request.form.get('sort_order', type=int, default=0)
        category.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        flash('服务类别已更新', 'success')
        return redirect(url_for('super_admin.service_categories'))
    
    return render_template('super_admin/edit_service_category.html', category=category)

@super_admin.route('/news')
@login_required
def news_list():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    news_type = request.args.get('type', '')
    query = News.query
    if news_type:
        query = query.filter_by(news_type=news_type)
    news = query.order_by(News.created_at.desc()).all()
    
    return render_template('super_admin/news_list.html', news=news)

@super_admin.route('/news/create', methods=['GET', 'POST'])
@login_required
def create_news():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        news = News(
            title=request.form.get('title'),
            content=request.form.get('content'),
            news_type=request.form.get('news_type', 'news'),
            author_id=current_user.id,
            community_id=None,  # 超级管理员创建的资讯属于平台级别
            is_published=request.form.get('is_published') == 'on'
        )
        if news.is_published:
            news.published_at = datetime.utcnow()
        db.session.add(news)
        db.session.commit()
        flash('资讯已创建', 'success')
        return redirect(url_for('super_admin.news_list'))
    
    return render_template('super_admin/create_news.html')

@super_admin.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    news = News.query.get_or_404(news_id)
    
    if request.method == 'POST':
        news.title = request.form.get('title')
        news.content = request.form.get('content')
        news.news_type = request.form.get('news_type', 'news')
        
        was_published = news.is_published
        news.is_published = request.form.get('is_published') == 'on'
        if news.is_published and not was_published:
            news.published_at = datetime.utcnow()
        
        db.session.commit()
        flash('资讯已更新', 'success')
        return redirect(url_for('super_admin.news_list'))
    
    return render_template('super_admin/edit_news.html', news=news)

@super_admin.route('/point-products')
@login_required
def point_products():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    products = PointProduct.query.order_by(PointProduct.created_at.desc()).all()
    return render_template('super_admin/point_products.html', products=products)

@super_admin.route('/point-products/create', methods=['GET', 'POST'])
@login_required
def create_point_product():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        product = PointProduct(
            name=request.form.get('name'),
            description=request.form.get('description'),
            points_required=request.form.get('points_required', type=int),
            stock=request.form.get('stock', type=int, default=0)
        )
        db.session.add(product)
        db.session.commit()
        flash('积分商品已创建', 'success')
        return redirect(url_for('super_admin.point_products'))
    
    return render_template('super_admin/create_point_product.html')

@super_admin.route('/logs')
@login_required
def logs():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50)
    
    return render_template('super_admin/logs.html', logs=logs)

@super_admin.route('/alert-rules')
@login_required
def alert_rules():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    rules = AlertRule.query.all()
    return render_template('super_admin/alert_rules.html', rules=rules)

@super_admin.route('/alert-rules/create', methods=['GET', 'POST'])
@login_required
def create_alert_rule():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        rule = AlertRule(
            name=request.form.get('name'),
            description=request.form.get('description'),
            rule_type=request.form.get('rule_type'),
            threshold=request.form.get('threshold', type=int),
            time_window_hours=request.form.get('time_window_hours', type=int),
            notify_roles=request.form.get('notify_roles'),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(rule)
        db.session.commit()
        flash('预警规则已创建', 'success')
        return redirect(url_for('super_admin.alert_rules'))
    
    return render_template('super_admin/create_alert_rule.html')

@super_admin.route('/reports')
@login_required
def reports():
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    from sqlalchemy import func
    from datetime import timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    orders_by_day = db.session.query(
        func.date(ServiceOrder.created_at).label('date'),
        func.count(ServiceOrder.id).label('count')
    ).filter(
        ServiceOrder.created_at >= start_date
    ).group_by(func.date(ServiceOrder.created_at)).all()
    
    service_hours = db.session.query(
        func.sum(VolunteerServiceRecord.duration_minutes)
    ).scalar() or 0
    
    return render_template('super_admin/reports.html', 
                         orders_by_day=orders_by_day,
                         service_hours=service_hours)

@super_admin.route('/point-products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_point_product(product_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    product = PointProduct.query.get_or_404(product_id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.points_required = request.form.get('points_required', type=int)
        product.stock = request.form.get('stock', type=int, default=0)
        product.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        flash('积分商品已更新', 'success')
        return redirect(url_for('super_admin.point_products'))
    
    return render_template('super_admin/edit_point_product.html', product=product)

@super_admin.route('/alert-rules/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_alert_rule(rule_id):
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    rule = AlertRule.query.get_or_404(rule_id)
    
    if request.method == 'POST':
        rule.name = request.form.get('name')
        rule.description = request.form.get('description')
        rule.rule_type = request.form.get('rule_type')
        rule.threshold = request.form.get('threshold', type=int)
        rule.time_window_hours = request.form.get('time_window_hours', type=int)
        rule.notify_roles = request.form.get('notify_roles')
        rule.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        flash('预警规则已更新', 'success')
        return redirect(url_for('super_admin.alert_rules'))
    
    return render_template('super_admin/edit_alert_rule.html', rule=rule)

@super_admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """超级管理员个人设置"""
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        current_user.real_name = request.form.get('real_name', current_user.real_name)
        current_user.email = request.form.get('email', current_user.email)
        new_password = request.form.get('new_password')
        if new_password:
            old_password = request.form.get('old_password')
            if not current_user.verify_password(old_password):
                flash('原密码错误', 'danger')
                return redirect(url_for('super_admin.profile'))
            current_user.password = new_password
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('super_admin.profile'))

    return render_template('super_admin/profile.html')

# ============= 统一内容管理（公告 + 资讯）============

@super_admin.route('/content-management')
@login_required
def content_management():
    """统一内容管理页面"""
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    # 获取公告（超级管理员看全部）
    announcements = CommunityAnnouncement.query.order_by(
        CommunityAnnouncement.is_pinned.desc(),
        CommunityAnnouncement.published_at.desc()
    ).all()

    # 获取资讯
    news = News.query.order_by(News.created_at.desc()).all()

    return render_template('community_admin/content_management.html',
                           announcements=announcements, news=news)

@super_admin.route('/content/create/<content_type>', methods=['GET', 'POST'])
@login_required
def create_content(content_type):
    """创建内容"""
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content_text = request.form.get('content', '').strip()

        if not title or not content_text:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('super_admin.create_content', content_type=content_type))

        if content_type == 'announcement':
            announcement = CommunityAnnouncement(
                title=title,
                content=content_text,
                cover_image=request.form.get('cover_image', ''),
                community_id=None,  # 超级管理员创建的是平台级公告
                publisher_id=current_user.id,
                is_pinned=request.form.get('is_pinned') == 'on',
                is_active=True,
                published_at=datetime.utcnow()
            )
            db.session.add(announcement)
            flash('公告已发布', 'success')
        elif content_type == 'news':
            news = News(
                title=title,
                content=content_text,
                cover_image=request.form.get('cover_image', ''),
                news_type=request.form.get('news_type', 'news'),
                author_id=current_user.id,
                community_id=None,  # 超级管理员创建的资讯属于平台级别
                is_published=True,
                published_at=datetime.utcnow()
            )
            db.session.add(news)
            flash('资讯已发布', 'success')
        else:
            flash('无效的内容类型', 'danger')
            return redirect(url_for('super_admin.content_management'))

        db.session.commit()
        return redirect(url_for('super_admin.content_management'))

    return render_template('community_admin/create_content.html', content_type=content_type)

@super_admin.route('/content/edit/<content_type>/<int:content_id>', methods=['GET', 'POST'])
@login_required
def edit_content(content_type, content_id):
    """编辑内容"""
    if not current_user.is_super_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    if content_type == 'announcement':
        content = CommunityAnnouncement.query.get_or_404(content_id)
    elif content_type == 'news':
        content = News.query.get_or_404(content_id)
    else:
        flash('无效的内容类型', 'danger')
        return redirect(url_for('super_admin.content_management'))

    if request.method == 'POST':
        content.title = request.form.get('title', '').strip()
        content.content = request.form.get('content', '').strip()
        content.cover_image = request.form.get('cover_image', '')

        if content_type == 'announcement':
            content.is_pinned = request.form.get('is_pinned') == 'on'
            content.is_active = request.form.get('is_active') == 'on'
            flash('公告已更新', 'success')
        elif content_type == 'news':
            content.news_type = request.form.get('news_type', 'news')
            content.is_published = request.form.get('is_published') == 'on'
            flash('资讯已更新', 'success')

        db.session.commit()
        return redirect(url_for('super_admin.content_management'))

    return render_template('community_admin/edit_content.html', content_type=content_type, content=content)

@super_admin.route('/content/delete/<content_type>/<int:content_id>', methods=['POST'])
@login_required
def delete_content(content_type, content_id):
    """删除内容"""
    if not current_user.is_super_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403

    if content_type == 'announcement':
        content = CommunityAnnouncement.query.get_or_404(content_id)
    elif content_type == 'news':
        content = News.query.get_or_404(content_id)
    else:
        return jsonify({'success': False, 'message': '无效的内容类型'}), 400

    db.session.delete(content)
    db.session.commit()

    flash_message = '公告已删除' if content_type == 'announcement' else '资讯已删除'
    flash(flash_message, 'success')
    return redirect(url_for('super_admin.content_management'))
