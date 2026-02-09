/**
 * Service pour la gestion des logs de puits
 * Import, export et visualisation des données de diagraphie
 */

import api from './api'

const logsService = {
    /**
     * Récupère les logs d'un puits
     * @param {number} wellId - ID du puits
     * @param {Object} params - Filtres (log_type, depth_from, depth_to)
     */
    async getLogs(wellId, params = {}) {
        const response = await api.get(`/logs/well/${wellId}`, { params })
        return response.data
    },

    /**
     * Récupère les types de logs disponibles pour un puits
     */
    async getLogTypes(wellId) {
        const response = await api.get(`/logs/well/${wellId}/types`)
        return response.data.log_types
    },

    /**
     * Importe des logs depuis un fichier CSV
     */
    async importLogs(wellId, file) {
        const formData = new FormData()
        formData.append('file', file)

        const response = await api.post(`/logs/well/${wellId}/import`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        return response.data
    },

    /**
     * Exporte les logs en format visualisation
     */
    async exportLogs(wellId, logType = null) {
        const params = logType ? { log_type: logType } : {}
        const response = await api.get(`/logs/well/${wellId}/export`, { params })
        return response.data
    },

    /**
     * Supprime un log
     */
    async deleteLog(logId) {
        const response = await api.delete(`/logs/${logId}`)
        return response.data
    }
}

export default logsService
