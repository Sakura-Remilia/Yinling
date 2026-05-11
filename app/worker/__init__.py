# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (User, ServiceOrder, WorkerProfile, ElderlyProfile, 
                        VisitRecord, FollowUpRecord, Community)
from datetime import datetime
from sqlalchemy import or_

worker = Blueprint('worker', __name__)

@worker.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.worker_profile
    pending_orders = ServiceOrder.query.filter_by(is_free=False, status='pending').count()
    my_active_orders = ServiceOrder.query.filter_by(provider_id=current_user.id, status='in_progress').count()
    my_completed_orders = ServiceOrder.query.filter_by(provider_id=current_user.id, status='completed').count()
    
    return render_template('worker/dashboard.html',
                         profile=profile,
                         pending_orders=pending_orders,
                         my_active_orders=my_active_orders,
                         my_completed_orders=my_completed_orders)

@worker.route('/orders')
@login_required
def orders():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    orders = ServiceOrder.query.filter_by(is_free=False, status='pending').order_by(ServiceOrder.created_at.desc()).all()
    return render_template('worker/orders.html', orders=orders)

@worker.route('/orders/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    if not current_user.is_worker():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    profile = current_user.worker_profile
    if not profile or not profile.is_verified:
        flash('您的工作资质尚未通过审核，暂时无法接单', 'warning')
        return redirect(url_for('worker.orders'))
    
    if not profile.is_trained:
        flash('您尚未完成工作培训，暂时无法接单', 'warning')
        return redirect(url_for('worker.orders'))
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.status != 'pending':
        flash('该订单已被接单', 'warning')
        return redirect(url_for('worker.orders'))
    
    order.provider_id = current_user.id
    order.provider_type = 'worker'
    order.status = 'accepted'
    order.accepted_at = datetime.utcnow()
    db.session.commit()
    
    flash('接单成功', 'success')
    return redirect(url_for('worker.my_orders'))

@worker.route('/my-orders')
@login_required
def my_orders():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    status = request.args.get('status', '')
    query = ServiceOrder.query.filter_by(provider_id=current_user.id, provider_type='worker')
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(ServiceOrder.created_at.desc()).all()
    return render_template('worker/my_orders.html', orders=orders)

@worker.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        flash('无权查看此订单', 'danger')
        return redirect(url_for('worker.my_orders'))
    
    return render_template('worker/order_detail.html', order=order)

@worker.route('/orders/<int:order_id>/arrive', methods=['POST'])
@login_required
def arrive(order_id):
    if not current_user.is_worker():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order.status = 'in_progress'
    order.arrived_at = datetime.utcnow()
    order.started_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': '已确认到达'})

@worker.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    if not current_user.is_worker():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    service_notes = request.form.get('service_notes', '')
    
    order.status = 'completed'
    order.completed_at = datetime.utcnow()
    order.service_notes = service_notes
    
    profile = current_user.worker_profile
    if profile:
        profile.total_orders += 1
    
    db.session.commit()
    flash('服务已完成', 'success')
    return redirect(url_for('worker.my_orders'))

@worker.route('/elderly')
@login_required
def elderly_list():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    elderly_users = User.query.filter_by(role_id=1).all()
    return render_template('worker/elderly_list.html', elderly_users=elderly_users)

@worker.route('/elderly/<int:elderly_id>')
@login_required
def elderly_detail(elderly_id):
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    elderly = User.query.get_or_404(elderly_id)
    if not elderly.is_elderly():
        flash('用户不是老人', 'danger')
        return redirect(url_for('worker.elderly_list'))
    
    return render_template('worker/elderly_detail.html', elderly=elderly)

@worker.route('/visits')
@login_required
def visits():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    visits = VisitRecord.query.filter_by(visitor_id=current_user.id).order_by(VisitRecord.created_at.desc()).all()
    return render_template('worker/visits.html', visits=visits)

@worker.route('/visits/create', methods=['GET', 'POST'])
@login_required
def create_visit():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        visit = VisitRecord(
            visitor_id=current_user.id,
            elderly_id=request.form.get('elderly_id'),
            visit_type=request.form.get('visit_type'),
            scheduled_time=datetime.strptime(request.form.get('scheduled_time'), '%Y-%m-%dT%H:%M') if request.form.get('scheduled_time') else None,
            notes=request.form.get('notes', '')
        )
        db.session.add(visit)
        db.session.commit()
        flash('走访任务已创建', 'success')
        return redirect(url_for('worker.visits'))
    
    elderly_users = User.query.filter_by(role_id=1).all()
    return render_template('worker/create_visit.html', elderly_users=elderly_users)

@worker.route('/visits/<int:visit_id>/complete', methods=['POST'])
@login_required
def complete_visit(visit_id):
    if not current_user.is_worker():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    visit = VisitRecord.query.get_or_404(visit_id)
    if visit.visitor_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    visit.status = 'completed'
    visit.actual_time = datetime.utcnow()
    visit.health_status = request.form.get('health_status')
    visit.needs = request.form.get('needs')
    visit.notes = request.form.get('notes')
    visit.longitude = request.form.get('longitude', type=float)
    visit.latitude = request.form.get('latitude', type=float)
    
    db.session.commit()
    flash('走访记录已提交', 'success')
    return redirect(url_for('worker.visits'))

@worker.route('/follow-ups')
@login_required
def follow_ups():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    follow_ups = FollowUpRecord.query.filter_by(follower_id=current_user.id).order_by(FollowUpRecord.created_at.desc()).all()
    return render_template('worker/follow_ups.html', follow_ups=follow_ups)

@worker.route('/follow-ups/create', methods=['GET', 'POST'])
@login_required
def create_follow_up():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        follow_up = FollowUpRecord(
            order_id=request.form.get('order_id'),
            follower_id=current_user.id,
            elderly_id=request.form.get('elderly_id'),
            follow_up_type=request.form.get('follow_up_type'),
            satisfaction_level=request.form.get('satisfaction_level', type=int),
            feedback=request.form.get('feedback'),
            issues_found=request.form.get('issues_found'),
            resolution=request.form.get('resolution')
        )
        db.session.add(follow_up)
        db.session.commit()
        flash('回访记录已提交', 'success')
        return redirect(url_for('worker.follow_ups'))
    
    elderly_users = User.query.filter_by(role_id=1).all()
    orders = ServiceOrder.query.filter_by(provider_id=current_user.id, status='completed').all()
    return render_template('worker/create_follow_up.html', elderly_users=elderly_users, orders=orders)

@worker.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_worker():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.worker_profile
    if not profile:
        profile = WorkerProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    if request.method == 'POST':
        profile.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d') if request.form.get('birth_date') else None
        profile.gender = request.form.get('gender')
        profile.id_card = request.form.get('id_card')
        profile.address = request.form.get('address')
        profile.longitude = request.form.get('longitude', type=float)
        profile.latitude = request.form.get('latitude', type=float)
        profile.skills = request.form.get('skills')
        profile.service_areas = request.form.get('service_areas')
        profile.work_type = request.form.get('work_type')
        profile.bio = request.form.get('bio')
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('worker.profile'))
    
    return render_template('worker/profile.html', profile=profile)
