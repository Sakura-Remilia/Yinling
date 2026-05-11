# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import User, Role, ElderlyProfile, VolunteerProfile, WorkerProfile, CommunityAdminProfile
from datetime import datetime
import random
import string

auth = Blueprint('auth', __name__)

def generate_order_no(prefix='U'):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'{prefix}{timestamp}{random_str}'

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_to_dashboard()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            if not user.is_active:
                flash('账号已被禁用，请联系管理员', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'欢迎回来，{user.real_name}！', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect_to_dashboard()
        else:
            flash('用户名或密码错误', 'danger')
    
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_to_dashboard()
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        real_name = request.form.get('real_name')
        phone = request.form.get('phone')
        email = request.form.get('email', '')
        role_name = 'elderly'
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(phone=phone).first():
            flash('手机号已被注册', 'danger')
            return redirect(url_for('auth.register'))
        
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            flash('角色不存在', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            real_name=real_name,
            phone=phone,
            email=email,
            role_id=role.id
        )
        user.password = password
        db.session.add(user)
        db.session.flush()
        
        if role_name == 'elderly':
            profile = ElderlyProfile(user_id=user.id)
            db.session.add(profile)
        elif role_name == 'volunteer':
            profile = VolunteerProfile(user_id=user.id)
            db.session.add(profile)
        elif role_name == 'worker':
            profile = WorkerProfile(user_id=user.id)
            db.session.add(profile)
        
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    roles = Role.query.filter(Role.name != 'super_admin').all()
    return render_template('auth/register.html', roles=roles)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.real_name = request.form.get('real_name', current_user.real_name)
        current_user.email = request.form.get('email', current_user.email)
        
        new_password = request.form.get('new_password')
        if new_password:
            old_password = request.form.get('old_password')
            if not current_user.verify_password(old_password):
                flash('原密码错误', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.password = new_password
        
        db.session.commit()
        flash('个人信息已更新', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

def redirect_to_dashboard():
    if current_user.is_super_admin():
        return redirect(url_for('super_admin.dashboard'))
    elif current_user.is_community_admin():
        return redirect(url_for('community_admin.dashboard'))
    elif current_user.is_worker():
        return redirect(url_for('worker.dashboard'))
    elif current_user.is_volunteer():
        return redirect(url_for('volunteer.dashboard'))
    elif current_user.is_elderly():
        return redirect(url_for('elderly.dashboard'))
    return redirect(url_for('main.index'))
