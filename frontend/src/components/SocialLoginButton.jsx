import { useState } from 'react'
import { motion } from 'framer-motion'
import Loader from './Loader'

export default function SocialLoginButton({ icon, label, onClick }) {
  const [loading, setLoading] = useState(false)

  const handle = async () => {
    if (loading) return
    setLoading(true)
    try { await onClick?.() }
    finally { setLoading(false) }
  }

  return (
    <motion.button
      className="ch-btn-social"
      onClick={handle}
      disabled={loading}
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.97 }}
    >
      {loading ? <Loader size={16} color="currentColor" /> : icon}
      <span>{label}</span>
    </motion.button>
  )
}
