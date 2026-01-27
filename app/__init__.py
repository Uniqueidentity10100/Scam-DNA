"""
Application factory and configuration
"""

from flask import Flask
import os

def create_app():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Application configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['DATABASE'] = os.path.join(os.getcwd(), 'data', 'scam_dna.db')
    
    # Initialize database
    from app.models.database import init_db
    with app.app_context():
        init_db(app.config['DATABASE'])
    
    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp
    from app.routes.intelligence_routes import bp as intelligence_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(intelligence_bp)
    
    return app
