/**
 * Page Dashboard - Vue d'ensemble
 * Affiche les statistiques générales et accès rapides
 */

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import wellsService from '../services/wellsService'
import './Dashboard.css'

function Dashboard() {
    const { user } = useAuth()
    const [stats, setStats] = useState({
        totalWells: 0,
        activeWells: 0,
        recentWells: []
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadDashboardData()
    }, [])

    const loadDashboardData = async () => {
        try {
            const data = await wellsService.getWells({ per_page: 5 })
            setStats({
                totalWells: data.total,
                activeWells: data.wells.filter(w => w.status === 'active').length,
                recentWells: data.wells
            })
        } catch (error) {
            console.error('Erreur chargement dashboard:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement du dashboard...</p>
            </div>
        )
    }

    return (
        <div className="dashboard">
            {/* Header */}
            <div className="page-header">
                <div>
                    <h1 className="page-title">Bonjour, {user?.username} 👋</h1>
                    <p className="page-subtitle">Bienvenue sur votre espace d'analyse pétrolière</p>
                </div>
                <Link to="/wells" className="btn btn-primary">
                    + Nouveau Puits
                </Link>
            </div>

            {/* Cartes statistiques */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">🛢️</div>
                    <div className="stat-content">
                        <span className="stat-value">{stats.totalWells}</span>
                        <span className="stat-label">Puits Total</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon active">✓</div>
                    <div className="stat-content">
                        <span className="stat-value">{stats.activeWells}</span>
                        <span className="stat-label">Puits Actifs</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon">📊</div>
                    <div className="stat-content">
                        <span className="stat-value">0</span>
                        <span className="stat-label">Analyses</span>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon warning">📈</div>
                    <div className="stat-content">
                        <span className="stat-value">0</span>
                        <span className="stat-label">Logs importés</span>
                    </div>
                </div>
            </div>

            {/* Accès rapides */}
            <div className="quick-actions">
                <h2>Actions Rapides</h2>
                <div className="actions-grid">
                    <Link to="/wells" className="action-card">
                        <span className="action-icon">🛢️</span>
                        <span className="action-title">Gérer les Puits</span>
                        <span className="action-desc">Créer, modifier ou supprimer des puits</span>
                    </Link>

                    <div className="action-card disabled">
                        <span className="action-icon">📤</span>
                        <span className="action-title">Importer des Logs</span>
                        <span className="action-desc">Charger des fichiers CSV/LAS</span>
                    </div>

                    <div className="action-card disabled">
                        <span className="action-icon">🔬</span>
                        <span className="action-title">Nouvelle Analyse</span>
                        <span className="action-desc">Lancer une analyse pétrophysique</span>
                    </div>

                    <div className="action-card disabled">
                        <span className="action-icon">📋</span>
                        <span className="action-title">Rapports</span>
                        <span className="action-desc">Générer des rapports d'analyse</span>
                    </div>
                </div>
            </div>

            {/* Puits récents */}
            <div className="recent-wells card">
                <div className="card-header">
                    <h3 className="card-title">Puits Récents</h3>
                    <Link to="/wells" className="btn btn-secondary">Voir tout</Link>
                </div>

                {stats.recentWells.length === 0 ? (
                    <div className="empty-state">
                        <p>Aucun puits créé pour le moment.</p>
                        <Link to="/wells" className="btn btn-primary">Créer votre premier puits</Link>
                    </div>
                ) : (
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Nom</th>
                                <th>Champ</th>
                                <th>Statut</th>
                                <th>Logs</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stats.recentWells.map(well => (
                                <tr key={well.id}>
                                    <td><strong>{well.name}</strong></td>
                                    <td>{well.field_name || '-'}</td>
                                    <td>
                                        <span className={`badge badge-${well.status === 'active' ? 'success' : 'warning'}`}>
                                            {well.status}
                                        </span>
                                    </td>
                                    <td>{well.logs_count || 0}</td>
                                    <td>
                                        <Link to={`/wells/${well.id}/logs`} className="btn btn-secondary btn-sm">
                                            Voir
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    )
}

export default Dashboard
