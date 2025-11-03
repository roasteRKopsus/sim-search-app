# app.py
from flask import Flask
from config import Config
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.config.from_object(Config)

from database import db, init_db
db.init_app(app)

from auth import init_auth
init_auth(app)

from admin import admin_bp
app.register_blueprint(admin_bp)

# Import all routes (must be last)
from routes import *

if __name__ == '__main__':
    with app.app_context():
        init_db(app)
    app.run(debug=True, port=5000)