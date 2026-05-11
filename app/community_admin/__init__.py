# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (User, Role, Community, ServiceOrder, SOSAlert, Activity,
                        VolunteerProfile, WorkerProfile, ElderlyProfile, AlertRule, AlertNotification,
                        CommunityAdminProfile, CommunityAnnouncement, News)
from datetime import datetime, timedelta
from sqlalchemy import func, or_

community_admin = Blueprint('community_admin', __name__)

@community_admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    total_elderly = User.query.filter_by(role_id=1)
    if community_id:
        total_elderly = total_elderly.filter_by(community_id=community_id)
    total_elderly = total_elderly.count()
    
    living_alone = 0
    if community_id:
        living_alone = ElderlyProfile.query.filter_by(is_living_alone=True).join(User).filter(User.community_id == community_id).count()
    
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    today_sos = SOSAlert.query.filter(SOSAlert.triggered_at >= today_start)
    if community_id:
        today_sos = today_sos.join(User).filter(User.community_id == community_id)
    today_sos = today_sos.count()
    
    pending_orders = ServiceOrder.query.filter_by(status='pending')
    if community_id:
        pending_orders = pending_orders.join(User).filter(User.community_id == community_id)
    pending_orders = pending_orders.count()
    
    active_sos = SOSAlert.query.filter_by(status='active')
    if community_id:
        active_sos = active_sos.join(User).filter(User.community_id == community_id)
    active_sos = active_sos.all()
    
    return render_template('community_admin/dashboard.html',
                         total_elderly=total_elderly,
                         living_alone=living_alone,
                         today_sos=today_sos,
                         pending_orders=pending_orders,
                         active_sos=active_sos,
                         profile=profile)

@community_admin.route('/elderly')
@login_required
def elderly_list():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = User.query.filter_by(role_id=1)
    if community_id:
        query = query.filter_by(community_id=community_id)
    
    elderly_users = query.all()
    return render_template('community_admin/elderly_list.html', elderly_users=elderly_users)

@community_admin.route('/elderly/<int:elderly_id>')
@login_required
def elderly_detail(elderly_id):
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    elderly = User.query.get_or_404(elderly_id)
    return render_template('community_admin/elderly_detail.html', elderly=elderly)

@community_admin.route('/volunteers')
@login_required
def volunteers():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = User.query.filter_by(role_id=2)
    if community_id:
        query = query.filter_by(community_id=community_id)
    
    volunteers = query.all()
    return render_template('community_admin/volunteers.html', volunteers=volunteers)

@community_admin.route('/volunteers/<int:volunteer_id>/verify', methods=['POST'])
@login_required
def verify_volunteer(volunteer_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    volunteer = User.query.get_or_404(volunteer_id)
    profile = volunteer.volunteer_profile
    if profile:
        profile.is_verified = True
        profile.verified_at = datetime.utcnow()
        db.session.commit()
        flash('志愿者资质已审核通过', 'success')
    
    return redirect(url_for('community_admin.volunteers'))

@community_admin.route('/workers')
@login_required
def workers():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = User.query.filter_by(role_id=3)
    if community_id:
        query = query.filter_by(community_id=community_id)
    
    workers = query.all()
    return render_template('community_admin/workers.html', workers=workers)

@community_admin.route('/workers/<int:worker_id>/verify', methods=['POST'])
@login_required
def verify_worker(worker_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    worker = User.query.get_or_404(worker_id)
    profile = worker.worker_profile
    if profile:
        profile.is_verified = True
        profile.verified_at = datetime.utcnow()
        db.session.commit()
        flash('工作人员资质已审核通过', 'success')
    
    return redirect(url_for('community_admin.workers'))

@community_admin.route('/workers/<int:worker_id>/train', methods=['POST'])
@login_required
def train_worker(worker_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    worker = User.query.get_or_404(worker_id)
    profile = worker.worker_profile
    if profile:
        profile.is_trained = True
        profile.trained_at = datetime.utcnow()
        db.session.commit()
        flash('工作人员培训状态已更新', 'success')
    
    return redirect(url_for('community_admin.workers'))

@community_admin.route('/orders')
@login_required
def orders():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    status = request.args.get('status', '')
    query = ServiceOrder.query
    if community_id:
        query = query.join(User).filter(User.community_id == community_id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(ServiceOrder.created_at.desc()).all()
    
    return render_template('community_admin/orders.html', orders=orders)

@community_admin.route('/sos')
@login_required
def sos_list():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = SOSAlert.query
    if community_id:
        query = query.join(User).filter(User.community_id == community_id)
    alerts = query.order_by(SOSAlert.triggered_at.desc()).all()
    
    return render_template('community_admin/sos_list.html', alerts=alerts)

@community_admin.route('/activities')
@login_required
def activities():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = Activity.query
    if community_id:
        query = query.filter_by(community_id=community_id)
    activities = query.order_by(Activity.created_at.desc()).all()
    
    return render_template('community_admin/activities.html', activities=activities)

@community_admin.route('/activities/create', methods=['GET', 'POST'])
@login_required
def create_activity():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    if request.method == 'POST':
        activity = Activity(
            title=request.form.get('title'),
            description=request.form.get('description'),
            activity_type=request.form.get('activity_type'),
            start_time=datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M'),
            end_time=datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M'),
            location=request.form.get('location'),
            longitude=request.form.get('longitude', type=float),
            latitude=request.form.get('latitude', type=float),
            max_participants=request.form.get('max_participants', type=int, default=0),
            organizer_id=current_user.id,
            community_id=community_id,
            status='published',
            is_public=True
        )
        db.session.add(activity)
        db.session.commit()
        flash('活动已发布', 'success')
        return redirect(url_for('community_admin.activities'))
    
    return render_template('community_admin/create_activity.html')

@community_admin.route('/activities/<int:activity_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_activity(activity_id):
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    activity = Activity.query.get_or_404(activity_id)
    
    if request.method == 'POST':
        activity.title = request.form.get('title')
        activity.description = request.form.get('description')
        activity.activity_type = request.form.get('activity_type')
        activity.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        activity.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        activity.location = request.form.get('location')
        activity.max_participants = request.form.get('max_participants', type=int, default=0)
        
        db.session.commit()
        flash('活动已更新', 'success')
        return redirect(url_for('community_admin.activities'))
    
    return render_template('community_admin/edit_activity.html', activity=activity)

@community_admin.route('/activities/<int:activity_id>/cancel', methods=['POST'])
@login_required
def cancel_activity(activity_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    activity.status = 'cancelled'
    db.session.commit()
    flash('活动已取消', 'success')
    return redirect(url_for('community_admin.activities'))

@community_admin.route('/accounts')
@login_required
def accounts():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = User.query
    if community_id:
        query = query.filter_by(community_id=community_id)
    # 排除系统管理员账户
    query = query.join(Role).filter(Role.name != 'super_admin')
    users = query.all()
    
    return render_template('community_admin/accounts.html', users=users)

@community_admin.route('/accounts/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '123456')
    user.password = new_password
    db.session.commit()
    flash(f'用户 {user.username} 的密码已重置为 {new_password}', 'success')
    return redirect(url_for('community_admin.accounts'))

@community_admin.route('/accounts/<int:user_id>/toggle-active', methods=['POST'])
@login_required
def toggle_active(user_id):
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = '启用' if user.is_active else '禁用'
    flash(f'用户 {user.username} 已{status}', 'success')
    return redirect(url_for('community_admin.accounts'))

@community_admin.route('/alerts')
@login_required
def alerts():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None
    
    query = AlertNotification.query
    if community_id:
        query = query.join(User).filter(User.community_id == community_id)
    notifications = query.order_by(AlertNotification.created_at.desc()).all()
    
    return render_template('community_admin/alerts.html', notifications=notifications)

@community_admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.community_admin_profile
    if not profile:
        profile = CommunityAdminProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    if request.method == 'POST':
        profile.position = request.form.get('position')
        profile.department = request.form.get('department')
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('community_admin.profile'))
    
    communities = Community.query.all()
    return render_template('community_admin/profile.html', profile=profile, communities=communities)

# ============= 社区公告管理 =============

@community_admin.route('/announcements')
@login_required
def announcements():
    """公告管理列表页"""
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None

    query = CommunityAnnouncement.query
    if community_id:
        query = query.filter_by(community_id=community_id)
    announcements = query.order_by(
        CommunityAnnouncement.is_pinned.desc(),
        CommunityAnnouncement.published_at.desc()
    ).all()

    return render_template('community_admin/announcements.html', announcements=announcements)

@community_admin.route('/announcements/create', methods=['GET', 'POST'])
@login_required
def create_announcement():
    """创建公告"""
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    profile = current_user.community_admin_profile
    community_id = profile.managed_community_id if profile else None

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_pinned = request.form.get('is_pinned') == 'on'

        if not title or not content:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('community_admin.create_announcement'))

        announcement = CommunityAnnouncement(
            title=title,
            content=content,
            cover_image=request.form.get('cover_image', ''),
            community_id=community_id,
            publisher_id=current_user.id,
            is_pinned=is_pinned,
            is_active=True,
            published_at=datetime.utcnow()
        )
        db.session.add(announcement)
        db.session.commit()
        flash('公告已发布', 'success')
        return redirect(url_for('community_admin.announcements'))

    return render_template('community_admin/create_announcement.html')

@community_admin.route('/announcements/<int:announcement_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_announcement(announcement_id):
    """编辑公告"""
    if not current_user.is_community_admin():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    announcement = CommunityAnnouncement.query.get_or_404(announcement_id)

    if request.method == 'POST':
        announcement.title = request.form.get('title', '').strip()
        announcement.content = request.form.get('content', '').strip()
        announcement.cover_image = request.form.get('cover_image', '')
        announcement.is_pinned = request.form.get('is_pinned') == 'on'
        announcement.is_active = request.form.get('is_active') == 'on'

        db.session.commit()
        flash('公告已更新', 'success')
        return redirect(url_for('community_admin.announcements'))

    return render_template('community_admin/edit_announcement.html', announcement=announcement)

@community_admin.route('/announcements/<int:announcement_id>/delete', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    """删除公告"""
    if not current_user.is_community_admin():
        return jsonify({'success': False, 'message': '无权操作'}), 403

    announcement = CommunityAnnouncement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('公告已删除', 'success')
    return redirect(url_for('community_admin.announcements'))

# ============= 统一内容管理（公告 + 资讯）============

@community_admin.route('/content-management')
@login_required
def content_management():
    """统一内容管理页面"""
    if not (current_user.is_community_admin() or current_user.is_super_admin()):
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    profile = current_user.community_admin_profile
    # 超级管理员没有 community_admin_profile，community_id 为 None 表示平台级别
    community_id = profile.managed_community_id if profile else None

    # 获取公告
    ann_query = CommunityAnnouncement.query
    if community_id:
        ann_query = ann_query.filter_by(community_id=community_id)
    announcements = ann_query.order_by(
        CommunityAnnouncement.is_pinned.desc(),
        CommunityAnnouncement.published_at.desc()
    ).all()

    # 获取资讯（超级管理员看全部，社区管理员看本社区或未关联社区的）
    news_query = News.query
    if community_id and not current_user.is_super_admin():
        news_query = news_query.filter(
            db.or_(News.community_id == community_id, News.community_id == None)
        )
    news = news_query.order_by(News.created_at.desc()).all()

    return render_template('community_admin/content_management.html',
                           announcements=announcements, news=news)

@community_admin.route('/content/create/<content_type>', methods=['GET', 'POST'])
@login_required
def create_content(content_type):
    """创建内容（公告或资讯）"""
    if not (current_user.is_community_admin() or current_user.is_super_admin()):
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    profile = current_user.community_admin_profile
    # 超级管理员没有 community_admin_profile，community_id 为 None 表示平台级别
    community_id = profile.managed_community_id if profile else None

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content_text = request.form.get('content', '').strip()

        if not title or not content_text:
            flash('标题和内容不能为空', 'danger')
            return redirect(url_for('community_admin.create_content', content_type=content_type))

        if content_type == 'announcement':
            announcement = CommunityAnnouncement(
                title=title,
                content=content_text,
                cover_image=request.form.get('cover_image', ''),
                community_id=community_id,
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
                community_id=community_id,
                is_published=True,
                published_at=datetime.utcnow()
            )
            db.session.add(news)
            flash('资讯已发布', 'success')

        db.session.commit()
        return redirect(url_for('community_admin.content_management'))

    return render_template('community_admin/create_content.html', content_type=content_type)

@community_admin.route('/content/edit/<content_type>/<int:content_id>', methods=['GET', 'POST'])
@login_required
def edit_content(content_type, content_id):
    """编辑内容"""
    if not (current_user.is_community_admin() or current_user.is_super_admin()):
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    if content_type == 'announcement':
        content = CommunityAnnouncement.query.get_or_404(content_id)
    elif content_type == 'news':
        content = News.query.get_or_404(content_id)
    else:
        flash('无效的内容类型', 'danger')
        return redirect(url_for('community_admin.content_management'))

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
        return redirect(url_for('community_admin.content_management'))

    return render_template('community_admin/edit_content.html', content_type=content_type, content=content)

@community_admin.route('/content/delete/<content_type>/<int:content_id>', methods=['POST'])
@login_required
def delete_content(content_type, content_id):
    """删除内容"""
    if not (current_user.is_community_admin() or current_user.is_super_admin()):
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
    return redirect(url_for('community_admin.content_management'))
