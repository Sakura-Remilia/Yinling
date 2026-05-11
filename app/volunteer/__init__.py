# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (User, ServiceOrder, VolunteerProfile, VolunteerServiceRecord, 
                        PointTransaction, PointProduct, PointExchange)
from datetime import datetime
from sqlalchemy import func

volunteer = Blueprint('volunteer', __name__)

@volunteer.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.volunteer_profile
    pending_orders = ServiceOrder.query.filter_by(is_free=True, status='pending').count()
    my_active_orders = ServiceOrder.query.filter_by(provider_id=current_user.id, status='in_progress').count()
    
    return render_template('volunteer/dashboard.html',
                         profile=profile,
                         pending_orders=pending_orders,
                         my_active_orders=my_active_orders)

@volunteer.route('/tasks')
@login_required
def tasks():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    orders = ServiceOrder.query.filter_by(is_free=True, status='pending').order_by(ServiceOrder.created_at.desc()).all()
    return render_template('volunteer/tasks.html', orders=orders)

@volunteer.route('/tasks/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_task(order_id):
    if not current_user.is_volunteer():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    profile = current_user.volunteer_profile
    if not profile or not profile.is_verified:
        flash('您的志愿者资质尚未通过审核，暂时无法接单', 'warning')
        return redirect(url_for('volunteer.tasks'))
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.status != 'pending':
        flash('该任务已被接单', 'warning')
        return redirect(url_for('volunteer.tasks'))
    
    order.provider_id = current_user.id
    order.provider_type = 'volunteer'
    order.status = 'accepted'
    order.accepted_at = datetime.utcnow()
    db.session.commit()
    
    flash('接单成功', 'success')
    return redirect(url_for('volunteer.my_orders'))

@volunteer.route('/my-orders')
@login_required
def my_orders():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    status = request.args.get('status', '')
    query = ServiceOrder.query.filter_by(provider_id=current_user.id, provider_type='volunteer')
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(ServiceOrder.created_at.desc()).all()
    return render_template('volunteer/my_orders.html', orders=orders)

@volunteer.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        flash('无权查看此订单', 'danger')
        return redirect(url_for('volunteer.my_orders'))
    
    return render_template('volunteer/order_detail.html', order=order)

@volunteer.route('/orders/<int:order_id>/checkin', methods=['POST'])
@login_required
def checkin(order_id):
    if not current_user.is_volunteer():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    longitude = request.form.get('longitude', type=float)
    latitude = request.form.get('latitude', type=float)
    
    order.status = 'in_progress'
    order.arrived_at = datetime.utcnow()
    order.started_at = datetime.utcnow()
    
    record = VolunteerServiceRecord(
        volunteer_id=current_user.id,
        order_id=order_id,
        elderly_id=order.elderly_id,
        service_type=order.service_type,
        start_time=datetime.utcnow(),
        check_in_longitude=longitude,
        check_in_latitude=latitude
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True, 'message': '签到成功'})

@volunteer.route('/orders/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    if not current_user.is_volunteer():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.provider_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    service_notes = request.form.get('service_notes', '')
    
    order.status = 'completed'
    order.completed_at = datetime.utcnow()
    order.service_notes = service_notes
    
    record = VolunteerServiceRecord.query.filter_by(order_id=order_id).first()
    if record:
        record.end_time = datetime.utcnow()
        record.service_notes = service_notes
        duration = (record.end_time - record.start_time).total_seconds() / 60 if record.start_time else 0
        record.duration_minutes = int(duration)
        points = int(duration / 60 * 10)
        record.points_earned = points
        record.status = 'completed'
        
        profile = current_user.volunteer_profile
        if profile:
            profile.total_service_hours += duration / 60
            profile.total_points += points
            
            transaction = PointTransaction(
                user_id=current_user.id,
                amount=points,
                transaction_type='earn',
                description=f'完成志愿服务：{order.service_type}',
                related_record_id=record.id,
                related_record_type='volunteer_service_record',
                balance_after=profile.total_points
            )
            db.session.add(transaction)
    
    db.session.commit()
    flash('服务已完成', 'success')
    return redirect(url_for('volunteer.my_orders'))

@volunteer.route('/records')
@login_required
def records():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    records = VolunteerServiceRecord.query.filter_by(volunteer_id=current_user.id).order_by(VolunteerServiceRecord.created_at.desc()).all()
    return render_template('volunteer/records.html', records=records)

@volunteer.route('/points')
@login_required
def points():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.volunteer_profile
    transactions = PointTransaction.query.filter_by(user_id=current_user.id).order_by(PointTransaction.created_at.desc()).limit(30).all()
    products = PointProduct.query.filter_by(is_active=True).filter(PointProduct.stock > 0).all()
    
    return render_template('volunteer/points.html', 
                         profile=profile, 
                         transactions=transactions,
                         products=products)

@volunteer.route('/points/exchange/<int:product_id>', methods=['POST'])
@login_required
def exchange_points(product_id):
    if not current_user.is_volunteer():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    profile = current_user.volunteer_profile
    product = PointProduct.query.get_or_404(product_id)
    
    if profile.total_points < product.points_required:
        flash('积分不足', 'warning')
        return redirect(url_for('volunteer.points'))
    
    if product.stock <= 0:
        flash('商品库存不足', 'warning')
        return redirect(url_for('volunteer.points'))
    
    profile.total_points -= product.points_required
    product.stock -= 1
    
    exchange = PointExchange(
        user_id=current_user.id,
        product_id=product_id,
        points_used=product.points_required
    )
    db.session.add(exchange)
    
    transaction = PointTransaction(
        user_id=current_user.id,
        amount=-product.points_required,
        transaction_type='exchange',
        description=f'兑换商品：{product.name}',
        related_record_id=exchange.id,
        related_record_type='point_exchange',
        balance_after=profile.total_points
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash('兑换成功', 'success')
    return redirect(url_for('volunteer.points'))

@volunteer.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_volunteer():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.volunteer_profile
    if not profile:
        profile = VolunteerProfile(user_id=current_user.id)
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
        profile.bio = request.form.get('bio')
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('volunteer.profile'))
    
    return render_template('volunteer/profile.html', profile=profile)
