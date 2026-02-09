/**
 * Page de visualisation des logs
 * Affichage graphique des logs de puits avec Plotly
 */

import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Plot from 'react-plotly.js'
import wellsService from '../services/wellsService'
import logsService from '../services/logsService'
import reportsService from '../services/reportsService'
import Crossplot from '../components/Crossplot'
import './LogViewer.css'

function LogViewer() {
    const { wellId } = useParams()
    const [well, setWell] = useState(null)
    const [logData, setLogData] = useState({})
    const [logTypes, setLogTypes] = useState([])
    const [selectedLogs, setSelectedLogs] = useState(['GR', 'RESIS'])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')
    const [importing, setImporting] = useState(false)
    const [activeTab, setActiveTab] = useState('logs') // 'logs' ou 'crossplot'
    const [downloadingReport, setDownloadingReport] = useState(false)

    useEffect(() => {
        loadData()
    }, [wellId])

    const loadData = async () => {
        try {
            setLoading(true)

            // Charger le puits
            const wellData = await wellsService.getWell(wellId)
            setWell(wellData)

            // Charger les types de logs
            const types = await logsService.getLogTypes(wellId)
            setLogTypes(types)

            // Charger les données des logs
            const exportData = await logsService.exportLogs(wellId)
            setLogData(exportData.data)

            // Sélectionner les premiers logs disponibles
            if (types.length > 0) {
                setSelectedLogs(types.slice(0, 2).map(t => t.type))
            }

        } catch (err) {
            setError('Erreur lors du chargement des données')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const handleFileImport = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setImporting(true)
        try {
            await logsService.importLogs(wellId, file)
            await loadData()
        } catch (err) {
            setError(err.response?.data?.error || 'Erreur lors de l\'import')
        } finally {
            setImporting(false)
        }
    }

    const handleDownloadReport = async () => {
        setDownloadingReport(true)
        try {
            await reportsService.downloadHtmlReport(wellId, well?.name)
        } catch (err) {
            setError('Erreur lors du téléchargement du rapport')
        } finally {
            setDownloadingReport(false)
        }
    }

    const toggleLog = (logType) => {
        if (selectedLogs.includes(logType)) {
            setSelectedLogs(selectedLogs.filter(l => l !== logType))
        } else {
            setSelectedLogs([...selectedLogs, logType])
        }
    }

    // Couleurs pour les différents types de logs
    const logColors = {
        GR: '#2ecc71',
        RESIS: '#e74c3c',
        DENS: '#3498db',
        NEUT: '#9b59b6',
        SP: '#f39c12',
        CALI: '#1abc9c'
    }

    // Générer les traces Plotly
    const generateTraces = () => {
        return selectedLogs
            .filter(type => logData[type])
            .map((type, index) => ({
                x: logData[type].values,
                y: logData[type].depths,
                type: 'scatter',
                mode: 'lines',
                name: `${type} (${logData[type].info?.unit || ''})`,
                line: {
                    color: logColors[type] || '#333',
                    width: 1.5
                },
                xaxis: index === 0 ? 'x' : `x${index + 1}`,
                yaxis: 'y'
            }))
    }

    // Configuration du layout Plotly
    const generateLayout = () => {
        const layout = {
            title: `Logs - ${well?.name || 'Puits'}`,
            height: 700,
            showlegend: true,
            legend: { x: 1.02, y: 1 },
            yaxis: {
                title: 'Profondeur (m)',
                autorange: 'reversed',
                gridcolor: '#e0e0e0'
            },
            margin: { l: 80, r: 150, t: 50, b: 50 }
        }

        // Ajouter les axes X pour chaque log
        selectedLogs.forEach((type, index) => {
            const axisKey = index === 0 ? 'xaxis' : `xaxis${index + 1}`
            layout[axisKey] = {
                title: type,
                titlefont: { color: logColors[type] || '#333' },
                tickfont: { color: logColors[type] || '#333' },
                side: index % 2 === 0 ? 'bottom' : 'top',
                overlaying: index === 0 ? undefined : 'x',
                position: index === 0 ? 0 : undefined
            }
        })

        return layout
    }

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement des logs...</p>
            </div>
        )
    }

    return (
        <div className="log-viewer">
            {/* Header */}
            <div className="page-header">
                <div>
                    <div className="breadcrumb">
                        <Link to="/wells">Puits</Link> / {well?.name}
                    </div>
                    <h1 className="page-title">Visualisation des Logs</h1>
                    <p className="page-subtitle">{well?.field_name || 'Champ non spécifié'}</p>
                </div>
                <div className="header-actions">
                    <label className="btn btn-secondary">
                        {importing ? 'Import...' : '📤 Importer CSV'}
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileImport}
                            style={{ display: 'none' }}
                            disabled={importing}
                        />
                    </label>
                    <button
                        className="btn btn-secondary"
                        onClick={handleDownloadReport}
                        disabled={downloadingReport}
                    >
                        {downloadingReport ? '⏳...' : '📄 Rapport'}
                    </button>
                    <Link to={`/wells/${wellId}/analysis`} className="btn btn-primary">
                        🔬 Analyse
                    </Link>
                </div>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            {/* Onglets */}
            <div className="tabs">
                <button
                    className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('logs')}
                >
                    📊 Logs
                </button>
                <button
                    className={`tab ${activeTab === 'crossplot' ? 'active' : ''}`}
                    onClick={() => setActiveTab('crossplot')}
                >
                    📈 Crossplot
                </button>
            </div>

            {activeTab === 'logs' ? (
                <div className="log-content">
                    {/* Sidebar des contrôles */}
                    <div className="log-controls card">
                        <h3>Types de Logs</h3>

                        {logTypes.length === 0 ? (
                            <p className="no-logs">Aucun log disponible. Importez un fichier CSV.</p>
                        ) : (
                            <div className="log-toggles">
                                {logTypes.map(log => (
                                    <label key={log.type} className="log-toggle">
                                        <input
                                            type="checkbox"
                                            checked={selectedLogs.includes(log.type)}
                                            onChange={() => toggleLog(log.type)}
                                        />
                                        <span
                                            className="toggle-color"
                                            style={{ backgroundColor: logColors[log.type] || '#333' }}
                                        />
                                        <span className="toggle-info">
                                            <span className="toggle-name">{log.name}</span>
                                            <span className="toggle-count">{log.count} pts</span>
                                        </span>
                                    </label>
                                ))}
                            </div>
                        )}

                        <div className="csv-format">
                            <h4>Format CSV attendu:</h4>
                            <pre>depth,GR,RESIS,DENS,NEUT{'\n'}1000.0,50.5,10.2,2.65,0.15{'\n'}1000.5,52.3,11.1,2.63,0.16</pre>
                        </div>
                    </div>

                    {/* Zone du graphique */}
                    <div className="log-chart card">
                        {Object.keys(logData).length === 0 ? (
                            <div className="empty-chart">
                                <span className="empty-icon">📊</span>
                                <h3>Aucune donnée à afficher</h3>
                                <p>Importez un fichier CSV pour visualiser les logs.</p>
                            </div>
                        ) : (
                            <Plot
                                data={generateTraces()}
                                layout={generateLayout()}
                                config={{
                                    responsive: true,
                                    displayModeBar: true,
                                    modeBarButtonsToRemove: ['lasso2d', 'select2d']
                                }}
                                style={{ width: '100%', height: '100%' }}
                            />
                        )}
                    </div>
                </div>
            ) : (
                <div className="crossplot-container card">
                    <Crossplot logData={logData} well={well} />
                </div>
            )}
        </div>
    )
}

export default LogViewer

