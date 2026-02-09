/**
 * Service pour l'analyse pétrophysique
 * Calculs automatiques et suggestions IA
 */

import api from './api'

const analysisService = {
    /**
     * Lance le calcul pétrophysique pour une zone
     * @param {number} wellId - ID du puits
     * @param {Object} params - Paramètres de calcul
     */
    async calculatePetrophysics(wellId, params) {
        const response = await api.post(`/analysis/well/${wellId}/calculate`, params)
        return response.data
    },

    /**
     * Récupère les zones analysées d'un puits
     */
    async getZones(wellId) {
        const response = await api.get(`/analysis/well/${wellId}/zones`)
        return response.data.zones
    },

    /**
     * Récupère les suggestions d'analyse
     */
    async getSuggestions(wellId) {
        const response = await api.get(`/analysis/well/${wellId}/suggestions`)
        return response.data.suggestions
    }
}

export default analysisService
