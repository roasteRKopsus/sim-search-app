# run.py
from app import app
from database import init_db

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    with app.app_context():
        init_db(app)
    app.run(debug=False, port=5000, use_reloader=True, host="0.0.0.0")