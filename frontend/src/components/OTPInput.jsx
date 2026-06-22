import { useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { OTP_LENGTH } from '../constants'

export default function OTPInput({ value = '', onChange, error, verified = false, autoFocus = true }) {
  const inputsRef = useRef([])
  const digits = Array.from({ length: OTP_LENGTH }, (_, i) => value[i] || '')

  useEffect(() => {
    if (autoFocus) setTimeout(() => inputsRef.current[0]?.focus(), 300)
  }, [autoFocus])

  const updateValue = (arr) => onChange?.(arr.join(''))

  const handleChange = (i, raw) => {
    const cleaned = raw.replace(/\D/g, '')
    if (!cleaned) return

    if (cleaned.length > 1) {
      /* Paste scenario */
      const pasted = cleaned.slice(0, OTP_LENGTH)
      const arr = Array.from({ length: OTP_LENGTH }, (_, k) => pasted[k] || '')
      updateValue(arr)
      const next = Math.min(pasted.length, OTP_LENGTH - 1)
      inputsRef.current[next]?.focus()
      return
    }
    const arr = [...digits]
    arr[i] = cleaned
    updateValue(arr)
    if (i < OTP_LENGTH - 1) inputsRef.current[i + 1]?.focus()
  }

  const handleKeyDown = (i, e) => {
    if (e.key === 'Backspace') {
      e.preventDefault()
      if (digits[i]) {
        const arr = [...digits]; arr[i] = ''; updateValue(arr)
      } else if (i > 0) {
        const arr = [...digits]; arr[i - 1] = ''; updateValue(arr)
        inputsRef.current[i - 1]?.focus()
      }
    }
    if (e.key === 'ArrowLeft'  && i > 0)              inputsRef.current[i - 1]?.focus()
    if (e.key === 'ArrowRight' && i < OTP_LENGTH - 1) inputsRef.current[i + 1]?.focus()
  }

  const getBoxClass = (digit) => {
    if (verified && digit) return 'otp-box verified'
    if (digit)             return 'otp-box filled'
    return 'otp-box'
  }

  return (
    <div>
      <div className="flex gap-2.5 sm:gap-3 justify-center my-8">
        {digits.map((digit, i) => (
          <motion.input
            key={i}
            ref={(el) => (inputsRef.current[i] = el)}
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            className={getBoxClass(digit)}
            value={digit}
            onChange={(e) => handleChange(i, e.target.value)}
            onKeyDown={(e) => handleKeyDown(i, e)}
            maxLength={6}
            autoComplete="one-time-code"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06, duration: 0.3 }}
          />
        ))}
      </div>

      <AnimatePresence mode="wait">
        {error ? (
          <motion.p
            key="otp-err"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="text-center text-red-400 text-sm font-medium flex items-center justify-center gap-1.5"
          >
            <span>⚠</span> {error}
          </motion.p>
        ) : null}
      </AnimatePresence>
    </div>
  )
}
