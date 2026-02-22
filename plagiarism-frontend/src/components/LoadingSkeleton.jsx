import { motion } from 'framer-motion'

export function CardSkeleton() {
  return (
    <motion.div
      className="skeleton-card"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-text" />
      <div className="skeleton skeleton-text short" />
    </motion.div>
  )
}

export function StatSkeleton() {
  return (
    <motion.div
      className="skeleton-stat"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.1 }}
    >
      <div className="skeleton skeleton-icon" />
      <div className="skeleton skeleton-value" />
      <div className="skeleton skeleton-label" />
    </motion.div>
  )
}

export function TableRowSkeleton({ cols = 5 }) {
  return (
    <tr className="skeleton-row">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i}><div className="skeleton skeleton-cell" /></td>
      ))}
    </tr>
  )
}
