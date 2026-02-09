/**
 * Application principale React
 * Gère le routage et le contexte d'authentification
 */

import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

// Pages
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import WellsPage from './pages/WellsPage'
import LogViewer from './pages/LogViewer'
import AnalysisPage from './pages/AnalysisPage'

// Composants
import Navbar from './components/Navbar'

/**
 * Route protégée - redirige vers login si non authentifié
 */
function ProtectedRoute({ children }) {
    const { user, loading } = useAuth()

    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Chargement...</p>
            </div>
        )
    }

    if (!user) {
        return <Navigate to="/login" replace />
    }

    return children
}

/**
 * Layout principal avec navigation
 */
function MainLayout({ children }) {
    return (
        <div className="app-container">
            <Navbar />
            <main className="main-content">
                {children}
            </main>
        </div>
    )
}

/**
 * Composant principal de l'application
 */
function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Route publique */}
                    <Route path="/login" element={<LoginPage />} />

                    {/* Routes protégées */}
                    <Route path="/" element={
                        <ProtectedRoute>
                            <MainLayout>
                                <Dashboard />
                            </MainLayout>
                        </ProtectedRoute>
                    } />

                    <Route path="/wells" element={
                        <ProtectedRoute>
                            <MainLayout>
                                <WellsPage />
                            </MainLayout>
                        </ProtectedRoute>
                    } />

                    <Route path="/wells/:wellId/logs" element={
                        <ProtectedRoute>
                            <MainLayout>
                                <LogViewer />
                            </MainLayout>
                        </ProtectedRoute>
                    } />

                    <Route path="/wells/:wellId/analysis" element={
                        <ProtectedRoute>
                            <MainLayout>
                                <AnalysisPage />
                            </MainLayout>
                        </ProtectedRoute>
                    } />

                    {/* Redirection par défaut */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    )
}

export default App
