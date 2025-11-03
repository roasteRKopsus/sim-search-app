from flask import Blueprint, render_template, request, send_from_directory, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db, UploadedFile, SimData, SearchLog
from config import Config
import os
import csv
from io import StringIO

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    total_files = UploadedFile.query.count()
    total_records = SimData.query.count()
    total_searches = SearchLog.query.count()
    recent = SearchLog.query.order_by(SearchLog.searched_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           total_files=total_files,
                           total_records=total_records,
                           total_searches=total_searches,
                           recent=recent)

@admin_bp.route('/files')
@login_required
def admin_files():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    files = UploadedFile.query.order_by(UploadedFile.uploaded_at.desc()).all()
    return render_template('admin/files.html', files=files)

@admin_bp.route('/files/delete/<int:file_id>')
@login_required
def delete_file(file_id):
    if not current_user.is_admin():
        return redirect(url_for('index'))
    file = UploadedFile.query.get_or_404(file_id)
    # Delete from DB
    SimData.query.filter_by(file_id=file_id).delete()
    db.session.delete(file)
    db.session.commit()
    # Delete physical file
    filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    flash(f"File {file.filename} deleted", 'success')
    return redirect(url_for('admin.admin_files'))

@admin_bp.route('/logs')
@login_required
def admin_logs():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    logs = SearchLog.query.order_by(SearchLog.searched_at.desc()).paginate(
        page=page, per_page=50)
    return render_template('admin/logs.html', logs=logs)

@admin_bp.route('/logs/export')
@login_required
def export_logs():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Input', 'File', 'Match Col', 'Match Val', 'SN', 'MSISDN', 'ICCID', 'IMSI', 'Status', 'Time'])
    for log in SearchLog.query.order_by(SearchLog.searched_at.desc()).all():
        writer.writerow([
            log.id, log.input_value, log.file_source or '',
            log.matched_column or '', log.matched_value or '',
            log.sn or '', log.msisdn or '', log.iccid or '', log.imsi or '',
            'TRUE' if log.status else 'FALSE',
            log.searched_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=logs_{timestamp}.csv'
    }