import { useState, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import AuthLayout from '../layouts/AuthLayout'
import PhoneInput from '../components/PhoneInput'
import PrimaryButton from '../components/PrimaryButton'
import SocialLoginButton from '../components/SocialLoginButton'
import { authApi } from '../api/authApi'
import { isValidPhone, extractError, shakeElement, formatMobileDisplay } from '../utils/helpers'

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
    <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57C21.36 18.1 22.56 15.35 22.56 12.25z" fill="#4285F4"/>
    <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
    <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
    <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
  </svg>
)
const AppleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.7 9.05 7.4c1.36.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.39-1.32 2.76-2.53 3.99zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
  </svg>
)

const fadeItem = {
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22,1,0.36,1] } },
}
const staggerWrap = { animate: { transition: { staggerChildren: 0.07 } } }

export default function Login() {
  const navigate  = useNavigate()
  const phoneRef  = useRef(null)

  const [country, setCountry] = useState('+91')
  const [phone,   setPhone]   = useState('')
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [apiErr,  setApiErr]  = useState('')

  const validate = () => {
    if (!isValidPhone(phone)) { setError('Enter a valid 10-digit mobile number'); shakeElement(phoneRef); return false }
    setError('')
    return true
  }

  const handleGetOTP = async () => {
    if (!validate()) return
    setLoading(true); setApiErr('')
    const mobile = `${country}${phone}`
    try {
      await authApi.loginMobile(mobile)
      navigate('/auth/otp', {
        state: {
          flow:   'login',
          mobile,
          display: formatMobileDisplay(country, phone),
        },
      })
    } catch (err) {
      const msg = extractError(err)
      /* 404 = not registered */
      if (err?.response?.status === 404) {
        setApiErr("This number isn't registered. Create an account first.")
      } else {
        setApiErr(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout>
      <div className="auth-card" ref={phoneRef}>
        <motion.div variants={staggerWrap} initial="initial" animate="animate">

          {/* Header */}
          <motion.div variants={fadeItem} className="mb-7">
            <div className="flex items-center gap-2 mb-3">
              <span className="block w-5 h-[1.5px] bg-[#F26522] rounded" />
              <span className="text-[0.68rem] font-bold tracking-[0.12em] uppercase" style={{color:'#F26522'}}>
                Step 1 of 2
              </span>
            </div>
            <h2 className="text-[1.7rem] font-extrabold tracking-[-0.025em] leading-[1.2] mb-2"
              style={{fontFamily:"'Poppins',sans-serif"}}>
              Welcome back 👋
            </h2>
            <p className="text-[0.875rem] text-muted font-light leading-relaxed">
              Enter your mobile number to continue your food journey.
            </p>
          </motion.div>

          {/* Social login */}
          <motion.div variants={fadeItem} className="grid grid-cols-2 gap-2.5 mb-1">
            <SocialLoginButton
              icon={<GoogleIcon />}
              label="Google"
              onClick={() => console.log('Google OAuth')}
            />
            <SocialLoginButton
              icon={<AppleIcon />}
              label="Apple"
              onClick={() => console.log('Apple OAuth')}
            />
          </motion.div>

          <motion.div variants={fadeItem} className="ch-divider">or with mobile</motion.div>

          {/* Phone input */}
          <motion.div variants={fadeItem}>
            <PhoneInput
              value={phone}
              onChange={(v) => { setPhone(v); if (error) setError('') }}
              error={error}
              countryCode={country}
              onCountryChange={setCountry}
            />
          </motion.div>

          {/* API error */}
          <AnimatePresence>
            {apiErr ? (
              <motion.div
                initial={{ opacity:0, height:0 }}
                animate={{ opacity:1, height:'auto' }}
                exit={{ opacity:0, height:0 }}
                className="mb-3 px-4 py-3 rounded-xl text-sm text-red-400 font-medium"
                style={{ background:'rgba(239,68,68,0.08)', border:'1px solid rgba(239,68,68,0.15)' }}
              >
                {apiErr}
              </motion.div>
            ) : null}
          </AnimatePresence>

          {/* CTA */}
          <motion.div variants={fadeItem}>
            <PrimaryButton loading={loading} onClick={handleGetOTP}>
              <span>Get OTP</span>
              <motion.span
                animate={{ x: loading ? 0 : [0, 4, 0] }}
                transition={{ repeat: Infinity, duration: 1.6, ease: 'easeInOut' }}
                className="text-base"
              >
                →
              </motion.span>
            </PrimaryButton>
          </motion.div>

          {/* Register link */}
          <motion.p variants={fadeItem} className="text-center text-[0.8rem] text-muted mt-5">
            New to CraveHub?{' '}
            <Link to="/auth/register" className="font-semibold hover:underline"
              style={{color:'#F26522'}}>
              Create account
            </Link>
          </motion.p>

          {/* Terms */}
          <motion.p variants={fadeItem}
            className="text-center text-[0.7rem] text-faint leading-relaxed mt-3">
            By continuing you agree to our{' '}
            <a href="#" className="underline">Terms of Service</a> &amp;{' '}
            <a href="#" className="underline">Privacy Policy</a>
          </motion.p>
        </motion.div>
      </div>
    </AuthLayout>
  )
}
