import { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate, Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AuthLayout from '../layouts/AuthLayout'
import OTPInput from '../components/OTPInput'
import PrimaryButton from '../components/PrimaryButton'
import BackgroundBlobs from '../components/BackgroundBlobs'
import ThemeToggle from '../components/ThemeToggle'
import { authApi } from '../api/authApi'
import { getDeviceInfo } from '../utils/deviceInfo'
import { extractError } from '../utils/helpers'
import { useAuthCtx } from '../store/authStore'
import { OTP_LENGTH, OTP_RESEND_SECONDS } from '../constants'

function SuccessOverlay({ name }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center"
      style={{ background: 'rgba(12,12,15,0.97)', backdropFilter:'blur(20px)' }}
    >
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, type:'spring', stiffness:220, damping:18 }}
        className="flex items-center justify-center w-24 h-24 rounded-full text-4xl mb-6"
        style={{
          background: 'rgba(34,197,94,0.12)',
          border: '2px solid rgba(34,197,94,0.4)',
          boxShadow: '0 0 40px rgba(34,197,94,0.2)',
        }}
      >
        ✓
      </motion.div>
      <motion.h2
        initial={{ opacity:0, y:14 }}
        animate={{ opacity:1, y:0 }}
        transition={{ delay: 0.3 }}
        className="text-[1.75rem] font-extrabold tracking-tight mb-2"
        style={{ fontFamily:"'Poppins',sans-serif" }}
      >
        Welcome{name ? `, ${name}` : ' to CraveHub'}! 🎉
      </motion.h2>
      <motion.p
        initial={{ opacity:0, y:10 }}
        animate={{ opacity:1, y:0 }}
        transition={{ delay: 0.42 }}
        className="text-muted text-sm"
      >
        Your AI food experience begins now…
      </motion.p>
    </motion.div>
  )
}

export default function OtpVerify() {
  const { state } = useLocation()
  const navigate  = useNavigate()
  const { login } = useAuthCtx()

  const flow      = state?.flow    || 'login'
  const mobile    = state?.mobile  || ''
  const display   = state?.display || mobile
  const firstName = state?.firstName || ''
  const lastName  = state?.lastName  || ''
  const email     = state?.email    || ''

  const [otp,       setOtp]       = useState('')
  const [error,     setError]     = useState('')
  const [loading,   setLoading]   = useState(false)
  const [verified,  setVerified]  = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [timer,     setTimer]     = useState(OTP_RESEND_SECONDS)
  const [canResend, setCanResend] = useState(false)
  const [resending, setResending] = useState(false)
  const [debugOtp,  setDebugOtp]  = useState(state?.debugOtp || '')
  const timerRef = useRef(null)

  /* Redirect guard */
  useEffect(() => {
    if (!mobile) navigate('/auth/login', { replace: true })
  }, [mobile, navigate])

  /* Countdown */
  useEffect(() => {
    startTimer()
    return () => clearInterval(timerRef.current)
  }, [])

  const startTimer = () => {
    setTimer(OTP_RESEND_SECONDS)
    setCanResend(false)
    clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setTimer((t) => {
        if (t <= 1) { clearInterval(timerRef.current); setCanResend(true); return 0 }
        return t - 1
      })
    }, 1000)
  }

  const handleVerify = async () => {
    if (otp.length < OTP_LENGTH) { setError('Enter all 6 digits'); return }
    setLoading(true); setError('')
    try {
      const device = getDeviceInfo()
      let data

      if (flow === 'login') {
        /* Step 2 login: verify OTP → get tokens */
        const res = await authApi.loginVerifyOtp({ mobile_number: mobile, otp, ...device })
        data = res.data?.data
      } else {
        /* Step 2 register: verify OTP */
        await authApi.registerVerifyOtp(mobile, otp)
        /* Step 3 register: complete profile → get tokens */
        const res = await authApi.registerComplete({
          mobile_number: mobile,
          full_name: `${firstName} ${lastName}`.trim(),
          email: email || undefined,
          ...device,
        })
        data = res.data?.data
      }

      /* Save tokens + user in store */
      if (data?.access_token) {
        login(data)
        setVerified(true)
        setShowSuccess(true)
        setTimeout(() => navigate("/dashboard", { replace: true }), 2200)
      }
    } catch (err) {
      setError(extractError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    if (!canResend || resending) return
    setResending(true); setError(''); setOtp('')
    try {
      let res
      if (flow === 'login') res = await authApi.loginMobile(mobile)
      else                  res = await authApi.registerMobile(mobile)
      const newDebugOtp = res?.data?.data?.debug_otp
      if (newDebugOtp) setDebugOtp(newDebugOtp)
      startTimer()
    } catch (err) {
      setError(extractError(err))
    } finally {
      setResending(false)
    }
  }

  const backPath = flow === 'login' ? '/auth/login' : '/auth/register'

  return (
    <>
      <AnimatePresence>
        {showSuccess && (
          <SuccessOverlay name={firstName || state?.user?.full_name?.split(' ')[0]} />
        )}
      </AnimatePresence>

      <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden px-5 py-10">
        <BackgroundBlobs />
        <ThemeToggle />

        <motion.div
          initial={{ opacity:0, y:24, scale:0.97 }}
          animate={{ opacity:1, y:0, scale:1 }}
          transition={{ duration:0.45, ease:[0.22,1,0.36,1] }}
          className="w-full max-w-[440px]"
        >
          {/* Back button */}
          <motion.div
            initial={{ opacity:0, x:-10 }}
            animate={{ opacity:1, x:0 }}
            transition={{ delay:0.1 }}
            className="mb-6"
          >
            <Link
              to={backPath}
              className="inline-flex items-center gap-2 text-sm font-semibold text-muted px-4 py-2.5 rounded-xl transition-all"
              style={{
                background:'rgba(255,255,255,0.04)',
                border:'1px solid rgba(255,255,255,0.08)',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background='rgba(255,255,255,0.08)'}
              onMouseLeave={(e) => e.currentTarget.style.background='rgba(255,255,255,0.04)'}
            >
              ← Back
            </Link>
          </motion.div>

          <div className="auth-card">
            {/* Logo */}
            <motion.div
              initial={{ opacity:0, y:10 }}
              animate={{ opacity:1, y:0 }}
              transition={{ delay:0.12 }}
              className="flex items-center justify-center gap-2.5 mb-7"
            >
              <div className="flex items-center justify-center w-9 h-9 rounded-[10px] text-lg"
                style={{ background:'linear-gradient(135deg,#E8470A,#F5893A)', boxShadow:'0 0 18px rgba(232,71,10,0.4)' }}>
                🍜
              </div>
              <span className="font-extrabold text-[1.1rem] tracking-tight">CraveHub</span>
            </motion.div>

            {/* Header */}
            <motion.div
              initial={{ opacity:0, y:12 }}
              animate={{ opacity:1, y:0 }}
              transition={{ delay:0.18 }}
              className="text-center mb-2"
            >
              <div className="flex items-center justify-center gap-2 mb-3">
                <span className="block w-5 h-[1.5px] bg-[#F26522] rounded" />
                <span className="text-[0.68rem] font-bold tracking-[0.12em] uppercase" style={{color:'#F26522'}}>
                  Step 2 of {flow === 'register' ? '3' : '2'}
                </span>
                <span className="block w-5 h-[1.5px] bg-[#F26522] rounded" />
              </div>
              <h2 className="text-[1.65rem] font-extrabold tracking-[-0.025em] leading-[1.2] mb-2"
                style={{fontFamily:"'Poppins',sans-serif"}}>
                Verify your number 🔐
              </h2>
              <p className="text-[0.875rem] text-muted font-light">
                We sent a 6-digit code to
              </p>
            </motion.div>

            {/* Phone display */}
            <motion.div
              initial={{ opacity:0 }}
              animate={{ opacity:1 }}
              transition={{ delay:0.24 }}
              className="text-center mb-1"
            >
              <span className="font-bold text-[1.15rem] tracking-wide">
                {display}
              </span>
              <Link
                to={backPath}
                className="block text-[0.73rem] font-medium mt-1 hover:underline"
                style={{color:'#F26522'}}
              >
                Change number
              </Link>
            </motion.div>

            {/* Dev-mode OTP hint banner */}
            {debugOtp && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.4, ease: [0.22,1,0.36,1] }}
                className="mb-4 mx-auto w-full rounded-2xl overflow-hidden"
                style={{
                  background: 'linear-gradient(135deg, rgba(251,191,36,0.08) 0%, rgba(245,137,58,0.10) 100%)',
                  border: '1px solid rgba(251,191,36,0.28)',
                  boxShadow: '0 0 28px rgba(251,191,36,0.07)',
                }}
              >
                <div className="flex items-center gap-2 px-3.5 pt-3 pb-1.5"
                  style={{ borderBottom: '1px solid rgba(251,191,36,0.15)' }}
                >
                  <span className="text-sm">🛠️</span>
                  <span className="text-[0.65rem] font-bold tracking-[0.12em] uppercase"
                    style={{ color: '#FBBF24' }}
                  >
                    Dev Mode — OTP Bypass
                  </span>
                </div>
                <div className="flex items-center justify-between px-3.5 py-3">
                  <span className="text-[0.75rem] text-muted font-medium">Your OTP is</span>
                  <span
                    className="font-extrabold text-[1.55rem] tracking-[0.22em] tabular-nums select-all"
                    style={{
                      fontFamily: "'Poppins',monospace",
                      background: 'linear-gradient(90deg,#F5893A,#FBBF24)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      letterSpacing: '0.2em',
                    }}
                  >
                    {debugOtp}
                  </span>
                </div>
              </motion.div>
            )}

            {/* OTP boxes */}
            <OTPInput
              value={otp}
              onChange={(v) => { setOtp(v); if(error) setError('') }}
              error={error}
              verified={verified}
              autoFocus
            />

            {/* Resend row */}
            <motion.div
              initial={{ opacity:0 }}
              animate={{ opacity:1 }}
              transition={{ delay:0.35 }}
              className="text-center mb-5 text-sm"
            >
              {!canResend ? (
                <span className="text-muted">
                  Resend code in{' '}
                  <span className="font-bold tabular-nums" style={{color:'#F26522'}}>
                    {String(Math.floor(timer/60)).padStart(2,'0')}:{String(timer%60).padStart(2,'0')}
                  </span>
                </span>
              ) : (
                <button
                  onClick={handleResend}
                  disabled={resending}
                  className="font-semibold hover:underline transition-opacity"
                  style={{
                    color:'#F26522',
                    background:'none', border:'none', cursor:'pointer',
                    opacity: resending ? 0.5 : 1,
                  }}
                >
                  {resending ? 'Sending…' : 'Resend OTP'}
                </button>
              )}
            </motion.div>

            {/* Verify button */}
            <PrimaryButton
              loading={loading}
              disabled={otp.length < OTP_LENGTH}
              successMode={verified}
              onClick={handleVerify}
            >
              <span>Verify &amp; Continue</span>
              <motion.span
                animate={{ x: loading||verified ? 0 : [0,4,0] }}
                transition={{ repeat:Infinity, duration:1.6, ease:'easeInOut' }}
                className="text-base"
              >→</motion.span>
            </PrimaryButton>

            {/* Security badge */}
            <div className="glow-line" />
            <div className="text-center">
              <p className="text-[0.68rem] text-faint mb-1 font-medium">Protected by</p>
              <div className="flex items-center justify-center gap-1.5 text-[0.78rem] text-muted font-semibold">
                🔒 256-bit AES Encryption
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </>
  )
}
