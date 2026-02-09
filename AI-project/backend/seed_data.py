"""
Script de génération de données de test pour démonstration.
Crée un puits avec des logs réalistes et des analyses pétrophysiques.

Usage: python seed_data.py
"""

import sys
import os
import numpy as np

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.well import Well
from app.models.log import WellLog
from app.models.petrophysics import Petrophysics


def generate_synthetic_logs(depth_start, depth_end, step=0.5):
    """
    Génère des logs synthétiques réalistes.
    Simule un intervalle avec des zones de sable et d'argile alternées.
    """
    depths = np.arange(depth_start, depth_end, step)
    n_points = len(depths)
    
    # Créer un pattern de lithologie (alternance sable/argile)
    lithology = np.zeros(n_points)
    zone_size = 50  # points par zone
    for i in range(0, n_points, zone_size):
        if (i // zone_size) % 3 != 0:  # 2/3 sable, 1/3 argile
            lithology[i:i+zone_size] = 1  # Sable
    
    # Ajouter du bruit et transition
    lithology = np.convolve(lithology, np.ones(10)/10, mode='same')
    lithology = np.clip(lithology + np.random.normal(0, 0.1, n_points), 0, 1)
    
    logs = {}
    
    # GR (Gamma Ray): 20-40 API pour sable, 100-140 API pour argile
    gr_sand = 30 + np.random.normal(0, 5, n_points)
    gr_shale = 120 + np.random.normal(0, 10, n_points)
    logs['GR'] = lithology * gr_shale + (1 - lithology) * gr_sand
    logs['GR'] = np.clip(logs['GR'], 15, 150)
    
    # Résistivité: haute dans les sables (10-100 ohm.m), basse dans les argiles (1-5)
    resis_sand = 50 + np.random.normal(0, 20, n_points)
    resis_shale = 3 + np.random.normal(0, 1, n_points)
    logs['RESIS'] = (1 - lithology) * resis_sand + lithology * resis_shale
    logs['RESIS'] = np.clip(logs['RESIS'], 0.5, 200)
    
    # Densité: 2.65 pour matrice, plus basse avec porosité
    porosity = (1 - lithology) * (0.15 + np.random.normal(0, 0.03, n_points))
    porosity = np.clip(porosity, 0, 0.35)
    logs['DENS'] = 2.65 - porosity * 1.65  # rho_matrix - phi * (rho_matrix - rho_fluid)
    logs['DENS'] = np.clip(logs['DENS'], 2.0, 2.8)
    
    # Neutron: corrélé avec porosité
    logs['NEUT'] = porosity + lithology * 0.15 + np.random.normal(0, 0.02, n_points)
    logs['NEUT'] = np.clip(logs['NEUT'], 0, 0.45)
    
    # SP (Potentiel Spontané)
    logs['SP'] = -60 * (1 - lithology) + np.random.normal(0, 5, n_points)
    logs['SP'] = np.clip(logs['SP'], -100, 20)
    
    return depths, logs, lithology


def seed_database():
    """Remplit la base de données avec des données de démonstration."""
    
    print("🌱 Création des données de démonstration...")
    
    # Supprimer les anciennes données
    db.drop_all()
    db.create_all()
    print("✓ Base de données réinitialisée")
    
    # Créer un utilisateur de démonstration
    demo_user = User(
        username='demo',
        email='demo@example.com',
        role='ingenieur'
    )
    demo_user.set_password('demo123')
    db.session.add(demo_user)
    db.session.commit()
    print(f"✓ Utilisateur créé: demo / demo123")
    
    # Créer un puits de démonstration - Hassi Messaoud (Algérie)
    well1 = Well(
        name='HMD-101',
        field_name='Hassi Messaoud',
        location='Algérie - Bloc 438',
        latitude=31.6667,
        longitude=6.0667,
        depth_total=3500.0,
        status='active',
        description='Puits d\'exploration - Réservoir Cambrien. Données de démonstration pour formation.',
        user_id=demo_user.id
    )
    db.session.add(well1)
    
    # Créer un deuxième puits
    well2 = Well(
        name='ORD-205',
        field_name='Oued Righ',
        location='Algérie - Bloc 404',
        latitude=33.5000,
        longitude=5.9500,
        depth_total=2800.0,
        status='drilling',
        description='Puits en cours de forage - Objectif Trias.',
        user_id=demo_user.id
    )
    db.session.add(well2)
    db.session.commit()
    print(f"✓ Puits créés: {well1.name}, {well2.name}")
    
    # Générer des logs pour le premier puits
    print("⏳ Génération des logs synthétiques...")
    depths, logs, lithology = generate_synthetic_logs(2800, 3200, step=0.5)
    
    log_count = 0
    for log_type, values in logs.items():
        unit = WellLog.get_log_info(log_type).get('unit', '')
        for depth, value in zip(depths, values):
            log = WellLog(
                well_id=well1.id,
                log_type=log_type,
                depth=float(depth),
                value=float(value),
                unit=unit
            )
            db.session.add(log)
            log_count += 1
    
    db.session.commit()
    print(f"✓ {log_count} points de log créés pour {well1.name}")
    
    # Créer des zones pétrophysiques
    zones = [
        # Zone argileuse (shale)
        {'depth_from': 2800, 'depth_to': 2850, 'vshale': 0.75, 'porosity': 0.08, 
         'porosity_effective': 0.02, 'saturation_water': 1.0, 'zone_type': 'shale',
         'lithology': 'shale'},
        
        # Zone réservoir 1 (sable avec hydrocarbures)
        {'depth_from': 2850, 'depth_to': 2920, 'vshale': 0.12, 'porosity': 0.18,
         'porosity_effective': 0.16, 'saturation_water': 0.35, 'zone_type': 'reservoir',
         'lithology': 'sandstone'},
        
        # Zone argileuse intercalaire
        {'depth_from': 2920, 'depth_to': 2960, 'vshale': 0.65, 'porosity': 0.10,
         'porosity_effective': 0.04, 'saturation_water': 0.90, 'zone_type': 'shale',
         'lithology': 'shale'},
        
        # Zone réservoir 2
        {'depth_from': 2960, 'depth_to': 3050, 'vshale': 0.08, 'porosity': 0.22,
         'porosity_effective': 0.20, 'saturation_water': 0.28, 'zone_type': 'reservoir',
         'lithology': 'sandstone'},
        
        # Zone aquifère (sable avec eau)
        {'depth_from': 3050, 'depth_to': 3120, 'vshale': 0.15, 'porosity': 0.19,
         'porosity_effective': 0.16, 'saturation_water': 0.85, 'zone_type': 'water_bearing',
         'lithology': 'sandstone'},
        
        # Zone de base (shale)
        {'depth_from': 3120, 'depth_to': 3200, 'vshale': 0.80, 'porosity': 0.06,
         'porosity_effective': 0.01, 'saturation_water': 1.0, 'zone_type': 'shale',
         'lithology': 'shale'},
    ]
    
    for zone in zones:
        petro = Petrophysics(
            well_id=well1.id,
            depth_from=zone['depth_from'],
            depth_to=zone['depth_to'],
            vshale=zone['vshale'],
            porosity=zone['porosity'],
            porosity_effective=zone['porosity_effective'],
            saturation_water=zone['saturation_water'],
            saturation_oil=1 - zone['saturation_water'] if zone['saturation_water'] < 1 else 0,
            zone_type=zone['zone_type'],
            lithology=zone['lithology'],
            calculated_by='seed'
        )
        db.session.add(petro)
    
    db.session.commit()
    print(f"✓ {len(zones)} zones pétrophysiques créées")
    
    print("\n" + "="*50)
    print("🎉 Données de démonstration créées avec succès!")
    print("="*50)
    print("\n📋 Résumé:")
    print(f"   • Utilisateur: demo / demo123")
    print(f"   • Puits: {well1.name} (avec logs), {well2.name}")
    print(f"   • Logs: GR, RESIS, DENS, NEUT, SP (2800-3200m)")
    print(f"   • Zones: 2 réservoirs, 1 aquifère, 3 argiles")
    print("\n🚀 Lancez l'application et connectez-vous!")


if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_database()
