import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiFileText, FiBarChart2, FiClipboard, FiPlus } from 'react-icons/fi'
import { StatSkeleton } from '../components/LoadingSkeleton'
import { getAnalytics, getResults } from '../api/client'

const stagger = { animate: { transition: { staggerChildren: 0.05 } } }
const fadeIn = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 } }

export default function Dashboard() {
  const [analytics, setAnalytics] = useState({
    total_checks: 0,
    average_score: 0,
    highest_score: 0,
    level_distribution: { Low: 0, Medium: 0, High: 0 },
  })
  const [recent, setRecent] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAnalytics(), getResults(1, 5)])
      .then(([aRes, rRes]) => {
        setAnalytics(aRes.data)
        setRecent(rRes.data.results || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <motion.div className="dashboard" initial="initial" animate="animate" variants={stagger}>
        <div className="skeleton skeleton-title" style={{ width: 200, height: 28, marginBottom: '1.5rem' }} />
        <div className="stats-grid">
          <StatSkeleton />
          <StatSkeleton />
          <StatSkeleton />
        </div>
        <div className="card">
          <div className="skeleton skeleton-title" style={{ width: 140, height: 20, marginBottom: '1rem' }} />
          <div className="skeleton skeleton-text" style={{ marginBottom: '0.5rem' }} />
          <div className="skeleton skeleton-text short" />
        </div>
      </motion.div>
    )
  }

  const { total_checks, average_score } = analytics

  return (
    <motion.div
      className="dashboard"
      initial="initial"
      animate="animate"
      variants={stagger}
    >
      <motion.h2 className="welcome" variants={fadeIn}>
        Welcome back
      </motion.h2>

      <div className="stats-grid">
        <motion.div className="stat-card" variants={fadeIn} whileHover={{ y: -2 }}>
          <span className="stat-icon"><FiFileText size={24} /></span>
          <span className="stat-value">{total_checks}</span>
          <span className="stat-label">Files Checked</span>
        </motion.div>
        <motion.div className="stat-card" variants={fadeIn} whileHover={{ y: -2 }}>
          <span className="stat-icon"><FiBarChart2 size={24} /></span>
          <span className="stat-value">{average_score}%</span>
          <span className="stat-label">Average Similarity</span>
          <div className="stat-progress">
            <motion.div
              className="stat-progress-fill"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(100, average_score)}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
        </motion.div>
        <motion.div className="stat-card" variants={fadeIn} whileHover={{ y: -2 }}>
          <span className="stat-icon"><FiClipboard size={24} /></span>
          <span className="stat-value">{total_checks}</span>
          <span className="stat-label">Recent Reports</span>
        </motion.div>
      </div>

      <motion.div className="card recent-reports" variants={fadeIn}>
        <h3>Recent Reports</h3>
        {recent.length === 0 ? (
          <p className="muted">No reports yet. Run a plagiarism check from Report.</p>
        ) : (
          <ul className="report-list">
            {recent.map((r, i) => (
              <motion.li
                key={r.result_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <span className="report-date">{r.created_at}</span>
                <span className="report-files">{r.file1_name} vs {r.file2_name}</span>
                <span className={`level-badge ${(r.level || '').toLowerCase()}`}>{r.level}</span>
                <Link to={`/results/${r.result_id}`} className="btn btn-secondary btn-sm">View</Link>
              </motion.li>
            ))}
          </ul>
        )}
        <Link to="/report" className="btn btn-primary" style={{ marginTop: '1rem' }}>
          <FiPlus size={18} />
          New Plagiarism Check
        </Link>
      </motion.div>
    </motion.div>
  )
}
