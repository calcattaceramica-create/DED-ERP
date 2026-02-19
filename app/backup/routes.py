from flask import render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from app.backup import bp
from app.auth.decorators import permission_required
from app import db
import os
import shutil
import sqlite3
from datetime import datetime
import zipfile
import json

@bp.route('/')
@login_required
@permission_required('settings.manage')
def index():
    """Backup management page"""
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Get list of existing backups
    backups = []
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                file_stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                    'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                    'path': filepath
                })
    
    # Sort by creation date (newest first)
    backups.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Get backup settings
    settings = get_backup_settings()
    
    return render_template('backup/index.html', backups=backups, settings=settings)

@bp.route('/create', methods=['POST'])
@login_required
@permission_required('settings.manage')
def create_backup():
    """Create a new backup"""
    try:
        basedir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        backup_dir = os.path.join(basedir, 'backups')
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Create zip file
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup database
            db_path = os.path.join(basedir, 'erp_system.db')
            if os.path.exists(db_path):
                zipf.write(db_path, 'erp_system.db')
            
            # Backup uploads folder
            uploads_dir = os.path.join(basedir, 'uploads')
            if os.path.exists(uploads_dir):
                for root, dirs, files in os.walk(uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, basedir)
                        zipf.write(file_path, arcname)
            
            # Backup config file
            config_path = os.path.join(basedir, 'config.py')
            if os.path.exists(config_path):
                zipf.write(config_path, 'config.py')
            
            # Create backup info file
            backup_info = {
                'created_at': datetime.now().isoformat(),
                'created_by': current_user.username,
                'database': 'erp_system.db',
                'version': '1.0'
            }
            zipf.writestr('backup_info.json', json.dumps(backup_info, indent=2, ensure_ascii=False))
        
        flash(f'✅ تم إنشاء النسخة الاحتياطية بنجاح: {backup_filename}', 'success')
        
    except Exception as e:
        flash(f'❌ حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

@bp.route('/download/<filename>')
@login_required
@permission_required('settings.manage')
def download_backup(filename):
    """Download a backup file"""
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
        backup_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_path):
            flash('❌ الملف غير موجود', 'danger')
            return redirect(url_for('backup.index'))
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f'❌ حدث خطأ أثناء تحميل النسخة الاحتياطية: {str(e)}', 'danger')
        return redirect(url_for('backup.index'))

@bp.route('/delete/<filename>', methods=['POST'])
@login_required
@permission_required('settings.manage')
def delete_backup(filename):
    """Delete a backup file"""
    try:
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backups')
        backup_path = os.path.join(backup_dir, filename)
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
            flash(f'✅ تم حذف النسخة الاحتياطية: {filename}', 'success')
        else:
            flash('❌ الملف غير موجود', 'danger')
            
    except Exception as e:
        flash(f'❌ حدث خطأ أثناء حذف النسخة الاحتياطية: {str(e)}', 'danger')
    
    return redirect(url_for('backup.index'))

def get_backup_settings():
    """Get backup settings from database or return defaults"""
    from app.models_settings import SystemSettings
    
    auto_backup = SystemSettings.query.filter_by(setting_key='auto_backup_enabled').first()
    backup_frequency = SystemSettings.query.filter_by(setting_key='backup_frequency').first()
    
    return {
        'auto_backup_enabled': auto_backup.setting_value == 'true' if auto_backup else False,
        'backup_frequency': backup_frequency.setting_value if backup_frequency else 'daily'
    }

