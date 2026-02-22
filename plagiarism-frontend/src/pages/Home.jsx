import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { FiUpload, FiFileText, FiGlobe, FiBarChart2 } from 'react-icons/fi'

const container = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1 } } }
const item = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

export default function Home() {
  const { user } = useAuth()

  return (
    <div className="home">
      <motion.section
        className="hero"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <motion.h2
          className="hero-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          Plagiarism Detection
        </motion.h2>
        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35, duration: 0.5 }}
        >
          Fast, accurate detection for code & documents
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          {user ? (
            <div className="hero-btns">
              <Link to="/report" className="btn btn-primary btn-hero">
                <FiUpload size={18} />
                Upload & Check
              </Link>
              <Link to="/dashboard" className="btn btn-hero-outline">Dashboard</Link>
            </div>
          ) : (
            <Link to="/report" className="btn btn-primary btn-hero">
              <FiUpload size={18} />
              Get Started
            </Link>
          )}
        </motion.div>
      </motion.section>

      <motion.section
        className="features"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiFileText size={24} /></div>
          <h3>Token Analysis</h3>
          <p>TF-IDF, Jaccard & sequence matching for code and documents.</p>
        </motion.div>
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiGlobe size={24} /></div>
          <h3>Web Source Detection</h3>
          <p>Find matches across the internet with similarity scores.</p>
        </motion.div>
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiBarChart2 size={24} /></div>
          <h3>PDF Reports</h3>
          <p>Download detailed reports with visual analytics.</p>
        </motion.div>
      </motion.section>

      {!user && (
        <motion.section
          className="cta"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <Link to="/register" className="btn btn-primary">Sign Up</Link>
          <Link to="/login" className="btn btn-outline">Login</Link>
        </motion.section>
      )}
    </div>
  )
}
