"""
Routes pour l'authentification des utilisateurs.
Gère l'inscription, la connexion et le profil.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inscription d'un nouvel utilisateur.
    
    Body JSON:
        - username: Nom d'utilisateur
        - email: Adresse email
        - password: Mot de passe
        - role: (optionnel) Rôle de l'utilisateur
    
    Returns:
        201: Utilisateur créé avec succès
        400: Données invalides ou utilisateur existant
    """
    data = request.get_json()
    
    # Validation des champs requis
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Champ requis manquant: {field}'}), 400
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Ce nom d\'utilisateur existe déjà'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Cette adresse email existe déjà'}), 400
    
    # Créer le nouvel utilisateur
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'etudiant')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Utilisateur créé avec succès',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Connexion d'un utilisateur.
    
    Body JSON:
        - username: Nom d'utilisateur ou email
        - password: Mot de passe
    
    Returns:
        200: Token JWT et informations utilisateur
        401: Identifiants invalides
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Données JSON requises'}), 400
    
    username = data.get('username', '')
    password = data.get('password', '')
    
    # Rechercher l'utilisateur par username ou email
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
    
    # Mettre à jour la date de dernière connexion
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Créer le token JWT
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Connexion réussie',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupère le profil de l'utilisateur connecté.
    
    Headers:
        Authorization: Bearer <token>
    
    Returns:
        200: Informations du profil
        401: Non authentifié
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Met à jour le profil de l'utilisateur connecté.
    
    Body JSON (tous optionnels):
        - email: Nouvelle adresse email
        - password: Nouveau mot de passe
    
    Returns:
        200: Profil mis à jour
        400: Données invalides
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    
    if 'email' in data:
        # Vérifier si l'email n'est pas déjà utilisé
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({'error': 'Cette adresse email est déjà utilisée'}), 400
        user.email = data['email']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profil mis à jour',
        'user': user.to_dict()
    }), 200
