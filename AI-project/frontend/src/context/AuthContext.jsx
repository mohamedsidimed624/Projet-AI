/**
 * Contexte d'authentification React
 * Gère l'état de connexion de l'utilisateur dans toute l'application
 */

import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

// Création du contexte
const AuthContext = createContext(null)

/**
 * Hook personnalisé pour accéder au contexte d'auth
 */
export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth doit être utilisé dans un AuthProvider')
    }
    return context
}

/**
 * Provider du contexte d'authentification
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    // Vérifier le token au chargement
    useEffect(() => {
        const token = localStorage.getItem('token')
        if (token) {
            // Vérifier la validité du token
            api.get('/auth/profile')
                .then(response => {
                    setUser(response.data.user)
                })
                .catch(() => {
                    // Token invalide, le supprimer
                    localStorage.removeItem('token')
                })
                .finally(() => {
                    setLoading(false)
                })
        } else {
            setLoading(false)
        }
    }, [])

    /**
     * Connexion de l'utilisateur
     */
    const login = async (username, password) => {
        try {
            setError(null)
            const response = await api.post('/auth/login', { username, password })
            const { access_token, user: userData } = response.data

            // Stocker le token
            localStorage.setItem('token', access_token)
            setUser(userData)

            return { success: true }
        } catch (err) {
            const message = err.response?.data?.error || 'Erreur de connexion'
            setError(message)
            return { success: false, error: message }
        }
    }

    /**
     * Inscription d'un nouvel utilisateur
     */
    const register = async (username, email, password) => {
        try {
            setError(null)
            const response = await api.post('/auth/register', { username, email, password })

            // Connexion automatique après inscription
            return await login(username, password)
        } catch (err) {
            const message = err.response?.data?.error || 'Erreur lors de l\'inscription'
            setError(message)
            return { success: false, error: message }
        }
    }

    /**
     * Déconnexion
     */
    const logout = () => {
        localStorage.removeItem('token')
        setUser(null)
    }

    /**
     * Mise à jour du profil
     */
    const updateProfile = async (data) => {
        try {
            const response = await api.put('/auth/profile', data)
            setUser(response.data.user)
            return { success: true }
        } catch (err) {
            const message = err.response?.data?.error || 'Erreur de mise à jour'
            return { success: false, error: message }
        }
    }

    const value = {
        user,
        loading,
        error,
        login,
        register,
        logout,
        updateProfile,
        isAuthenticated: !!user
    }

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext
