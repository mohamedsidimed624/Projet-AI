/**
 * Page de gestion des puits
 * Liste, création et sélection des puits
 */

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import wellsService from '../services/wellsService'
import './WellsPage.css'

function WellsPage() {
    const [wells, setWells] = useState([])
    const [loading, setLoading] = useState(true)
    const [showModal, setShowModal] = useState(false)
    const [formData, setFormData] = useState({
        name: '',
        field_name: '',
        location: '',
        depth_total: '',
        status: 'active',
        description: ''
    })
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    useEffect(() => {
        loadWells()
    }, [])

    const loadWells = async () => {
        try {
            const data = await wellsService.getWells()
            setWells(data.wells)
        } catch (err) {
            setError('Erreur lors du chargement des puits')
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')

        try {
            await wellsService.createWell({
                ...formData,
                depth_total: formData.depth_total ? parseFloat(formData.depth_total) : null
            })
            setSuccess('Puits créé avec succès!')
            setShowModal(false)
            setFormData({
                name: '',
                field_name: '',
                location: '',
                depth_total: '',
                status: 'active',
                description: ''
            })
            loadWells()
        } catch (err) {
            setError(err.response?.data?.error || 'Erreur lors de la création')
        }
    }

    const handleDelete = async (wellId) => {
        if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce puits ?')) {
            return
        }

        try {
            await wellsService.deleteWell(wellId)
            setSuccess('Puits supprimé')
            loadWells()
        } catch (err) {
            setError('Erreur lors de la suppression')
        }
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        )
    }

    return (
        <div className="wells-page">
            {/* Header */}
            <div className="page-header">
                <div>
                    <h1 className="page-title">Gestion des Puits</h1>
                    <p className="page-subtitle">Créez et gérez vos puits pétroliers</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    + Nouveau Puits
                </button>
            </div>

            {/* Messages */}
            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            {/* Grille des puits */}
            {wells.length === 0 ? (
                <div className="empty-state card">
                    <span className="empty-icon">🛢️</span>
                    <h3>Aucun puits</h3>
                    <p>Commencez par créer votre premier puits.</p>
                    <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                        Créer un puits
                    </button>
                </div>
            ) : (
                <div className="wells-grid">
                    {wells.map(well => (
                        <div key={well.id} className="well-card card">
                            <div className="well-header">
                                <h3 className="well-name">{well.name}</h3>
                                <span className={`badge badge-${well.status === 'active' ? 'success' : 'warning'}`}>
                                    {well.status}
                                </span>
                            </div>

                            <div className="well-info">
                                <div className="info-row">
                                    <span className="info-label">Champ:</span>
                                    <span className="info-value">{well.field_name || '-'}</span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label">Localisation:</span>
                                    <span className="info-value">{well.location || '-'}</span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label">Profondeur:</span>
                                    <span className="info-value">
                                        {well.depth_total ? `${well.depth_total} m` : '-'}
                                    </span>
                                </div>
                                <div className="info-row">
                                    <span className="info-label">Logs:</span>
                                    <span className="info-value">{well.logs_count || 0}</span>
                                </div>
                            </div>

                            <div className="well-actions">
                                <Link to={`/wells/${well.id}/logs`} className="btn btn-primary">
                                    📊 Logs
                                </Link>
                                <Link to={`/wells/${well.id}/analysis`} className="btn btn-secondary">
                                    🔬 Analyse
                                </Link>
                                <button
                                    className="btn btn-danger"
                                    onClick={() => handleDelete(well.id)}
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal de création */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Nouveau Puits</h2>
                            <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
                        </div>

                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label className="form-label">Nom du puits *</label>
                                <input
                                    type="text"
                                    name="name"
                                    className="form-input"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="Ex: WELL-001"
                                    required
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Nom du champ</label>
                                    <input
                                        type="text"
                                        name="field_name"
                                        className="form-input"
                                        value={formData.field_name}
                                        onChange={handleChange}
                                        placeholder="Ex: Hassi Messaoud"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Statut</label>
                                    <select
                                        name="status"
                                        className="form-input"
                                        value={formData.status}
                                        onChange={handleChange}
                                    >
                                        <option value="active">Actif</option>
                                        <option value="drilling">En forage</option>
                                        <option value="abandoned">Abandonné</option>
                                    </select>
                                </div>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label className="form-label">Localisation</label>
                                    <input
                                        type="text"
                                        name="location"
                                        className="form-input"
                                        value={formData.location}
                                        onChange={handleChange}
                                        placeholder="Coordonnées ou description"
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">Profondeur totale (m)</label>
                                    <input
                                        type="number"
                                        name="depth_total"
                                        className="form-input"
                                        value={formData.depth_total}
                                        onChange={handleChange}
                                        placeholder="3500"
                                        step="0.1"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label className="form-label">Description</label>
                                <textarea
                                    name="description"
                                    className="form-input"
                                    value={formData.description}
                                    onChange={handleChange}
                                    placeholder="Description du puits..."
                                    rows="3"
                                />
                            </div>

                            <div className="modal-actions">
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    Annuler
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    Créer le puits
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    )
}

export default WellsPage
