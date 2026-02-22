import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT to requests when available
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// On 401, clear token and redirect to login
client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// —— Auth ——
export const register = (email, password) =>
  client.post('/auth/register', { email, password })

export const login = (email, password) =>
  client.post('/auth/login', { email, password })

// —— File & Plagiarism ——
export const uploadFile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return client.post('/files/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** Two-file comparison (code/document). */
export const checkPlagiarism = (file1, file2) => {
  const form = new FormData()
  form.append('file1', file1)
  form.append('file2', file2)
  return client.post('/files/check', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** Internet source detection (single file). */
export const internetCheck = (file) => {
  const form = new FormData()
  form.append('file', file)
  return client.post('/files/internet-check', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// —— Results & Analytics ——
export const getResults = (page = 1, perPage = 10) =>
  client.get('/files/results', { params: { page, per_page: perPage } })

export const getSingleResult = (resultId) =>
  client.get(`/files/results/${resultId}`)

export const getAnalytics = () => client.get('/files/analytics')

export const deleteResult = (resultId) =>
  client.delete(`/files/results/${resultId}`)

/** PDF report download; returns blob URL for same-origin download. */
export const getReportPdfUrl = (resultId) =>
  `/api/files/report/${resultId}`
