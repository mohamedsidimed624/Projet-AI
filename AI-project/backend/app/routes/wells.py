"""
Routes pour la gestion des puits pétroliers.
CRUD complet avec sécurité JWT.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.well import Well
from app.models.user import User

wells_bp = Blueprint('wells', __name__)


@wells_bp.route('', methods=['GET'])
@jwt_required()
def get_wells():
    """
    Récupère la liste des puits de l'utilisateur.
    
    Query params:
        - page: Numéro de page (défaut: 1)
        - per_page: Éléments par page (défaut: 10)
        - status: Filtrer par statut
        - search: Recherche par nom
    
    Returns:
        200: Liste paginée des puits
    """
    user_id = get_jwt_identity()
    
    # Paramètres de pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    
    # Construire la requête
    query = Well.query.filter_by(user_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(Well.name.ilike(f'%{search}%'))
    
    # Pagination
    pagination = query.order_by(Well.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'wells': [well.to_dict() for well in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@wells_bp.route('', methods=['POST'])
@jwt_required()
def create_well():
    """
    Crée un nouveau puits.
    
    Body JSON:
        - name: Nom du puits (requis)
        - field_name: Nom du champ
        - location: Localisation
        - latitude: Latitude
        - longitude: Longitude
        - depth_total: Profondeur totale
        - status: Statut (active, drilling, abandoned)
        - description: Description
    
    Returns:
        201: Puits créé
        400: Données invalides
    """
    try:
        user_id = int(get_jwt_identity())  # Convertir en int
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Le nom du puits est requis'}), 400
        
        # Créer le puits
        well = Well(
            name=data['name'],
            field_name=data.get('field_name'),
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            depth_total=data.get('depth_total'),
            status=data.get('status', 'active'),
            description=data.get('description'),
            user_id=user_id
        )
        
        db.session.add(well)
        db.session.commit()
    
        return jsonify({
            'message': 'Puits créé avec succès',
            'well': well.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500


@wells_bp.route('/<int:well_id>', methods=['GET'])
@jwt_required()
def get_well(well_id):
    """
    Récupère les détails d'un puits.
    
    Returns:
        200: Détails du puits
        404: Puits non trouvé
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    return jsonify({'well': well.to_dict()}), 200


@wells_bp.route('/<int:well_id>', methods=['PUT'])
@jwt_required()
def update_well(well_id):
    """
    Met à jour un puits.
    
    Returns:
        200: Puits mis à jour
        404: Puits non trouvé
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    data = request.get_json()
    
    # Mettre à jour les champs fournis
    updatable_fields = [
        'name', 'field_name', 'location', 'latitude', 'longitude',
        'depth_total', 'status', 'description'
    ]
    
    for field in updatable_fields:
        if field in data:
            setattr(well, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Puits mis à jour',
        'well': well.to_dict()
    }), 200


@wells_bp.route('/<int:well_id>', methods=['DELETE'])
@jwt_required()
def delete_well(well_id):
    """
    Supprime un puits et toutes ses données associées.
    
    Returns:
        200: Puits supprimé
        404: Puits non trouvé
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    db.session.delete(well)
    db.session.commit()
    
    return jsonify({'message': 'Puits supprimé avec succès'}), 200


@wells_bp.route('/<int:well_id>/stats', methods=['GET'])
@jwt_required()
def get_well_stats(well_id):
    """
    Récupère les statistiques d'un puits.
    
    Returns:
        200: Statistiques du puits
    """
    user_id = get_jwt_identity()
    well = Well.query.filter_by(id=well_id, user_id=user_id).first()
    
    if not well:
        return jsonify({'error': 'Puits non trouvé'}), 404
    
    # Calculer les statistiques
    stats = {
        'well_id': well.id,
        'name': well.name,
        'logs_count': well.logs.count(),
        'petrophysics_count': well.petrophysics.count(),
        'log_types': [],
        'depth_range': {'min': None, 'max': None}
    }
    
    # Types de logs disponibles
    from app.models.log import WellLog
    log_types = db.session.query(WellLog.log_type).filter_by(
        well_id=well_id
    ).distinct().all()
    stats['log_types'] = [lt[0] for lt in log_types]
    
    # Plage de profondeur
    from sqlalchemy import func
    depth_stats = db.session.query(
        func.min(WellLog.depth),
        func.max(WellLog.depth)
    ).filter_by(well_id=well_id).first()
    
    if depth_stats[0] is not None:
        stats['depth_range'] = {
            'min': depth_stats[0],
            'max': depth_stats[1]
        }
    
    return jsonify({'stats': stats}), 200
