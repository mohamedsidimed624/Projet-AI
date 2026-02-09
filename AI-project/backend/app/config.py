"""
Configuration de l'application Flask.
Centralise tous les paramètres de configuration.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()


class Config:
    """Configuration de base."""
    
    # Clé secrète pour JWT et sessions
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 heures (en secondes)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Configuration base de données
    # Utilise SQLite par défaut pour le développement (pas besoin de MySQL)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, '..', 'well_analysis.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class DevelopmentConfig(Config):
    """Configuration pour le développement."""
    DEBUG = True
    

class ProductionConfig(Config):
    """Configuration pour la production."""
    DEBUG = False
    # En production, utiliser MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'well_analysis_db')
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Dictionnaire des configurations disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
