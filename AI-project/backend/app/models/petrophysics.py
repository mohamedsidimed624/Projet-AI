"""
Modèle Petrophysics pour stocker les paramètres pétrophysiques calculés.
Inclut: porosité, perméabilité, saturation, volume d'argile, etc.
"""

from datetime import datetime
from app import db


class Petrophysics(db.Model):
    """
    Modèle représentant les paramètres pétrophysiques d'une zone.
    
    Ces paramètres sont généralement calculés à partir des logs
    et représentent les propriétés du réservoir.
    
    Attributs:
        id: Identifiant unique
        well_id: ID du puits associé
        depth_from: Profondeur de début de la zone (m)
        depth_to: Profondeur de fin de la zone (m)
        porosity: Porosité totale (fraction, 0-1)
        porosity_effective: Porosité effective (fraction, 0-1)
        permeability: Perméabilité (mD - millidarcy)
        saturation_water: Saturation en eau (Sw, fraction, 0-1)
        saturation_oil: Saturation en huile (So = 1 - Sw - Sg)
        saturation_gas: Saturation en gaz (Sg, fraction, 0-1)
        vshale: Volume d'argile (Vsh, fraction, 0-1)
        lithology: Lithologie dominante
        zone_type: Type de zone (reservoir, cap_rock, source_rock)
    """
    
    __tablename__ = 'petrophysics'
    
    id = db.Column(db.Integer, primary_key=True)
    well_id = db.Column(db.Integer, db.ForeignKey('wells.id'), nullable=False)
    
    # Intervalle de profondeur
    depth_from = db.Column(db.Float, nullable=False)  # en mètres
    depth_to = db.Column(db.Float, nullable=False)    # en mètres
    
    # Paramètres pétrophysiques principaux
    porosity = db.Column(db.Float, nullable=True)           # Porosité totale (0-1)
    porosity_effective = db.Column(db.Float, nullable=True) # Porosité effective (0-1)
    permeability = db.Column(db.Float, nullable=True)       # Perméabilité (mD)
    
    # Saturations
    saturation_water = db.Column(db.Float, nullable=True)   # Sw (0-1)
    saturation_oil = db.Column(db.Float, nullable=True)     # So (0-1)
    saturation_gas = db.Column(db.Float, nullable=True)     # Sg (0-1)
    
    # Volume d'argile
    vshale = db.Column(db.Float, nullable=True)  # Vsh (0-1)
    
    # Classification
    lithology = db.Column(db.String(50), nullable=True)  # sandstone, limestone, shale, etc.
    zone_type = db.Column(db.String(30), nullable=True)  # reservoir, cap_rock, source_rock
    
    # Métadonnées
    notes = db.Column(db.Text, nullable=True)
    calculated_by = db.Column(db.String(50), default='manual')  # manual, auto, ai
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convertit les paramètres en dictionnaire."""
        return {
            'id': self.id,
            'well_id': self.well_id,
            'depth_from': self.depth_from,
            'depth_to': self.depth_to,
            'porosity': self.porosity,
            'porosity_effective': self.porosity_effective,
            'permeability': self.permeability,
            'saturation_water': self.saturation_water,
            'saturation_oil': self.saturation_oil,
            'saturation_gas': self.saturation_gas,
            'vshale': self.vshale,
            'lithology': self.lithology,
            'zone_type': self.zone_type,
            'notes': self.notes,
            'calculated_by': self.calculated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def thickness(self):
        """Calcule l'épaisseur de la zone."""
        return self.depth_to - self.depth_from
    
    @property
    def is_reservoir(self):
        """Vérifie si la zone est un réservoir potentiel."""
        if self.porosity and self.vshale and self.saturation_water:
            # Critères simples pour un réservoir
            return (
                self.porosity > 0.10 and 
                self.vshale < 0.40 and 
                self.saturation_water < 0.60
            )
        return False
    
    def __repr__(self):
        return f'<Petrophysics {self.depth_from}-{self.depth_to}m, φ={self.porosity}>'
