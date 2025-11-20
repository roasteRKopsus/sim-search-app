
from flask import render_template, request, send_from_directory, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import app
from database import db, UploadedFile, SimData, SearchLog
from utils import extract_longest_number, map_columns  # ← FIXED
import pandas as pd
import os
from datetime import datetime
import csv
from io import StringIO

from flask import Response
import csv
from io import StringIO

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    val = 1
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        provider = request.form.get('provider', 'Unknown').strip()  # Get from form
        if not provider:
            flash('Provider required', 'danger')
            return redirect(request.url)
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                df = pd.read_excel(filepath)
                mapped = map_columns(df)

                required = ['sn', 'iccid', 'msisdn']
                if not all(k in mapped for k in required):
                    flash(f"Missing columns. Found: {list(mapped.keys())}", 'danger')
                    os.remove(filepath)
                    return redirect(request.url)

                upload_record = UploadedFile(
                    filename=filename,
                    provider=provider,  # Use user input
                    row_count=0
                )
                db.session.add(upload_record)
                db.session.flush()

                inserted = 0
                for _, row in df.iterrows():
                    sn = str(row[mapped['sn']]).strip() if pd.notna(row[mapped['sn']]) else None
                    iccid = str(row[mapped['iccid']]).strip() if pd.notna(row[mapped['iccid']]) else None
                    msisdn = str(row[mapped['msisdn']]).strip() if pd.notna(row[mapped['msisdn']]) else None
                    imsi = str(row[mapped['imsi']]).strip() if 'imsi' in mapped and pd.notna(row[mapped['imsi']]) else None

                    if not sn and not iccid:
                        continue

                    exists = SimData.query.filter(
                        SimData.file_id == upload_record.id,
                        db.or_(SimData.sn == sn, SimData.iccid == iccid)
                    ).first()

                    if not exists:
                        sim = SimData(sn=sn, iccid=iccid, msisdn=msisdn, imsi=imsi, file_id=upload_record.id)
                        db.session.add(sim)
                        inserted += 1

                upload_record.row_count = inserted
                db.session.commit()
                flash(f"Success: {inserted} unique rows uploaded from {filename} (Provider: {provider})", 'success')
            except Exception as e:
                db.session.rollback()
                flash(f"Error: {str(e)}", 'danger')
                if os.path.exists(filepath):
                    os.remove(filepath)
            return redirect(url_for('upload'))
    return render_template('upload.html')




@app.route('/search', methods=['POST'])
@login_required
def search():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    input_val = request.form['query'].strip()
    number = extract_longest_number(input_val)  # ← NOW RETURNS LIST
    print("Extracted numbers:", number)

    if not number:
        flash("No valid number found in input", 'danger')
        return redirect(url_for('index'))

    results = []
    matched = False

    # session = SessionLocal()
    print(number)
    queries = [
        SimData.sn.ilike(number),
        SimData.iccid.ilike(number),
        SimData.msisdn.ilike(number),
        SimData.imsi.ilike(number)
    ]

    for q in queries:
        matches = SimData.query.filter(q).all()
        for m in matches:
            matched = True
            log = SearchLog(
                input_value=input_val,
                file_source=m.file.filename,
                status=True,
                sn=m.sn, msisdn=m.msisdn, iccid=m.iccid, imsi=m.imsi,
                searched_at=datetime.utcnow()
            )

            log = SearchLog(
            input_value=input_val,
            file_source=m.file.filename,
            status=True,
            sn=m.sn, msisdn=m.msisdn, iccid=m.iccid, imsi=m.imsi,
            matched_sim_id=m.id,  # ← LINK TO REAL SIM
            searched_at=datetime.utcnow())
   #find and match
            if m.sn and number in m.sn:
                log.matched_column, log.matched_value = 'SN', m.sn
            elif m.iccid and number in m.iccid:
                log.matched_column, log.matched_value = 'ICCID', m.iccid
            elif m.msisdn and number in m.msisdn:
                log.matched_column, log.matched_value = 'MSISDN', m.msisdn
            else:
                log.matched_column, log.matched_value = 'IMSI', m.imsi

            db.session.add(log)
            results.append(log)
            

    if not matched:
        log = SearchLog(input_value=input_val, status=False, searched_at=datetime.utcnow())
        db.session.add(log)
        results.append(log)

    db.session.commit()

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'input_value', 'file_source', 'matched_column', 'matched_value',
        'sn', 'msisdn', 'iccid', 'imsi', 'status', 'datetime'
    ])
    for r in results:
        writer.writerow([
            r.input_value, r.file_source or '',
            r.matched_column or '', r.matched_value or '',
            r.sn or '', r.msisdn or '', r.iccid or '', r.imsi or '',
            'TRUE' if r.status else 'FALSE',
            r.searched_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"result_{timestamp}.csv"

    return jsonify({
        'csv': output.getvalue(),
        'filename': filename,
        'matches': len([r for r in results if r.status])
    })





from sqlalchemy import select, func

@app.route('/data')
@login_required
def data_view():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')

    # Subquery: SIMs that were ACTUALLY matched
    matched_subq = db.session.query(SearchLog.matched_sim_id).filter(
        SearchLog.status == True,
        SearchLog.matched_sim_id.is_not(None)
    ).subquery()

    query = db.session.query(
        SimData,
        SimData.id.in_(matched_subq).label('checked')
    ).join(UploadedFile)

    if date_filter:
        try:
            fdate = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(func.date(UploadedFile.uploaded_at) == fdate.date())
        except:
            pass

    if status_filter == 'checked':
        query = query.filter(SimData.id.in_(matched_subq))
    elif status_filter == 'unchecked':
        query = query.filter(~SimData.id.in_(matched_subq))

    pagination = query.order_by(UploadedFile.uploaded_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )

    return render_template(
        'data.html',
        sims=pagination.items,
        pagination=pagination,
        date_filter=date_filter,
        status_filter=status_filter
    )
@app.route('/data/download')

def download_data():
    if not current_user.is_admin():
        return redirect(url_for('index'))
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')

    # Subquery: matched SIMs
    matched_subq = db.session.query(SearchLog.matched_sim_id).filter(
        SearchLog.status == True,
        SearchLog.matched_sim_id.is_not(None)
    ).subquery()

    # Base query
    query = db.session.query(
        SimData.sn,
        SimData.msisdn,
        SimData.iccid,
        SimData.imsi,
        UploadedFile.provider,
        UploadedFile.filename,
        UploadedFile.uploaded_at,
        SimData.id.in_(matched_subq).label('checked')
    ).join(UploadedFile)

    # Filters
    if date_filter:
        try:
            fdate = datetime.strptime(date_filter, '%Y-%m-%d')
            query = query.filter(func.date(UploadedFile.uploaded_at) == fdate.date())
        except:
            pass

    if status_filter == 'checked':
        query = query.filter(SimData.id.in_(matched_subq))
    elif status_filter == 'unchecked':
        query = query.filter(~SimData.id.in_(matched_subq))

    results = query.order_by(UploadedFile.uploaded_at.desc()).all()

    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['SN', 'MSISDN', 'ICCID', 'IMSI', 'Provider', 'File', 'Uploaded', 'Status'])

    for row in results:
        status = 'Checked' if row.checked else '—'
        writer.writerow([
            row.sn or '',
            row.msisdn or '',
            row.iccid or '',
            row.imsi or '',
            row.provider or '',
            row.filename,
            row.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            status
        ])

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"sim_data_{timestamp}.csv"

    # RETURN VALID RESPONSE
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment;filename={filename}',
            'Cache-Control': 'no-cache'
        }
    )





@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)