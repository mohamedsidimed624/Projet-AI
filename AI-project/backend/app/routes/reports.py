"""
Routes pour la génération de rapports d'analyse.
Export des résultats en format JSON/HTML.
"""

from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.well import Well
from app.models.log import WellLog
from app.models.petrophysics import Petrophysics

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/well/<int:well_id>', methods=['GET'])
@jwt_required()
def generate_report(well_id):
    """
    Génère un rapport complet d'analyse pour un puits.
    
    Query params:
        - format: 'json' ou 'html' (défaut: json)
    
    Returns:
        200: Rapport complet
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    report_format = request.args.get('format', 'json')
    
    # Collecter les données du rapport
    report_data = _build_report_data(well)
    
    if report_format == 'html':
        html_content = _generate_html_report(report_data)
        return Response(
            html_content,
            mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename=rapport_{well.name}.html'}
        )
    
    return jsonify({'report': report_data}), 200


@reports_bp.route('/well/<int:well_id>/summary', methods=['GET'])
@jwt_required()
def get_summary(well_id):
    """
    Génère un résumé rapide des analyses d'un puits.
    
    Returns:
        200: Résumé des analyses
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    # Statistiques des logs
    from sqlalchemy import func
    log_stats = db.session.query(
        WellLog.log_type,
        func.count(WellLog.id).label('count'),
        func.min(WellLog.depth).label('min_depth'),
        func.max(WellLog.depth).label('max_depth'),
        func.avg(WellLog.value).label('avg_value'),
        func.min(WellLog.value).label('min_value'),
        func.max(WellLog.value).label('max_value')
    ).filter_by(well_id=well_id).group_by(WellLog.log_type).all()
    
    # Résumé des zones
    zones = Petrophysics.query.filter_by(well_id=well_id).order_by(Petrophysics.depth_from).all()
    reservoir_zones = [z for z in zones if z.zone_type == 'reservoir']
    
    # Calculs de synthèse
    total_thickness = sum(z.depth_to - z.depth_from for z in zones)
    reservoir_thickness = sum(z.depth_to - z.depth_from for z in reservoir_zones)
    net_to_gross = reservoir_thickness / total_thickness if total_thickness > 0 else 0
    
    avg_porosity = 0
    avg_sw = 0
    if reservoir_zones:
        avg_porosity = sum(z.porosity_effective or 0 for z in reservoir_zones) / len(reservoir_zones)
        avg_sw = sum(z.saturation_water or 0 for z in reservoir_zones) / len(reservoir_zones)
    
    summary = {
        'well': well.to_dict(),
        'log_statistics': [
            {
                'type': stat.log_type,
                'count': stat.count,
                'depth_range': [stat.min_depth, stat.max_depth],
                'value_range': [round(stat.min_value, 2), round(stat.max_value, 2)],
                'average': round(stat.avg_value, 2)
            }
            for stat in log_stats
        ],
        'analysis_summary': {
            'total_zones': len(zones),
            'reservoir_zones': len(reservoir_zones),
            'total_thickness': round(total_thickness, 1),
            'net_reservoir_thickness': round(reservoir_thickness, 1),
            'net_to_gross': round(net_to_gross, 3),
            'average_porosity': round(avg_porosity, 3) if avg_porosity else None,
            'average_water_saturation': round(avg_sw, 3) if avg_sw else None,
            'average_hydrocarbon_saturation': round(1 - avg_sw, 3) if avg_sw else None
        },
        'interpretation': _generate_interpretation(
            reservoir_zones, net_to_gross, avg_porosity, avg_sw
        )
    }
    
    return jsonify({'summary': summary}), 200


def _build_report_data(well):
    """Construit les données complètes du rapport."""
    
    # Informations du puits
    zones = Petrophysics.query.filter_by(well_id=well.id).order_by(Petrophysics.depth_from).all()
    
    # Statistiques des logs
    from sqlalchemy import func
    log_stats = db.session.query(
        WellLog.log_type,
        func.min(WellLog.depth).label('min_depth'),
        func.max(WellLog.depth).label('max_depth')
    ).filter_by(well_id=well.id).group_by(WellLog.log_type).all()
    
    depth_range = [None, None]
    if log_stats:
        depth_range = [
            min(s.min_depth for s in log_stats),
            max(s.max_depth for s in log_stats)
        ]
    
    return {
        'metadata': {
            'generated_at': datetime.utcnow().isoformat(),
            'report_type': 'Petrophysical Analysis Report'
        },
        'well': {
            'name': well.name,
            'field': well.field_name,
            'location': well.location,
            'total_depth': well.depth_total,
            'status': well.status,
            'description': well.description
        },
        'data_summary': {
            'log_types': [s.log_type for s in log_stats],
            'depth_range': depth_range,
            'zones_analyzed': len(zones)
        },
        'zones': [z.to_dict() for z in zones],
        'recommendations': _generate_recommendations(zones)
    }


def _generate_interpretation(reservoir_zones, ntg, avg_phi, avg_sw):
    """Génère une interprétation textuelle des résultats."""
    interpretations = []
    
    if not reservoir_zones:
        interpretations.append("Aucune zone réservoir identifiée dans l'intervalle analysé.")
        return interpretations
    
    # Net-to-Gross
    if ntg > 0.5:
        interpretations.append(f"Excellent ratio Net/Gross ({ntg:.1%}) indiquant une prédominance de réservoir.")
    elif ntg > 0.3:
        interpretations.append(f"Bon ratio Net/Gross ({ntg:.1%}) avec une proportion significative de réservoir.")
    else:
        interpretations.append(f"Faible ratio Net/Gross ({ntg:.1%}) indiquant une séquence argileuse dominante.")
    
    # Porosité
    if avg_phi and avg_phi > 0.15:
        interpretations.append(f"Porosité moyenne élevée ({avg_phi:.1%}) suggérant un bon potentiel de stockage.")
    elif avg_phi and avg_phi > 0.10:
        interpretations.append(f"Porosité moyenne acceptable ({avg_phi:.1%}).")
    elif avg_phi:
        interpretations.append(f"Porosité faible ({avg_phi:.1%}) pouvant limiter la productivité.")
    
    # Saturation
    if avg_sw and avg_sw < 0.4:
        interpretations.append(f"Faible saturation en eau ({avg_sw:.1%}) indiquant une bonne saturation en hydrocarbures.")
    elif avg_sw and avg_sw < 0.6:
        interpretations.append(f"Saturation en eau modérée ({avg_sw:.1%}).")
    elif avg_sw:
        interpretations.append(f"Saturation en eau élevée ({avg_sw:.1%}) - zone probablement aquifère ou à faible production.")
    
    return interpretations


def _generate_recommendations(zones):
    """Génère des recommandations basées sur l'analyse."""
    recommendations = []
    
    reservoir_zones = [z for z in zones if z.zone_type == 'reservoir']
    
    if not zones:
        recommendations.append("Lancer une analyse pétrophysique sur les intervalles d'intérêt.")
        return recommendations
    
    if reservoir_zones:
        # Trouver la meilleure zone
        best_zone = max(reservoir_zones, 
                       key=lambda z: (z.porosity_effective or 0) * (1 - (z.saturation_water or 1)))
        recommendations.append(
            f"Zone optimale identifiée: {best_zone.depth_from}-{best_zone.depth_to}m "
            f"(φeff={best_zone.porosity_effective:.1%}, Sw={best_zone.saturation_water:.1%})"
        )
        
        if len(reservoir_zones) > 1:
            recommendations.append(f"{len(reservoir_zones)} zones réservoir identifiées - envisager complétion multi-zones.")
    
    # Vérifier les zones aquifères proches
    water_zones = [z for z in zones if z.zone_type == 'water_bearing']
    if water_zones and reservoir_zones:
        for wz in water_zones:
            for rz in reservoir_zones:
                if abs(wz.depth_from - rz.depth_to) < 20:
                    recommendations.append(
                        f"Attention: zone aquifère proche du réservoir à {wz.depth_from}m - "
                        "risque de venue d'eau."
                    )
                    break
    
    return recommendations


def _generate_html_report(data):
    """Génère un rapport HTML formaté."""
    
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Analyse - {data['well']['name']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
        .header {{ background: #1a365d; color: white; padding: 30px; margin: -40px -40px 30px; }}
        .header h1 {{ margin: 0 0 10px; }}
        .header p {{ margin: 0; opacity: 0.8; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #f0f0f0; font-weight: 600; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #1a365d; border-bottom: 2px solid #1a365d; padding-bottom: 10px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; }}
        .badge-reservoir {{ background: #c6f6d5; color: #276749; }}
        .badge-shale {{ background: #e2e8f0; color: #4a5568; }}
        .badge-water {{ background: #bee3f8; color: #2b6cb0; }}
        .recommendation {{ background: #fffbeb; border-left: 4px solid #d69e2e; padding: 15px; margin: 10px 0; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Rapport d'Analyse Pétrophysique</h1>
        <p>Puits: {data['well']['name']} | Champ: {data['well']['field'] or 'N/A'}</p>
    </div>

    <div class="section">
        <h2>Informations du Puits</h2>
        <table>
            <tr><th>Nom</th><td>{data['well']['name']}</td></tr>
            <tr><th>Champ</th><td>{data['well']['field'] or '-'}</td></tr>
            <tr><th>Localisation</th><td>{data['well']['location'] or '-'}</td></tr>
            <tr><th>Profondeur Totale</th><td>{data['well']['total_depth'] or '-'} m</td></tr>
            <tr><th>Statut</th><td>{data['well']['status']}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Résumé des Données</h2>
        <p><strong>Types de logs:</strong> {', '.join(data['data_summary']['log_types']) or 'Aucun'}</p>
        <p><strong>Intervalle analysé:</strong> {data['data_summary']['depth_range'][0] or '-'} - {data['data_summary']['depth_range'][1] or '-'} m</p>
        <p><strong>Zones analysées:</strong> {data['data_summary']['zones_analyzed']}</p>
    </div>

    <div class="section">
        <h2>Zones Pétrophysiques</h2>
        <table>
            <tr>
                <th>Intervalle (m)</th>
                <th>Type</th>
                <th>Vshale</th>
                <th>Porosité</th>
                <th>φ Effective</th>
                <th>Sw</th>
            </tr>
            {''.join(_zone_to_html_row(z) for z in data['zones'])}
        </table>
    </div>

    <div class="section">
        <h2>Recommandations</h2>
        {''.join(f'<div class="recommendation">{r}</div>' for r in data['recommendations'])}
    </div>

    <div class="footer">
        <p>Rapport généré le {data['metadata']['generated_at'][:10]} | Well Analysis System</p>
    </div>
</body>
</html>
"""
    return html


def _zone_to_html_row(zone):
    """Convertit une zone en ligne HTML de tableau."""
    badge_class = {
        'reservoir': 'badge-reservoir',
        'shale': 'badge-shale',
        'water_bearing': 'badge-water'
    }.get(zone.get('zone_type'), 'badge-shale')
    
    def fmt_pct(val):
        return f"{val*100:.1f}%" if val is not None else '-'
    
    return f"""
    <tr>
        <td>{zone.get('depth_from'):.1f} - {zone.get('depth_to'):.1f}</td>
        <td><span class="badge {badge_class}">{zone.get('zone_type', '-')}</span></td>
        <td>{fmt_pct(zone.get('vshale'))}</td>
        <td>{fmt_pct(zone.get('porosity'))}</td>
        <td>{fmt_pct(zone.get('porosity_effective'))}</td>
        <td>{fmt_pct(zone.get('saturation_water'))}</td>
    </tr>
    """
