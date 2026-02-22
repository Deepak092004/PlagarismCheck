import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { getSingleResult, getReportPdfUrl } from '../api/client'

export default function Results() {
  const { resultId } = useParams()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)

  // Always fetch from API — navigation state can be lost/stale (e.g. after new-user redirects)
  useEffect(() => {
    if (!resultId) {
      setLoading(false)
      return
    }
    getSingleResult(resultId)
      .then((r) => setResult(r.data))
      .catch(() => setResult(null))
      .finally(() => setLoading(false))
  }, [resultId])

  const handleDownloadPdf = () => {
    const token = localStorage.getItem('access_token')
    const url = getReportPdfUrl(resultId)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `plagiarism-report-${resultId}.pdf`)
    link.style.display = 'none'
    document.body.appendChild(link)
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.blob())
      .then((blob) => {
        const blobUrl = URL.createObjectURL(blob)
        link.href = blobUrl
        link.click()
        URL.revokeObjectURL(blobUrl)
      })
      .catch(() => link.click())
    document.body.removeChild(link)
  }

  if (loading) {
    return (
      <div className="results-page">
        <div className="skeleton skeleton-title" style={{ width: 200, height: 24, marginBottom: '1rem' }} />
        <div className="results-grid">
          <div className="card">
            <div className="skeleton" style={{ width: 140, height: 140, borderRadius: '50%', margin: '1rem auto' }} />
            <div className="skeleton skeleton-text" style={{ marginTop: '1rem' }} />
          </div>
          <div className="card">
            <div className="skeleton skeleton-text" />
            <div className="skeleton skeleton-text" />
          </div>
        </div>
      </div>
    )
  }
  if (!result) return <div className="card"><p>Result not found.</p><Link to="/history">Back to History</Link></div>

  // Internet-check returns "overall_score", API/DB uses "plagiarism_score" - use both for compatibility
  const score = Number(result.plagiarism_score ?? result.overall_score) || 0
  const level = result.level || 'Low'
  const isInternet = result.file2_name === 'Web Search'
  const matches = result.internet_matches || []

  // For internet results, tfidf_score holds overall_score; jaccard/sequence are 0
  const tfidf = Number(result.tfidf_score ?? result.overall_score) || 0
  const jaccard = Number(result.jaccard_score) || 0
  const sequence = Number(result.sequence_score) || 0
  const similarityScores = [
    { label: 'Exact match', value: tfidf, color: 'var(--danger)' },
    { label: 'Minimal match', value: jaccard, color: 'var(--warning)' },
    { label: 'Moderate match', value: sequence, color: 'var(--success)' },
    { label: 'High match', value: Math.max(0, score - tfidf), color: 'var(--primary)' },
  ]

  const processData = [
    { step: 'Preprocessing', value: 85 },
    { step: 'Lexical', value: 72 },
    { step: 'Tokenization', value: 90 },
    { step: 'Matching', value: score },
  ]

  return (
    <div className="results-page">
      <div className="results-grid">
        <div className="card result-main">
          <div className="tabs">
            <span className="tab active">Website Statistics</span>
            <span className="tab">Report</span>
          </div>
          <div className="score-circle-wrap">
            <div className="score-circle" style={{ '--score': score }}>
              <span className="score-value">{score}%</span>
            </div>
            <p className={`level-label ${level.toLowerCase()}`}>
              {score <= 30 ? 'Low' : score <= 70 ? 'Moderate' : 'High'} Plagiarism
            </p>
          </div>
          {isInternet && matches.length > 0 && (
            <div className="website-breakdown">
              <h4>Website Similarity</h4>
              {matches.slice(0, 5).map((m, i) => (
                <div key={i} className="website-row">
                  <span className="website-name">{m.source || m.url || 'Source'}</span>
                  <div className="website-bar-wrap">
                    <div className="website-bar" style={{ width: `${m.score || 0}%` }} />
                  </div>
                  <span className="website-pct">{m.score || 0}%</span>
                </div>
              ))}
            </div>
          )}
          <button type="button" className="btn btn-secondary" onClick={handleDownloadPdf}>
            Download PDF Report
          </button>
        </div>

        <div className="card result-chart">
          <h4>Methodology & Process</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={processData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="step" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="var(--primary)" strokeWidth={2} dot={{ fill: 'var(--primary)' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card result-scores">
          <h4>Similarity Score</h4>
          <div className="score-bars">
            {similarityScores.map((s, i) => (
              <div key={i} className="score-bar-row">
                <span className="score-bar-label">{s.label}</span>
                <div className="score-bar-track">
                  <div className="score-bar-fill" style={{ width: `${Math.min(100, s.value)}%`, backgroundColor: s.color }} />
                </div>
                <span className="score-bar-value">{s.value.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <button type="button" className="btn btn-primary" onClick={handleDownloadPdf}>
            Download PDF Report
          </button>
        </div>
      </div>

      <div className="card methodology">
        <h4>Methodology & Process Explanation</h4>
        <div className="method-steps">
          <div className="method-step">
            <strong>Preprocessing</strong> — Normalize and clean text (lowercase, remove punctuation, tokenize).
          </div>
          <div className="method-arrow">→</div>
          <div className="method-step">
            <strong>Tokenization</strong> — Split into tokens and apply lexical analysis.
          </div>
          <div className="method-arrow">→</div>
          <div className="method-step">
            <strong>Token Sequence Matching</strong> — Detect plagiarism based on TF-IDF, Jaccard, and sequence similarity.
          </div>
        </div>
      </div>

      <p className="muted">
        <Link to="/history">← Back to History</Link> · <Link to="/report">New Check</Link>
      </p>
    </div>
  )
}
