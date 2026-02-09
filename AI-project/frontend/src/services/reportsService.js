/**
 * Service API pour les rapports
 */

import api from './api'

const reportsService = {
    /**
     * Génère un rapport complet pour un puits
     * @param {number} wellId - ID du puits
     * @param {string} format - Format du rapport: 'json' ou 'html'
     */
    async generateReport(wellId, format = 'json') {
        if (format === 'html') {
            // Pour HTML, on récupère directement le blob
            const response = await api.get(`/reports/well/${wellId}?format=html`, {
                responseType: 'blob'
            })
            return response.data
        }
        const response = await api.get(`/reports/well/${wellId}?format=json`)
        return response.data.report
    },

    /**
     * Récupère le résumé d'analyse d'un puits
     * @param {number} wellId - ID du puits
     */
    async getSummary(wellId) {
        const response = await api.get(`/reports/well/${wellId}/summary`)
        return response.data.summary
    },

    /**
     * Télécharge un rapport HTML
     * @param {number} wellId - ID du puits
     * @param {string} wellName - Nom du puits pour le fichier
     */
    async downloadHtmlReport(wellId, wellName) {
        const blob = await this.generateReport(wellId, 'html')
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `rapport_${wellName || wellId}.html`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    }
}

export default reportsService
