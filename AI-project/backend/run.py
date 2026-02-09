"""
Point d'entrée de l'application Flask.
Exécuter avec: python run.py
"""

import os
from app import create_app, db

# Déterminer l'environnement (development par défaut)
config_name = os.getenv('FLASK_ENV', 'development')

# Créer l'application
app = create_app(config_name)

if __name__ == '__main__':
    # Créer les tables si elles n'existent pas
    with app.app_context():
        db.create_all()
        print("✓ Base de données initialisée")
    
    # Démarrer le serveur de développement
    print(f"🚀 Serveur Flask démarré en mode {config_name}")
    print("📍 API disponible sur: http://localhost:5000/api")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(config_name == 'development')
    )
