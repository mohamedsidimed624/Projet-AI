"""
Modèle Utilisateur pour l'authentification et la gestion des accès.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """
    Modèle représentant un utilisateur de l'application.
    
    Attributs:
        id: Identifiant unique
        username: Nom d'utilisateur unique
        email: Adresse email unique
        password_hash: Mot de passe hashé (bcrypt)
        role: Rôle de l'utilisateur (admin, ingenieur, etudiant)
        created_at: Date de création du compte
        last_login: Date de dernière connexion
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='etudiant')  # admin, ingenieur, etudiant
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relation avec les puits créés par l'utilisateur
    wells = db.relationship('Well', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        """Hash et stocke le mot de passe."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie si le mot de passe correspond."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire (sans le mot de passe)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
