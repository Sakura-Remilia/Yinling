# -*- coding: utf-8 -*-
from flask import request, jsonify
from app.api_v1 import api_v1
from app.models import User, ElderlyProfile, HealthRecord, MedicationReminder, AppointmentReminder, db
from app.auth.jwt_auth import jwt_required, role_required
from datetime import datetime

@api_v1.route('/elderly/profile', methods=['GET'])
@jwt_required
def get_elderly_profile():
    """获取老人档案"""
    user = request.current_user

    profile = ElderlyProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        # 如果没有档案，返回用户基本信息
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.id,
                'real_name': user.real_name,
                'phone': user.phone,
                'birth_date': None,
                'gender': None,
                'emergency_contact': None,
                'emergency_phone': None,
                'health_status': None,
                'chronic_diseases': None,
                'is_living_alone': None
            }
        })

    return jsonify({
        'success': True,
        'data': {
            'user_id': user.id,
            'real_name': user.real_name,
            'phone': user.phone,
            'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
            'gender': profile.gender,
            'emergency_contact': profile.emergency_contact,
            'emergency_phone': profile.emergency_phone,
            'health_status': profile.health_status,
            'chronic_diseases': profile.chronic_diseases,
            'is_living_alone': profile.is_living_alone
        }
    })

@api_v1.route('/elderly/profile', methods=['PUT'])
@jwt_required
def update_elderly_profile():
    """更新老人档案"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    profile = ElderlyProfile.query.filter_by(user_id=user.id).first()

    if not profile:
        profile = ElderlyProfile(user_id=user.id)
        db.session.add(profile)

    # 更新字段
    if 'birth_date' in data:
        profile.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data['birth_date'] else None
    if 'gender' in data:
        profile.gender = data['gender']
    if 'emergency_contact' in data:
        profile.emergency_contact = data['emergency_contact']
    if 'emergency_phone' in data:
        profile.emergency_phone = data['emergency_phone']
    if 'health_status' in data:
        profile.health_status = data['health_status']
    if 'chronic_diseases' in data:
        profile.chronic_diseases = data['chronic_diseases']
    if 'is_living_alone' in data:
        profile.is_living_alone = data['is_living_alone']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '档案更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/elderly/health-records', methods=['GET'])
@jwt_required
def get_health_records():
    """获取健康记录列表"""
    user = request.current_user
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    record_type = request.args.get('type', None)

    query = HealthRecord.query.filter_by(elderly_id=user.id)

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
            'blood_pressure_systolic': r.systolic,
            'blood_pressure_diastolic': r.diastolic,
            'blood_sugar': r.blood_sugar,
            'heart_rate': r.heart_rate,
            'temperature': r.temperature,
            'notes': r.notes,
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
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

@api_v1.route('/elderly/health-records', methods=['POST'])
@jwt_required
def create_health_record():
    """添加健康记录"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    record_type = data.get('record_type', 'blood_pressure')

    record = HealthRecord(
        elderly_id=user.id,
        creator_id=user.id,  # 老人自己录入
        record_type=record_type,
        record_date=datetime.strptime(data.get('record_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date() if data.get('record_date') else datetime.now().date(),
        systolic=data.get('systolic'),
        diastolic=data.get('diastolic'),
        blood_sugar=data.get('blood_sugar'),
        heart_rate=data.get('heart_rate'),
        temperature=data.get('temperature'),
        notes=data.get('notes')
    )

    try:
        db.session.add(record)
        db.session.commit()
        return jsonify({'success': True, 'message': '健康记录添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@api_v1.route('/elderly/medication-reminders', methods=['GET'])
@jwt_required
def get_medication_reminders():
    """获取用药提醒列表"""
    user = request.current_user

    reminders = MedicationReminder.query.filter_by(elderly_id=user.id).order_by(
        MedicationReminder.created_at.desc()
    ).all()

    data = []
    for r in reminders:
        data.append({
            'id': r.id,
            'medication_name': r.medication_name,
            'dosage': r.dosage,
            'frequency': r.frequency,
            'reminder_times': r.reminder_times,
            'is_active': r.is_active,
            'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
        })

    return jsonify({'success': True, 'data': data})

@api_v1.route('/elderly/medication-reminders', methods=['POST'])
@jwt_required
def create_medication_reminder():
    """添加用药提醒"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    medication_name = data.get('medication_name', '').strip()
    if not medication_name:
        return jsonify({'success': False, 'message': '药品名称不能为空'}), 400

    reminder = MedicationReminder(
        elderly_id=user.id,
        medication_name=medication_name,
        dosage=data.get('dosage', ''),
        frequency=data.get('frequency', 'daily'),
        reminder_times=data.get('reminder_times', ''),
        is_active=True
    )

    try:
        db.session.add(reminder)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '用药提醒添加成功',
            'data': {'id': reminder.id}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@api_v1.route('/elderly/medication-reminders/<int:reminder_id>', methods=['PUT'])
@jwt_required
def update_medication_reminder(reminder_id):
    """更新用药提醒"""
    user = request.current_user
    reminder = MedicationReminder.query.filter_by(id=reminder_id, elderly_id=user.id).first_or_404()
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    if 'medication_name' in data:
        reminder.medication_name = data['medication_name']
    if 'dosage' in data:
        reminder.dosage = data['dosage']
    if 'frequency' in data:
        reminder.frequency = data['frequency']
    if 'reminder_times' in data:
        reminder.reminder_times = data['reminder_times']
    if 'is_active' in data:
        reminder.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/elderly/medication-reminders/<int:reminder_id>', methods=['DELETE'])
@jwt_required
def delete_medication_reminder(reminder_id):
    """删除用药提醒"""
    user = request.current_user
    reminder = MedicationReminder.query.filter_by(id=reminder_id, elderly_id=user.id).first_or_404()

    try:
        db.session.delete(reminder)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/elderly/appointments', methods=['GET'])
@jwt_required
def get_appointments():
    """获取复诊提醒列表"""
    user = request.current_user

    appointments = AppointmentReminder.query.filter_by(elderly_id=user.id).order_by(
        AppointmentReminder.appointment_time.asc()
    ).all()

    data = []
    for a in appointments:
        data.append({
            'id': a.id,
            'hospital': a.hospital,
            'department': a.department,
            'doctor': a.doctor,
            'appointment_time': a.appointment_time.isoformat() if a.appointment_time else None,
            'notes': a.notes,
            'is_completed': a.is_completed,
            'created_at': a.created_at.isoformat() if hasattr(a, 'created_at') else None
        })

    return jsonify({'success': True, 'data': data})

@api_v1.route('/elderly/appointments', methods=['POST'])
@jwt_required
def create_appointment():
    """添加复诊提醒"""
    user = request.current_user
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    appointment_time = data.get('appointment_time')
    if not appointment_time:
        return jsonify({'success': False, 'message': '预约时间不能为空'}), 400

    appointment = AppointmentReminder(
        elderly_id=user.id,
        hospital=data.get('hospital', ''),
        department=data.get('department', ''),
        doctor=data.get('doctor', ''),
        appointment_time=datetime.strptime(appointment_time, '%Y-%m-%d %H:%M'),
        notes=data.get('notes', ''),
        is_completed=False
    )

    try:
        db.session.add(appointment)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '复诊提醒添加成功',
            'data': {'id': appointment.id}
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}), 500

@api_v1.route('/elderly/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required
def update_appointment(appointment_id):
    """更新复诊提醒"""
    user = request.current_user
    appointment = AppointmentReminder.query.filter_by(id=appointment_id, elderly_id=user.id).first_or_404()
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': '请求数据无效'}), 400

    if 'hospital' in data:
        appointment.hospital = data['hospital']
    if 'department' in data:
        appointment.department = data['department']
    if 'doctor' in data:
        appointment.doctor = data['doctor']
    if 'appointment_time' in data:
        appointment.appointment_time = datetime.strptime(data['appointment_time'], '%Y-%m-%d %H:%M')
    if 'notes' in data:
        appointment.notes = data['notes']
    if 'is_completed' in data:
        appointment.is_completed = data['is_completed']

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

@api_v1.route('/elderly/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required
def delete_appointment(appointment_id):
    """删除复诊提醒"""
    user = request.current_user
    appointment = AppointmentReminder.query.filter_by(id=appointment_id, elderly_id=user.id).first_or_404()

    try:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@api_v1.route('/elderly/appointments/<int:appointment_id>/complete', methods=['POST'])
@jwt_required
def complete_appointment(appointment_id):
    """标记复诊完成"""
    user = request.current_user
    appointment = AppointmentReminder.query.filter_by(id=appointment_id, elderly_id=user.id).first_or_404()

    appointment.is_completed = True

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': '已标记为完成'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500