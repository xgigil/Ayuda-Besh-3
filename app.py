#!/usr/bin/env python3
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# DEBUG — prints as early as possible
print("\n===== DEBUG INFO (from app.py) =====")
print("Python executable:", os.sys.executable)
print("Working directory:", os.getcwd())
print("app.py __file__:", __file__)
print(".env absolute path:", env_path)
print(".env exists (os.path.exists):", os.path.exists(env_path))
print(".env readable (try open):", end=" ")
try:
    with open(env_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
    print("yes; first line starts with:", first_line[:80])
except Exception as e:
    print("no (error):", e)
print("MONGODB_URI from os.environ:", os.getenv("MONGODB_URI"))
print("MONGODB_URI from dotenv.find_dotenv():", end=" ")
try:
    import dotenv
    print(dotenv.find_dotenv())
except Exception as e:
    print("python-dotenv not installed or import error:", e)
print("====================================\n")

# Now import the rest of your app (unchanged)
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from lib.mongodb import init_db
from routes.auth import auth_bp
from routes.requests import requests_bp
from routes.frontend import frontend_bp
# ✅ NEW BLUEPRINTS
from routes.services import services_bp
from routes.bookings import bookings_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app, origins="*", supports_credentials=True)
    init_db(app)
    
    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(requests_bp, url_prefix='/api/requests')
    app.register_blueprint(frontend_bp)
    # ✅ NEW BLUEPRINTS
    app.register_blueprint(services_bp, url_prefix='/api')
    app.register_blueprint(bookings_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'ok', 'message': 'AyudaBesh API is running'}), 200
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        host=os.getenv('FLASK_HOST', '127.0.0.1'),
        port=int(os.getenv('FLASK_PORT', 5000))
    )
