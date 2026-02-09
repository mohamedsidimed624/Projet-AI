/**
 * Composant Navbar - Navigation principale
 * Sidebar fixe avec liens vers les différentes sections
 */

import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Navbar.css'

function Navbar() {
    const { user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <nav className="navbar">
            {/* Logo et titre */}
            <div className="navbar-brand">
                <div className="navbar-logo">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z" />
                    </svg>
                </div>
                <div className="navbar-title">
                    <span className="title-main">Well Analysis</span>
                    <span className="title-sub">Analyse Pétrolière</span>
                </div>
            </div>

            {/* Liens de navigation */}
            <ul className="navbar-nav">
                <li className="nav-item">
                    <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                        <span className="nav-icon">📊</span>
                        <span className="nav-text">Dashboard</span>
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink to="/wells" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
                        <span className="nav-icon">🛢️</span>
                        <span className="nav-text">Puits</span>
                    </NavLink>
                </li>
            </ul>

            {/* Section utilisateur */}
            <div className="navbar-user">
                <div className="user-info">
                    <div className="user-avatar">
                        {user?.username?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <div className="user-details">
                        <span className="user-name">{user?.username}</span>
                        <span className="user-role">{user?.role}</span>
                    </div>
                </div>
                <button className="btn-logout" onClick={handleLogout} title="Déconnexion">
                    <span>🚪</span>
                </button>
            </div>
        </nav>
    )
}

export default Navbar
