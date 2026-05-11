# -*- coding: utf-8 -*-
from flask import Flask, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    from config import config
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # 提供 uploads 文件夹的访问
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.isabs(upload_folder):
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), upload_folder)
        return send_from_directory(upload_folder, filename)

    @app.before_request
    def log_request():
        print(f"[REQUEST] {request.method} {request.path}")
    
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.elderly import elderly as elderly_blueprint
    app.register_blueprint(elderly_blueprint, url_prefix='/elderly')
    
    from app.volunteer import volunteer as volunteer_blueprint
    app.register_blueprint(volunteer_blueprint, url_prefix='/volunteer')
    
    from app.worker import worker as worker_blueprint
    app.register_blueprint(worker_blueprint, url_prefix='/worker')
    
    from app.community_admin import community_admin as ca_blueprint
    app.register_blueprint(ca_blueprint, url_prefix='/community_admin')
    
    from app.super_admin import super_admin as sa_blueprint
    app.register_blueprint(sa_blueprint, url_prefix='/super_admin')
    
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from app.api_v1 import api_v1 as api_v1_blueprint
    app.register_blueprint(api_v1_blueprint)
    
    with app.app_context():
        db.create_all()
        # 自动检查并添加缺失的数据库列
        _check_and_update_db()

    return app


def _check_and_update_db():
    """检查并添加缺失的数据库列"""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)

    # 定义各表需要的新列
    tables_columns = {
        'health_records': {
            'heart_rate': 'INTEGER',
            'temperature': 'FLOAT',
            'height': 'FLOAT',
            'weight': 'FLOAT',
            'vision_left': 'VARCHAR(10)',
            'vision_right': 'VARCHAR(10)',
            'hearing': 'VARCHAR(50)',
            'blood_type': 'VARCHAR(10)',
            'record_date': 'DATE',
            'exam_summary': 'TEXT',
            'creator_id': 'INTEGER'
        },
        'service_orders': {
            'community_id': 'INTEGER',
            'check_in_time': 'DATETIME',
            'check_out_time': 'DATETIME',
            'price': 'FLOAT',
            'completion_notes': 'TEXT'
        },
        'sos_alerts': {
            'community_id': 'INTEGER'
        },
        'news': {
            'community_id': 'INTEGER'
        }
    }

    for table_name, columns in tables_columns.items():
        try:
            existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        except Exception:
            print(f"[DB] ⚠️ 表 {table_name} 不存在，跳过")
            continue

        for column_name, column_type in columns.items():
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                    db.session.execute(text(sql))
                    db.session.commit()
                    print(f"[DB] ✅ 已添加列: {table_name}.{column_name}")
                except Exception as e:
                    print(f"[DB] ⚠️ 添加列 {table_name}.{column_name} 时出错: {e}")
