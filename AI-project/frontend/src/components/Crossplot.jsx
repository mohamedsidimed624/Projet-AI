/**
 * Composant Crossplot - Graphique Densité vs Neutron
 * Permet l'identification lithologique et la détection de fluides
 */

import React, { useState, useMemo } from 'react'
import Plot from 'react-plotly.js'
import './Crossplot.css'

// Lignes de référence lithologiques
const LITHOLOGY_LINES = {
    sandstone: {
        name: 'Sandstone',
        color: '#f1c40f',
        // Points: [Neutron, Densité]
        points: [[0.02, 2.65], [0.35, 2.0]]
    },
    limestone: {
        name: 'Limestone',
        color: '#3498db',
        points: [[0.0, 2.71], [0.30, 2.1]]
    },
    dolomite: {
        name: 'Dolomite',
        color: '#9b59b6',
        points: [[0.02, 2.87], [0.25, 2.3]]
    }
}

function Crossplot({ logData, well }) {
    const [colorBy, setColorBy] = useState('depth')
    const [showLithologyLines, setShowLithologyLines] = useState(true)

    // Préparer les données pour le crossplot
    const plotData = useMemo(() => {
        if (!logData?.DENS || !logData?.NEUT) {
            return null
        }

        const densData = logData.DENS
        const neutData = logData.NEUT

        // Aligner les données sur les mêmes profondeurs
        const depthSet = new Set(densData.depths)
        const alignedData = {
            depths: [],
            dens: [],
            neut: []
        }

        neutData.depths.forEach((depth, i) => {
            if (depthSet.has(depth)) {
                const densIdx = densData.depths.indexOf(depth)
                if (densIdx !== -1) {
                    alignedData.depths.push(depth)
                    alignedData.dens.push(densData.values[densIdx])
                    alignedData.neut.push(neutData.values[i])
                }
            }
        })

        return alignedData
    }, [logData])

    // Générer les traces Plotly
    const traces = useMemo(() => {
        const result = []

        if (plotData) {
            // Trace principale - points de données
            result.push({
                x: plotData.neut,
                y: plotData.dens,
                mode: 'markers',
                type: 'scatter',
                marker: {
                    color: plotData.depths,
                    colorscale: 'Viridis',
                    size: 6,
                    colorbar: {
                        title: 'Profondeur (m)',
                        thickness: 15
                    }
                },
                text: plotData.depths.map(d => `Profondeur: ${d.toFixed(1)}m`),
                hoverinfo: 'text+x+y',
                name: 'Données'
            })
        }

        // Lignes lithologiques de référence
        if (showLithologyLines) {
            Object.entries(LITHOLOGY_LINES).forEach(([key, litho]) => {
                result.push({
                    x: litho.points.map(p => p[0]),
                    y: litho.points.map(p => p[1]),
                    mode: 'lines+markers',
                    type: 'scatter',
                    line: {
                        color: litho.color,
                        width: 2,
                        dash: 'dash'
                    },
                    marker: { size: 8 },
                    name: litho.name
                })
            })
        }

        return result
    }, [plotData, showLithologyLines])

    const layout = {
        title: `Crossplot Densité-Neutron - ${well?.name || 'Puits'}`,
        xaxis: {
            title: 'Porosité Neutron (fraction)',
            range: [-0.05, 0.50],
            autorange: false,
            gridcolor: '#e0e0e0'
        },
        yaxis: {
            title: 'Densité (g/cm³)',
            range: [3.0, 1.8],
            autorange: false,
            gridcolor: '#e0e0e0'
        },
        showlegend: true,
        legend: {
            x: 1.02,
            y: 0.5
        },
        hovermode: 'closest',
        height: 500,
        margin: { l: 60, r: 150, t: 50, b: 50 }
    }

    if (!logData?.DENS || !logData?.NEUT) {
        return (
            <div className="crossplot-empty">
                <span className="empty-icon">📊</span>
                <h3>Crossplot indisponible</h3>
                <p>Les logs DENS et NEUT sont requis pour afficher le crossplot.</p>
            </div>
        )
    }

    return (
        <div className="crossplot">
            <div className="crossplot-controls">
                <label className="control-item">
                    <input
                        type="checkbox"
                        checked={showLithologyLines}
                        onChange={(e) => setShowLithologyLines(e.target.checked)}
                    />
                    <span>Afficher lignes lithologiques</span>
                </label>
            </div>

            <div className="crossplot-chart">
                <Plot
                    data={traces}
                    layout={layout}
                    config={{
                        responsive: true,
                        displayModeBar: true,
                        modeBarButtonsToRemove: ['lasso2d', 'select2d']
                    }}
                    style={{ width: '100%', height: '100%' }}
                />
            </div>

            <div className="crossplot-legend">
                <h4>Interprétation</h4>
                <ul>
                    <li><strong>Au-dessus</strong> de la ligne grès: présence de gaz (effet gaz)</li>
                    <li><strong>Sur</strong> la ligne grès: sable propre saturé en eau/huile</li>
                    <li><strong>Entre</strong> grès et calcaire: mélange ou sable argileux</li>
                    <li><strong>Cluster serré</strong>: zone homogène</li>
                </ul>
            </div>
        </div>
    )
}

export default Crossplot
