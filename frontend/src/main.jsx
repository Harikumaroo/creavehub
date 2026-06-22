import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthProvider } from './store/authStore'
import { SettingsProvider } from './context/SettingsContext'
import AppRouter from './routes/AppRouter'
import './styles/index.css'

// Polyfill for Framer Motion DevTools integration
if (typeof window.__chromium_devtools_metrics_reporter === 'undefined') {
  window.__chromium_devtools_metrics_reporter = () => {}
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <SettingsProvider>
        <AppRouter />
      </SettingsProvider>
    </AuthProvider>
  </React.StrictMode>
)
