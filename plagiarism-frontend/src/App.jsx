import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Report from './pages/Report'
import Results from './pages/Results'
import History from './pages/History'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout title=""> <Home /> </Layout>} />
      <Route path="/login" element={<Layout title=""> <Login /> </Layout>} />
      <Route path="/register" element={<Layout title=""> <Register /> </Layout>} />
      <Route
        path="/dashboard"
        element={
          <Layout title="Plagiarism Report">
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route
        path="/report"
        element={
          <Layout title="Plagiarism Process">
            <ProtectedRoute>
              <Report />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route
        path="/results/:resultId"
        element={
          <Layout title="Results">
            <ProtectedRoute>
              <Results />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route
        path="/history"
        element={
          <Layout title="Plagiarism Report">
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          </Layout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
