import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout({ children, title = 'Plagiarism Process' }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMenuOpen(false)
  }

  return (
    <div className="app">
      <header className={`header ${scrolled ? 'scrolled' : ''}`}>
        <Link to="/" className="logo" onClick={() => setMenuOpen(false)}>
          Plagiarism Check
        </Link>
        <button
          type="button"
          className={`nav-toggle ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Menu"
          aria-expanded={menuOpen}
        >
          <span /><span /><span />
        </button>
        <nav className={`nav ${menuOpen ? 'open' : ''}`}>
          <Link to="/" onClick={() => setMenuOpen(false)}>Home</Link>
          {user && (
            <>
              <Link to="/report" onClick={() => setMenuOpen(false)}>Report</Link>
              <Link to="/history" onClick={() => setMenuOpen(false)}>History</Link>
              <Link to="/dashboard" onClick={() => setMenuOpen(false)}>Dashboard</Link>
            </>
          )}
          {user ? (
            <button type="button" className="btn-link" onClick={handleLogout}>
              Logout
            </button>
          ) : (
            <>
              <Link to="/login" onClick={() => setMenuOpen(false)}>Login</Link>
              <Link to="/register" className="nav-cta" onClick={() => setMenuOpen(false)}>Sign Up</Link>
            </>
          )}
        </nav>
      </header>
      <main className="main">
        {title ? <h1 className="page-heading">{title}</h1> : null}
        {children}
      </main>
    </div>
  )
}
