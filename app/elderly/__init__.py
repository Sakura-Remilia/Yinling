# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (User, ServiceCategory, ServiceOrder, SOSAlert, HealthRecord, 
                        MedicationReminder, AppointmentReminder, Activity, ActivityRegistration, News)
from datetime import datetime
import random
import string

elderly = Blueprint('elderly', __name__)

def generate_order_no(prefix='SO'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'{prefix}{timestamp}{random_str}'

@elderly.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    pending_orders = ServiceOrder.query.filter_by(elderly_id=current_user.id, status='pending').count()
    in_progress_orders = ServiceOrder.query.filter_by(elderly_id=current_user.id, status='in_progress').count()
    upcoming_activities = ActivityRegistration.query.filter_by(
        elderly_id=current_user.id, status='registered'
    ).join(Activity).filter(Activity.start_time > datetime.utcnow()).count()
    
    return render_template('elderly/dashboard.html',
                         pending_orders=pending_orders,
                         in_progress_orders=in_progress_orders,
                         upcoming_activities=upcoming_activities)

@elderly.route('/mobile')
@login_required
def mobile_view():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('elderly/mobile.html')

@elderly.route('/sos', methods=['GET', 'POST'])
@login_required
def sos():
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    if request.method == 'POST':
        data = request.get_json() or {}
        longitude = data.get('longitude', type=float)
        latitude = data.get('latitude', type=float)
        address = data.get('address', '')
        
        alert = SOSAlert(
            alert_no=generate_order_no('SOS'),
            elderly_id=current_user.id,
            longitude=longitude,
            latitude=latitude,
            address=address,
            status='active'
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'SOS警报已发送，紧急联系人将收到通知',
            'alert_id': alert.id
        })
    
    return render_template('elderly/sos.html')

@elderly.route('/sos/cancel/<int:alert_id>', methods=['POST'])
@login_required
def cancel_sos(alert_id):
    alert = SOSAlert.query.get_or_404(alert_id)
    if alert.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    alert.status = 'cancelled'
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = '老人主动取消'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'SOS已取消'})

@elderly.route('/health', methods=['GET', 'POST'])
@login_required
def health():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        record_type = request.form.get('record_type')
        notes = request.form.get('notes', '')
        
        record = HealthRecord(
            elderly_id=current_user.id,
            record_type=record_type,
            notes=notes
        )
        
        if record_type == 'blood_pressure':
            record.systolic = request.form.get('systolic', type=int)
            record.diastolic = request.form.get('diastolic', type=int)
        elif record_type == 'blood_sugar':
            record.blood_sugar = request.form.get('blood_sugar', type=float)
        
        db.session.add(record)
        db.session.commit()
        flash('健康数据已记录', 'success')
        return redirect(url_for('elderly.health'))
    
    records = HealthRecord.query.filter_by(elderly_id=current_user.id).order_by(HealthRecord.recorded_at.desc()).limit(30).all()
    return render_template('elderly/health.html', records=records)

@elderly.route('/medication', methods=['GET', 'POST'])
@login_required
def medication():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        reminder = MedicationReminder(
            elderly_id=current_user.id,
            medication_name=request.form.get('medication_name'),
            dosage=request.form.get('dosage'),
            frequency=request.form.get('frequency'),
            reminder_times=request.form.get('reminder_times'),
            notes=request.form.get('notes', '')
        )
        db.session.add(reminder)
        db.session.commit()
        flash('用药提醒已添加', 'success')
        return redirect(url_for('elderly.medication'))
    
    reminders = MedicationReminder.query.filter_by(elderly_id=current_user.id, is_active=True).all()
    return render_template('elderly/medication.html', reminders=reminders)

@elderly.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        reminder = AppointmentReminder(
            elderly_id=current_user.id,
            hospital=request.form.get('hospital'),
            department=request.form.get('department'),
            doctor=request.form.get('doctor'),
            appointment_time=datetime.strptime(request.form.get('appointment_time'), '%Y-%m-%dT%H:%M'),
            notes=request.form.get('notes', '')
        )
        db.session.add(reminder)
        db.session.commit()
        flash('复诊提醒已添加', 'success')
        return redirect(url_for('elderly.appointment'))
    
    reminders = AppointmentReminder.query.filter_by(elderly_id=current_user.id, is_completed=False).order_by(AppointmentReminder.appointment_time).all()
    return render_template('elderly/appointment.html', reminders=reminders)

@elderly.route('/services')
@login_required
def services():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
    return render_template('elderly/services.html', categories=categories)

@elderly.route('/services/order/<int:category_id>', methods=['GET', 'POST'])
@login_required
def order_service(category_id):
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    category = ServiceCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        profile = current_user.elderly_profile
        
        order = ServiceOrder(
            order_no=generate_order_no(),
            elderly_id=current_user.id,
            category_id=category_id,
            service_type=category.name,
            is_free=category.is_free,
            address=request.form.get('address', profile.address if profile else ''),
            longitude=request.form.get('longitude', type=float),
            latitude=request.form.get('latitude', type=float),
            contact_phone=request.form.get('contact_phone', current_user.phone),
            scheduled_time=datetime.strptime(request.form.get('scheduled_time'), '%Y-%m-%dT%H:%M') if request.form.get('scheduled_time') else None,
            description=request.form.get('description', ''),
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        flash('服务订单已提交', 'success')
        return redirect(url_for('elderly.orders'))
    
    return render_template('elderly/order_service.html', category=category)

@elderly.route('/orders')
@login_required
def orders():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    status = request.args.get('status', '')
    query = ServiceOrder.query.filter_by(elderly_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    orders = query.order_by(ServiceOrder.created_at.desc()).all()
    return render_template('elderly/orders.html', orders=orders)

@elderly.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.elderly_id != current_user.id:
        flash('无权查看此订单', 'danger')
        return redirect(url_for('elderly.orders'))
    
    return render_template('elderly/order_detail.html', order=order)

@elderly.route('/orders/<int:order_id>/review', methods=['POST'])
@login_required
def review_order(order_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order = ServiceOrder.query.get_or_404(order_id)
    if order.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    order.rating = request.form.get('rating', type=int)
    order.review = request.form.get('review', '')
    order.reviewed_at = datetime.utcnow()
    db.session.commit()
    
    flash('评价已提交', 'success')
    return redirect(url_for('elderly.order_detail', order_id=order_id))

@elderly.route('/activities')
@login_required
def activities():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    activities = Activity.query.filter(
        Activity.status == 'published',
        Activity.is_public == True,
        Activity.end_time > datetime.utcnow()
    ).order_by(Activity.start_time).all()
    return render_template('elderly/activities.html', activities=activities)

@elderly.route('/activities/<int:activity_id>/register', methods=['POST'])
@login_required
def register_activity(activity_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    activity = Activity.query.get_or_404(activity_id)
    
    existing = ActivityRegistration.query.filter_by(activity_id=activity_id, elderly_id=current_user.id).first()
    if existing:
        flash('您已报名此活动', 'warning')
        return redirect(url_for('elderly.activities'))
    
    is_waitlist = activity.current_participants >= activity.max_participants if activity.max_participants > 0 else False
    
    registration = ActivityRegistration(
        activity_id=activity_id,
        elderly_id=current_user.id,
        is_waitlist=is_waitlist
    )
    db.session.add(registration)
    
    if not is_waitlist:
        activity.current_participants += 1
    
    db.session.commit()
    flash('报名成功' + ('，您在候补名单中' if is_waitlist else ''), 'success')
    return redirect(url_for('elderly.my_activities'))

@elderly.route('/my-activities')
@login_required
def my_activities():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    registrations = ActivityRegistration.query.filter_by(elderly_id=current_user.id).join(Activity).order_by(Activity.start_time.desc()).all()
    return render_template('elderly/my_activities.html', registrations=registrations)

@elderly.route('/news')
@login_required
def news():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    news_type = request.args.get('type', '')
    query = News.query.filter_by(is_published=True)
    if news_type:
        query = query.filter_by(news_type=news_type)
    news_list = query.order_by(News.published_at.desc()).limit(20).all()
    return render_template('elderly/news.html', news_list=news_list, current_type=news_type)

@elderly.route('/news/<int:news_id>')
@login_required
def news_detail(news_id):
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))

    news = News.query.get_or_404(news_id)
    news.view_count += 1
    db.session.commit()

    # 获取作者名称
    author_name = '未知'
    if news.author:
        author_name = news.author.real_name

    # 格式化日期
    created_at = ''
    if news.created_at:
        created_at = news.created_at.strftime('%Y-%m-%d')

    # 获取资讯类型标签
    news_type_map = {
        'news': '时事新闻',
        'health': '健康资讯',
        'anti_fraud': '防诈骗',
        'community': '社区公告'
    }
    news_type_label = news_type_map.get(news.news_type, news.news_type)

    return render_template('main/news_detail.html',
        news={
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'cover_image': news.cover_image,
            'author_name': author_name,
            'created_at': created_at,
            'news_type': news_type_label
        }
    )

@elderly.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.elderly_profile
    if not profile:
        profile = ElderlyProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    if request.method == 'POST':
        profile.birth_date = datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d') if request.form.get('birth_date') else None
        profile.gender = request.form.get('gender')
        profile.id_card = request.form.get('id_card')
        profile.address = request.form.get('address')
        profile.longitude = request.form.get('longitude', type=float)
        profile.latitude = request.form.get('latitude', type=float)
        profile.emergency_contact = request.form.get('emergency_contact')
        profile.emergency_phone = request.form.get('emergency_phone')
        profile.emergency_contact2 = request.form.get('emergency_contact2')
        profile.emergency_phone2 = request.form.get('emergency_phone2')
        profile.health_status = request.form.get('health_status')
        profile.chronic_diseases = request.form.get('chronic_diseases')
        profile.allergies = request.form.get('allergies')
        profile.is_living_alone = request.form.get('is_living_alone') == 'on'
        profile.children_info = request.form.get('children_info')
        profile.medical_history = request.form.get('medical_history')
        
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('elderly.profile'))
    
    return render_template('elderly/profile.html', profile=profile)

@elderly.route('/medication/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_medication(reminder_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    reminder = MedicationReminder.query.get_or_404(reminder_id)
    if reminder.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    reminder.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': '用药提醒已删除'})

@elderly.route('/medication/<int:reminder_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medication(reminder_id):
    if not current_user.is_elderly():
        flash('无权访问此页面', 'danger')
        return redirect(url_for('main.index'))
    
    reminder = MedicationReminder.query.get_or_404(reminder_id)
    if reminder.elderly_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('elderly.medication'))
    
    if request.method == 'POST':
        reminder.medication_name = request.form.get('medication_name')
        reminder.dosage = request.form.get('dosage')
        reminder.frequency = request.form.get('frequency')
        reminder.reminder_times = request.form.get('reminder_times')
        reminder.notes = request.form.get('notes', '')
        
        db.session.commit()
        flash('用药提醒已更新', 'success')
        return redirect(url_for('elderly.medication'))
    
    return render_template('elderly/edit_medication.html', reminder=reminder)

@elderly.route('/appointment/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete_appointment(reminder_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    reminder = AppointmentReminder.query.get_or_404(reminder_id)
    if reminder.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    reminder.is_completed = True
    db.session.commit()
    return jsonify({'success': True, 'message': '复诊提醒已标记为完成'})

@elderly.route('/appointment/<int:reminder_id>', methods=['DELETE'])
@login_required
def delete_appointment(reminder_id):
    if not current_user.is_elderly():
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    reminder = AppointmentReminder.query.get_or_404(reminder_id)
    if reminder.elderly_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'}), 403
    
    db.session.delete(reminder)
    db.session.commit()
    return jsonify({'success': True, 'message': '复诊提醒已删除'})
