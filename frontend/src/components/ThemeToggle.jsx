import { motion } from 'framer-motion'
import { useTheme } from '../hooks/useTheme'

export default function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <motion.button
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className="fixed top-5 right-5 z-50 flex items-center p-[3px] rounded-full cursor-pointer border"
      style={{
        width: 58, height: 30,
        background: isDark ? 'rgba(22,22,30,0.9)' : 'rgba(245,244,240,0.9)',
        borderColor: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.11)',
        backdropFilter: 'blur(16px)',
        boxShadow: isDark
          ? '0 4px 16px rgba(0,0,0,0.4), 0 0 0 1px rgba(255,255,255,0.05) inset'
          : '0 4px 14px rgba(0,0,0,0.1)',
      }}
      whileTap={{ scale: 0.93 }}
    >
      <motion.div
        className="flex items-center justify-center w-[22px] h-[22px] rounded-full text-[11px] select-none"
        animate={{ x: isDark ? 0 : 28 }}
        transition={{ type: 'spring', stiffness: 440, damping: 32 }}
        style={{
          background: 'linear-gradient(135deg,#E8470A,#F26522)',
          boxShadow: '0 2px 10px rgba(232,71,10,0.45)',
        }}
      >
        {isDark ? '🌙' : '☀️'}
      </motion.div>
    </motion.button>
  )
}
