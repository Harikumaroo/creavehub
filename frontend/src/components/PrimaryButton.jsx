import { motion } from 'framer-motion'
import Loader from './Loader'

export default function PrimaryButton({
  children,
  loading = false,
  disabled = false,
  onClick,
  type = 'button',
  successMode = false,
  className = '',
}) {
  const isDisabled = disabled || loading
  return (
    <motion.button
      type={type}
      className={`ch-btn-primary mt-1 ${className}`}
      onClick={onClick}
      disabled={isDisabled}
      whileHover={!isDisabled ? { y: -2 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      animate={successMode
        ? { background: 'linear-gradient(135deg,#16A34A,#22C55E)', boxShadow: '0 8px 28px rgba(34,197,94,0.4)' }
        : {}}
      transition={{ duration: 0.3 }}
    >
      {loading ? (
        <>
          <Loader size={18} color="#fff" />
          <span>Please wait…</span>
        </>
      ) : successMode ? (
        <>
          <span className="text-base">✓</span>
          <span>Verified!</span>
        </>
      ) : children}
    </motion.button>
  )
}
