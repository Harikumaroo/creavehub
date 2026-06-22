import { motion, AnimatePresence } from 'framer-motion'

export default function InputField({ label, error, className = '', inputRef, ...props }) {
  return (
    <div className={`ch-input-group ${className}`}>
      {label && <label className="ch-label">{label}</label>}
      <input
        ref={inputRef}
        className={`ch-input ${error ? 'has-error' : ''}`}
        {...props}
      />
      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="err"
            initial={{ opacity: 0, y: -6, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -4, height: 0 }}
            transition={{ duration: 0.18 }}
            className="flex items-center gap-1.5 mt-1.5 text-[0.74rem] font-medium text-red-400"
          >
            <span>⚠</span> {error}
          </motion.p>
        ) : null}
      </AnimatePresence>
    </div>
  )
}
