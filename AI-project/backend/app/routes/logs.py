"""
Routes pour la gestion des logs de puits (diagraphie).
Import, visualisation et export des données de logging.
"""

import io
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.well import Well
from app.models.log import WellLog

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/well/<int:well_id>', methods=['GET'])
@jwt_required()
def get_logs(well_id):
    """
    Récupère les logs d'un puits.
    
    Query params:
        - log_type: Type de log (GR, RESIS, DENS, NEUT)
        - depth_from: Profondeur minimum
        - depth_to: Profondeur maximum
    
    Returns:
        200: Liste des logs
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    # Filtres
    log_type = request.args.get('log_type')
    depth_from = request.args.get('depth_from', type=float)
    depth_to = request.args.get('depth_to', type=float)
    
    query = WellLog.query.filter_by(well_id=well_id)
    
    if log_type:
        query = query.filter_by(log_type=log_type)
    if depth_from is not None:
        query = query.filter(WellLog.depth >= depth_from)
    if depth_to is not None:
        query = query.filter(WellLog.depth <= depth_to)
    
    logs = query.order_by(WellLog.depth).all()
    
    return jsonify({
        'well_id': well_id,
        'count': len(logs),
        'logs': [log.to_dict() for log in logs]
    }), 200


@logs_bp.route('/well/<int:well_id>/types', methods=['GET'])
@jwt_required()
def get_log_types(well_id):
    """
    Récupère les types de logs disponibles pour un puits.
    
    Returns:
        200: Liste des types de logs
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    log_types = db.session.query(WellLog.log_type).filter_by(
        well_id=well_id
    ).distinct().all()
    
    types_info = []
    for lt in log_types:
        type_name = lt[0]
        count = WellLog.query.filter_by(well_id=well_id, log_type=type_name).count()
        info = WellLog.get_log_info(type_name)
        types_info.append({
            'type': type_name,
            'name': info.get('name', type_name),
            'unit': info.get('unit', ''),
            'count': count
        })
    
    return jsonify({'log_types': types_info}), 200


@logs_bp.route('/well/<int:well_id>/import', methods=['POST'])
@jwt_required()
def import_logs(well_id):
    """
    Importe des logs depuis un fichier CSV.
    
    Format CSV attendu:
        depth,GR,RESIS,DENS,NEUT
        1000.0,50.5,10.2,2.65,0.15
        1000.5,52.3,11.1,2.63,0.16
        ...
    
    Returns:
        201: Logs importés
        400: Erreur d'import
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    # Vérifier le fichier
    if 'file' not in request.files:
        return jsonify({'error': 'Fichier CSV requis'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Le fichier doit être au format CSV'}), 400
    
    try:
        import pandas as pd
        
        # Lire le fichier CSV
        df = pd.read_csv(io.BytesIO(file.read()))
        
        if 'depth' not in df.columns:
            return jsonify({'error': 'Colonne "depth" requise'}), 400
        
        # Colonnes de logs supportées
        log_columns = ['GR', 'RESIS', 'DENS', 'NEUT', 'SP', 'CALI']
        found_columns = [col for col in log_columns if col in df.columns]
        
        if not found_columns:
            return jsonify({
                'error': 'Aucune colonne de log trouvée',
                'expected': log_columns,
                'found': list(df.columns)
            }), 400
        
        # Insérer les logs
        logs_created = 0
        for _, row in df.iterrows():
            depth = row['depth']
            for log_type in found_columns:
                value = row[log_type]
                if pd.notna(value):
                    log = WellLog(
                        well_id=well_id,
                        log_type=log_type,
                        depth=float(depth),
                        value=float(value),
                        unit=WellLog.get_log_info(log_type).get('unit', '')
                    )
                    db.session.add(log)
                    logs_created += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Import réussi',
            'logs_created': logs_created,
            'log_types': found_columns
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de l\'import: {str(e)}'}), 400


@logs_bp.route('/well/<int:well_id>/export', methods=['GET'])
@jwt_required()
def export_logs(well_id):
    """
    Exporte les logs d'un puits en format JSON structuré.
    
    Query params:
        - log_type: Type de log spécifique (optionnel)
    
    Returns:
        200: Données des logs formatées pour graphiques
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    log_type = request.args.get('log_type')
    
    query = WellLog.query.filter_by(well_id=well_id)
    if log_type:
        query = query.filter_by(log_type=log_type)
    
    logs = query.order_by(WellLog.depth).all()
    
    # Grouper par type de log
    data = {}
    for log in logs:
        if log.log_type not in data:
            data[log.log_type] = {
                'info': WellLog.get_log_info(log.log_type),
                'depths': [],
                'values': []
            }
        data[log.log_type]['depths'].append(log.depth)
        data[log.log_type]['values'].append(log.value)
    
    return jsonify({
        'well': well.to_dict(),
        'data': data
    }), 200


@logs_bp.route('/<int:log_id>', methods=['DELETE'])
@jwt_required()
def delete_log(log_id):
    """
    Supprime un log spécifique.
    """
    user_id = get_jwt_identity()
    log = WellLog.query.get(log_id)
    
    if not log:
        return jsonify({'error': 'Log non trouvé'}), 404
    
    # Vérifier que l'utilisateur possède le puits
    well = Well.query.filter_by(id=log.well_id, user_id=user_id).first()
    if not well:
        return jsonify({'error': 'Non autorisé'}), 403
    
    db.session.delete(log)
    db.session.commit()
    
    return jsonify({'message': 'Log supprimé'}), 200
