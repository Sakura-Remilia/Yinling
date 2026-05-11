# -*- coding: utf-8 -*-
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Text)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    @staticmethod
    def insert_roles():
        roles = {
            'elderly': '老人',
            'volunteer': '志愿者',
            'worker': '工作人员',
            'community_admin': '社区管理员',
            'super_admin': '后台管理员'
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, description=roles[r])
                db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120))
    avatar = db.Column(db.String(255), default='default_avatar.svg')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_elderly(self):
        return self.role and self.role.name == 'elderly'
    
    def is_volunteer(self):
        return self.role and self.role.name == 'volunteer'
    
    def is_worker(self):
        return self.role and self.role.name == 'worker'
    
    def is_community_admin(self):
        return self.role and self.role.name == 'community_admin'
    
    def is_super_admin(self):
        return self.role and self.role.name == 'super_admin'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Community(db.Model):
    __tablename__ = 'communities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    contact_phone = db.Column(db.String(20))
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    level = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='community', lazy='dynamic')
    children = db.relationship('Community', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class ElderlyProfile(db.Model):
    __tablename__ = 'elderly_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    id_card = db.Column(db.String(18))
    address = db.Column(db.String(255))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    emergency_contact = db.Column(db.String(64))
    emergency_phone = db.Column(db.String(20))
    emergency_contact2 = db.Column(db.String(64))
    emergency_phone2 = db.Column(db.String(20))
    health_status = db.Column(db.Text)
    chronic_diseases = db.Column(db.Text)
    allergies = db.Column(db.Text)
    is_living_alone = db.Column(db.Boolean, default=False)
    children_info = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('elderly_profile', uselist=False))

class VolunteerProfile(db.Model):
    __tablename__ = 'volunteer_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    id_card = db.Column(db.String(18))
    address = db.Column(db.String(255))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    skills = db.Column(db.Text)
    service_areas = db.Column(db.Text)
    total_service_hours = db.Column(db.Float, default=0.0)
    total_points = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('volunteer_profile', uselist=False))

class WorkerProfile(db.Model):
    __tablename__ = 'worker_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.String(10))
    id_card = db.Column(db.String(18))
    address = db.Column(db.String(255))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    skills = db.Column(db.Text)
    service_areas = db.Column(db.Text)
    work_type = db.Column(db.String(50))
    is_trained = db.Column(db.Boolean, default=False)
    trained_at = db.Column(db.DateTime)
    training_certificate = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    verified_at = db.Column(db.DateTime)
    bio = db.Column(db.Text)
    total_orders = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('worker_profile', uselist=False))

class CommunityAdminProfile(db.Model):
    __tablename__ = 'community_admin_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    position = db.Column(db.String(50))
    department = db.Column(db.String(100))
    managed_community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('community_admin_profile', uselist=False))
    managed_community = db.relationship('Community', backref='admins')

class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_range = db.Column(db.String(100))
    is_free = db.Column(db.Boolean, default=False)
    icon = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    services = db.relationship('ServiceOrder', backref='category', lazy='dynamic')

class ServiceOrder(db.Model):
    __tablename__ = 'service_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))  # 新增
    service_type = db.Column(db.String(50), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=False)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    contact_phone = db.Column(db.String(20))
    scheduled_time = db.Column(db.DateTime)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    provider_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    provider_type = db.Column(db.String(20))
    accepted_at = db.Column(db.DateTime)
    arrived_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    check_in_time = db.Column(db.DateTime)  # 新增
    check_out_time = db.Column(db.DateTime)  # 新增
    price = db.Column(db.Float)  # 新增
    completion_notes = db.Column(db.Text)  # 新增
    service_photos = db.Column(db.Text)
    service_notes = db.Column(db.Text)
    rating = db.Column(db.Integer)
    review = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)
    cancel_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='service_orders')
    provider = db.relationship('User', foreign_keys=[provider_id], backref='provided_orders')
    canceller = db.relationship('User', foreign_keys=[cancelled_by])
    community = db.relationship('Community', backref='service_orders')

class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_no = db.Column(db.String(32), unique=True, nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))  # 新增
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    address = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')
    triggered_at = db.Column(db.DateTime, default=datetime.utcnow)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    responded_at = db.Column(db.DateTime)
    arrived_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)
    resolution_photos = db.Column(db.Text)
    is_escalated = db.Column(db.Boolean, default=False)
    escalated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='sos_alerts')
    responder = db.relationship('User', foreign_keys=[responder_id], backref='responded_alerts')
    community = db.relationship('Community', backref='sos_alerts')

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)  # blood_pressure, blood_sugar, physical_exam, visit_check
    systolic = db.Column(db.Integer)      # 收缩压
    diastolic = db.Column(db.Integer)      # 舒张压
    blood_sugar = db.Column(db.Float)     # 血糖
    heart_rate = db.Column(db.Integer)     # 心率
    temperature = db.Column(db.Float)      # 体温
    height = db.Column(db.Float)          # 身高(cm)
    weight = db.Column(db.Float)          # 体重(kg)
    vision_left = db.Column(db.String(10)) # 左眼视力
    vision_right = db.Column(db.String(10)) # 右眼视力
    hearing = db.Column(db.String(50))     # 听力状况
    blood_type = db.Column(db.String(10))  # 血型
    record_date = db.Column(db.Date)      # 记录日期（用于排序）
    exam_summary = db.Column(db.Text)     # 体检小结
    notes = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 记录创建者
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='health_records')
    creator = db.relationship('User', foreign_keys=[creator_id])

class MedicationReminder(db.Model):
    __tablename__ = 'medication_reminders'
    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    reminder_times = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    elderly = db.relationship('User', backref='medication_reminders')

class AppointmentReminder(db.Model):
    __tablename__ = 'appointment_reminders'
    id = db.Column(db.Integer, primary_key=True)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    doctor = db.Column(db.String(50))
    appointment_time = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    elderly = db.relationship('User', backref='appointment_reminders')

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))
    activity_type = db.Column(db.String(50))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    max_participants = db.Column(db.Integer, default=0)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft')
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    organizer = db.relationship('User', backref='organized_activities')
    community = db.relationship('Community', backref='activities')
    registrations = db.relationship('ActivityRegistration', backref='activity', lazy='dynamic')

class ActivityRegistration(db.Model):
    __tablename__ = 'activity_registrations'
    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')
    is_waitlist = db.Column(db.Boolean, default=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)
    attended_at = db.Column(db.DateTime)
    elderly = db.relationship('User', backref='activity_registrations')

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255))
    news_type = db.Column(db.String(50), default='news')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author = db.relationship('User', backref='authored_news')
    community = db.relationship('Community', backref='news')

class VolunteerServiceRecord(db.Model):
    __tablename__ = 'volunteer_service_records'
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('service_orders.id'))
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_type = db.Column(db.String(50))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=0)
    check_in_longitude = db.Column(db.Float)
    check_in_latitude = db.Column(db.Float)
    check_out_longitude = db.Column(db.Float)
    check_out_latitude = db.Column(db.Float)
    service_photos = db.Column(db.Text)
    service_notes = db.Column(db.Text)
    points_earned = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    volunteer = db.relationship('User', foreign_keys=[volunteer_id], backref='volunteer_records')
    elderly = db.relationship('User', foreign_keys=[elderly_id])
    order = db.relationship('ServiceOrder', backref='volunteer_record')

class PointTransaction(db.Model):
    __tablename__ = 'point_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(255))
    related_record_id = db.Column(db.Integer)
    related_record_type = db.Column(db.String(50))
    balance_after = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='point_transactions')

class VisitRecord(db.Model):
    __tablename__ = 'visit_records'
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visit_type = db.Column(db.String(50))
    scheduled_time = db.Column(db.DateTime)
    actual_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    health_status = db.Column(db.Text)
    needs = db.Column(db.Text)
    notes = db.Column(db.Text)
    photos = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visitor = db.relationship('User', foreign_keys=[visitor_id], backref='visit_records_as_visitor')
    elderly = db.relationship('User', foreign_keys=[elderly_id], backref='visit_records_as_elderly')

class FollowUpRecord(db.Model):
    __tablename__ = 'follow_up_records'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('service_orders.id'))
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    elderly_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    follow_up_type = db.Column(db.String(50))
    follow_up_time = db.Column(db.DateTime, default=datetime.utcnow)
    satisfaction_level = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    issues_found = db.Column(db.Text)
    resolution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id], backref='follow_up_records')
    elderly = db.relationship('User', foreign_keys=[elderly_id])
    order = db.relationship('ServiceOrder', backref='follow_ups')

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50))
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    request_url = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    request_data = db.Column(db.Text)
    response_status = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='system_logs')

class AlertRule(db.Model):
    __tablename__ = 'alert_rules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rule_type = db.Column(db.String(50), nullable=False)
    threshold = db.Column(db.Integer)
    time_window_hours = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    notify_roles = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AlertNotification(db.Model):
    __tablename__ = 'alert_notifications'
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rule = db.relationship('AlertRule', backref='notifications')
    user = db.relationship('User', backref='alert_notifications')

class PointProduct(db.Model):
    __tablename__ = 'point_products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    points_required = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PointExchange(db.Model):
    __tablename__ = 'point_exchanges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('point_products.id'))
    points_used = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')
    exchange_time = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    user = db.relationship('User', backref='point_exchanges')
    product = db.relationship('PointProduct', backref='exchanges')

class CommunityAnnouncement(db.Model):
    """社区公告"""
    __tablename__ = 'community_announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(255))
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_pinned = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    community = db.relationship('Community', backref='announcements')
    publisher = db.relationship('User', backref='published_announcements')
