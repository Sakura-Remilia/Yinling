# -*- coding: utf-8 -*-
import os
import uuid
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.api_v1 import api_v1
from app.auth.jwt_auth import jwt_required, role_required

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_v1.route('/upload/image', methods=['POST'])
@jwt_required
@role_required('super_admin', 'community_admin')
def upload_image():
    """上传图片（用于公告、资讯等封面图）"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '不支持的文件类型'}), 400

    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    # 确保上传目录存在
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.isabs(upload_folder):
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), upload_folder)

    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    # 返回访问URL
    file_url = f"/uploads/{filename}"

    return jsonify({
        'success': True,
        'message': '上传成功',
        'data': {
            'url': file_url,
            'filename': filename
        }
    })
