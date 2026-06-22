import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthCtx } from '../store/authStore'
import { dashboardApi } from '../api/dashboardApi'
import { profileApi } from '../api/profileApi'
import RestaurantView from '../components/RestaurantView'
import LocationDrawer from '../components/LocationDrawer'
import InstamartPage from './InstamartPage'
import DiningPage from './DiningPage'
import PartiesPage from './PartiesPage'
import GiftsPage from './GiftsPage'
import CateringPage from './CateringPage'
import SupportCenter from './SupportCenter'
import { useSettings } from '../context/SettingsContext'

/* ── Design tokens ─────────────────────────────────────────── */
const C = {
  saffron: 'var(--c-saffron, #FC8019)', amber: 'var(--c-amber, #FF9E2A)', tomato: 'var(--c-tomato, #E25E1A)',
  cream: 'var(--c-cream, #FDF6EE)',   warm: 'var(--c-warm, #FFFFFF)', charcoal: 'var(--c-charcoal, #02060C)',
  bark: 'var(--c-bark, #02060C99)',  mocha: 'var(--c-mocha, #02060CEB)', sand: 'var(--c-sand, #F0F0F5)',
  sage: 'var(--c-sage, #118C4F)',    cardBg: 'var(--c-cardBg, #FFFFFF)', border: 'var(--c-border, #F0F0F5)',
  muted: 'var(--c-muted, #02060C99)', bg: 'var(--c-bg, #F0F0F5)',
  maroon: 'var(--c-maroon, #6B0B22)',  maroonLight: '#8A1538',
  lightGray: '#F2F6FC'
}
const font = "'Proxima Nova', 'Inter', system-ui, sans-serif"

/* ── Skeleton ──────────────────────────────────────────────── */
function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: r, marginBottom: mb,
      background: `linear-gradient(90deg,${C.sand} 25%,#FDE8CC 50%,${C.sand} 75%)`,
      backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite',
    }} />
  )
}

function Section({ children, style = {} }) {
  return <div style={{ background: C.cardBg, marginBottom: 8, ...style }}>{children}</div>
}

function SectionHead({ title, sub, emoji, onSeeAll }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', padding: '18px 16px 10px' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {emoji && <span style={{ fontSize: 18 }}>{emoji}</span>}
          <span style={{ fontSize: 16, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{title}</span>
        </div>
        {sub && <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>{sub}</div>}
      </div>
      {onSeeAll && (
        <button onClick={onSeeAll} style={{ background: 'none', border: 'none', color: C.saffron, fontSize: 12, fontWeight: 700, cursor: 'pointer', fontFamily: font }}>
          See All →
        </button>
      )}
    </div>
  )
}

/* ── Top Navigation & Search ─────────────────────────────────── */
function Header({ user, notifCount, onNotif, onLocationClick, onProfileClick, selectedAddress }) {
  return (
    <div className="px-4 pt-5 pb-3 sticky top-0 z-50 flex justify-between items-center bg-[#FC8019]">
      <div onClick={onLocationClick} className="flex flex-col cursor-pointer group">
        <div className="flex items-center gap-1.5 text-white/80 text-[11px] font-bold mb-0.5">
          <span className="text-white text-base">📍</span>
          Deliver to
        </div>
        <div className="flex items-center gap-1">
          <span className="text-[15px] font-extrabold text-white transition-colors truncate max-w-[200px]">
            {selectedAddress?.label || 'Select the delivery address'}
          </span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-white/80 ml-0.5 mt-0.5">
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div onClick={onNotif} className="relative cursor-pointer">
          <span className="text-[24px] text-white">🔔</span>
          <span className="absolute -top-1 -right-1 bg-white text-[#FC8019] rounded-full text-[9px] font-black w-[18px] h-[18px] flex items-center justify-center border-2 border-[#FC8019] shadow-sm">{notifCount > 0 ? notifCount : 3}</span>
        </div>
        <div onClick={onProfileClick} className="w-10 h-10 rounded-full overflow-hidden cursor-pointer border-2 border-white/20 shadow-sm flex items-center justify-center bg-[#E06A11]">
          {user?.avatar ? (
            <img src={user.avatar} alt="Profile" className="w-full h-full object-cover" />
          ) : (
            <span className="text-xl">👤</span>
          )}
        </div>
      </div>
    </div>
  )
}

function GreetingSection({ user, onAI }) {
  const { t } = useSettings()
  const name = user?.full_name?.split(' ')[0] || 'Hari'
  return (
    <div className="px-4 pb-4 flex justify-between items-end" style={{ background: 'var(--c-saffron)' }}>
      <div>
        <div className="text-white/90 text-sm font-semibold mb-1 flex items-center gap-1.5">
          {t('Good Evening')}, {name} <span className="text-base">🌙</span>
        </div>
        <div className="text-white text-[22px] font-black leading-tight tracking-tight">
          {t('What are you craving today?')}
        </div>
      </div>
      <button onClick={onAI} className="bg-gradient-to-r from-brand-amber via-pink-500 to-purple-600 text-white px-4 py-2.5 rounded-full font-bold text-xs shadow-md flex items-center gap-1.5 hover:scale-105 transition-transform">
        <span className="text-sm">✨</span> CraveHub AI
      </button>
    </div>
  )
}

function SearchBar({ onSearch }) {
  const { t } = useSettings()
  const [q, setQ] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)

  const handleChange = async (e) => {
    const val = e.target.value
    setQ(val)
    if (val.length >= 1) {
      try {
        const res = await dashboardApi.getSuggestions(val)
        if (res.data?.success) {
          setSuggestions(res.data.data.suggestions || [])
          setShowDropdown(true)
        }
      } catch (err) {}
    } else {
      setSuggestions([])
      setShowDropdown(false)
    }
  }

  const handleSubmit = (searchVal) => {
    setShowDropdown(false)
    if (searchVal.trim()) {
      onSearch?.(searchVal)
    }
  }

  return (
    <div className="px-4 pb-4 pt-2 relative" style={{ background: 'var(--c-saffron)', position: 'sticky', top: 60, zIndex: 40 }}>
      <div className="w-full bg-white rounded-2xl h-[52px] flex items-center px-4 shadow-sm gap-3 overflow-hidden">
        <span className="text-xl">🔍</span>
        <input 
          value={q} 
          onChange={handleChange}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit(q)}
          onFocus={() => q.length >= 1 && setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
          placeholder={t('Search food, restaurants, groceries, cuisines...')}
          className="flex-1 bg-transparent border-none outline-none text-[#02060C99] text-[13px] font-bold"
        />
      </div>
      
      {showDropdown && suggestions.length > 0 && (
        <div className="absolute left-4 right-4 top-[74px] bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50 max-h-[300px] overflow-y-auto">
          {suggestions.map((sug, i) => (
            <div 
              key={i} 
              onClick={() => { setQ(sug); handleSubmit(sug); }}
              className="px-4 py-3 border-b border-gray-50 text-[13px] font-bold text-gray-800 hover:bg-gray-50 cursor-pointer flex items-center gap-3"
            >
              <span className="text-gray-400">🔍</span> {sug}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function FilterPills({ onFilter }) {
  const pills = ['Biryani', 'Pizza', 'Burger', 'Healthy', 'Desserts', 'North Indian', 'South Indian', 'Chinese', 'Street Food', 'Cakes', 'Rolls', 'Sandwich', 'More ⌄']
  return (
    <div className="px-4 pb-5 flex gap-2.5 overflow-x-auto no-scrollbar" style={{ background: '#FC8019' }}>
      {pills.map((pill, i) => (
        <button 
          key={i} 
          onClick={() => {
            if (pill !== 'More ⌄') onFilter?.(pill)
          }}
          className="whitespace-nowrap px-4 py-2 rounded-full border border-gray-200 text-[13px] font-bold text-brand-charcoal bg-white hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
        >
          {pill}
        </button>
      ))}
    </div>
  )
}

/* ── AI Recommendation Banner ────────────────────────────────── */
function AIBanner({ selectedAddress, onSearch }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let lat = 13.08
    let lng = 80.27
    if (selectedAddress?.latitude && selectedAddress?.longitude) {
      lat = selectedAddress.latitude
      lng = selectedAddress.longitude
    }
    
    setLoading(true)
    dashboardApi.getWeatherFood(lat, lng)
      .then(res => {
        setData(res.data?.data || null)
      })
      .catch(err => {
        console.error('Weather food err:', err)
        setData(null)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [selectedAddress])

  if (loading || !data) {
    return (
      <div className="px-4 pb-4" style={{ background: '#FC8019' }}>
        <div className="relative rounded-[22px] overflow-hidden shadow-xl h-[210px] p-5 flex flex-col justify-center" style={{ background: '#7c2d12' }}>
          <Skel w={120} h={20} r={10} mb={20} />
          <Skel w={200} h={20} r={10} mb={10} />
          <Skel w={250} h={30} r={10} mb={10} />
          <Skel w={150} h={20} r={10} />
        </div>
      </div>
    )
  }

  const colors = (() => {
    const c = data.condition || 'Cloudy';
    const t = data.temp || 25;
    if (t >= 32) return { bg: '#991b1b', light: '#dc2626' }; // Hot red
    if (t > 25 && c === 'Clear') return { bg: '#c2410c', light: '#ea580c' }; // Warm orange
    switch (c) {
      case 'Clear': return { bg: '#0369a1', light: '#0ea5e9' }; // Sky blue
      case 'Rainy': return { bg: '#1e3a8a', light: '#3b82f6' }; // Deep blue
      case 'Stormy': return { bg: '#312e81', light: '#4f46e5' }; // Indigo
      case 'Snowy': return { bg: '#0f766e', light: '#14b8a6' }; // Teal
      case 'Foggy': return { bg: '#475569', light: '#64748b' }; // Slate
      case 'Cloudy': return { bg: '#7c2d12', light: '#9a3412' }; // Brown
      default: return { bg: '#7c2d12', light: '#9a3412' };
    }
  })();

  return (
    <div className="px-4 pb-4" style={{ background: '#FC8019' }}>
      <div className="relative rounded-[22px] overflow-hidden shadow-xl" style={{ background: colors.bg }}>
        {/* Background gradient and image */}
        <div className="absolute inset-0 opacity-40">
           <img src="https://images.unsplash.com/photo-1550547660-d9450f859349?w=800&h=400&fit=crop" className="w-full h-full object-cover blur-sm" />
        </div>
        <div className="absolute inset-0" style={{ background: `linear-gradient(to right, ${colors.bg}, ${colors.bg}F2, transparent)` }} />
        
        <div className="relative z-10 flex flex-row items-center h-[210px]">
          <div className="p-5 flex-1 pr-0 z-20">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/10 border border-white/20 text-[9px] font-bold text-white/90 tracking-widest uppercase mb-4 backdrop-blur-md">
              <span className="text-brand-saffron">✨</span> AI RECOMMENDATION
            </div>
            <h2 className="text-white font-extrabold text-[16px] leading-tight mb-1">{data.weather_title || 'Cozy day detected ☁️'}</h2>
            <h1 className="text-white font-black text-[24px] leading-tight mb-1">{data.food_name || 'Hot Coffee & Snacks'}</h1>
            <p className="text-white/90 font-bold text-[14px] mb-5">{data.reason || 'Perfect for this weather!'}</p>
            <button 
              onClick={() => onSearch && onSearch(data.search_term || data.food_name)}
              className="bg-gradient-to-r from-brand-saffron to-[#E84E6E] text-white px-5 py-2.5 rounded-full font-bold text-[13px] shadow-[0_4px_15px_rgba(232,78,110,0.5)] hover:scale-105 transition-transform flex items-center gap-1.5">
              Order Now <span className="text-base leading-none">→</span>
            </button>
          </div>
          
          <div className="absolute right-[-50px] top-1/2 transform -translate-y-1/2 w-[270px] h-[270px] z-10">
            <img src="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500&h=500&fit=crop" alt="Food" className="w-full h-full object-cover rounded-full shadow-[0_10px_40px_rgba(0,0,0,0.6)] border-[6px]" style={{ borderColor: `${colors.bg}80` }} />
            <div className="absolute bottom-[40px] right-[65px] backdrop-blur-md border border-white/10 text-white text-[10px] font-bold px-3.5 py-2 rounded-[14px] flex items-center gap-2.5 shadow-2xl" style={{ background: `${colors.light}E6` }}>
              <span className="text-[20px] leading-none">{data.tag_emoji || '☁️'}</span> <span className="leading-tight">{data.tag || 'Weather Special'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Services Hub ────────────────────────────────────────────── */
const SERVICES = [
  { id: 'home', icon: '🍔', label: 'Food' },
  { id: 'instamart', icon: '🛒', label: 'Instamart' },
  { id: 'dining', icon: '🍽️', label: 'Dineout' },
  { id: 'party', icon: '🎉', label: 'Party' },
  { id: 'gifts', icon: '🎁', label: 'Gifts' },
  { id: 'catering', icon: '👨‍🍳', label: 'Catering' },
]

function ServiceHub({ activeService, onService }) {
  return (
    <div className="pt-3 pb-0" style={{ background: '#FC8019' }}>
      <div className="flex px-2 overflow-x-auto no-scrollbar gap-1">
        {SERVICES.map((s, i) => {
          const isActive = activeService === s.id;
          return (
            <div
              key={s.id}
              onClick={() => onService?.(s.id)}
              className="relative flex-1 min-w-[72px] flex flex-col items-center justify-center cursor-pointer transition-all duration-300"
              style={{
                padding: '12px 4px 16px',
                background: isActive ? '#FFFFFF' : 'rgba(255,255,255,0.15)',
                borderRadius: isActive ? '24px 24px 0 0' : '20px 20px 0 0',
                borderTopRightRadius: isActive ? '12px' : '20px',
                borderBottom: 'none',
                opacity: isActive ? 1 : 0.85,
                transform: isActive ? 'scale(1)' : 'scale(0.95) translateY(4px)',
                zIndex: isActive ? 10 : 1,
              }}
            >
              <div className="text-[32px] mb-1 drop-shadow-md transition-transform duration-300" style={{ transform: isActive ? 'scale(1.1)' : 'scale(1)' }}>
                {s.icon}
              </div>
              <span className={`text-[12px] font-extrabold text-center leading-tight ${isActive ? 'text-[#FC8019]' : 'text-white'}`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  )
}

/* ── Category Pills ──────────────────────────────────────────── */
function CategoryRow({ onSelect }) {
  const [showAll, setShowAll] = useState(false);
  const items = [
    { name: 'Biryani', query: 'Biryani', image: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop' },
    { name: 'Pizza', query: 'Pizza', image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=200&h=200&fit=crop' },
    { name: 'Burgers', query: 'Burger', image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=200&h=200&fit=crop' },
    { name: 'South Indian', query: 'South Indian', image: 'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=200&h=200&fit=crop' },
    { name: 'Chinese', query: 'Chinese', image: 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=200&h=200&fit=crop' },
    { name: 'Desserts', query: 'Dessert', image: 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=200&h=200&fit=crop' },
    { name: 'Healthy', query: 'Healthy', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&h=200&fit=crop' },
    { name: 'Beverages', query: 'Beverage', image: 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=200&h=200&fit=crop' },
    { name: 'North Indian', query: 'North Indian', image: 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=200&h=200&fit=crop' },
    { name: 'Rolls', query: 'Rolls', image: 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=200&h=200&fit=crop' },
    { name: 'Ice Cream', query: 'Ice Cream', image: 'https://images.unsplash.com/photo-1497034825429-c343d7c6a68f?w=200&h=200&fit=crop' },
    { name: 'Street Food', query: 'Street Food', image: 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=200&h=200&fit=crop' },
    { name: 'Bakery', query: 'Bakery', image: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=200&h=200&fit=crop' },
    { name: 'Kebab', query: 'Kebab', image: 'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=200&h=200&fit=crop' },
    { name: 'Momos', query: 'Momos', image: 'https://images.unsplash.com/photo-1625220194771-7ebdea0b70b9?w=200&h=200&fit=crop' },
    { name: 'Noodles', query: 'Noodles', image: 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=200&h=200&fit=crop' },
  ];

  return (
    <div className="bg-white pt-2 pb-5 border-b border-gray-100">
      <div className="flex justify-between items-center px-4 pb-5">
        <h2 className="text-[18px] font-black text-brand-charcoal">Popular Categories</h2>
        <button onClick={() => setShowAll(true)} className="text-[#E8621A] text-[13px] font-bold hover:underline cursor-pointer">See All &gt;</button>
      </div>
      <div className="flex gap-4 px-4 overflow-x-auto no-scrollbar snap-x pb-2">
        {items.map((c, i) => (
          <motion.div 
            key={i} 
            whileTap={{ scale: 0.95 }}
            onClick={() => onSelect?.(c.query || c.name)} 
            className="flex flex-col items-center gap-2 cursor-pointer min-w-[70px] snap-start"
          >
            <div className="w-[74px] h-[74px] rounded-full overflow-hidden bg-brand-sand shadow-sm border border-gray-50">
              <img src={c.image} alt={c.name} className="w-full h-full object-cover hover:scale-105 transition-transform duration-300" />
            </div>
            <span className="text-[12px] font-bold text-brand-charcoal whitespace-nowrap">{c.name}</span>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {showAll && (
          <div className="fixed inset-0 z-[600] flex flex-col justify-end">
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              exit={{ opacity: 0 }} 
              onClick={() => setShowAll(false)} 
              className="absolute inset-0 bg-black/60 backdrop-blur-sm" 
            />
            <motion.div 
              initial={{ y: '100%' }} 
              animate={{ y: 0 }} 
              exit={{ y: '100%' }} 
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="relative bg-white rounded-t-[24px] max-h-[85vh] flex flex-col w-full max-w-md mx-auto shadow-2xl"
            >
              <div className="p-4 flex justify-between items-center border-b border-gray-100">
                <h3 className="text-[18px] font-black text-brand-charcoal">All Categories</h3>
                <button onClick={() => setShowAll(false)} className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 font-bold hover:bg-gray-200 transition-colors">✕</button>
              </div>
              <div className="p-5 overflow-y-auto no-scrollbar flex flex-wrap gap-x-4 gap-y-6 justify-center">
                {items.map((c, i) => (
                  <motion.div 
                    key={i} 
                    whileTap={{ scale: 0.95 }}
                    onClick={() => { onSelect?.(c.query || c.name); setShowAll(false); }} 
                    className="flex flex-col items-center gap-2 cursor-pointer w-[74px]"
                  >
                    <div className="w-[74px] h-[74px] rounded-full overflow-hidden bg-brand-sand shadow-sm border border-gray-50">
                      <img src={c.image} alt={c.name} className="w-full h-full object-cover hover:scale-105 transition-transform duration-300" />
                    </div>
                    <span className="text-[12px] font-bold text-brand-charcoal text-center leading-tight">{c.name}</span>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

/* ── Today's Deals ───────────────────────────────────────────── */
function TodaysDeals({ offers, loading, onOfferClick }) {
  if (!loading && (!offers || offers.length === 0)) return null;

  return (
    <div className="bg-white py-4 mt-2">
      <div className="px-4 mb-4 flex items-center gap-2">
        <span className="text-brand-saffron text-lg">🏷️</span>
        <h2 className="text-[18px] font-black text-brand-charcoal">Today's Deals</h2>
      </div>
      <div className="flex gap-3 px-4 overflow-x-auto no-scrollbar snap-x pb-4">
        {loading ? (
          [...Array(3)].map((_, i) => <Skel key={i} w={180} h={80} r={16} />)
        ) : (
          offers.map((o, i) => (
            <motion.div 
              key={o.id || i} 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onOfferClick?.(o)}
              className="flex-shrink-0 w-[180px] bg-[#FFF8EE] border border-[#FFE8CD] rounded-[16px] p-3 snap-start cursor-pointer flex flex-col gap-1.5 shadow-sm"
            >
              <div className="text-[13px] font-black text-brand-saffron flex items-center gap-1">
                <span className="text-[14px]">🏷️</span> {o.coupon_code}
              </div>
              <div className="text-[12px] font-bold text-brand-charcoal truncate">{o.title}</div>
              <div className="text-[10px] font-extrabold text-[#E8621A] mt-1.5 uppercase tracking-wide">
                Tap to view deals <span className="text-[14px] leading-none ml-1">→</span>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  )
}


/* ── Restaurant Card ─────────────────────────────────────────── */
function RestaurantCard({ r, compact = false, onClick, isFavorite, onToggleFavorite }) {
  const ratingNum = parseFloat(r.rating) || 4.5;
  const ratingColor = ratingNum >= 4.0 ? 'bg-green-700' : ratingNum >= 3.0 ? 'bg-orange-500' : 'bg-red-500';
  
  return (
    <motion.div 
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => { if (r.is_currently_open !== false) onClick?.(r) }}
      className={`flex flex-col ${r.is_currently_open === false ? 'opacity-70 grayscale-[30%]' : 'cursor-pointer'} bg-white ${compact ? 'min-w-[280px] w-[280px]' : 'w-full mb-6'} snap-start group`}
    >
      <div className="relative w-full aspect-[1.4/1] rounded-[22px] overflow-hidden shadow-sm">
        <img src={r.image_url || r.cover_image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&h=400&fit=crop'} alt={r.name} className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
        
        {/* Gradient Overlay for bottom text */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent" />
        
        {/* Closed Overlay */}
        {r.is_currently_open === false && (
          <div className="absolute inset-0 bg-black/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center">
            <span className="text-white text-[20px] font-black tracking-widest bg-black/50 px-3 py-1 rounded-md border border-white/20">CLOSED</span>
            <span className="text-white/90 text-[12px] font-bold mt-2 text-center px-4">{r.formatted_hours}</span>
          </div>
        )}

        {/* Midnight Badge */}
        {r.is_midnight_restaurant && (
          <div className="absolute top-3 right-12 bg-[#181131]/90 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-extrabold text-[#E0E0FF] border border-[#3E315A] shadow-md z-10 flex items-center gap-1">
            🌙 Midnight
          </div>
        )}

        {/* Promoted Tag */}
        <div className="absolute top-3 left-3 bg-black/70 backdrop-blur-sm px-2 py-1 rounded text-[9px] font-extrabold text-white tracking-widest border border-white/20 uppercase">
          Promoted
        </div>

        {/* Heart Icon */}
        <div 
          onClick={(e) => { e.stopPropagation(); onToggleFavorite?.(r); }}
          className="absolute top-3 right-3 w-8 h-8 bg-white/95 backdrop-blur-md rounded-full flex items-center justify-center shadow-lg z-20 cursor-pointer transition-transform hover:scale-110">
          <span className="text-[18px]" style={{ color: isFavorite ? '#E25E1A' : '#D1D5DB' }}>{isFavorite ? '❤️' : '🤍'}</span>
        </div>

        {/* Offers Text */}
        <div className="absolute bottom-3 left-3 flex flex-col z-10">
          <span className="text-white text-[24px] font-black leading-[1.1] tracking-tight">60% OFF</span>
          <span className="text-white/90 text-[12px] font-bold">Up to ₹120</span>
        </div>

        {/* Time Pill */}
        <div className="absolute bottom-3 right-3 bg-white px-2.5 py-1.5 rounded-[12px] text-brand-charcoal text-[12px] font-extrabold shadow-xl z-10">
          {r.delivery_time || r.average_delivery_time || '40 mins'}
        </div>
      </div>

      <div className="pt-3 px-1">
        <h3 className="text-[17px] font-black text-brand-charcoal truncate mb-1">{r.name}</h3>
        <div className="flex items-center gap-2 mb-1">
          <div className={`flex items-center gap-1 ${ratingColor} px-1.5 py-0.5 rounded text-[11px] font-bold text-white`}>
            <span>⭐</span> {r.rating || '4.5'}
          </div>
          <span className="text-gray-500 text-[13px] font-bold">• {r.delivery_time || r.average_delivery_time || '30-35 mins'}</span>
        </div>
        <div className="text-[13px] text-gray-500 font-medium truncate mb-1">
          {r.categories?.[0]?.name || 'Indian'}, {r.categories?.[1]?.name || 'Fast Food'}
        </div>
        <div className="text-[12px] font-bold flex items-center">
          <span className={r.is_currently_open === false ? 'text-red-500' : 'text-green-600'}>
            {r.is_currently_open === false ? 'Closed' : 'Open'}
          </span>
          <span className="text-gray-400 mx-1.5">•</span>
          <span className="text-gray-500">{r.formatted_hours}</span>
        </div>
      </div>
    </motion.div>
  )
}


/* ── Mood Bar ────────────────────────────────────────────────── */
const MOODS = [
  { emoji: '😊', label: 'Happy', col: '#F59E0B' }, { emoji: '🎉', label: 'Party', col: '#EC4899' },
  { emoji: '💪', label: 'Healthy', col: '#10B981' }, { emoji: '😔', label: 'Comfort', col: '#8B5CF6' },
  { emoji: '❤️', label: 'Romantic', col: '#EF4444' }, { emoji: '🌙', label: 'Late Night', col: '#6366F1' },
]

function MoodBar({ onMood }) {
  const [sel, setSel] = useState(null)
  return (
    <Section style={{ padding: '0 0 16px' }}>
      <SectionHead title="What's your mood?" sub="We'll suggest the perfect meal" emoji="✨" />
      <div style={{ display: 'flex', gap: 8, padding: '0 16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
        {MOODS.map((m, i) => (
          <button key={i} onClick={() => { setSel(i); onMood?.(m) }}
            style={{ flexShrink: 0, border: `1.5px solid ${sel === i ? m.col : C.border}`, background: sel === i ? `${m.col}18` : C.warm, borderRadius: 99, padding: '8px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6, transition: 'all 0.2s' }}>
            <span style={{ fontSize: 16 }}>{m.emoji}</span>
            <span style={{ fontSize: 11.5, fontWeight: 700, color: sel === i ? m.col : C.charcoal, fontFamily: font }}>{m.label}</span>
          </button>
        ))}
      </div>
    </Section>
  )
}




/* ── Cart Drawer with Offers, Bill, Payment & Checkout ──────── */
function CartDrawer({ open, onClose, cart, onUpdate, onRemove, onPlaceOrder, onPayWithRazorpay, onClearCart }) {
  const [payMode, setPayMode] = useState('cod')
  const [offers, setOffers] = useState([])
  const [offersLoading, setOffersLoading] = useState(false)
  const [appliedOffer, setAppliedOffer] = useState(null)
  const [manualCode, setManualCode] = useState('')
  const [codeError, setCodeError] = useState('')
  const [checkoutState, setCheckoutState] = useState('cart')
  const [showOffers, setShowOffers] = useState(false)

  useEffect(() => {
    if (open && cart?.item_count > 0) {
      setOffersLoading(true)
      dashboardApi.getOffers()
        .then(r => { if (r.data?.success) setOffers(r.data.data || []) })
        .catch(() => {})
        .finally(() => setOffersLoading(false))
      setCheckoutState('cart')
      setAppliedOffer(null)
    }
  }, [open])

  if (!open) return null

  const subtotal = Number(cart?.subtotal || 0)
  const deliveryFee = 30
  let discountAmt = 0

  if (appliedOffer) {
    if (appliedOffer.discount_type === 'PERCENTAGE') {
      discountAmt = (subtotal * Number(appliedOffer.discount_value)) / 100
      if (appliedOffer.maximum_discount && discountAmt > Number(appliedOffer.maximum_discount)) {
        discountAmt = Number(appliedOffer.maximum_discount)
      }
    } else if (appliedOffer.discount_type === 'FLAT') {
      discountAmt = Number(appliedOffer.discount_value)
    } else if (appliedOffer.discount_type === 'FREE_DELIVERY') {
      discountAmt = deliveryFee
    }
  }

  const tax = Math.max(0, ((subtotal - discountAmt) * 0.05))
  const grandTotal = Math.max(0, subtotal + deliveryFee + tax - discountAmt)

  const applyOffer = (offer) => {
    if (subtotal < Number(offer.minimum_order_amount)) {
      setCodeError(`Min order ₹${offer.minimum_order_amount} required`)
      setTimeout(() => setCodeError(''), 3000)
      return
    }
    setAppliedOffer(offer)
    setShowOffers(false)
    setCodeError('')
  }

  const applyManualCode = () => {
    const found = offers.find(o => o.coupon_code.toLowerCase() === manualCode.trim().toLowerCase())
    if (!found) { setCodeError('Invalid coupon code'); setTimeout(() => setCodeError(''), 3000); return }
    applyOffer(found)
  }

  const handleCheckout = async () => {
    setCheckoutState('processing')
    try {
      if (payMode === 'cod') {
        const res = await onPlaceOrder('cod', appliedOffer?.coupon_code || '')
        if (res) {
          setCheckoutState('success')
          setTimeout(() => { setCheckoutState('cart'); onClose() }, 3000)
        } else {
          setCheckoutState('failed')
          if (onClearCart) onClearCart()
          setTimeout(() => { setCheckoutState('cart'); onClose() }, 3000)
        }
      } else {
        const success = await onPayWithRazorpay(appliedOffer?.coupon_code || '')
        if (success === false) {
          setCheckoutState('failed')
          if (onClearCart) onClearCart()
          setTimeout(() => { setCheckoutState('cart'); onClose() }, 3000)
        } else {
          setCheckoutState('success')
          setTimeout(() => { setCheckoutState('cart'); onClose() }, 3000)
        }
      }
    } catch {
      setCheckoutState('failed')
      if (onClearCart) onClearCart()
      setTimeout(() => { setCheckoutState('cart'); onClose() }, 3000)
    }
  }

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 500 }}>
      <div onClick={onClose} style={{ position: 'absolute', inset: 0, background: 'rgba(28,20,16,0.6)', backdropFilter: 'blur(4px)' }} />
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, maxWidth: 500, margin: '0 auto', background: C.cardBg, borderRadius: '22px 22px 0 0', maxHeight: '88vh', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '10px 0 0', display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: 36, height: 4, borderRadius: 99, background: C.sand }} />
        </div>

        {checkoutState === 'processing' && (
          <div style={{ padding: '80px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 48, marginBottom: 16, animation: 'pulse 1.5s infinite' }}>🔄</div>
            <div style={{ fontSize: 18, fontWeight: 800, color: C.charcoal, fontFamily: font }}>Processing your order...</div>
            <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 8 }}>Please wait while we confirm</div>
          </div>
        )}

        {checkoutState === 'success' && (
          <div style={{ padding: '60px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🎉</div>
            <div style={{ fontSize: 22, fontWeight: 900, color: C.sage, fontFamily: font, marginBottom: 8 }}>Order Placed!</div>
            <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>Your food is being prepared</div>
            {appliedOffer && <div style={{ fontSize: 13, color: C.saffron, fontWeight: 700, fontFamily: font, marginTop: 8 }}>🎁 You saved ₹{discountAmt.toFixed(2)}!</div>}
          </div>
        )}

        {checkoutState === 'failed' && (
          <div style={{ padding: '60px 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>😞</div>
            <div style={{ fontSize: 22, fontWeight: 900, color: '#D94F2B', fontFamily: font, marginBottom: 8 }}>Payment Failed</div>
            <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>Your cart has been cleared. Please try again.</div>
          </div>
        )}

        {checkoutState === 'cart' && (
          <>
            <div style={{ padding: '12px 20px 14px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 17, fontWeight: 800, color: C.charcoal, fontFamily: font }}>🛒 Your Cart</div>
                <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>{cart?.item_count || 0} item{(cart?.item_count || 0) !== 1 ? 's' : ''}</div>
              </div>
              <button onClick={onClose} style={{ background: C.warm, border: `1px solid ${C.border}`, borderRadius: 10, width: 32, height: 32, cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
              {!cart || cart.item_count === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0' }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>🛒</div>
                  <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>Your cart is empty</div>
                </div>
              ) : (
                <>
                  {cart.items.map(item => (
                    <div key={item.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 0', borderBottom: `1px solid ${C.border}` }}>
                      <div style={{ width: 50, height: 50, borderRadius: 12, background: C.sand, overflow: 'hidden', flexShrink: 0 }}>
                        {item.menu_item_image
                          ? <img src={item.menu_item_image} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>🍽️</div>}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.menu_item_name}</div>
                        <div style={{ fontSize: 12, color: C.saffron, fontWeight: 700, fontFamily: font }}>₹{item.price_at_purchase}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <button onClick={() => item.quantity === 1 ? onRemove(item.id) : onUpdate(item.id, item.quantity - 1)}
                          style={{ width: 26, height: 26, borderRadius: 8, background: C.warm, border: `1px solid ${C.border}`, cursor: 'pointer', fontSize: 14, fontWeight: 800, color: C.saffron, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>-</button>
                        <span style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font, minWidth: 16, textAlign: 'center' }}>{item.quantity}</span>
                        <button onClick={() => onUpdate(item.id, item.quantity + 1)}
                          style={{ width: 26, height: 26, borderRadius: 8, background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, border: 'none', cursor: 'pointer', fontSize: 14, fontWeight: 800, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>+</button>
                      </div>
                    </div>
                  ))}

                  {/* Offers Section */}
                  <div style={{ marginTop: 16 }}>
                    {appliedOffer ? (
                      <div style={{ background: '#E8F5E9', borderRadius: 14, padding: '12px 16px', border: '1px solid #A5D6A7', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 800, color: '#1B5E20', fontFamily: font }}>🎉 {appliedOffer.coupon_code} applied!</div>
                          <div style={{ fontSize: 11, color: '#4CAF50', fontFamily: font }}>You save ₹{discountAmt.toFixed(2)}</div>
                        </div>
                        <button onClick={() => setAppliedOffer(null)} style={{ background: 'none', border: 'none', fontSize: 18, color: '#1B5E20', cursor: 'pointer', fontWeight: 800 }}>×</button>
                      </div>
                    ) : (
                      <div>
                        <button onClick={() => setShowOffers(!showOffers)} style={{
                          width: '100%', padding: '12px 16px', borderRadius: 14,
                          border: `2px dashed ${C.saffron}`, background: `${C.saffron}08`,
                          cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          fontFamily: font, fontSize: 13, fontWeight: 700, color: C.saffron,
                        }}>
                          <span>🏷️ Apply Coupon or Offer</span>
                          <span style={{ fontSize: 18, transform: showOffers ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}>▾</span>
                        </button>

                        {showOffers && (
                          <div style={{ marginTop: 10, background: C.warm, borderRadius: 14, border: `1px solid ${C.border}`, overflow: 'hidden' }}>
                            <div style={{ display: 'flex', gap: 8, padding: '12px' }}>
                              <input
                                value={manualCode} onChange={e => { setManualCode(e.target.value); setCodeError('') }}
                                placeholder="Enter coupon code"
                                style={{ flex: 1, padding: '10px 12px', borderRadius: 10, border: `1px solid ${C.border}`, fontSize: 13, fontFamily: font, outline: 'none', background: C.bg, textTransform: 'uppercase' }}
                              />
                              <button onClick={applyManualCode} style={{
                                padding: '10px 16px', borderRadius: 10, border: 'none',
                                background: `linear-gradient(135deg,${C.saffron},${C.tomato})`,
                                color: '#fff', fontSize: 12, fontWeight: 800, cursor: 'pointer', fontFamily: font
                              }}>Apply</button>
                            </div>
                            {codeError && <div style={{ padding: '0 12px 8px', fontSize: 11, color: '#D94F2B', fontFamily: font }}>{codeError}</div>}
                            <div style={{ padding: '0 12px 12px' }}>
                              <div style={{ fontSize: 11, fontWeight: 700, color: C.muted, fontFamily: font, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>Available Offers</div>
                              {offersLoading ? (
                                <div style={{ padding: '12px 0' }}><Skel h={50} r={10} mb={8} /><Skel h={50} r={10} /></div>
                              ) : offers.length === 0 ? (
                                <div style={{ fontSize: 12, color: C.muted, fontFamily: font, padding: '8px 0' }}>No offers available right now</div>
                              ) : offers.map(offer => (
                                <div key={offer.id || offer.coupon_code} style={{
                                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                  padding: '10px 12px', marginBottom: 6, borderRadius: 10,
                                  border: `1px solid ${C.border}`, background: '#FFFAF5',
                                }}>
                                  <div style={{ flex: 1 }}>
                                    <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{offer.coupon_code}</div>
                                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>{offer.title}</div>
                                    {Number(offer.minimum_order_amount) > 0 && (
                                      <div style={{ fontSize: 10, color: C.saffron, fontFamily: font, marginTop: 2 }}>Min order ₹{offer.minimum_order_amount}</div>
                                    )}
                                  </div>
                                  <button onClick={() => applyOffer(offer)} style={{
                                    padding: '6px 14px', borderRadius: 8,
                                    border: `1.5px solid ${C.saffron}`, background: 'transparent',
                                    color: C.saffron, fontSize: 11, fontWeight: 800, cursor: 'pointer', fontFamily: font,
                                  }}>APPLY</button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {cart && cart.item_count > 0 && (
              <div style={{ padding: '16px 20px 28px', borderTop: `1px solid ${C.border}` }}>
                <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 10 }}>Bill Details</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, color: C.muted, fontFamily: font }}>Item Total</span>
                  <span style={{ fontSize: 12, fontWeight: 600, color: C.charcoal, fontFamily: font }}>₹{subtotal.toFixed(2)}</span>
                </div>
                {appliedOffer && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontSize: 12, color: '#1B5E20', fontWeight: 700, fontFamily: font }}>Discount ({appliedOffer.coupon_code})</span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: '#1B5E20', fontFamily: font }}>-₹{discountAmt.toFixed(2)}</span>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, color: C.muted, fontFamily: font }}>Delivery Fee</span>
                  <span style={{ fontSize: 12, fontWeight: 600, color: C.charcoal, fontFamily: font }}>₹{deliveryFee.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, color: C.muted, fontFamily: font }}>Taxes (5%)</span>
                  <span style={{ fontSize: 12, fontWeight: 600, color: C.charcoal, fontFamily: font }}>₹{tax.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14, paddingTop: 8, borderTop: `1px dashed ${C.border}` }}>
                  <span style={{ fontSize: 15, fontWeight: 900, color: C.charcoal, fontFamily: font }}>To Pay</span>
                  <span style={{ fontSize: 15, fontWeight: 900, color: C.saffron, fontFamily: font }}>₹{grandTotal.toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                  {[{ id: 'cod', label: '💵 Cash on Delivery' }, { id: 'razorpay', label: '💳 Pay Online' }].map(m => (
                    <button key={m.id} onClick={() => setPayMode(m.id)}
                      style={{ flex: 1, padding: '10px 8px', borderRadius: 12, border: `2px solid ${payMode === m.id ? C.saffron : C.border}`, background: payMode === m.id ? `${C.saffron}10` : C.warm, cursor: 'pointer', fontSize: 11, fontWeight: 700, color: payMode === m.id ? C.saffron : C.charcoal, fontFamily: font, transition: 'all 0.2s' }}>
                      {m.label}
                    </button>
                  ))}
                </div>
                <button onClick={handleCheckout}
                  style={{ width: '100%', background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, border: 'none', borderRadius: 14, padding: '14px', color: '#fff', fontSize: 14, fontWeight: 800, cursor: 'pointer', fontFamily: font, boxShadow: `0 4px 20px rgba(232,98,26,0.35)` }}>
                  {payMode === 'cod' ? `Place Order → ₹${grandTotal.toFixed(2)}` : `Pay ₹${grandTotal.toFixed(2)} Online →`}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}


/* ── Order Tracking ──────────────────────────────────────────── */
function TrackingView({ order, onClose }) {
  const [tracking, setTracking] = useState(null)
  const [progress, setProgress] = useState(0)
  const STEPS = [
    { key: 'pending', label: 'Order Placed', emoji: '✅' },
    { key: 'confirmed', label: 'Confirmed', emoji: '🍳' },
    { key: 'preparing', label: 'Preparing', emoji: '👨‍🍳' },
    { key: 'out_for_delivery', label: 'On the way', emoji: '🛵' },
    { key: 'delivered', label: 'Delivered', emoji: '🎉' },
  ]
  const statusIdx = STEPS.findIndex(s => s.key === order?.status)
  const curStep = statusIdx >= 0 ? statusIdx : 0

  useEffect(() => {
    if (!order?.id) return
    dashboardApi.getTracking(order.id).then(r => r.data?.success && setTracking(r.data.data)).catch(() => {})
    const target = (curStep / (STEPS.length - 1)) * 100
    const t = setTimeout(() => setProgress(target), 300)
    return () => clearTimeout(t)
  }, [order?.id, curStep])

  if (!order) return null

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 300, background: C.bg, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
      <div style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, padding: '52px 20px 24px', position: 'relative', flexShrink: 0 }}>
        <button onClick={onClose} style={{ position: 'absolute', top: 52, left: 16, background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 10, width: 36, height: 36, cursor: 'pointer', fontSize: 18, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>←</button>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>{STEPS[curStep]?.emoji || '📦'}</div>
          <div style={{ fontSize: 20, fontWeight: 900, color: '#fff', fontFamily: font }}>{STEPS[curStep]?.label || 'Processing'}</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.85)', marginTop: 4, fontFamily: font }}>Order #{String(order.id).slice(0, 8).toUpperCase()}</div>
          {order.estimated_delivery_time && (
            <div style={{ marginTop: 10, display: 'inline-block', background: 'rgba(255,255,255,0.2)', borderRadius: 99, padding: '6px 16px' }}>
              <span style={{ color: '#fff', fontSize: 12, fontWeight: 700, fontFamily: font }}>⏱ Est. {order.estimated_delivery_time} min</span>
            </div>
          )}
        </div>
      </div>
      <div style={{ flex: 1, padding: '20px 20px 32px' }}>
        <div style={{ background: C.cardBg, borderRadius: 18, padding: '20px', marginBottom: 14, border: `1px solid ${C.border}` }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, marginBottom: 16 }}>Order Progress</div>
          <div style={{ position: 'relative' }}>
            <div style={{ position: 'absolute', top: 16, left: 16, right: 16, height: 3, background: C.sand, borderRadius: 99, zIndex: 0 }}>
              <div style={{ height: '100%', width: `${progress}%`, background: `linear-gradient(90deg,${C.saffron},${C.tomato})`, borderRadius: 99, transition: 'width 1s cubic-bezier(0.4,0,0.2,1)' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', position: 'relative', zIndex: 1 }}>
              {STEPS.map((step, i) => {
                const done = i <= curStep
                const active = i === curStep
                return (
                  <div key={step.key} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, flex: 1 }}>
                    <div style={{ width: 32, height: 32, borderRadius: '50%', background: done ? `linear-gradient(135deg,${C.saffron},${C.tomato})` : C.sand, border: `3px solid ${done ? C.saffron : C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, transition: 'all 0.5s', boxShadow: active ? `0 0 0 4px ${C.saffron}30` : 'none', animation: active ? 'pulse 1.5s infinite' : 'none' }}>
                      {done ? <span style={{ fontSize: 13 }}>{step.emoji}</span> : <span style={{ fontSize: 10, fontWeight: 800, color: C.muted }}>{i + 1}</span>}
                    </div>
                    <span style={{ fontSize: 9, fontWeight: 700, color: done ? C.saffron : C.muted, fontFamily: font, textAlign: 'center', lineHeight: 1.3, maxWidth: 48 }}>{step.label}</span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
        {tracking?.agent && (
          <div style={{ background: C.cardBg, borderRadius: 18, padding: '18px', marginBottom: 14, border: `1px solid ${C.border}` }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>Delivery Partner</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
              <div style={{ width: 52, height: 52, borderRadius: 16, background: `linear-gradient(135deg,${C.amber},${C.saffron})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, flexShrink: 0 }}>🧑‍🦱</div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{tracking.agent.full_name}</div>
                <div style={{ fontSize: 11, color: C.muted, fontFamily: font, marginTop: 2 }}>🏍️ {tracking.agent.vehicle_type} · {tracking.agent.vehicle_number || 'On the way'}</div>
              </div>
            </div>
          </div>
        )}
        <div style={{ background: C.cardBg, borderRadius: 18, padding: '18px', border: `1px solid ${C.border}` }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>Order Summary</div>
          {order.items?.map(item => (
            <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: `1px solid ${C.border}` }}>
              <span style={{ fontSize: 12, color: C.charcoal, fontFamily: font }}>{item.quantity}× {item.name}</span>
              <span style={{ fontSize: 12, color: C.mocha, fontFamily: font, fontWeight: 600 }}>₹{Number(item.price_at_purchase * item.quantity).toFixed(0)}</span>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 10 }}>
            <span style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>Total Paid</span>
            <span style={{ fontSize: 14, fontWeight: 800, color: C.saffron, fontFamily: font }}>₹{Number(order.grand_total).toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Menu Filtered View (99 Store / EatRight / Offers) ────────── */
function MenuFilteredView({ items, loading, title, emoji, sub, onAdd, highlightOffer, allOffers, favItemIds, onToggleFavItem }) {
  return (
    <div style={{ padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <div style={{ fontSize: 24 }}>{emoji}</div>
        <div>
          <div style={{ fontSize: 16, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{title}</div>
          <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>{sub}</div>
        </div>
      </div>

      {/* Highlighted offer card */}
      {highlightOffer && (
        <div style={{ background: `linear-gradient(135deg, #FFF0E0, #FFE4CC)`, border: `2px dashed ${C.amber}`, borderRadius: 16, padding: '14px 16px', marginBottom: 16, position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: -10, right: -10, width: 60, height: 60, background: `${C.saffron}15`, borderRadius: '50%' }} />
          <div style={{ fontSize: 14, fontWeight: 900, color: C.saffron, fontFamily: font, marginBottom: 2 }}>🎉 {highlightOffer.coupon_code}</div>
          <div style={{ fontSize: 12, color: C.charcoal, fontFamily: font }}>{highlightOffer.title}</div>
          <div style={{ fontSize: 11, color: C.muted, fontFamily: font, marginTop: 4 }}>
            {highlightOffer.discount_type === 'PERCENTAGE' ? `${highlightOffer.discount_value}% off` : highlightOffer.discount_type === 'FLAT' ? `₹${highlightOffer.discount_value} off` : 'Free delivery'}
            {Number(highlightOffer.minimum_order_amount) > 0 && ` • Min order ₹${highlightOffer.minimum_order_amount}`}
          </div>
          <div style={{ fontSize: 10, color: C.sage, fontFamily: font, marginTop: 4, fontWeight: 700 }}>✓ Will be auto-applied at checkout</div>
        </div>
      )}

      {/* All available offers strip */}
      {allOffers && allOffers.length > 1 && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: C.muted, fontFamily: font, marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.5 }}>More Offers</div>
          <div style={{ display: 'flex', gap: 8, overflowX: 'auto', scrollbarWidth: 'none' }}>
            {allOffers.filter(o => o.id !== highlightOffer?.id).map(o => (
              <div key={o.id} style={{ flexShrink: 0, background: C.warm, border: `1px solid ${C.border}`, borderRadius: 10, padding: '8px 12px', minWidth: 120 }}>
                <div style={{ fontSize: 11, fontWeight: 800, color: C.saffron, fontFamily: font }}>🏷️ {o.coupon_code}</div>
                <div style={{ fontSize: 9, color: C.muted, fontFamily: font, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 100 }}>{o.title}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? [...Array(4)].map((_, i) => <Skel key={i} h={100} r={16} mb={10} />)
        : items.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🤔</div>
            <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>No items found.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {items.map(item => (
              <div key={item.id} style={{ display: 'flex', gap: 12, background: C.cardBg, borderRadius: 16, padding: '12px', border: `1px solid ${C.border}` }}>
                <div style={{ width: 80, height: 80, borderRadius: 12, background: C.sand, flexShrink: 0, overflow: 'hidden' }}>
                  {item.image ? <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>🍲</div>}
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{item.name}</div>
                      <div style={{ fontSize: 10, color: C.muted, fontFamily: font, marginTop: 2 }}>{item.restaurant_name}</div>
                    </div>
                    <div onClick={(e) => { e.stopPropagation(); onToggleFavItem?.(item); }} style={{ cursor: 'pointer', padding: 4, transition: 'transform 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform='scale(1.1)'} onMouseLeave={e => e.currentTarget.style.transform='scale(1)'}>
                      <span style={{ fontSize: 16 }}>{(favItemIds && favItemIds.has(item.id)) ? '❤️' : '🤍'}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                    <div>
                      <span style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font }}>₹{Number(item.effective_price).toFixed(0)}</span>
                      {item.discounted_price && <span style={{ fontSize: 11, color: C.muted, textDecoration: 'line-through', marginLeft: 6 }}>₹{Number(item.price).toFixed(0)}</span>}
                    </div>
                    <button onClick={() => onAdd(item)} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 8, padding: '6px 14px', fontSize: 11, fontWeight: 800, fontFamily: font, cursor: 'pointer', boxShadow: '0 2px 8px rgba(232,98,26,0.25)' }}>ADD</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )
      }
    </div>
  )
}

/* ── Orders List ─────────────────────────────────────────────── */
function OrdersView({ orders, loading, onTrack, onReorder }) {
  const STATUS_COLORS = {
    pending:          { bg: '#FFF8E6', color: '#D97706', label: 'Pending' },
    confirmed:        { bg: '#EFF9ED', color: '#2E8B57', label: 'Confirmed' },
    preparing:        { bg: '#FFF0E6', color: '#E8621A', label: 'Preparing' },
    out_for_delivery: { bg: '#E8F4FF', color: '#2563EB', label: 'On the Way' },
    delivered:        { bg: '#EFF9ED', color: '#2E8B57', label: 'Delivered' },
    cancelled:        { bg: '#FEF0F0', color: '#DC2626', label: 'Cancelled' },
  }
  return (
    <div style={{ padding: '16px' }}>
      <div style={{ fontSize: 16, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 16 }}>Your Orders</div>
      {loading ? [...Array(3)].map((_, i) => <Skel key={i} h={110} r={16} mb={10} />)
        : orders.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0' }}>
            <div style={{ fontSize: 52, marginBottom: 12 }}>📦</div>
            <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>No orders yet</div>
            <div style={{ fontSize: 12, color: C.muted, marginTop: 6, fontFamily: font }}>Your order history will appear here</div>
          </div>
        ) : orders.map(o => {
          const stat = STATUS_COLORS[o.status] || STATUS_COLORS.pending
          const active = ['pending', 'confirmed', 'preparing', 'out_for_delivery'].includes(o.status)
          return (
            <div key={o.id} style={{ background: C.cardBg, borderRadius: 16, padding: '14px', marginBottom: 10, border: `1px solid ${C.border}`, boxShadow: '0 2px 12px rgba(92,42,15,0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{o.restaurant_name}</div>
                  <div style={{ fontSize: 10, color: C.muted, fontFamily: font, marginTop: 2 }}>
                    {new Date(o.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                <div style={{ background: stat.bg, borderRadius: 8, padding: '4px 10px' }}>
                  <span style={{ fontSize: 10, fontWeight: 800, color: stat.color, fontFamily: font }}>{stat.label}</span>
                </div>
              </div>
              
              <div style={{ fontSize: 11, color: C.muted, fontFamily: font, marginBottom: 10, lineHeight: 1.4 }}>
                {o.items?.map(i => `${i.quantity} x ${i.name}`).join(', ')}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: C.saffron, fontFamily: font }}>₹{Number(o.grand_total).toFixed(2)}</span>
                <div style={{ display: 'flex', gap: 8 }}>
                  {!active && (
                    <button onClick={() => onReorder(o)} style={{ background: C.maroonLight, color: C.maroon, border: 'none', borderRadius: 8, padding: '6px 12px', fontSize: 11, fontWeight: 800, cursor: 'pointer', fontFamily: font }}>
                      Reorder
                    </button>
                  )}
                  {active && (
                    <button onClick={() => onTrack(o)} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, border: 'none', borderRadius: 10, padding: '6px 12px', color: '#fff', fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: font }}>
                      Track Order 🛵
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })
      }
    </div>
  )
}

/* ── Notifications Panel ─────────────────────────────────────── */
function NotifPanel({ notifs, loading, onClose, onMarkAll }) {
  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 200 }}>
      <div onClick={onClose} style={{ position: 'absolute', inset: 0, background: 'rgba(28,20,16,0.5)', backdropFilter: 'blur(4px)' }} />
      <div style={{ position: 'absolute', top: 0, right: 0, bottom: 0, width: 'min(320px, 90vw)', background: C.cardBg, display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '52px 20px 16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: `linear-gradient(135deg,${C.saffron}15,${C.amber}10)` }}>
          <div style={{ fontSize: 16, fontWeight: 800, color: C.charcoal, fontFamily: font }}>🔔 Notifications</div>
          <button onClick={onMarkAll} style={{ background: 'none', border: 'none', color: C.saffron, fontSize: 11, fontWeight: 700, cursor: 'pointer', fontFamily: font }}>Mark all read</button>
        </div>
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px' }}>
          {loading ? [...Array(4)].map((_, i) => <Skel key={i} h={60} r={12} mb={8} />)
            : notifs.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ fontSize: 40, marginBottom: 8 }}>🔕</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font }}>No notifications</div>
              </div>
            ) : notifs.map(n => (
              <div key={n.id} style={{ padding: '12px', borderRadius: 12, background: n.is_read ? 'transparent' : `${C.saffron}08`, border: `1px solid ${n.is_read ? C.border : `${C.saffron}25`}`, marginBottom: 8 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, marginBottom: 3 }}>{n.title}</div>
                <div style={{ fontSize: 11, color: C.muted, fontFamily: font, lineHeight: 1.4 }}>{n.body}</div>
                <div style={{ fontSize: 10, color: C.muted, marginTop: 5, fontFamily: font }}>{new Date(n.created_at).toLocaleDateString()}</div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}

/* ── Bottom Nav ──────────────────────────────────────────────── */
const NAV_TABS = [
  { id: 'home', emoji: '🏠', label: 'Home' },
  { id: 'search', emoji: '🔍', label: 'Search' },
  { id: 'orders', emoji: '📦', label: 'Orders' },
  { id: 'profile', emoji: '👤', label: 'Profile' },
]

function BottomNav({ active, onChange }) {
  const tabs = [
    { id: 'home', icon: '🍲', label: 'Food' },
    { id: '99store', icon: '🏪', label: '99 store' },
    { id: 'eatright', icon: '🥗', label: 'EatRight' },
    { id: 'reorder', icon: '🛒', label: 'Reorder' },
  ]
  return (
    <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: C.cardBg, borderTop: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-around', padding: '10px 0 16px', zIndex: 100 }}>
      {tabs.map(t => (
        <button key={t.id} onClick={() => onChange(t.id)} style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}>
          <span style={{ fontSize: 22, opacity: active === t.id ? 1 : 0.5 }}>{t.icon}</span>
          <span style={{ fontSize: 10, fontWeight: 800, color: active === t.id ? C.saffron : C.muted, fontFamily: font }}>{t.label}</span>
        </button>
      ))}
    </div>
  )
}

/* ── Profile Sub View ─────────────────────────────────────────── */
function ProfileSubView({ section, onClose, user, onRestaurantClick, onMenuItemClick, allOffers, onOfferClick }) {
  const { updateSetting, C, t } = useSettings();
  const [data, setData] = useState(null)
  const [favItemsData, setFavItemsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editingAddress, setEditingAddress] = useState(null)

  useEffect(() => {
    setLoading(true)
    if (section === 'favorites') {
      Promise.allSettled([profileApi.getFavorites(), profileApi.getFavoriteItems()]).then(results => {
        const [resRest, resItems] = results;
        if (resRest.status === 'fulfilled') {
          setData(Array.isArray(resRest.value.data) ? resRest.value.data : (resRest.value.data?.data || resRest.value.data?.results || []))
        } else setData([])
        
        if (resItems.status === 'fulfilled') {
          setFavItemsData(Array.isArray(resItems.value.data) ? resItems.value.data : (resItems.value.data?.data || resItems.value.data?.results || []))
        } else setFavItemsData([])
      }).finally(() => setLoading(false))
      return;
    }

    let req = null
    if (section === 'addresses') req = profileApi.getAddresses()
    else if (section === 'payments') req = profileApi.getPaymentMethods()
    else if (section === 'favorites') req = profileApi.getFavorites()
    else if (section === 'offers') req = profileApi.getSavedOffers()
    else if (section === 'settings') req = profileApi.getSettings()
    else if (section === 'support') req = profileApi.getTickets()

    if (req) {
      req.then(r => {
        if (section === 'settings') {
          setData(r.data);
        } else {
          setData(Array.isArray(r.data) ? r.data : (r.data?.data || r.data?.results || []));
        }
      })
         .catch(() => setData(section === 'settings' ? {} : []))
         .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [section])

  const handleSettingToggle = async (key, value) => {
    try {
      setData(prev => ({ ...prev, [key]: value }));
      await updateSetting(key, value);
    } catch (err) {
      alert("Failed to update setting");
    }
  };

  const sectionTitles = {
    addresses: '📍 Saved Addresses',
    payments: '💳 Payment Methods',
    favorites: '❤️ Favourites',
    offers: '🏷️ Offers & Coupons',
    settings: '⚙️ Settings',
    support: '🆘 Help & Support'
  }

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 300, background: C.bg, display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '52px 20px 16px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', gap: 12, background: C.cardBg }}>
        <button onClick={onClose} style={{ background: C.warm, border: `1px solid ${C.border}`, borderRadius: 10, width: 36, height: 36, cursor: 'pointer', fontSize: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>←</button>
        <div style={{ fontSize: 18, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{sectionTitles[section]}</div>
      </div>
      <div style={{ flex: 1, overflowY: section === 'support' ? 'hidden' : 'auto', padding: section === 'support' ? 0 : '20px 16px', display: 'flex', flexDirection: 'column' }}>
        {loading ? <div style={{ padding: '20px 16px' }}>{[...Array(3)].map((_, i) => <Skel key={i} h={80} r={16} mb={12} />)}</div> : (
          <>
            {/* Render based on section */}
            {section === 'addresses' && (
              data?.length > 0 ? data.map(a => (
                <div key={a.id} style={{ background: C.cardBg, borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px solid ${C.border}` }}>
                  {editingAddress?.id === a.id ? (
                    <form onSubmit={async (e) => {
                      e.preventDefault();
                      try {
                        const res = await profileApi.updateAddress(editingAddress.id, editingAddress);
                        setData(prev => prev.map(item => item.id === editingAddress.id ? res.data : item));
                        setEditingAddress(null);
                      } catch (err) {
                        alert("Failed to update address");
                      }
                    }}>
                      <input style={{width: '100%', marginBottom: 8, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.label || ''} onChange={e => setEditingAddress({...editingAddress, label: e.target.value})} placeholder="Label (Home, Work, etc.)" />
                      <input style={{width: '100%', marginBottom: 8, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.flat_no || ''} onChange={e => setEditingAddress({...editingAddress, flat_no: e.target.value})} placeholder="Flat / House No." />
                      <input style={{width: '100%', marginBottom: 8, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.street || ''} onChange={e => setEditingAddress({...editingAddress, street: e.target.value})} placeholder="Street" />
                      <input style={{width: '100%', marginBottom: 8, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.city || ''} onChange={e => setEditingAddress({...editingAddress, city: e.target.value})} placeholder="City" />
                      <input style={{width: '100%', marginBottom: 8, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.state || ''} onChange={e => setEditingAddress({...editingAddress, state: e.target.value})} placeholder="State" />
                      <input style={{width: '100%', marginBottom: 12, padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, fontFamily: font, boxSizing: 'border-box'}} value={editingAddress.pincode || ''} onChange={e => setEditingAddress({...editingAddress, pincode: e.target.value})} placeholder="Pincode" />
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button type="submit" style={{ flex: 1, background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 8, padding: '8px', fontWeight: 800, cursor: 'pointer', fontFamily: font }}>Save</button>
                        <button type="button" onClick={() => setEditingAddress(null)} style={{ flex: 1, background: C.sand, color: C.charcoal, border: 'none', borderRadius: 8, padding: '8px', fontWeight: 800, cursor: 'pointer', fontFamily: font }}>Cancel</button>
                      </div>
                    </form>
                  ) : (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>
                          {a.label || 'Home'}
                          {a.is_default && <span style={{ marginLeft: 8, fontSize: 10, background: `${C.saffron}20`, color: C.saffron, borderRadius: 6, padding: '2px 7px', fontWeight: 700 }}>DEFAULT</span>}
                        </div>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <button onClick={() => setEditingAddress(a)} style={{ background: C.sand, border: 'none', padding: '4px 8px', borderRadius: 6, fontSize: 12, cursor: 'pointer', fontWeight: 700, color: C.charcoal, fontFamily: font }}>Edit</button>
                          <button onClick={async () => {
                            if (!window.confirm("Delete this address?")) return;
                            try {
                              await profileApi.deleteAddress(a.id);
                              setData(prev => prev.filter(item => item.id !== a.id));
                            } catch (err) {
                              alert("Failed to delete address");
                            }
                          }} style={{ background: '#FEE2E2', border: 'none', padding: '4px 8px', borderRadius: 6, fontSize: 12, cursor: 'pointer', fontWeight: 700, color: '#DC2626', fontFamily: font }}>Delete</button>
                        </div>
                      </div>
                      <div style={{ fontSize: 12, color: C.muted, fontFamily: font, marginTop: 4 }}>
                        {a.full_address || [a.flat_no, a.building_name, a.street, a.city, a.state, a.pincode].filter(Boolean).join(', ')}
                      </div>
                    </>
                  )}
                </div>
              )) : <div style={{ textAlign: 'center', color: C.muted, padding: 40, fontFamily: font }}>No saved addresses</div>
            )}
            
            {section === 'payments' && (
              data?.length > 0 ? data.map(p => (
                <div key={p.id} style={{ background: C.cardBg, borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px solid ${C.border}` }}>
                  <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{p.provider} ({p.method_type})</div>
                  <div style={{ fontSize: 12, color: C.muted, fontFamily: font, marginTop: 4 }}>Last used: {new Date(p.updated_at).toLocaleDateString()}</div>
                </div>
              )) : <div style={{ textAlign: 'center', color: C.muted, padding: 40, fontFamily: font }}>No saved payment methods</div>
            )}

            {section === 'favorites' && (
              <>
                <div style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>Favorite Restaurants</div>
                {data?.length > 0 ? data.map(f => (
                  <div key={f.id} onClick={() => f.restaurant?.id && onRestaurantClick?.(f.restaurant.id)} style={{ background: C.cardBg, borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px solid ${C.border}`, cursor: 'pointer' }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{f.restaurant?.name || 'Restaurant'}</div>
                    <div style={{ fontSize: 12, color: C.muted, fontFamily: font, marginTop: 4 }}>Added on: {new Date(f.created_at).toLocaleDateString()}</div>
                  </div>
                )) : <div style={{ textAlign: 'center', color: C.muted, padding: 20, fontFamily: font, marginBottom: 20 }}>No favorite restaurants yet</div>}

                <div style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 12, marginTop: 12 }}>Favorite Dishes</div>
                {favItemsData?.length > 0 ? favItemsData.map(f => (
                  <div key={f.id} onClick={() => f.menu_item_detail?.restaurant && onMenuItemClick?.(f.menu_item_detail.restaurant, f.menu_item_detail.id)} style={{ background: C.cardBg, borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px solid ${C.border}`, cursor: 'pointer' }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{f.menu_item_detail?.name || 'Menu Item'}</div>
                    <div style={{ fontSize: 12, color: C.muted, fontFamily: font, marginTop: 4 }}>Added on: {new Date(f.created_at).toLocaleDateString()}</div>
                  </div>
                )) : <div style={{ textAlign: 'center', color: C.muted, padding: 20, fontFamily: font }}>No favorite dishes yet</div>}
              </>
            )}

            {section === 'offers' && (
              allOffers?.length > 0 ? allOffers.map(o => (
                <div key={o.id} onClick={() => onOfferClick?.(o)} style={{ background: `linear-gradient(135deg,${C.warm},#FFF0E0)`, borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px dashed ${C.amber}`, cursor: 'pointer', transition: 'transform 0.2s' }}>
                  <div style={{ fontSize: 15, fontWeight: 800, color: C.saffron, fontFamily: font }}>{o.coupon_code || o.title}</div>
                  <div style={{ fontSize: 12, color: C.charcoal, fontFamily: font, marginTop: 4 }}>{o.description || o.title}</div>
                  <div style={{ fontSize: 10, fontWeight: 800, color: C.tomato, marginTop: 8 }}>Tap to apply & view foods →</div>
                </div>
              )) : <div style={{ textAlign: 'center', color: C.muted, padding: 40, fontFamily: font }}>No offers available</div>
            )}

            {section === 'settings' && (
              <div style={{ background: C.cardBg, borderRadius: 16, border: `1px solid ${C.border}`, overflow: 'hidden' }}>
                
                {/* Push Notifications */}
                <div style={{ padding: '16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Push Notifications</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Receive order updates via push</div>
                  </div>
                  <div onClick={() => handleSettingToggle('push_notifications', !data?.push_notifications)} style={{ width: 44, height: 24, background: data?.push_notifications ? C.saffron : C.sand, borderRadius: 99, position: 'relative', cursor: 'pointer' }}>
                    <div style={{ position: 'absolute', top: 2, left: data?.push_notifications ? 22 : 2, width: 20, height: 20, background: '#fff', borderRadius: '50%', transition: 'left 0.2s' }} />
                  </div>
                </div>

                {/* SMS Notifications */}
                <div style={{ padding: '16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>SMS Notifications</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Get order updates via SMS</div>
                  </div>
                  <div onClick={() => handleSettingToggle('sms_notifications', !data?.sms_notifications)} style={{ width: 44, height: 24, background: data?.sms_notifications ? C.saffron : C.sand, borderRadius: 99, position: 'relative', cursor: 'pointer' }}>
                    <div style={{ position: 'absolute', top: 2, left: data?.sms_notifications ? 22 : 2, width: 20, height: 20, background: '#fff', borderRadius: '50%', transition: 'left 0.2s' }} />
                  </div>
                </div>

                {/* WhatsApp Notifications */}
                <div style={{ padding: '16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>WhatsApp Notifications</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Get updates directly on WhatsApp</div>
                  </div>
                  <div onClick={() => handleSettingToggle('whatsapp_notifications', !data?.whatsapp_notifications)} style={{ width: 44, height: 24, background: data?.whatsapp_notifications ? C.saffron : C.sand, borderRadius: 99, position: 'relative', cursor: 'pointer' }}>
                    <div style={{ position: 'absolute', top: 2, left: data?.whatsapp_notifications ? 22 : 2, width: 20, height: 20, background: '#fff', borderRadius: '50%', transition: 'left 0.2s' }} />
                  </div>
                </div>

                {/* Email Notifications */}
                <div style={{ padding: '16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Email Notifications</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Receive promotional offers via Email</div>
                  </div>
                  <div onClick={() => handleSettingToggle('email_notifications', !data?.email_notifications)} style={{ width: 44, height: 24, background: data?.email_notifications ? C.saffron : C.sand, borderRadius: 99, position: 'relative', cursor: 'pointer' }}>
                    <div style={{ position: 'absolute', top: 2, left: data?.email_notifications ? 22 : 2, width: 20, height: 20, background: '#fff', borderRadius: '50%', transition: 'left 0.2s' }} />
                  </div>
                </div>

                {/* Dark Mode */}
                <div style={{ padding: '16px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Dark Mode</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Dark app appearance</div>
                  </div>
                  <div onClick={() => handleSettingToggle('dark_mode', !data?.dark_mode)} style={{ width: 44, height: 24, background: data?.dark_mode ? C.saffron : C.sand, borderRadius: 99, position: 'relative', cursor: 'pointer' }}>
                    <div style={{ position: 'absolute', top: 2, left: data?.dark_mode ? 22 : 2, width: 20, height: 20, background: '#fff', borderRadius: '50%', transition: 'left 0.2s' }} />
                  </div>
                </div>

                {/* Language */}
                <div style={{ padding: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Language</div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Choose app language</div>
                  </div>
                  <div>
                    <select 
                      value={data?.language || 'en'} 
                      onChange={(e) => handleSettingToggle('language', e.target.value)}
                      style={{ padding: '6px 12px', borderRadius: 8, border: `1px solid ${C.border}`, background: '#fff', fontFamily: font, outline: 'none', cursor: 'pointer' }}
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                      <option value="te">Telugu</option>
                      <option value="es">Spanish</option>
                    </select>
                  </div>
                </div>

              </div>
            )}

            {section === 'support' && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <SupportCenter />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

/* ── Profile View ────────────────────────────────────────────── */
function ProfileView({ user, onLogout, onSectionClick }) {
  const { t, C } = useSettings()
  const items = [
    { id: 'orders', emoji: '📦', label: t('My Orders'), sub: 'Track and reorder' },
    { id: 'addresses', emoji: '📍', label: t('Saved Addresses'), sub: 'Home, work & more' },
    { id: 'payments', emoji: '💳', label: t('Payment Methods'), sub: 'Cards and wallets' },
    { id: 'favorites', emoji: '❤️', label: t('Favourites'), sub: 'Saved restaurants & dishes' },
    { id: 'offers', emoji: '🏷️', label: t('Offers & Coupons'), sub: 'Your saved deals' },
    { id: 'settings', emoji: '⚙️', label: t('Settings'), sub: 'App preferences' },
    { id: 'support', emoji: '🆘', label: t('Help & Support'), sub: 'FAQs and chat' },
  ]
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleAvatarUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('avatar', file)
      const res = await dashboardApi.updateProfile(formData)
      if (res.data?.success) {
        // Force reload to update user state if needed, or rely on a state update
        window.location.reload()
      }
    } catch (err) {
      alert("Failed to upload avatar: " + (err.response?.data?.message || err.message))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={{ padding: '20px 16px' }}>
      <div style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, borderRadius: 20, padding: '24px', marginBottom: 16, position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: -20, right: -20, width: 100, height: 100, background: 'rgba(255,255,255,0.1)', borderRadius: '50%' }} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ position: 'relative' }}>
            <div 
              onClick={() => fileInputRef.current?.click()}
              style={{ width: 60, height: 60, borderRadius: 18, background: 'rgba(255,255,255,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, flexShrink: 0, cursor: 'pointer', position: 'relative', overflow: 'hidden' }}
            >
              {user?.avatar ? (
                <img src={user.avatar} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              ) : (
                user?.full_name?.[0]?.toUpperCase() || '👤'
              )}
              {uploading && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>⏳</div>}
            </div>
            <div 
              onClick={() => fileInputRef.current?.click()}
              style={{ position: 'absolute', bottom: -4, right: -4, width: 22, height: 22, background: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.tomato, fontSize: 16, fontWeight: 900, cursor: 'pointer', boxShadow: '0 2px 5px rgba(0,0,0,0.2)' }}
            >
              +
            </div>
          </div>
          <input type="file" ref={fileInputRef} accept="image/*" style={{ display: 'none' }} onChange={handleAvatarUpload} />
          <div>
            <div style={{ fontSize: 18, fontWeight: 900, color: '#fff', fontFamily: font }}>{user?.full_name || 'Foodie'}</div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.85)', fontFamily: font, marginTop: 2 }}>{user?.mobile_number}</div>
          </div>
        </div>
      </div>
      <div style={{ background: C.cardBg, borderRadius: 18, overflow: 'hidden', border: `1px solid ${C.border}`, marginBottom: 16 }}>
        {items.map((item, i) => (
          <button key={i} onClick={() => onSectionClick(item.id)} style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderBottom: i < items.length - 1 ? `1px solid ${C.border}` : 'none', fontFamily: font }}>
            <div style={{ width: 38, height: 38, borderRadius: 12, background: C.warm, border: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, flexShrink: 0 }}>{item.emoji}</div>
            <div style={{ flex: 1, textAlign: 'left' }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.charcoal }}>{item.label}</div>
              <div style={{ fontSize: 11, color: C.muted, marginTop: 1 }}>{item.sub}</div>
            </div>
            <span style={{ color: C.muted, fontSize: 14 }}>›</span>
          </button>
        ))}
      </div>
      <button onClick={onLogout} style={{ width: '100%', background: C.warm, border: `1.5px solid ${C.border}`, borderRadius: 14, padding: '14px', cursor: 'pointer', fontSize: 13, fontWeight: 700, color: C.tomato, fontFamily: font, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
        🚪 Sign Out
      </button>
    </div>
  )
}

/* ── Search Results ──────────────────────────────────────────── */
function SearchResultsView({ query, results, loading, onRestaurant, onAddDish, favRestIds, onToggleFavRest, favItemIds, onToggleFavItem }) {
  return (
    <div style={{ padding: '16px' }}>
      <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginBottom: 14 }}>
        {loading ? `Searching for "${query}"...` : `${(results?.total_restaurants || 0) + (results?.total_menu_items || 0)} results for "${query}"`}
      </div>
      {loading ? [...Array(3)].map((_, i) => <Skel key={i} h={120} r={16} mb={10} />) : (
        <>
          {results?.restaurants?.length > 0 && (
            <>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 10 }}>Restaurants</div>
              {results.restaurants.map(r => <RestaurantCard key={r.id} r={r} onClick={onRestaurant} isFavorite={favRestIds?.has(r.id)} onToggleFavorite={onToggleFavRest} />)}
            </>
          )}
          {results?.menu_items?.length > 0 && (
            <>
              <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font, margin: '16px 0 10px' }}>Dishes</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: 10 }}>
                {results.menu_items.map(item => (
                  <div key={item.id} onClick={() => onRestaurant && onRestaurant({ id: item.restaurant, itemId: item.id })} style={{ background: C.cardBg, borderRadius: 14, overflow: 'hidden', border: `1px solid ${C.border}`, display: 'flex', flexDirection: 'column', cursor: 'pointer' }}>
                    <div style={{ height: 100, background: C.sand, overflow: 'hidden' }}>
                      {item.image ? <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        : <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32 }}>🍽️</div>}
                    </div>
                    <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', flex: 1, justifyContent: 'space-between' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <div style={{ fontSize: 12, fontWeight: 800, color: C.charcoal, fontFamily: font, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{item.name}</div>
                          <div style={{ fontSize: 10, color: C.muted, fontFamily: font, marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.restaurant_name || 'Restaurant'}</div>
                        </div>
                        <div onClick={(e) => { e.stopPropagation(); onToggleFavItem?.(item); }} style={{ cursor: 'pointer', padding: 4, transition: 'transform 0.2s' }} onMouseEnter={e => e.currentTarget.style.transform='scale(1.1)'} onMouseLeave={e => e.currentTarget.style.transform='scale(1)'}>
                          <span style={{ fontSize: 16 }}>{(favItemIds && favItemIds.has(item.id)) ? '❤️' : '🤍'}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10 }}>
                        <div style={{ fontSize: 13, color: C.saffron, fontWeight: 800, fontFamily: font }}>₹{Number(item.effective_price).toFixed(0)}</div>
                        <button onClick={(e) => { e.stopPropagation(); onAddDish && onAddDish(item); }} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 8, padding: '4px 12px', fontSize: 10, fontWeight: 800, fontFamily: font, cursor: 'pointer', boxShadow: '0 2px 8px rgba(232,98,26,0.25)' }}>ADD</button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
          {results && results.total_restaurants === 0 && results.total_menu_items === 0 && (
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
              <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>No results found for "{query}"</div>
            </div>
          )}
        </>
      )}
    </div>
  )
}


/* ══════════════════════════════════════════════════════════════
   MOOD SELECTOR — Powered by Groq AI
══════════════════════════════════════════════════════════════ */
function MoodSelector({ onSearch }) {
  const moods = [
    { id: 'happy', emoji: '😊', label: 'Happy' },
    { id: 'sad', emoji: '😔', label: 'Comfort' },
    { id: 'romantic', emoji: '❤️', label: 'Romantic' },
    { id: 'party', emoji: '🎉', label: 'Party' },
    { id: 'study', emoji: '📚', label: 'Study' },
    { id: 'gaming', emoji: '🎮', label: 'Gaming' },
    { id: 'workout', emoji: '💪', label: 'Workout' },
    { id: 'family', emoji: '👨‍👩‍👧', label: 'Family' },
    { id: 'tired', emoji: '🥱', label: 'Tired' },
    { id: 'adventurous', emoji: '🤠', label: 'Adventure' },
    { id: 'chill', emoji: '😎', label: 'Chill' },
    { id: 'stressed', emoji: '😫', label: 'Stressed' },
    { id: 'angry', emoji: '😠', label: 'Angry' },
  ]
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const selectMood = async (mood) => {
    setSelected(mood.id)
    setLoading(true)
    setResult(null)
    try {
      const res = await dashboardApi.getMoodFood(mood.id)
      const data = res.data?.data || res.data
      setResult(data)
    } catch {
      setResult({ categories: ['Biryani', 'Pizza', 'Desserts'], message: `Great ${mood.label} food picks for you!`, emoji: mood.emoji })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ background: '#FC8019', padding: '16px', paddingBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <span style={{ fontSize: 18 }}>✨</span>
        <div>
          <div style={{ fontSize: 15, fontWeight: 800, color: '#fff', fontFamily: font }}>What's your mood?</div>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', fontFamily: font }}>AI picks food just for you</div>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: 10, fontWeight: 700, color: '#fff', background: 'rgba(255,255,255,0.2)', padding: '4px 10px', borderRadius: 20, border: 'none', fontFamily: font }}>
          Groq AI ⚡
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', scrollbarWidth: 'none', paddingBottom: 4, alignItems: 'center', justifyContent: 'space-between' }}>
        {moods.map(m => (
          <motion.button
            key={m.id}
            whileTap={{ scale: 0.92 }}
            onClick={() => selectMood(m)}
            style={{
              flexShrink: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              gap: 6, padding: '12px 14px', borderRadius: 16, border: 'none', cursor: 'pointer',
              background: selected === m.id ? '#ffffff' : 'rgba(255,255,255,0.15)',
              transition: 'all 0.2s ease',
              boxShadow: selected === m.id ? '0 4px 16px rgba(0,0,0,0.15)' : 'none',
              minWidth: '72px',
            }}
          >
            <span style={{ fontSize: 24, dropShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>{m.emoji}</span>
            <span style={{ fontSize: 11, fontWeight: 800, color: selected === m.id ? '#0a3822' : '#ffffff', fontFamily: font, whiteSpace: 'nowrap' }}>{m.label}</span>
          </motion.button>
        ))}
      </div>

      <AnimatePresence>
        {(loading || result) && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{ marginTop: 12, overflow: 'hidden' }}
          >
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 0' }}>
                <div style={{ width: 16, height: 16, border: `2px solid ${C.saffron}`, borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.6s linear infinite' }} />
                <span style={{ fontSize: 12, color: C.muted, fontFamily: font }}>AI is finding the perfect food for your mood...</span>
              </div>
            ) : result && (
              <div style={{ background: '#FFF8F0', borderRadius: 14, padding: '12px 14px', border: `1px solid #FFE8CD` }}>
                <div style={{ fontSize: 12, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 10 }}>
                  {result.emoji || '🍽️'} {result.message}
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {(result.dishes || result.categories || []).slice(0, 10).map((item, i) => (
                    <button
                      key={i}
                      onClick={() => onSearch(item)}
                      style={{
                        background: '#fff', border: `1px solid ${C.saffron}`, borderRadius: 20,
                        padding: '5px 12px', fontSize: 11, fontWeight: 700, color: C.saffron,
                        cursor: 'pointer', fontFamily: font, transition: 'all 0.2s',
                      }}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════
   AI CHAT PANEL — Live Groq Integration
══════════════════════════════════════════════════════════════ */
function AIChatPanel({ open, onClose, user }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hey! 🍽️ I'm CraveHub AI. I can help you with Food Delivery, Instamart, Dineout, Parties, and Catering! What are you looking for today?" }
  ])
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const endRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)

  const quickReplies = ['Recommend something', 'Veg options', 'Best deals today', 'Fast delivery']

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 300)
      endRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [open, messages])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg) return
    setInput('')

    // Only keep role, content, and optionally action for history
    const history = messages.map(m => ({ role: m.role, content: m.content }))
    
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: msg
    }])
    setThinking(true)

    try {
      const payload = { message: msg, history }

      const res = await dashboardApi.sendAgentMessage(payload)
      const data = res.data?.data || {}
      const reply = data.reply || "I'm here to help you find amazing food! 😊"
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: reply,
        action: data.action,
        action_data: data.action_data
      }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now. Please try again! 🙏" }])
    } finally {
      setThinking(false)
    }
  }

  if (!open) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)', zIndex: 500, display: 'flex', alignItems: 'flex-end', justifyContent: 'center' }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
      >
        <motion.div
          initial={{ y: '100%' }}
          animate={{ y: 0 }}
          exit={{ y: '100%' }}
          transition={{ type: 'spring', damping: 28, stiffness: 300 }}
          style={{ width: '100%', maxWidth: 480, background: '#fff', borderRadius: '24px 24px 0 0', height: '80vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 -8px 40px rgba(0,0,0,0.15)' }}
        >
          {/* Header */}
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #f0f0f5', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0 }}>
            <div style={{ width: 44, height: 44, borderRadius: 14, background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0 }}>
              🤖
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font }}>CraveHub AI</div>
              <div style={{ fontSize: 11, color: '#22c55e', fontWeight: 700, fontFamily: font, display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 6, height: 6, background: '#22c55e', borderRadius: '50%', display: 'inline-block' }} />
                Online · Powered by Groq AI
              </div>
            </div>
            <button onClick={onClose} style={{ background: '#f0f0f5', border: 'none', borderRadius: 10, width: 32, height: 32, cursor: 'pointer', fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
          </div>

          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.map((m, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start', alignItems: 'flex-end', gap: 8 }}
              >
                {m.role === 'assistant' && (
                  <div style={{ width: 28, height: 28, borderRadius: 10, background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, flexShrink: 0 }}>🤖</div>
                )}
                <div style={{
                  maxWidth: '85%', padding: '10px 14px', borderRadius: m.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                  background: m.role === 'user' ? `linear-gradient(135deg,${C.saffron},${C.tomato})` : '#F8F8F8',
                  color: m.role === 'user' ? '#fff' : C.charcoal,
                  fontSize: 13, fontWeight: 500, fontFamily: font, lineHeight: 1.5,
                }}>
                  {m.content}
                  
                  {/* Rich UI for Action Data */}
                  {m.action && m.action_data && (
                    <div style={{ marginTop: 12, borderTop: `1px solid ${C.border}`, paddingTop: 10 }}>
                      
                      {/* Search Food Results */}
                      {m.action === 'search_food' && m.action_data.dishes && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          <div style={{ fontSize: 11, fontWeight: 700, color: C.sage, textTransform: 'uppercase' }}>Found Items:</div>
                          {m.action_data.dishes.map((dish, idx) => (
                            <div key={idx} style={{ background: '#fff', padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div>
                                <div style={{ fontSize: 13, fontWeight: 700 }}>{dish.name}</div>
                                <div style={{ fontSize: 11, color: C.sage }}>{dish.restaurant}</div>
                              </div>
                              <div style={{ fontSize: 12, fontWeight: 700, color: C.tomato }}>{dish.price}</div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Order Tracking */}
                      {m.action === 'track_order' && m.action_data.found && (
                        <div style={{ background: '#fff', padding: 12, borderRadius: 10, border: `1px solid ${C.border}` }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                            <div style={{ fontSize: 12, fontWeight: 700 }}>Order #{m.action_data.order_number}</div>
                            <div style={{ fontSize: 12, fontWeight: 700, color: '#22c55e' }}>{m.action_data.status_message}</div>
                          </div>
                          <div style={{ fontSize: 11, color: C.sage }}>{m.action_data.restaurant} • ETA: {m.action_data.eta}</div>
                        </div>
                      )}

                      {/* Cancel Order */}
                      {m.action === 'cancel_order' && (
                        <div style={{ background: m.action_data.success ? '#ecfdf5' : '#fef2f2', padding: 10, borderRadius: 8, border: `1px solid ${m.action_data.success ? '#a7f3d0' : '#fecaca'}`, color: m.action_data.success ? '#065f46' : '#991b1b', fontSize: 12, fontWeight: 600 }}>
                          {m.action_data.success ? '✅ ' : '❌ '}{m.action_data.message}
                        </div>
                      )}

                      {/* Orders List */}
                      {m.action === 'get_my_orders' && m.action_data.orders && (
                         <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                           {m.action_data.orders.map((o, idx) => (
                             <div key={idx} style={{ background: '#fff', padding: 10, borderRadius: 8, border: `1px solid ${C.border}` }}>
                               <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                                 <div style={{ fontSize: 12, fontWeight: 700 }}>{o.restaurant}</div>
                                 <div style={{ fontSize: 11, fontWeight: 700, color: o.status === 'delivered' ? '#22c55e' : (o.status === 'cancelled' ? '#ef4444' : C.tomato) }}>{o.status_display}</div>
                               </div>
                               <div style={{ fontSize: 11, color: C.sage, marginBottom: 4 }}>{o.items}</div>
                               <div style={{ fontSize: 11, color: C.charcoal, fontWeight: 600 }}>{o.total} • {o.placed_at}</div>
                             </div>
                           ))}
                         </div>
                      )}
                      
                      {/* Offers */}
                      {m.action === 'get_offers' && m.action_data.offers && (
                         <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                           {m.action_data.offers.map((offer, idx) => (
                             <div key={idx} style={{ background: '#fff', padding: 8, borderRadius: 8, border: `1px dashed ${C.tomato}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                               <div>
                                 <div style={{ fontSize: 12, fontWeight: 800 }}>{offer.code}</div>
                                 <div style={{ fontSize: 11, color: C.sage }}>{offer.title}</div>
                               </div>
                               <div style={{ fontSize: 12, fontWeight: 800, color: '#22c55e', background: '#ecfdf5', padding: '2px 6px', borderRadius: 4 }}>{offer.discount}</div>
                             </div>
                           ))}
                         </div>
                      )}

                      {/* Restaurant Menu */}
                      {m.action === 'get_restaurant_menu' && m.action_data.found && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                          <div style={{ fontSize: 11, fontWeight: 700, color: C.sage, textTransform: 'uppercase' }}>Menu — {m.action_data.restaurant_name}</div>
                          {m.action_data.items.map((item, idx) => (
                            <div key={idx} style={{ background: '#fff', padding: 8, borderRadius: 8, border: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <div style={{ flex: 1 }}>
                                <div style={{ fontSize: 13, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                                  <span style={{ fontSize: 10 }}>{item.is_veg ? '🟢' : '🔴'}</span>
                                  {item.name}
                                </div>
                                {item.description && <div style={{ fontSize: 10, color: C.sage, marginTop: 2 }}>{item.description}</div>}
                              </div>
                              <div style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, marginLeft: 8 }}>{item.price}</div>
                            </div>
                          ))}
                        </div>
                      )}

                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {thinking && (
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8 }}>
                <div style={{ width: 28, height: 28, borderRadius: 10, background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>🤖</div>
                <div style={{ background: '#F8F8F8', borderRadius: '18px 18px 18px 4px', padding: '12px 16px', display: 'flex', gap: 4 }}>
                  {[0, 1, 2].map(i => (
                    <div key={i} style={{ width: 6, height: 6, background: C.saffron, borderRadius: '50%', animation: `bounce 1.2s ${i * 0.2}s infinite` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Quick replies */}
          <div style={{ padding: '8px 16px', display: 'flex', gap: 8, overflowX: 'auto', scrollbarWidth: 'none', flexShrink: 0 }}>
            {quickReplies.map((q, i) => (
              <button key={i} onClick={() => sendMessage(q)}
                style={{ flexShrink: 0, background: '#fff', border: `1px solid ${C.border}`, borderRadius: 20, padding: '6px 14px', fontSize: 11, fontWeight: 700, color: C.charcoal, cursor: 'pointer', fontFamily: font, whiteSpace: 'nowrap' }}
              >{q}</button>
            ))}
          </div>

          {/* Input Area */}
          <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f5', display: 'flex', gap: 10, flexShrink: 0 }}>
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask me anything about food..."
              style={{ flex: 1, background: '#F8F8F8', border: 'none', borderRadius: 20, padding: '12px 16px', fontSize: 13, fontFamily: font, outline: 'none', color: C.charcoal }}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || thinking}
              style={{ width: 44, height: 44, borderRadius: 14, background: input.trim() ? `linear-gradient(135deg,${C.saffron},${C.tomato})` : '#f0f0f5', border: 'none', cursor: input.trim() ? 'pointer' : 'default', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, transition: 'all 0.2s', flexShrink: 0, color: input.trim() ? '#fff' : '#a0a0a0' }}
            >
              ▶
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}

/* ══════════════════════════════════════════════════════════════
   RAZORPAY INTEGRATION HELPER
══════════════════════════════════════════════════════════════ */
function loadRazorpayScript() {
  return new Promise(resolve => {
    if (window.Razorpay) { resolve(true); return }
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}


/* ══════════════════════════════════════════════════════════════
   MAIN DASHBOARD
══════════════════════════════════════════════════════════════ */
export default function CraveHubDashboard() {
  const { user, logout } = useAuthCtx()
  const { C, t } = useSettings()

  /* Data state */
  const [dashData, setDashData]   = useState(null)
  const [loading, setLoading]     = useState(true)
  const [cart, setCart]           = useState(null)
  const [orders, setOrders]       = useState([])
  const [ordersLoading, setOrdersLoading] = useState(false)
  const [notifs, setNotifs]       = useState([])
  const [notifsLoading, setNotifsLoading] = useState(false)
  const [searchResults, setSearchResults] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)
  const [filteredItems, setFilteredItems] = useState([])
  const [filteredLoading, setFilteredLoading] = useState(false)
  const [selectedOffer, setSelectedOffer] = useState(null)

  /* UI state */
  const [activeTab, setActiveTab] = useState('home')
  const [filterType, setFilterType] = useState('All')
  const [sortType, setSortType] = useState('Relevance')
  const [activeProfileSection, setActiveProfileSection] = useState(null)
  const [activeRestaurant, setActiveRestaurant] = useState(null)
  const [activeItemId, setActiveItemId] = useState(null)
  const [cartOpen, setCartOpen]   = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)
  const [aiOpen, setAiOpen]       = useState(false)
  const [trackingOrder, setTrackingOrder] = useState(null)
  const [cartLoading, setCartLoading]     = useState(false)
  const [toast, setToast]         = useState(null)
  
  const [locationDrawerOpen, setLocationDrawerOpen] = useState(false)
  const [selectedAddress, setSelectedAddress] = useState(null)
  const [pendingOrderParams, setPendingOrderParams] = useState(null)

  /* Favorites State */
  const [favRests, setFavRests] = useState([]);
  const [favItems, setFavItems] = useState([]);
  
  const favRestIds = new Set(favRests.map(f => f.restaurant?.id || f.restaurant));
  const favItemIds = new Set(favItems.map(f => f.menu_item_detail?.id || f.menu_item));

  /* Fetch Favorites */
  useEffect(() => {
    if (user) {
      Promise.allSettled([profileApi.getFavorites(), profileApi.getFavoriteItems()]).then(([r1, r2]) => {
        if (r1.status === 'fulfilled') {
           const arr = Array.isArray(r1.value.data) ? r1.value.data : (r1.value.data?.data || r1.value.data?.results || []);
           setFavRests(arr);
        }
        if (r2.status === 'fulfilled') {
           const arr = Array.isArray(r2.value.data) ? r2.value.data : (r2.value.data?.data || r2.value.data?.results || []);
           setFavItems(arr);
        }
      });
    }
  }, [user]);

  const toggleFavRest = async (r) => {
    const rId = r.id;
    const fav = favRests.find(f => f.restaurant?.id === rId || f.restaurant === rId);
    if (fav) {
      setFavRests(prev => prev.filter(f => f.id !== fav.id));
      profileApi.deleteFavorite(fav.id).catch(() => setFavRests(prev => [...prev, fav]));
    } else {
      const tempId = Date.now();
      setFavRests(prev => [...prev, { id: tempId, restaurant: r }]);
      profileApi.addFavorite({ restaurant_id: rId }).then(res => {
        setFavRests(prev => prev.map(f => f.id === tempId ? res.data : f));
      }).catch(() => setFavRests(prev => prev.filter(f => f.id !== tempId)));
    }
  }

  const toggleFavItem = async (item) => {
    const itemId = item.id;
    const fav = favItems.find(f => f.menu_item_detail?.id === itemId || f.menu_item === itemId);
    if (fav) {
      setFavItems(prev => prev.filter(f => f.id !== fav.id));
      profileApi.deleteFavoriteItem(fav.id).catch(() => setFavItems(prev => [...prev, fav]));
    } else {
      const tempId = Date.now();
      setFavItems(prev => [...prev, { id: tempId, menu_item_detail: item }]);
      profileApi.addFavoriteItem({ menu_item: itemId }).then(res => {
        setFavItems(prev => prev.map(f => f.id === tempId ? res.data : f));
      }).catch(() => setFavItems(prev => prev.filter(f => f.id !== tempId)));
    }
  }

  const showToast = useCallback((msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }, [])

  /* Load dashboard */
  useEffect(() => {
    dashboardApi.getHome()
      .then(r => r.data?.success && setDashData(r.data.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  /* Load cart */
  const loadCart = useCallback(() => {
    dashboardApi.getCart()
      .then(r => r.data?.success && setCart(r.data.data))
      .catch(() => {})
  }, [])
  useEffect(() => { loadCart() }, [loadCart])

  /* Tab effects */
  useEffect(() => {
    if (activeTab === 'orders' && orders.length === 0) {
      setOrdersLoading(true)
      dashboardApi.getOrders()
        .then(r => r.data?.success && setOrders(r.data.data?.results || r.data.data || []))
        .catch(() => {})
        .finally(() => setOrdersLoading(false))
    }
    if (activeTab === 'reorder') {
      setOrdersLoading(true)
      dashboardApi.getOrders()
        .then(r => r.data?.success && setOrders(r.data.data?.results || r.data.data || []))
        .catch(() => {})
        .finally(() => setOrdersLoading(false))
    }
    if (activeTab === '99store') {
      setFilteredLoading(true)
      dashboardApi.filterMenu({ max_price: 99, available: true, page_size: 50 })
        .then(r => setFilteredItems(r.data?.data?.results || r.data?.data || []))
        .catch(() => setFilteredItems([]))
        .finally(() => setFilteredLoading(false))
    }
    if (activeTab === 'eatright') {
      setFilteredLoading(true)
      dashboardApi.filterMenu({ is_healthy: true, available: true, page_size: 50 })
        .then(r => setFilteredItems(r.data?.data?.results || r.data?.data || []))
        .catch(() => setFilteredItems([]))
        .finally(() => setFilteredLoading(false))
    }
    if (activeTab === 'offers') {
      setFilteredLoading(true)
      dashboardApi.filterMenu({ has_discount: true, available: true, page_size: 50 })
        .then(r => setFilteredItems(r.data?.data?.results || r.data?.data || []))
        .catch(() => setFilteredItems([]))
        .finally(() => setFilteredLoading(false))
    }
  }, [activeTab])

  const fetchNotifications = useCallback(async (showNewToasts = false) => {
    try {
      const r = await dashboardApi.getNotifications()
      if (r.data?.success) {
        const fetchedNotifs = r.data.data?.results || []
        setNotifs(prev => {
          if (showNewToasts) {
            const prevIds = new Set(prev.map(n => n.id))
            const newUnread = fetchedNotifs.filter(n => !prevIds.has(n.id) && !n.is_read)
            if (newUnread.length > 0) {
              showToast(`🔔 ${newUnread[0].title}`, 'success')
            }
          }
          return fetchedNotifs
        })
      }
    } catch (e) {}
  }, [showToast])

  useEffect(() => {
    fetchNotifications(false)
    const interval = setInterval(() => fetchNotifications(true), 10000)
    return () => clearInterval(interval)
  }, [fetchNotifications])

  const handleNotifOpen = () => {
    setNotifOpen(true)
    if (notifs.length === 0) {
      setNotifsLoading(true)
      fetchNotifications().finally(() => setNotifsLoading(false))
    }
  }

  /* Cart actions */
  const addToCart = async (itemId) => {
    setCartLoading(true)
    try {
      await dashboardApi.addToCart({ menu_item_id: itemId, quantity: 1 })
      await loadCart()
      setCartOpen(true)
    } catch (e) {
      showToast('Failed to add to cart', 'error')
    } finally { setCartLoading(false) }
  }

  const updateCartItem = async (id, qty) => {
    try { await dashboardApi.updateCartItem(id, { quantity: qty }); await loadCart() } catch {}
  }
  const removeCartItem = async (id) => {
    try { await dashboardApi.removeCartItem(id); await loadCart() } catch {}
  }

  /* Add a menu item object to cart (from 99store / eatright) */
  const addMenuItemToCart = async (item) => {
    try {
      await dashboardApi.addToCart({ menu_item_id: item.id, quantity: 1 })
      await loadCart()
      setCartOpen(true)
      showToast(`${item.name} added to cart!`)
    } catch {
      showToast('Failed to add to cart', 'error')
    }
  }

  /* Reorder — clear cart then re-add all items from a past order */
  const handleReorder = async (order) => {
    try {
      await dashboardApi.clearCart()
      for (const item of order.items || []) {
        await dashboardApi.addToCart({ menu_item_id: item.menu_item, quantity: item.quantity })
      }
      await loadCart()
      setCartOpen(true)
      showToast('Items added to cart! 🛒')
    } catch {
      showToast('Failed to reorder', 'error')
    }
  }

  /* Place order (COD) */
  const placeOrder = async (paymentMethod = 'cod', offerCode = '', overrideAddr = null) => {
    try {
      const activeAddr = overrideAddr || selectedAddress;
      const selectedAddrStr = activeAddr ? (activeAddr.full_address || [activeAddr.flat_no, activeAddr.building_name, activeAddr.street, activeAddr.city, activeAddr.state, activeAddr.pincode].filter(Boolean).join(', ')) : null;
      const addr = selectedAddrStr || dashData?.user?.address || user?.address;
      if (!addr || addr === 'Default Address') {
        showToast('Please select a delivery location first!', 'error');
        setCartOpen(false);
        setPendingOrderParams({ type: 'cod', paymentMethod, offerCode });
        setLocationDrawerOpen(true);
        return null;
      }
      const payload = { payment_method: paymentMethod, delivery_address: addr }
      if (offerCode) payload.offer_code = offerCode

      const res = await dashboardApi.placeOrder(payload)
      if (res.data?.success) {
        setCartOpen(false)
        await loadCart()
        setOrders([])
        setActiveTab('orders')
        showToast('Order placed successfully! 🎉')
        return res.data.data
      }
    } catch (e) {
      showToast('Failed to place order: ' + (e?.response?.data?.message || e?.message || ''), 'error')
    }
    return null
  }

  /* Razorpay payment */
  const handleRazorpay = async (offerCode = '', overrideAddr = null) => {
    try {
      const activeAddr = overrideAddr || selectedAddress;
      const selectedAddrStr = activeAddr ? (activeAddr.full_address || [activeAddr.flat_no, activeAddr.building_name, activeAddr.street, activeAddr.city, activeAddr.state, activeAddr.pincode].filter(Boolean).join(', ')) : null;
      const addr = selectedAddrStr || dashData?.user?.address || user?.address;
      if (!addr || addr === 'Default Address') {
        showToast('Please select a delivery location first!', 'error');
        setCartOpen(false);
        setPendingOrderParams({ type: 'razorpay', offerCode });
        setLocationDrawerOpen(true);
        return false;
      }
      const payload = { payment_method: 'razorpay', delivery_address: addr }
      if (offerCode) payload.offer_code = offerCode

      const orderRes = await dashboardApi.placeOrder(payload)
      if (!orderRes.data?.success) { showToast('Failed to create order', 'error'); return false }
      const order = orderRes.data.data

      const payRes = await dashboardApi.initiatePayment({ order_id: order.id })
      if (!payRes.data?.success) { showToast('Payment initiation failed', 'error'); return false }
      const payData = payRes.data.data

      const loaded = await loadRazorpayScript()
      if (!loaded) { showToast('Razorpay SDK failed to load', 'error'); return false }

      return new Promise((resolve) => {
        const options = {
          key:        payData.key_id,
          amount:     payData.amount,
          currency:   payData.currency,
          name:       'CraveHub',
          description: `Order #${String(order.id).slice(0, 8).toUpperCase()}`,
          order_id:   payData.razorpay_order_id,
          prefill: {
            name:    user?.full_name || '',
            contact: user?.mobile_number || '',
          },
          theme: { color: '#E8621A' },
          handler: async (response) => {
            try {
              const verifyRes = await dashboardApi.verifyPayment({
                razorpay_order_id:   response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature:  response.razorpay_signature,
              })
              if (verifyRes.data?.success) {
                setCartOpen(false)
                loadCart() // Don't await here to not block UI
                setOrders([])
                setActiveTab('orders')
                showToast('Payment successful! 🎉')
                resolve(true)
              } else {
                showToast('Payment verification failed', 'error')
                resolve(false)
              }
            } catch {
              showToast('Payment verification error', 'error')
              resolve(false)
            }
          },
          modal: {
            ondismiss: () => {
              showToast('Payment cancelled', 'error')
              resolve(false)
            },
          },
        }
        const rzp = new window.Razorpay(options)
        rzp.open()
      })
    } catch (e) {
      showToast('Payment error: ' + (e?.response?.data?.message || e?.message || 'Unknown error'), 'error')
      return false
    }
  }

  /* Search */
  const handleSearch = async (q) => {
    setSearchQuery(q)
    setActiveTab('search')
    setSearchLoading(true)
    try {
      const lat = selectedAddress?.latitude || null
      const lng = selectedAddress?.longitude || null
      const res = await dashboardApi.search(q, lat, lng)
      res.data?.success && setSearchResults(res.data.data)
    } catch {} finally { setSearchLoading(false) }
  }

  const sectors    = dashData?.sectors    || []
  const categories = dashData?.categories || []
  const banners    = dashData?.banners    || []
  const offers     = dashData?.offers     || []
  let featured = dashData?.featured_restaurants || [];
  let trending = dashData?.trending_restaurants || [];
  let allRests = dashData?.all_restaurants || [];

  const applyFilters = (list) => {
    let res = [...list];
    if (filterType === 'Top Rated') res = res.filter(r => parseFloat(r.rating || 0) >= 4.5);
    if (filterType === 'Fast Delivery') res = res.filter(r => parseInt((r.delivery_time || r.average_delivery_time || '40').match(/\d+/)?.[0] || '40', 10) <= 30);
    
    if (sortType === 'Rating') res.sort((a, b) => parseFloat(b.rating || 0) - parseFloat(a.rating || 0));
    if (sortType === 'Delivery Time') res.sort((a, b) => parseInt((a.delivery_time || a.average_delivery_time || '40').match(/\d+/)?.[0] || '40', 10) - parseInt((b.delivery_time || b.average_delivery_time || '40').match(/\d+/)?.[0] || '40', 10));
    return res;
  };

  featured = applyFilters(featured);
  trending = applyFilters(trending);
  allRests = applyFilters(allRests);
  const notifCount = notifs.filter(n => !n.is_read).length

  if (trackingOrder) {
    return <TrackingView order={trackingOrder} onClose={() => setTrackingOrder(null)} />
  }

  return (
    <div className="flex flex-col relative w-full min-h-screen border-gray-200" style={{
      '--c-saffron': C.saffron,
      '--c-amber': C.amber,
      '--c-tomato': C.tomato,
      '--c-cream': C.cream,
      '--c-warm': C.warm,
      '--c-charcoal': C.charcoal,
      '--c-bark': C.bark,
      '--c-mocha': C.mocha,
      '--c-sand': C.sand,
      '--c-sage': C.sage,
      '--c-muted': C.muted,
      '--c-bg': C.bg,
      '--c-cardBg': C.cardBg,
      '--c-border': C.border,
      '--c-maroon': C.maroon,
      background: C.bg,
      color: C.charcoal
    }}>
      <style>{`
        @keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }
        @keyframes pulse { 0%,100%{box-shadow:0 0 0 0 rgba(232,98,26,0.4)} 50%{box-shadow:0 0 0 8px rgba(232,98,26,0)} }
        @keyframes bounce { 0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)} }
        @keyframes slideUp { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
        @keyframes spin { to { transform: rotate(360deg) } }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { display: none; }
        button { font-family: ${font}; }
        input { font-family: ${font}; }
      `}</style>

      {/* AI Chat Panel — Groq Powered */}
      <AIChatPanel open={aiOpen} onClose={() => setAiOpen(false)} user={user} />

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 60, left: '50%', transform: 'translateX(-50%)',
          zIndex: 999, background: toast.type === 'error' ? '#D94F2B' : '#2E8B57',
          color: '#fff', padding: '10px 20px', borderRadius: 12, fontSize: 13, fontWeight: 700,
          fontFamily: font, boxShadow: '0 4px 20px rgba(0,0,0,0.2)', animation: 'slideUp 0.3s ease',
          whiteSpace: 'nowrap',
        }}>
          {toast.type === 'error' ? '❌' : '✅'} {toast.msg}
        </div>
      )}

      <Header
        user={user || dashData?.user}
        notifCount={notifCount}
        onNotif={handleNotifOpen}
        onLocationClick={() => setLocationDrawerOpen(true)}
        onProfileClick={() => setActiveTab('profile')}
        selectedAddress={selectedAddress}
      />

      {/* Main content */}
      <div style={{ flex: 1, overflowY: 'auto', paddingBottom: 80, backgroundColor: '#fff' }}>
        <GreetingSection user={user || dashData?.user} onAI={() => setAiOpen(true)} />

        {/* Global Service Hub */}
        <ServiceHub activeService={activeTab} onService={(id) => setActiveTab(id)} />
        
        {(activeTab === 'home' || activeTab === 'search') && <SearchBar onSearch={handleSearch} />}
        {activeTab === 'home' && <MoodSelector onSearch={handleSearch} />}

        {/* Home tab */}
        {activeTab === 'home' && (
          <>
            <AIBanner selectedAddress={selectedAddress} onSearch={handleSearch} />
            <div style={{ height: 8, background: C.bg }} />
            <CategoryRow onSelect={handleSearch} />
            <TodaysDeals offers={offers} loading={loading} onOfferClick={(o) => {
              setSelectedOffer(o)
              setActiveTab('offers')
            }} />
            
            <div style={{ height: 8, background: C.bg }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', overflowX: 'auto', scrollbarWidth: 'none', borderBottom: `1px solid ${C.border}` }}>
              <div style={{ position: 'relative' }}>
                <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, display: 'flex', alignItems: 'center', gap: 6, background: filterType !== 'All' ? '#FFF8EE' : '#fff', borderColor: filterType !== 'All' ? C.saffron : C.border }}><span style={{fontSize:14}}>⚙️</span> {filterType === 'All' ? 'Filter' : filterType}</div>
                <select value={filterType} onChange={e => setFilterType(e.target.value)} style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%' }}>
                  <option value="All">All Filters</option>
                  <option value="Top Rated">Top Rated 4.5+</option>
                  <option value="Fast Delivery">Fast Delivery</option>
                </select>
              </div>
              <div style={{ position: 'relative' }}>
                <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, display: 'flex', alignItems: 'center', gap: 6, background: sortType !== 'Relevance' ? '#FFF8EE' : '#fff', borderColor: sortType !== 'Relevance' ? C.saffron : C.border }}>{sortType === 'Relevance' ? 'Sort by' : sortType} <span style={{fontSize:10}}>▼</span></div>
                <select value={sortType} onChange={e => setSortType(e.target.value)} style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer', width: '100%' }}>
                  <option value="Relevance">Relevance</option>
                  <option value="Rating">Rating</option>
                  <option value="Delivery Time">Delivery Time</option>
                </select>
              </div>
              <div onClick={() => setActiveTab('99store')} style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, cursor: 'pointer', whiteSpace: 'nowrap' }}>99 Store</div>
              <div onClick={() => setActiveTab('offers')} style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, cursor: 'pointer', whiteSpace: 'nowrap' }}>Offers</div>
            </div>

            {/* Featured */}
            {(loading || featured.length > 0) && (
              <>
                <Section>
                  <SectionHead title="Featured Picks" sub="Handpicked today" emoji="⭐" />
                  {loading
                    ? <div style={{ display: 'flex', gap: 12, padding: '0 16px 16px', overflowX: 'auto' }}>{[...Array(3)].map((_, i) => <Skel key={i} w={188} h={220} r={18} />)}</div>
                    : <div style={{ display: 'flex', gap: 12, padding: '0 16px 16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
                        {featured.map(r => <RestaurantCard key={r.id} r={r} compact onClick={() => setActiveRestaurant(r.id)} isFavorite={favRestIds.has(r.id)} onToggleFavorite={toggleFavRest} />)}
                      </div>
                  }
                </Section>
                <div style={{ height: 8, background: C.bg }} />
              </>
            )}

            {/* Trending */}
            {(loading || trending.length > 0) && (
              <>
                <Section>
                  <SectionHead title="Trending Near You" sub="Most ordered right now" emoji="🔥" />
                  {loading
                    ? <div style={{ display: 'flex', gap: 12, padding: '0 16px 16px', overflowX: 'auto' }}>{[...Array(3)].map((_, i) => <Skel key={i} w={188} h={220} r={18} />)}</div>
                    : <div style={{ display: 'flex', gap: 12, padding: '0 16px 16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
                        {trending.map(r => <RestaurantCard key={r.id} r={r} compact onClick={() => setActiveRestaurant(r.id)} isFavorite={favRestIds.has(r.id)} onToggleFavorite={toggleFavRest} />)}
                      </div>
                  }
                </Section>
                <div style={{ height: 8, background: C.bg }} />
              </>
            )}



            {/* All restaurants */}
            <div className="px-4 pb-4">
              <SectionHead title="All Restaurants" sub={loading ? '...' : `${allRests.length} available`} emoji="🍴" />
              {loading
                ? [...Array(4)].map((_, i) => <Skel key={i} h={200} r={18} mb={10} />)
                : <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-2">
                    {allRests.map(r => <RestaurantCard key={r.id} r={r} onClick={() => setActiveRestaurant(r.id)} isFavorite={favRestIds.has(r.id)} onToggleFavorite={toggleFavRest} />)}
                  </div>
              }
            </div>
          </>
        )}

        {/* Search tab */}
        {activeTab === 'search' && (
          <SearchResultsView query={searchQuery} results={searchResults} loading={searchLoading} onRestaurant={(r) => { setActiveRestaurant(r.id); setActiveItemId(r.itemId || null); }} onAddDish={addMenuItemToCart} favRestIds={favRestIds} onToggleFavRest={toggleFavRest} favItemIds={favItemIds} onToggleFavItem={toggleFavItem} />
        )}

        {/* Orders tab */}
        {activeTab === 'orders' && (
          <OrdersView orders={orders} loading={ordersLoading} onTrack={(o) => setTrackingOrder(o)} onReorder={handleReorder} />
        )}

        {/* 99 Store tab */}
        {activeTab === '99store' && (
          <MenuFilteredView
            title="99 Store"
            emoji="🏪"
            sub="Everything under ₹99"
            items={filteredItems}
            loading={filteredLoading}
            onAdd={addMenuItemToCart}
            favItemIds={favItemIds}
            onToggleFavItem={toggleFavItem}
          />
        )}

        {/* EatRight tab */}
        {activeTab === 'eatright' && (
          <MenuFilteredView
            title="EatRight"
            emoji="🥗"
            sub="Nutritious & healthy picks"
            items={filteredItems}
            loading={filteredLoading}
            onAdd={addMenuItemToCart}
            favItemIds={favItemIds}
            onToggleFavItem={toggleFavItem}
          />
        )}

        {/* Offers/Deals tab */}
        {activeTab === 'offers' && (
          <MenuFilteredView
            title="Today's Deals"
            emoji="🏷️"
            sub="Discounted items & special offers"
            items={filteredItems}
            loading={filteredLoading}
            onAdd={addMenuItemToCart}
            highlightOffer={selectedOffer}
            allOffers={offers}
            favItemIds={favItemIds}
            onToggleFavItem={toggleFavItem}
          />
        )}

        {/* Reorder tab */}
        {activeTab === 'reorder' && (
          <OrdersView orders={orders} loading={ordersLoading} onTrack={(o) => setTrackingOrder(o)} onReorder={handleReorder} />
        )}

        {/* Profile tab */}
        {activeTab === 'profile' && (
          <ProfileView user={user || dashData?.user} onLogout={logout} onSectionClick={(sec) => {
            if (sec === 'orders') setActiveTab('orders')
            else setActiveProfileSection(sec)
          }} />
        )}

        {/* Service Pages */}
        {activeTab === 'instamart' && <InstamartPage onBack={() => setActiveTab('home')} goHome={() => setActiveTab('home')} />}
        {activeTab === 'dining' && <DiningPage goHome={() => setActiveTab('home')} />}
        {activeTab === 'party' && <PartiesPage goHome={() => setActiveTab('home')} />}
        {activeTab === 'gifts' && <GiftsPage goHome={() => setActiveTab('home')} />}
        {activeTab === 'catering' && <CateringPage goHome={() => setActiveTab('home')} />}
        
        {/* Genie Placeholder */}
        {activeTab === 'genie' && (
          <div style={{ padding: '60px 20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <div style={{ fontSize: 48 }}>🧞‍♂️</div>
            <div style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, fontFamily: font }}>Genie</div>
            <div style={{ fontSize: 15, color: C.muted, fontFamily: font, maxWidth: 280, lineHeight: 1.5 }}>
              We are working hard to bring this feature to you. Stay tuned!
            </div>
          </div>
        )}
      </div>

      {/* Floating Cart for Food Delivery */}
      {cart?.item_count > 0 && ['home', 'search', 'orders', '99store', 'eatright', 'offers', 'profile'].includes(activeTab) && (
        <div style={{ position: 'fixed', bottom: activeRestaurant ? 20 : 80, left: 16, right: 16, background: 'linear-gradient(135deg, #D94F2B, #E8621A)', borderRadius: 16, padding: '14px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 450, boxShadow: '0 4px 20px rgba(217,79,43,0.4)' }}>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, color: '#fff', fontFamily: font }}>{cart.item_count} item{cart.item_count !== 1 ? 's' : ''} added</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.8)', fontFamily: font }}>Extra charges may apply</div>
          </div>
          <button onClick={() => setCartOpen(true)} style={{ background: '#fff', border: 'none', borderRadius: 10, padding: '10px 20px', fontSize: 13, fontWeight: 800, color: '#D94F2B', cursor: 'pointer', fontFamily: font }}>View Cart →</button>
        </div>
      )}

      {/* Global Bottom Navigation (Only for Food Hub) */}
      {['home', 'search', 'orders', '99store', 'eatright', 'offers', 'profile'].includes(activeTab) && <BottomNav active={activeTab} onChange={setActiveTab} />}



      {/* Cart Drawer */}
      <CartDrawer
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        cart={cart}
        onUpdate={updateCartItem}
        onRemove={removeCartItem}
        onPlaceOrder={placeOrder}
        onPayWithRazorpay={handleRazorpay}
        onClearCart={async () => {
          try { await dashboardApi.clearCart(); await loadCart() } catch {}
        }}
      />

      {/* Notifications Panel */}
      {notifOpen && (
        <NotifPanel
          notifs={notifs}
          loading={notifsLoading}
          onClose={() => setNotifOpen(false)}
          onMarkAll={() => {
            dashboardApi.markAllRead().catch(() => {})
            setNotifs(prev => prev.map(n => ({ ...n, is_read: true })))
          }}
        />
      )}


      {/* Profile Sub View */}
      {activeProfileSection && (
        <ProfileSubView
          section={activeProfileSection}
          onClose={() => setActiveProfileSection(null)}
          user={user || dashData?.user}
          onRestaurantClick={(id) => { setActiveProfileSection(null); setActiveRestaurant(id); }}
          onMenuItemClick={(restId, itemId) => { setActiveProfileSection(null); setActiveRestaurant(restId); setActiveItemId(itemId); }}
          allOffers={offers}
          onOfferClick={(o) => {
            setActiveProfileSection(null);
            setSelectedOffer(o);
            setActiveTab('offers');
          }}
        />
      )}

      {/* Restaurant View */}
      {activeRestaurant && (
        <RestaurantView 
          restaurantId={activeRestaurant} 
          highlightItemId={activeItemId}
          onClose={() => { setActiveRestaurant(null); setActiveItemId(null); }} 
          onAdd={addToCart} 
          favRestIds={favRestIds}
          favItemIds={favItemIds}
          onToggleFavRest={toggleFavRest}
          onToggleFavItem={toggleFavItem}
        />
      )}

      {/* Location Drawer */}
      <LocationDrawer
        open={locationDrawerOpen}
        onClose={() => setLocationDrawerOpen(false)}
        onSelectAddress={(addr) => {
          setSelectedAddress(addr);
          setLocationDrawerOpen(false);
          if (pendingOrderParams) {
            setTimeout(() => {
              if (pendingOrderParams.type === 'cod') {
                placeOrder(pendingOrderParams.paymentMethod, pendingOrderParams.offerCode, addr);
              } else if (pendingOrderParams.type === 'razorpay') {
                handleRazorpay(pendingOrderParams.offerCode, addr);
              }
            }, 300);
            setPendingOrderParams(null);
          }
        }}
      />
    </div>
  )
}
