import { motion } from 'framer-motion'

export default function Loader({ size = 20, color = '#fff', thickness = 2 }) {
  return (
    <motion.span
      className="inline-block rounded-full flex-shrink-0"
      style={{
        width: size, height: size,
        border: `${thickness}px solid ${color}33`,
        borderTopColor: color,
      }}
      animate={{ rotate: 360 }}
      transition={{ duration: 0.72, repeat: Infinity, ease: 'linear' }}
    />
  )
}
