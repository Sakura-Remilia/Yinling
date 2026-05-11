# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Role, Community, News, Activity
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
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
    
    return render_template('main/index.html')

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    return render_template('main/contact.html')

@main.route('/news/<int:news_id>')
def news_detail(news_id):
    """资讯详情页"""
    from app.models import User
    news = News.query.get_or_404(news_id)

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
