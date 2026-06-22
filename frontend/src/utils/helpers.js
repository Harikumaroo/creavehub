/** Format mobile number for display: +91 98765 43210 */
export const formatMobileDisplay = (code, number) => {
  const d = number.replace(/\D/g, '')
  const fmt = d.length === 10 ? d.replace(/(\d{5})(\d{5})/, '$1 $2') : d
  return `${code} ${fmt}`
}

/** Strip all non-digits */
export const sanitizeDigits = (v) => v.replace(/\D/g, '')

/** Validate 10-digit phone */
export const isValidPhone = (v) => /^\d{10}$/.test(v.replace(/\D/g, ''))

/** Validate email */
export const isValidEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())

/** Validate name (≥2 chars) */
export const isValidName = (v) => v.trim().length >= 2

/** Extract error message from Axios error */
export const extractError = (err) => {
  const d = err?.response?.data
  if (!d) return 'Network error. Please try again.'
  if (typeof d.message === 'string') return d.message
  if (d.errors) {
    const first = Object.values(d.errors)[0]
    return Array.isArray(first) ? first[0] : first
  }
  return 'Something went wrong. Please try again.'
}

/** Trigger CSS shake on an element by ref */
export const shakeElement = (ref) => {
  if (!ref?.current) return
  ref.current.classList.remove('anim-shake')
  void ref.current.offsetWidth // reflow
  ref.current.classList.add('anim-shake')
  setTimeout(() => ref.current?.classList.remove('anim-shake'), 450)
}
