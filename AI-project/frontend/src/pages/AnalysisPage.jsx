/**
 * Page d'analyse pétrophysique
 * Calculs automatiques et suggestions IA
 */

import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import wellsService from '../services/wellsService'
import analysisService from '../services/analysisService'
import './AnalysisPage.css'

function AnalysisPage() {
    const { wellId } = useParams()
    const [well, setWell] = useState(null)
    const [zones, setZones] = useState([])
    const [suggestions, setSuggestions] = useState([])
    const [loading, setLoading] = useState(true)
    const [calculating, setCalculating] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    // Formulaire de calcul
    const [calcParams, setCalcParams] = useState({
        depth_from: '',
        depth_to: '',
        gr_clean: 20,
        gr_shale: 120,
        rho_matrix: 2.65,
        rho_fluid: 1.0
    })

    useEffect(() => {
        loadData()
    }, [wellId])

    const loadData = async () => {
        try {
            setLoading(true)

            const [wellData, zonesData, suggestionsData] = await Promise.all([
                wellsService.getWell(wellId),
                analysisService.getZones(wellId),
                analysisService.getSuggestions(wellId)
            ])

            setWell(wellData)
            setZones(zonesData)
            setSuggestions(suggestionsData)

        } catch (err) {
            setError('Erreur lors du chargement des données')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        setCalcParams({
            ...calcParams,
            [e.target.name]: parseFloat(e.target.value) || e.target.value
        })
    }

    const handleCalculate = async (e) => {
        e.preventDefault()
        setCalculating(true)
        setError('')
        setSuccess('')

        try {
            const result = await analysisService.calculatePetrophysics(wellId, {
                depth_from: parseFloat(calcParams.depth_from),
                depth_to: parseFloat(calcParams.depth_to),
                gr_clean: calcParams.gr_clean,
                gr_shale: calcParams.gr_shale,
                rho_matrix: calcParams.rho_matrix,
                rho_fluid: calcParams.rho_fluid
            })

            setSuccess('Calcul effectué avec succès!')
            await loadData()

        } catch (err) {
            setError(err.response?.data?.error || 'Erreur lors du calcul')
        } finally {
            setCalculating(false)
        }
    }

    // Formatage des valeurs
    const formatValue = (value, decimals = 3) => {
        if (value === null || value === undefined) return '-'
        return value.toFixed(decimals)
    }

    const formatPercent = (value) => {
        if (value === null || value === undefined) return '-'
        return `${(value * 100).toFixed(1)}%`
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement de l'analyse...</p>
            </div>
        )
    }

    return (
        <div className="analysis-page">
            {/* Header */}
            <div className="page-header">
                <div>
                    <div className="breadcrumb">
                        <Link to="/wells">Puits</Link> / <Link to={`/wells/${wellId}/logs`}>{well?.name}</Link> / Analyse
                    </div>
                    <h1 className="page-title">Analyse Pétrophysique</h1>
                    <p className="page-subtitle">Calculs automatiques et interprétation assistée</p>
                </div>
                <Link to={`/wells/${wellId}/logs`} className="btn btn-secondary">
                    📊 Voir les Logs
                </Link>
            </div>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <div className="analysis-content">
                {/* Panneau de calcul */}
                <div className="calc-panel card">
                    <h3>🧮 Nouveau Calcul</h3>
                    <p className="panel-desc">
                        Sélectionnez une zone de profondeur pour calculer les paramètres pétrophysiques.
                    </p>

                    <form onSubmit={handleCalculate}>
                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Profondeur début (m)</label>
                                <input
                                    type="number"
                                    name="depth_from"
                                    className="form-input"
                                    value={calcParams.depth_from}
                                    onChange={handleChange}
                                    placeholder="1000"
                                    required
                                    step="0.1"
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Profondeur fin (m)</label>
                                <input
                                    type="number"
                                    name="depth_to"
                                    className="form-input"
                                    value={calcParams.depth_to}
                                    onChange={handleChange}
                                    placeholder="1100"
                                    required
                                    step="0.1"
                                />
                            </div>
                        </div>

                        <details className="advanced-params">
                            <summary>Paramètres avancés</summary>
                            <div className="params-grid">
                                <div className="form-group">
                                    <label className="form-label">GR Clean (API)</label>
                                    <input
                                        type="number"
                                        name="gr_clean"
                                        className="form-input"
                                        value={calcParams.gr_clean}
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">GR Shale (API)</label>
                                    <input
                                        type="number"
                                        name="gr_shale"
                                        className="form-input"
                                        value={calcParams.gr_shale}
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">ρ Matrice (g/cm³)</label>
                                    <input
                                        type="number"
                                        name="rho_matrix"
                                        className="form-input"
                                        value={calcParams.rho_matrix}
                                        onChange={handleChange}
                                        step="0.01"
                                    />
                                </div>
                                <div className="form-group">
                                    <label className="form-label">ρ Fluide (g/cm³)</label>
                                    <input
                                        type="number"
                                        name="rho_fluid"
                                        className="form-input"
                                        value={calcParams.rho_fluid}
                                        onChange={handleChange}
                                        step="0.01"
                                    />
                                </div>
                            </div>
                        </details>

                        <button
                            type="submit"
                            className="btn btn-primary btn-full"
                            disabled={calculating}
                        >
                            {calculating ? '⏳ Calcul en cours...' : '🔬 Lancer le calcul'}
                        </button>
                    </form>
                </div>

                {/* Suggestions IA */}
                <div className="suggestions-panel card">
                    <h3>💡 Suggestions</h3>

                    {suggestions.length === 0 ? (
                        <p className="no-suggestions">Aucune suggestion disponible.</p>
                    ) : (
                        <div className="suggestions-list">
                            {suggestions.map((sug, index) => (
                                <div key={index} className={`suggestion ${sug.type}`}>
                                    <span className="suggestion-icon">
                                        {sug.type === 'success' && '✅'}
                                        {sug.type === 'warning' && '⚠️'}
                                        {sug.type === 'action' && '🎯'}
                                        {sug.type === 'info' && 'ℹ️'}
                                    </span>
                                    <span className="suggestion-text">{sug.message}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Tableau des zones */}
            <div className="zones-section card">
                <div className="card-header">
                    <h3 className="card-title">📋 Zones Analysées</h3>
                    <span className="badge badge-info">{zones.length} zones</span>
                </div>

                {zones.length === 0 ? (
                    <div className="empty-state">
                        <p>Aucune zone analysée. Lancez un calcul pour commencer.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Profondeur</th>
                                    <th>Épaisseur</th>
                                    <th>Vshale</th>
                                    <th>Porosité</th>
                                    <th>φ Effective</th>
                                    <th>Sw</th>
                                    <th>Type</th>
                                </tr>
                            </thead>
                            <tbody>
                                {zones.map(zone => (
                                    <tr key={zone.id} className={zone.zone_type === 'reservoir' ? 'row-highlight' : ''}>
                                        <td>{zone.depth_from} - {zone.depth_to} m</td>
                                        <td>{(zone.depth_to - zone.depth_from).toFixed(1)} m</td>
                                        <td>{formatPercent(zone.vshale)}</td>
                                        <td>{formatPercent(zone.porosity)}</td>
                                        <td>{formatPercent(zone.porosity_effective)}</td>
                                        <td>{formatPercent(zone.saturation_water)}</td>
                                        <td>
                                            <span className={`badge badge-${zone.zone_type === 'reservoir' ? 'success' : 'info'}`}>
                                                {zone.zone_type}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Légende */}
            <div className="legend card">
                <h4>Légende des paramètres</h4>
                <div className="legend-grid">
                    <div className="legend-item">
                        <strong>Vshale:</strong> Volume d'argile (0 = propre, 1 = argileux)
                    </div>
                    <div className="legend-item">
                        <strong>Porosité:</strong> Volume des pores / Volume total
                    </div>
                    <div className="legend-item">
                        <strong>φ Effective:</strong> Porosité corrigée de l'argile
                    </div>
                    <div className="legend-item">
                        <strong>Sw:</strong> Saturation en eau (1 - Sw = saturation en hydrocarbures)
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AnalysisPage
