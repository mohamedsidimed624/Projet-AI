/**
 * Service API - Configuration Axios
 * Gère toutes les requêtes HTTP vers le backend Flask
 */

import axios from 'axios'

// Créer une instance Axios configurée
const api = axios.create({
    baseURL: '/api',  // Proxy Vite redirige vers http://localhost:5000/api
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 10000  // 10 secondes
})

// Intercepteur pour ajouter le token JWT
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            // Format correct pour Flask-JWT-Extended
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Intercepteur pour gérer les erreurs de réponse
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Erreur 401 ou 422: Token invalide ou expiré
        if (error.response?.status === 401 || error.response?.status === 422) {
            // Seulement rediriger si ce n'est pas une requête d'auth
            const isAuthRequest = error.config?.url?.includes('/auth/')
            if (!isAuthRequest) {
                localStorage.removeItem('token')
                // Rediriger vers login si nécessaire
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login'
                }
            }
        }
        return Promise.reject(error)
    }
)

export default api

