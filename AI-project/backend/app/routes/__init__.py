"""
Package des routes API.
Exporte tous les blueprints.
"""

from .auth import auth_bp
from .wells import wells_bp
from .logs import logs_bp
from .analysis import analysis_bp
from .reports import reports_bp

__all__ = ['auth_bp', 'wells_bp', 'logs_bp', 'analysis_bp', 'reports_bp']

