"""
Modèle Puits (Well) pour stocker les informations des puits pétroliers.
"""

from datetime import datetime
from app import db


class Well(db.Model):
    """
    Modèle représentant un puits pétrolier.
    
    Attributs:
        id: Identifiant unique
        name: Nom du puits (ex: "WELL-001")
        field_name: Nom du champ pétrolier
        location: Localisation (coordonnées ou description)
        depth_total: Profondeur totale du puits (en mètres)
        status: Statut du puits (active, abandoned, drilling)
        description: Description additionnelle
        created_at: Date d'ajout dans le système
        user_id: ID de l'utilisateur propriétaire
    """
    
    __tablename__ = 'wells'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    field_name = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    depth_total = db.Column(db.Float, nullable=True)  # en mètres
    status = db.Column(db.String(20), default='active')  # active, abandoned, drilling
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Clé étrangère vers l'utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    logs = db.relationship('WellLog', backref='well', lazy='dynamic', cascade='all, delete-orphan')
    petrophysics = db.relationship('Petrophysics', backref='well', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertit le puits en dictionnaire."""
        return {
            'id': self.id,
            'name': self.name,
            'field_name': self.field_name,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'depth_total': self.depth_total,
            'status': self.status,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'logs_count': self.logs.count(),
            'petrophysics_count': self.petrophysics.count()
        }
    
    def __repr__(self):
        return f'<Well {self.name}>'
