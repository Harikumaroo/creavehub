import { motion } from 'framer-motion'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from '../components/ThemeToggle'
import BackgroundBlobs from '../components/BackgroundBlobs'
import FloatingIcons from '../components/FloatingIcons'

const STATS = [
  { num: '2.4M+', label: 'Happy Foodies' },
  { num: '99.2%', label: 'On-time Delivery' },
  { num: '4.9 ★', label: 'App Rating' },
]

const FEATURES = [
  { icon: '⚡', text: 'AI Recommendations' },
  { icon: '🎯', text: '500+ Restaurants' },
  { icon: '🔮', text: 'Predictive Ordering' },
  { icon: '⏱', text: '20-min Delivery' },
]

const stagger = {
  animate: { transition: { staggerChildren: 0.09 } },
}
const item = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22,1,0.36,1] } },
}

function HeroPanel() {
  return (
    <motion.div
      variants={stagger}
      initial="initial"
      animate="animate"
      className="flex flex-col h-full justify-between py-11 px-12 relative z-10"
    >
      {/* Logo */}
      <motion.div variants={item} className="flex items-center gap-3">
        <div className="flex items-center justify-center w-10 h-10 rounded-[11px] text-xl"
          style={{ background:'linear-gradient(135deg,#E8470A,#F5893A)', boxShadow:'0 0 22px rgba(232,71,10,0.4)' }}>
          🍜
        </div>
        <div>
          <div className="font-extrabold text-[1.18rem] tracking-tight"
            style={{ fontFamily:"'Poppins',sans-serif" }}>
            CraveHub
          </div>
          <div className="text-[0.58rem] font-bold tracking-[0.13em] uppercase"
            style={{ color:'#F26522' }}>
            AI Food Intelligence
          </div>
        </div>
      </motion.div>

      {/* Main hero */}
      <div className="flex-1 flex flex-col justify-center py-10 max-w-[440px]">
        {/* AI Badge */}
        <motion.div variants={item}
          className="inline-flex items-center gap-2 px-4 py-[7px] rounded-full mb-7 text-[0.7rem] font-bold tracking-[0.09em] uppercase w-fit"
          style={{ background:'rgba(232,71,10,0.09)', border:'1px solid rgba(232,71,10,0.2)', color:'#F26522' }}>
          <span className="w-[6px] h-[6px] rounded-full bg-[#E8470A] anim-pulse-dot inline-block" />
          Powered by Generative AI
        </motion.div>

        {/* Headline */}
        <motion.h1 variants={item}
          className="leading-[1.07] mb-5 tracking-[-0.03em]"
          style={{ fontFamily:"'Playfair Display',Georgia,serif", fontWeight:800, fontSize:'3.3rem' }}>
          Order Smarter.<br />
          <em className="text-brand-grad not-italic">Eat Better.</em><br />
          Always.
        </motion.h1>

        <motion.p variants={item}
          className="text-[0.95rem] font-light leading-[1.78] mb-9 text-muted">
          CraveHub uses real-time AI to personalise every order, predict your cravings, and connect you to the city's finest kitchens — all in one seamless experience.
        </motion.p>

        {/* Feature pills */}
        <motion.div variants={item} className="flex flex-wrap gap-2.5">
          {FEATURES.map((f) => (
            <div key={f.text}
              className="flex items-center gap-2 px-3.5 py-2 rounded-full text-[0.78rem] font-medium text-muted"
              style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.07)', transition:'all 0.25s' }}
              onMouseEnter={(e) => { e.currentTarget.style.background='rgba(255,255,255,0.08)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.13)' }}
              onMouseLeave={(e) => { e.currentTarget.style.background='rgba(255,255,255,0.04)'; e.currentTarget.style.borderColor='rgba(255,255,255,0.07)' }}
            >
              <span>{f.icon}</span> {f.text}
            </div>
          ))}
        </motion.div>
      </div>

      {/* Stats */}
      <motion.div variants={item}
        className="flex gap-9 pt-8"
        style={{ borderTop:'1px solid rgba(255,255,255,0.07)' }}>
        {STATS.map((s) => (
          <div key={s.label}>
            <div className="font-extrabold text-[1.6rem] tracking-[-0.03em]"
              style={{ fontFamily:"'Poppins',sans-serif" }}>
              {s.num}
            </div>
            <div className="text-[0.68rem] font-semibold tracking-[0.08em] uppercase text-faint mt-0.5">
              {s.label}
            </div>
          </div>
        ))}
      </motion.div>
    </motion.div>
  )
}

export default function AuthLayout({ children }) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      <BackgroundBlobs />
      <ThemeToggle />

      {/* ── LEFT HERO (desktop only) ── */}
      <div className="relative hidden lg:flex flex-col w-[52%] overflow-hidden">
        <FloatingIcons count={14} />
        <HeroPanel />
        {/* Vertical separator */}
        <div className="absolute right-0 top-[10%] bottom-[10%] w-px"
          style={{ background:'linear-gradient(to bottom,transparent,rgba(255,255,255,0.09),transparent)' }} />
      </div>

      {/* ── RIGHT AUTH PANEL ── */}
      <div className="flex-1 flex flex-col items-center justify-center relative z-10 p-6 sm:p-10 lg:p-12 min-h-screen">

        {/* Mobile logo (visible only on small) */}
        <Link to="/auth/login" className="flex items-center gap-2.5 mb-8 lg:hidden">
          <div className="flex items-center justify-center w-9 h-9 rounded-[10px] text-lg"
            style={{ background:'linear-gradient(135deg,#E8470A,#F5893A)', boxShadow:'0 0 16px rgba(232,71,10,0.4)' }}>
            🍜
          </div>
          <span className="font-extrabold text-[1.1rem] tracking-tight">CraveHub</span>
        </Link>

        {/* Animated card entrance */}
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 24, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -18, scale: 0.97 }}
          transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-[428px]"
        >
          {children}
        </motion.div>
      </div>
    </div>
  )
}
