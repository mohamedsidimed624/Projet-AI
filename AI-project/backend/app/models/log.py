"""
Modèle WellLog pour stocker les données de diagraphie (logging).
Types de logs: GR (Gamma Ray), RESIS (Résistivité), DENS (Densité), NEUT (Neutron)
"""

from datetime import datetime
from app import db


class WellLog(db.Model):
    """
    Modèle représentant une mesure de diagraphie.
    
    Types de logs supportés:
        - GR: Gamma Ray (radioactivité naturelle, unités API)
        - RESIS: Résistivité (ohm.m)
        - DENS: Densité (g/cm³)
        - NEUT: Porosité Neutron (fraction ou %)
        - SP: Potentiel Spontané (mV)
        - CALI: Calibre du trou (pouces)
    
    Attributs:
        id: Identifiant unique
        well_id: ID du puits associé
        log_type: Type de log (GR, RESIS, DENS, NEUT, etc.)
        depth: Profondeur de la mesure (en mètres)
        value: Valeur de la mesure
        unit: Unité de mesure
        created_at: Date d'import
    """
    
    __tablename__ = 'well_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    well_id = db.Column(db.Integer, db.ForeignKey('wells.id'), nullable=False)
    log_type = db.Column(db.String(20), nullable=False)  # GR, RESIS, DENS, NEUT, SP, CALI
    depth = db.Column(db.Float, nullable=False)  # en mètres
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)  # API, ohm.m, g/cm3, fraction, mV, inch
    quality = db.Column(db.String(10), default='good')  # good, suspect, bad
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index pour optimiser les requêtes par profondeur
    __table_args__ = (
        db.Index('idx_well_log_depth', 'well_id', 'log_type', 'depth'),
    )
    
    # Constantes pour les types de logs
    LOG_TYPES = {
        'GR': {'name': 'Gamma Ray', 'unit': 'API', 'min': 0, 'max': 200},
        'RESIS': {'name': 'Résistivité', 'unit': 'ohm.m', 'min': 0.1, 'max': 1000},
        'DENS': {'name': 'Densité', 'unit': 'g/cm³', 'min': 1.8, 'max': 3.0},
        'NEUT': {'name': 'Porosité Neutron', 'unit': 'fraction', 'min': 0, 'max': 0.6},
        'SP': {'name': 'Potentiel Spontané', 'unit': 'mV', 'min': -200, 'max': 100},
        'CALI': {'name': 'Calibre', 'unit': 'inch', 'min': 6, 'max': 20}
    }
    
    def to_dict(self):
        """Convertit le log en dictionnaire."""
        return {
            'id': self.id,
            'well_id': self.well_id,
            'log_type': self.log_type,
            'depth': self.depth,
            'value': self.value,
            'unit': self.unit,
            'quality': self.quality,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_log_info(cls, log_type):
        """Retourne les informations sur un type de log."""
        return cls.LOG_TYPES.get(log_type, {})
    
    def __repr__(self):
        return f'<WellLog {self.log_type} @ {self.depth}m: {self.value}>'
