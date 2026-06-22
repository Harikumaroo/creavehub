import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { COUNTRY_CODES } from '../constants'

export default function PhoneInput({ value, onChange, error, countryCode = '+91', onCountryChange }) {
  const [open, setOpen] = useState(false)
  const ddRef = useRef(null)
  const selected = COUNTRY_CODES.find((c) => c.code === countryCode) || COUNTRY_CODES[0]

  /* Close dropdown on outside click */
  useEffect(() => {
    const handler = (e) => { if (ddRef.current && !ddRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const pick = (code) => { onCountryChange?.(code); setOpen(false) }

  return (
    <div className="ch-input-group">
      <label className="ch-label">Mobile Number</label>
      <div className="flex gap-2 relative">
        {/* Country selector */}
        <div ref={ddRef} className="relative">
          <motion.button
            type="button"
            onClick={() => setOpen((p) => !p)}
            className="ch-input flex items-center gap-2 cursor-pointer select-none whitespace-nowrap"
            style={{ width: 'auto', padding: '14px 12px', minWidth: 92 }}
            whileTap={{ scale: 0.97 }}
          >
            <span className="text-base">{selected.flag}</span>
            <span className="text-sm font-semibold">{selected.code}</span>
            <motion.svg
              width="10" height="6" viewBox="0 0 10 6" fill="none"
              animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }}
              className="opacity-40 flex-shrink-0"
            >
              <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </motion.svg>
          </motion.button>

          <AnimatePresence>
            {open && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.96 }}
                animate={{ opacity: 1, y: 4, scale: 1 }}
                exit={{ opacity: 0, y: -6, scale: 0.96 }}
                transition={{ duration: 0.18 }}
                className="absolute top-full left-0 z-50 min-w-[210px] rounded-2xl overflow-hidden overflow-y-auto"
                style={{
                  maxHeight: 240,
                  background: 'rgba(16,16,22,0.97)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  backdropFilter: 'blur(24px)',
                  boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
                }}
              >
                {COUNTRY_CODES.map((c) => (
                  <button
                    key={c.code}
                    type="button"
                    onClick={() => pick(c.code)}
                    className="flex items-center gap-3 w-full text-left px-4 py-3 text-sm transition-colors"
                    style={{
                      color: c.code === countryCode ? '#F26522' : 'rgba(240,239,244,0.85)',
                      background: c.code === countryCode ? 'rgba(232,71,10,0.08)' : 'transparent',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.05)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = c.code === countryCode ? 'rgba(232,71,10,0.08)' : 'transparent'}
                  >
                    <span className="text-base">{c.flag}</span>
                    <span className="flex-1 font-medium">{c.name}</span>
                    <span className="opacity-40 text-xs font-mono">{c.code}</span>
                  </button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Number input */}
        <input
          type="tel"
          inputMode="numeric"
          className={`ch-input flex-1 ${error ? 'has-error' : ''}`}
          placeholder={`${selected.maxLen}-digit number`}
          value={value}
          onChange={(e) => onChange?.(e.target.value.replace(/\D/g, '').slice(0, selected.maxLen))}
          maxLength={selected.maxLen}
          autoComplete="tel-national"
        />
      </div>

      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="ph-err"
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
