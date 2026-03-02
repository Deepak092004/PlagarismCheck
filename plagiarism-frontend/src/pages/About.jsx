import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiUpload, FiFileText, FiGlobe, FiBarChart2, FiLock, FiClock } from 'react-icons/fi'
import { useAuth } from '../context/AuthContext'

const container = { hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1 } } }
const item = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }

export default function About() {
  const { user } = useAuth()

  return (
    <div className="home">
      {/* Hero Section */}
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
          About Plagiarism Check
        </motion.h2>
        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35, duration: 0.5 }}
        >
          A simple tool to detect plagiarism in your documents and code
        </motion.p>
      </motion.section>

      {/* How It Works - Section Title */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>How It Works</h2>
      </div>

      {/* How It Works - Cards */}
      <motion.section
        className="features"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon" style={{ fontSize: '2rem', marginBottom: '1rem' }}>1</div>
          <h3>Upload Document</h3>
          <p>Upload your document in .txt, .pdf, or .docx format</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiFileText size={24} /></div>
          <h3>Analysis</h3>
          <p>Our system analyzes your content against multiple sources</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiGlobe size={24} /></div>
          <h3>Web Search</h3>
          <p>Check against billions of web pages and online sources</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiBarChart2 size={24} /></div>
          <h3>Get Report</h3>
          <p>View plagiarism percentage and matching sources</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiClock size={24} /></div>
          <h3>Save History</h3>
          <p>Keep track of all your previous plagiarism checks</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiLock size={24} /></div>
          <h3>Secure & Private</h3>
          <p>Your documents are encrypted and kept safe</p>
        </motion.div>
      </motion.section>

      {/* Our Features - Section Title */}
      <div style={{ textAlign: 'center', marginBottom: '2rem', marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Our Features</h2>
      </div>

      {/* Our Features - Cards */}
      <motion.section
        className="features"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiFileText size={24} /></div>
          <h3>Token Analysis</h3>
          <p>TF-IDF, Jaccard & sequence matching for documents</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiGlobe size={24} /></div>
          <h3>Web Detection</h3>
          <p>Find matches across the internet with similarity scores</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiBarChart2 size={24} /></div>
          <h3>Detailed Reports</h3>
          <p>Download comprehensive reports with visual analytics</p>
        </motion.div>
      </motion.section>

      {/* Why Choose Us - Section Title */}
      <div style={{ textAlign: 'center', marginBottom: '2rem', marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.8rem', fontWeight: 700, margin: 0 }}>Why Choose Us?</h2>
      </div>

      {/* Why Choose Us - Cards */}
      <motion.section
        className="features"
        variants={container}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiClock size={24} /></div>
          <h3>Detailed Analysis</h3>
          <p>Get a comprehensive plagiarism report</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiFileText size={24} /></div>
          <h3>Easy to Use</h3>
          <p>Simple interface, no technical knowledge needed</p>
        </motion.div>

        <motion.div className="feature-card" variants={item} whileHover={{ y: -4 }}>
          <div className="feature-icon"><FiLock size={24} /></div>
          <h3>Secure</h3>
          <p>Your data is protected with encryption</p>
        </motion.div>
      </motion.section>

      {/* CTA */}
      <motion.section
        className="cta"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        {user ? (
          <Link to="/report" className="btn btn-primary">Start Checking</Link>
        ) : (
          <>
            <Link to="/report" className="btn btn-primary">Start Checking</Link>
            <Link to="/register" className="btn btn-outline">Create Account</Link>
          </>
        )}
      </motion.section>
    </div>
  )
}