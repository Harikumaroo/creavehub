import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useAuthCtx } from '../store/authStore'
import Login             from '../pages/Login'
import Register          from '../pages/Register'
import OtpVerify         from '../pages/OtpVerify'
import CraveHubDashboard from '../pages/CraveHubDashboard'

function Spinner() {
  return (
    <div style={{ minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center', background:'#FAF3EC' }}>
      <div style={{ textAlign:'center' }}>
        <div style={{ fontSize:40, marginBottom:12 }}>🍽️</div>
        <div style={{ width:36, height:36, borderRadius:'50%', border:'3px solid #F0E4D4', borderTopColor:'#E8621A', animation:'spin 0.8s linear infinite', margin:'0 auto' }} />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    </div>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuthCtx()
  if (loading) return <Spinner />
  return isAuthenticated ? children : <Navigate to="/auth/login" replace />
}

function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuthCtx()
  if (loading) return null
  return isAuthenticated ? <Navigate to="/home" replace /> : children
}

export default function AppRouter() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/auth/login"    element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/auth/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route path="/auth/otp"      element={<OtpVerify />} />
          <Route path="/home"          element={<ProtectedRoute><CraveHubDashboard /></ProtectedRoute>} />
          <Route path="/CraveHubDashboard" element={<ProtectedRoute><CraveHubDashboard /></ProtectedRoute>} />
          <Route path="/"              element={<ProtectedRoute><CraveHubDashboard /></ProtectedRoute>} />
          <Route path="*"              element={<Navigate to="/auth/login" replace />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}
