/**
 * Page de connexion / inscription
 * Formulaire d'authentification avec design moderne
 */

import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './LoginPage.css'

function LoginPage() {
    const [isLogin, setIsLogin] = useState(true)
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    })
    const [error, setError] = useState('')

    const { login, register } = useAuth()
    const navigate = useNavigate()

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        })
        setError('')
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            if (isLogin) {
                // Connexion
                const result = await login(formData.username, formData.password)
                if (result.success) {
                    navigate('/')
                } else {
                    setError(result.error)
                }
            } else {
                // Inscription
                if (formData.password !== formData.confirmPassword) {
                    setError('Les mots de passe ne correspondent pas')
                    setLoading(false)
                    return
                }

                const result = await register(formData.username, formData.email, formData.password)
                if (result.success) {
                    navigate('/')
                } else {
                    setError(result.error)
                }
            }
        } catch (err) {
            setError('Une erreur est survenue')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-page">
            {/* Section gauche - Branding */}
            <div className="login-hero">
                <div className="hero-content">
                    <div className="hero-logo">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="64" height="64">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                        </svg>
                    </div>
                    <h1>Well Analysis</h1>
                    <p>Plateforme d'analyse de données pétrolières</p>
                    <div className="hero-features">
                        <div className="feature">
                            <span className="feature-icon">📊</span>
                            <span>Visualisation des logs</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🔬</span>
                            <span>Analyse pétrophysique</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🤖</span>
                            <span>Assistance IA</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Section droite - Formulaire */}
            <div className="login-form-section">
                <div className="login-form-container">
                    <h2>{isLogin ? 'Connexion' : 'Inscription'}</h2>
                    <p className="form-subtitle">
                        {isLogin
                            ? 'Accédez à votre espace de travail'
                            : 'Créez votre compte pour commencer'
                        }
                    </p>

                    {error && (
                        <div className="alert alert-error">{error}</div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label className="form-label" htmlFor="username">
                                Nom d'utilisateur
                            </label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                className="form-input"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="Entrez votre nom d'utilisateur"
                                required
                            />
                        </div>

                        {!isLogin && (
                            <div className="form-group">
                                <label className="form-label" htmlFor="email">
                                    Email
                                </label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    className="form-input"
                                    value={formData.email}
                                    onChange={handleChange}
                                    placeholder="Entrez votre email"
                                    required
                                />
                            </div>
                        )}

                        <div className="form-group">
                            <label className="form-label" htmlFor="password">
                                Mot de passe
                            </label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                className="form-input"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Entrez votre mot de passe"
                                required
                            />
                        </div>

                        {!isLogin && (
                            <div className="form-group">
                                <label className="form-label" htmlFor="confirmPassword">
                                    Confirmer le mot de passe
                                </label>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    className="form-input"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    placeholder="Confirmez votre mot de passe"
                                    required
                                />
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn btn-primary btn-full"
                            disabled={loading}
                        >
                            {loading ? 'Chargement...' : (isLogin ? 'Se connecter' : 'S\'inscrire')}
                        </button>
                    </form>

                    <p className="form-toggle">
                        {isLogin ? "Pas encore de compte ?" : "Déjà un compte ?"}
                        <button
                            type="button"
                            className="toggle-link"
                            onClick={() => {
                                setIsLogin(!isLogin)
                                setError('')
                            }}
                        >
                            {isLogin ? "S'inscrire" : "Se connecter"}
                        </button>
                    </p>
                </div>
            </div>
        </div>
    )
}

export default LoginPage
