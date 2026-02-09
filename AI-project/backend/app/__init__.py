"""
Factory Pattern pour l'application Flask.
Permet une initialisation modulaire et testable.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from .config import config

# Instances globales des extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_name='default'):
    """
    Factory function pour créer l'application Flask.
    
    Args:
        config_name: Nom de la configuration ('development', 'production', 'testing')
    
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    
    # Charger la configuration
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']), supports_credentials=True)
    
    # Enregistrer les blueprints (routes)
    from .routes.auth import auth_bp
    from .routes.wells import wells_bp
    from .routes.logs import logs_bp
    from .routes.analysis import analysis_bp
    from .routes.reports import reports_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(wells_bp, url_prefix='/api/wells')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    
    # Route de test / santé
    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'API Well Analysis is running'}
    
    return app
