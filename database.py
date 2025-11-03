# database.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Create db instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database and create tables + uploads folder."""
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()


# === MODELS ===
class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(50))
    row_count = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    sims = db.relationship('SimData', backref='file', lazy=True, cascade='all, delete-orphan')


class SimData(db.Model):
    __tablename__ = 'sim_data'
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(100), index=True)
    iccid = db.Column(db.String(100), index=True)
    msisdn = db.Column(db.String(100), index=True)
    imsi = db.Column(db.String(100), index=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('sn', 'file_id', name='uix_sn_file'),
        db.UniqueConstraint('iccid', 'file_id', name='uix_iccid_file'),
    )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# database.py
class SearchLog(db.Model):
    __tablename__ = 'search_logs'
    id = db.Column(db.Integer, primary_key=True)
    input_value = db.Column(db.Text, nullable=False)
    file_source = db.Column(db.String(255))
    matched_column = db.Column(db.String(50))
    matched_value = db.Column(db.String(255))
    sn = db.Column(db.String(255))
    msisdn = db.Column(db.String(255))
    iccid = db.Column(db.String(255))
    imsi = db.Column(db.String(255))
    status = db.Column(db.Boolean, default=False)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NEW: Link to actual SimData row
    matched_sim_id = db.Column(db.Integer, db.ForeignKey('sim_data.id'), nullable=True)
    matched_sim = db.relationship('SimData', backref='search_logs')