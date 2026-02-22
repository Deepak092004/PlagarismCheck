import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FiTrash2 } from 'react-icons/fi'
import { getResults, deleteResult } from '../api/client'

export default function History() {
  const [data, setData] = useState({ results: [], total_results: 0, total_pages: 1, current_page: 1 })
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)

  useEffect(() => {
    getResults(page, 10)
      .then((r) => setData(r.data))
      .catch(() => setData({ results: [], total_results: 0, total_pages: 1, current_page: 1 }))
      .finally(() => setLoading(false))
  }, [page])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this result?')) return
    try {
      await deleteResult(id)
      setData((prev) => ({
        ...prev,
        results: prev.results.filter((r) => r.result_id !== id),
        total_results: Math.max(0, prev.total_results - 1),
      }))
    } catch {
      // ignore
    }
  }

  const results = data.results || []

  if (loading) {
    return (
      <div className="container">
        <div className="skeleton skeleton-title" style={{ width: 120, height: 24, marginBottom: '1rem' }} />
        <div className="card">
          <div className="skeleton skeleton-text" style={{ marginBottom: '1rem' }} />
          <div className="skeleton skeleton-text" />
          <div className="skeleton skeleton-text short" style={{ marginTop: '0.5rem' }} />
        </div>
      </div>
    )
  }

  return (
    <motion.div
      className="container"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <h2 className="page-title">History</h2>
      <div className="card">
        {results.length === 0 ? (
          <p className="muted">No results yet. Run a check from Report or Dashboard.</p>
        ) : (
          <>
            <div className="table-wrap">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>File 1</th>
                    <th>File 2</th>
                    <th>Score</th>
                    <th>Level</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, i) => (
                    <motion.tr
                      key={r.result_id}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <td>{r.created_at}</td>
                      <td>{r.file1_name}</td>
                      <td>{r.file2_name}</td>
                      <td><strong>{r.plagiarism_score}%</strong></td>
                      <td><span className={`level-badge ${(r.level || '').toLowerCase()}`}>{r.level}</span></td>
                      <td>
                        <Link to={`/results/${r.result_id}`} className="btn btn-secondary btn-sm">View</Link>
                        <button
                          type="button"
                          className="btn btn-danger btn-sm"
                          onClick={() => handleDelete(r.result_id)}
                          title="Delete"
                        >
                          <FiTrash2 size={14} />
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.total_pages > 1 && (
              <div className="pagination">
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </button>
                <span className="muted">Page {data.current_page} of {data.total_pages}</span>
                <button
                  type="button"
                  className="btn btn-secondary"
                  disabled={page >= data.total_pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </motion.div>
  )
}
