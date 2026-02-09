"""
Routes pour l'analyse pétrophysique assistée.
Calculs automatiques et suggestions basées sur les logs.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.well import Well
from app.models.log import WellLog
from app.models.petrophysics import Petrophysics
import numpy as np

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/well/<int:well_id>/calculate', methods=['POST'])
@jwt_required()
def calculate_petrophysics(well_id):
    """
    Calcule les paramètres pétrophysiques à partir des logs.
    
    Body JSON:
        - depth_from: Profondeur de début
        - depth_to: Profondeur de fin
        - gr_clean: Valeur GR des zones propres (défaut: 20)
        - gr_shale: Valeur GR des argiles (défaut: 120)
        - rho_matrix: Densité de la matrice (défaut: 2.65)
        - rho_fluid: Densité du fluide (défaut: 1.0)
    
    Returns:
        201: Paramètres calculés et sauvegardés
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    data = request.get_json() or {}
    
    depth_from = data.get('depth_from')
    depth_to = data.get('depth_to')
    
    if not depth_from or not depth_to:
        return jsonify({'error': 'depth_from et depth_to sont requis'}), 400
    
    # Paramètres de calcul (valeurs par défaut typiques)
    gr_clean = data.get('gr_clean', 20)    # GR des sables propres (API)
    gr_shale = data.get('gr_shale', 120)   # GR des argiles (API)
    rho_matrix = data.get('rho_matrix', 2.65)  # Densité matrice (g/cm³)
    rho_fluid = data.get('rho_fluid', 1.0)     # Densité fluide (g/cm³)
    
    # Récupérer les logs
    logs = {}
    for log_type in ['GR', 'DENS', 'NEUT', 'RESIS']:
        log_data = WellLog.query.filter_by(well_id=well_id, log_type=log_type)\
            .filter(WellLog.depth >= depth_from)\
            .filter(WellLog.depth <= depth_to)\
            .order_by(WellLog.depth).all()
        if log_data:
            logs[log_type] = {
                'depths': [l.depth for l in log_data],
                'values': [l.value for l in log_data]
            }
    
    if 'GR' not in logs:
        return jsonify({'error': 'Log GR requis pour le calcul'}), 400
    
    # Calculer le volume d'argile (Vshale) à partir du GR
    gr_values = np.array(logs['GR']['values'])
    igr = (gr_values - gr_clean) / (gr_shale - gr_clean)  # Index Gamma Ray
    igr = np.clip(igr, 0, 1)  # Borner entre 0 et 1
    
    # Formule de Larionov (vieux roches)
    vshale = 0.33 * (2**(2 * igr) - 1)
    vshale = np.clip(vshale, 0, 1)
    vshale_mean = float(np.mean(vshale))
    
    # Calculer la porosité si densité disponible
    porosity = None
    if 'DENS' in logs:
        dens_values = np.array(logs['DENS']['values'])
        # Porosité densité
        porosity_dens = (rho_matrix - dens_values) / (rho_matrix - rho_fluid)
        porosity_dens = np.clip(porosity_dens, 0, 0.5)
        porosity = float(np.mean(porosity_dens))
    
    # Porosité effective (corrigée de l'argile)
    porosity_effective = None
    if porosity is not None:
        porosity_effective = porosity * (1 - vshale_mean)
    
    # Estimer la saturation en eau si résistivité disponible (formule d'Archie simplifiée)
    saturation_water = None
    if 'RESIS' in logs and porosity_effective:
        rw = 0.1  # Résistivité de l'eau de formation (hypothèse)
        a = 1.0   # Facteur de tortuosité
        m = 2.0   # Exposant de cimentation
        n = 2.0   # Exposant de saturation
        
        rt_values = np.array(logs['RESIS']['values'])
        rt_mean = np.mean(rt_values)
        
        # Formule d'Archie: Sw^n = (a * Rw) / (phi^m * Rt)
        if porosity_effective > 0 and rt_mean > 0:
            sw_n = (a * rw) / (porosity_effective**m * rt_mean)
            saturation_water = min(1.0, sw_n**(1/n))
    
    # Déterminer le type de zone
    zone_type = 'shale'
    if vshale_mean < 0.3:
        if saturation_water and saturation_water < 0.5:
            zone_type = 'reservoir'
        else:
            zone_type = 'water_bearing'
    
    # Sauvegarder les résultats
    petro = Petrophysics(
        well_id=well_id,
        depth_from=depth_from,
        depth_to=depth_to,
        porosity=porosity,
        porosity_effective=porosity_effective,
        saturation_water=saturation_water,
        saturation_oil=1 - saturation_water if saturation_water else None,
        vshale=vshale_mean,
        zone_type=zone_type,
        calculated_by='auto'
    )
    
    db.session.add(petro)
    db.session.commit()
    
    return jsonify({
        'message': 'Calcul effectué',
        'petrophysics': petro.to_dict(),
        'interpretation': {
            'zone_type': zone_type,
            'is_reservoir': petro.is_reservoir,
            'recommendations': _get_recommendations(petro)
        }
    }), 201


@analysis_bp.route('/well/<int:well_id>/zones', methods=['GET'])
@jwt_required()
def get_zones(well_id):
    """
    Récupère les zones pétrophysiques analysées d'un puits.
    
    Returns:
        200: Liste des zones avec leurs paramètres
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    zones = Petrophysics.query.filter_by(well_id=well_id)\
        .order_by(Petrophysics.depth_from).all()
    
    return jsonify({
        'well_id': well_id,
        'zones': [z.to_dict() for z in zones]
    }), 200


@analysis_bp.route('/well/<int:well_id>/suggestions', methods=['GET'])
@jwt_required()
def get_suggestions(well_id):
    """
    Génère des suggestions d'analyse basées sur les données disponibles.
    
    Returns:
        200: Liste de suggestions
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    suggestions = []
    
    # Vérifier les logs disponibles
    available_logs = db.session.query(WellLog.log_type).filter_by(
        well_id=well_id
    ).distinct().all()
    available_log_types = [lt[0] for lt in available_logs]
    
    if not available_log_types:
        suggestions.append({
            'type': 'warning',
            'message': 'Aucun log disponible. Importez des données pour commencer l\'analyse.'
        })
        return jsonify({'suggestions': suggestions}), 200
    
    # Suggestions basées sur les logs disponibles
    if 'GR' in available_log_types:
        suggestions.append({
            'type': 'action',
            'message': 'Log GR disponible: Vous pouvez calculer le volume d\'argile (Vshale).'
        })
    
    if 'DENS' in available_log_types and 'NEUT' in available_log_types:
        suggestions.append({
            'type': 'action',
            'message': 'Logs DENS et NEUT disponibles: Créez un crossplot Neutron-Densité pour identifier la lithologie.'
        })
    
    if 'RESIS' in available_log_types:
        suggestions.append({
            'type': 'action',
            'message': 'Log Résistivité disponible: Estimez la saturation en eau (Sw) avec la formule d\'Archie.'
        })
    
    # Vérifier les analyses existantes
    zones_count = Petrophysics.query.filter_by(well_id=well_id).count()
    if zones_count == 0:
        suggestions.append({
            'type': 'info',
            'message': 'Aucune analyse pétrophysique. Utilisez /calculate pour analyser une zone.'
        })
    else:
        # Identifier les zones réservoir
        reservoir_zones = Petrophysics.query.filter_by(
            well_id=well_id, zone_type='reservoir'
        ).all()
        if reservoir_zones:
            suggestions.append({
                'type': 'success',
                'message': f'{len(reservoir_zones)} zone(s) réservoir identifiée(s).'
            })
    
    return jsonify({'suggestions': suggestions}), 200


def _get_recommendations(petro):
    """Génère des recommandations basées sur les paramètres calculés."""
    recommendations = []
    
    if petro.vshale:
        if petro.vshale > 0.5:
            recommendations.append("Zone argileuse - faible potentiel réservoir")
        elif petro.vshale < 0.2:
            recommendations.append("Zone propre - bon potentiel réservoir")
    
    if petro.porosity_effective:
        if petro.porosity_effective > 0.15:
            recommendations.append("Bonne porosité effective (>15%)")
        elif petro.porosity_effective < 0.08:
            recommendations.append("Porosité faible - réservoir marginal")
    
    if petro.saturation_water:
        if petro.saturation_water < 0.4:
            recommendations.append("Saturation en eau faible - zone à hydrocarbures potentielle")
        elif petro.saturation_water > 0.7:
            recommendations.append("Saturation en eau élevée - zone aquifère probable")
    
    return recommendations
