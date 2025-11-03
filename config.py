# config.py
import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Config:
    SECRET_KEY = 'your-super-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://postgres:admin@localhost/simsearch_db'  # <-- CHANGED
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB
    # engine = 
    # SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # Admin credentials
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    