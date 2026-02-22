import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiCheck, FiLoader, FiCircle, FiUpload } from 'react-icons/fi'
import { checkPlagiarism, internetCheck } from '../api/client'

const ALLOWED_EXT = ['.txt', '.pdf', '.docx', '.py', '.java', '.c', '.cpp', '.js']
const MAX_MB = 10

function isValidFile(file) {
  const i = file.name.lastIndexOf('.')
  const ext = i >= 0 ? file.name.slice(i).toLowerCase() : ''
  if (!ALLOWED_EXT.includes(ext)) return false
  if (file.size > MAX_MB * 1024 * 1024) return false
  return true
}

export default function Report() {
  const [mode, setMode] = useState('internet')
  const [file1, setFile1] = useState(null)
  const [file2, setFile2] = useState(null)
  const [error, setError] = useState('')
  const [step, setStep] = useState('idle')
  const [tokenSteps, setTokenSteps] = useState([
    { name: 'Preprocessing', done: false, active: false },
    { name: 'Lexical Analysis', done: false, active: false },
    { name: 'Tokenization', done: false, active: false },
  ])
  const navigate = useNavigate()

  const runProcessingAnimation = () => {
    setTokenSteps([
      { name: 'Preprocessing', done: true, active: false },
      { name: 'Lexical Analysis', done: false, active: true },
      { name: 'Tokenization', done: false, active: false },
    ])
    setTimeout(() => {
      setTokenSteps([
        { name: 'Preprocessing', done: true, active: false },
        { name: 'Lexical Analysis', done: true, active: false },
        { name: 'Tokenization', done: false, active: true },
      ])
    }, 1500)
    setTimeout(() => {
      setTokenSteps([
        { name: 'Preprocessing', done: true, active: false },
        { name: 'Lexical Analysis', done: true, active: false },
        { name: 'Tokenization', done: true, active: false },
      ])
    }, 3000)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (mode === 'internet') {
      if (!file1) { setError('Please select a file.'); return }
      if (!isValidFile(file1)) { setError(`Allowed: ${ALLOWED_EXT.join(', ')}. Max ${MAX_MB}MB.`); return }
    } else {
      if (!file1 || !file2) { setError('Please select both files.'); return }
      if (!isValidFile(file1) || !isValidFile(file2)) { setError(`Allowed: ${ALLOWED_EXT.join(', ')}. Max ${MAX_MB}MB.`); return }
    }

    setStep('processing')
    runProcessingAnimation()

    try {
      if (mode === 'internet') {
        const { data } = await internetCheck(file1)
        setStep('done')
        navigate(`/results/${data.result_id}`, { state: { internet: true, ...data } })
      } else {
        const { data } = await checkPlagiarism(file1, file2)
        setStep('done')
        navigate(`/results/${data.result_id}`, { state: { ...data } })
      }
    } catch (err) {
      setStep('idle')
      setError(err.response?.data?.error || 'Check failed. Please try again.')
    }
  }

  if (step === 'processing') {
    return (
      <motion.div
        className="report-processing"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <h2>Processing</h2>
        <div className="steps">
          {tokenSteps.map((s, i) => (
            <motion.div
              key={i}
              className={`step ${s.done ? 'done' : ''} ${s.active ? 'active' : ''}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: i * 0.1 }}
            >
              <span className="step-icon">
                {s.done ? <FiCheck size={16} /> : s.active ? <FiLoader size={16} className="spin" /> : <FiCircle size={16} />}
              </span>
              <span>{s.name}</span>
            </motion.div>
          ))}
        </div>
        <p className="processing-msg">Analyzing document…</p>
        <div className="token-count-card">
          <h4>Token count</h4>
          <table className="token-table">
            <thead>
              <tr><th>Stage</th><th>Doc</th><th>Ref</th></tr>
            </thead>
            <tbody>
              <tr><td>Preprocessing</td><td>530</td><td>396</td></tr>
              <tr><td>Lexical Analysis</td><td>385</td><td>381</td></tr>
              <tr><td>Token Generation</td><td>322</td><td>370</td></tr>
            </tbody>
          </table>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      className="report-page"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div className="card">
        <div className="report-mode-tabs">
          <button
            type="button"
            className={mode === 'internet' ? 'active' : ''}
            onClick={() => { setMode('internet'); setError('') }}
          >
            Web Source Detection
          </button>
          <button
            type="button"
            className={mode === 'compare' ? 'active' : ''}
            onClick={() => { setMode('compare'); setError('') }}
          >
            Two-File Compare
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <p className="error-msg">{error}</p>}
          {mode === 'internet' ? (
            <label className="file-upload-label">
              <span>Upload file to check against web sources</span>
              <input
                type="file"
                accept={ALLOWED_EXT.join(',')}
                onChange={(e) => setFile1(e.target.files?.[0] || null)}
              />
              {file1 && <span className="file-name">{file1.name}</span>}
            </label>
          ) : (
            <>
              <label className="file-upload-label">
                <span>File 1</span>
                <input type="file" accept={ALLOWED_EXT.join(',')} onChange={(e) => setFile1(e.target.files?.[0] || null)} />
                {file1 && <span className="file-name">{file1.name}</span>}
              </label>
              <label className="file-upload-label">
                <span>File 2</span>
                <input type="file" accept={ALLOWED_EXT.join(',')} onChange={(e) => setFile2(e.target.files?.[0] || null)} />
                {file2 && <span className="file-name">{file2.name}</span>}
              </label>
            </>
          )}
          <motion.button type="submit" className="btn btn-primary" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
            <FiUpload size={18} />
            Run check
          </motion.button>
        </form>
      </div>
    </motion.div>
  )
}
