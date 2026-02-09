/**
 * Service pour la gestion des puits
 * Fonctions CRUD pour interagir avec l'API des puits
 */

import api from './api'

const wellsService = {
    /**
     * Récupère la liste des puits
     * @param {Object} params - Paramètres de filtrage (page, status, search)
     */
    async getWells(params = {}) {
        const response = await api.get('/wells', { params })
        return response.data
    },

    /**
     * Récupère un puits par son ID
     */
    async getWell(wellId) {
        const response = await api.get(`/wells/${wellId}`)
        return response.data.well
    },

    /**
     * Crée un nouveau puits
     */
    async createWell(wellData) {
        const response = await api.post('/wells', wellData)
        return response.data
    },

    /**
     * Met à jour un puits
     */
    async updateWell(wellId, wellData) {
        const response = await api.put(`/wells/${wellId}`, wellData)
        return response.data
    },

    /**
     * Supprime un puits
     */
    async deleteWell(wellId) {
        const response = await api.delete(`/wells/${wellId}`)
        return response.data
    },

    /**
     * Récupère les statistiques d'un puits
     */
    async getWellStats(wellId) {
        const response = await api.get(`/wells/${wellId}/stats`)
        return response.data.stats
    }
}

export default wellsService
