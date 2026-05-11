# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Role, User, Community, ServiceCategory

def init_database():
    app = create_app('development')
    
    with app.app_context():
        print("正在创建数据库表...")
        db.create_all()
        
        print("正在初始化角色数据...")
        Role.insert_roles()
        
        print("正在创建默认社区...")
        if Community.query.count() == 0:
            community = Community(
                name='示例社区',
                address='示例街道100号',
                contact_phone='400-123-4567',
                description='这是一个示例社区',
                level=1
            )
            db.session.add(community)
            db.session.commit()
            print("默认社区创建成功")
        
        print("正在创建服务类别...")
        if ServiceCategory.query.count() == 0:
            categories = [
                {'name': '助浴服务', 'description': '专业助浴服务，安全舒适', 'is_free': False, 'sort_order': 1},
                {'name': '家政清洁', 'description': '家庭清洁打扫服务', 'is_free': False, 'sort_order': 2},
                {'name': '理发服务', 'description': '上门理发服务', 'is_free': False, 'sort_order': 3},
                {'name': '陪诊服务', 'description': '医院陪诊服务', 'is_free': False, 'sort_order': 4},
                {'name': '送餐服务', 'description': '营养餐配送服务', 'is_free': False, 'sort_order': 5},
                {'name': '孤独陪伴', 'description': '志愿者陪伴聊天服务', 'is_free': True, 'sort_order': 6},
                {'name': '代购代办', 'description': '志愿者代购代办服务', 'is_free': True, 'sort_order': 7},
            ]
            for cat in categories:
                category = ServiceCategory(**cat)
                db.session.add(category)
            db.session.commit()
            print("服务类别创建成功")
        
        print("正在创建超级管理员账号...")
        admin_role = Role.query.filter_by(name='super_admin').first()
        if admin_role and not User.query.filter_by(role_id=admin_role.id).first():
            admin = User(
                username='admin',
                real_name='系统管理员',
                phone='13800000000',
                email='admin@yinling.com',
                role_id=admin_role.id
            )
            admin.password = 'admin123'
            db.session.add(admin)
            db.session.commit()
            print("超级管理员创建成功 - 用户名: admin, 密码: admin123")
        
        print("\n数据库初始化完成！")
        print("请运行 python run.py 启动服务器")

if __name__ == '__main__':
    init_database()
