import re

with open('src/pages/CraveHubDashboard.jsx.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace Design tokens
content = re.sub(
    r'/\* ── Design tokens ──.*?const font = [^\n]*\n',
    '''/* ── Design tokens ─────────────────────────────────────────── */
const C = {
  saffron: '#FC8019', amber: '#FF9E2A', tomato: '#E25E1A',
  cream: '#FDF6EE',   warm: '#FFFFFF', charcoal: '#02060C',
  bark: '#02060C99',  mocha: '#02060CEB', sand: '#F0F0F5',
  sage: '#118C4F',    cardBg: '#FFFFFF', border: '#F0F0F5',
  muted: '#02060C99', bg: '#F0F0F5',
  maroon: '#6B0B22',  maroonLight: '#8A1538',
  lightGray: '#F2F6FC'
}
const font = "'Proxima Nova', 'Inter', system-ui, sans-serif"
''',
    content,
    flags=re.DOTALL
)

# 2. Replace Header
content = re.sub(
    r'/\* ── Header ──.*?/\* ── Search ──',
    '''/* ── Header ─────────────────────────────────────────────────── */
function Header({ user, notifCount, onNotif, onCart, cartCount, onAI }) {
  return (
    <div style={{ background: C.maroon, padding: '16px 16px 0', position: 'sticky', top: 0, zIndex: 50, color: '#fff' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ fontSize: 20 }}>🏠</span>
            <span style={{ fontSize: 18, fontWeight: 800, fontFamily: font }}>Home</span>
            <span style={{ fontSize: 14 }}>⌵</span>
          </div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', fontFamily: font, maxWidth: 200, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
            1/103, Venkateswara Nagar, Perungu...
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ background: '#fff', borderRadius: 20, padding: '4px 10px', display: 'flex', alignItems: 'center', gap: 6, cursor: 'pointer' }}>
            <div style={{ fontSize: 14 }}>📱</div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: 11, fontWeight: 800, color: C.charcoal, lineHeight: 1 }}>1st year</span>
              <span style={{ fontSize: 11, fontWeight: 800, color: C.charcoal, lineHeight: 1 }}>FREE</span>
            </div>
          </div>
          <div onClick={onNotif} style={{ width: 40, height: 40, borderRadius: '50%', background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.charcoal, fontSize: 20, cursor: 'pointer', position: 'relative' }}>
            👤
            {notifCount > 0 && <span style={{ position: 'absolute', top: -2, right: -2, background: C.saffron, color: '#fff', borderRadius: 99, fontSize: 8, fontWeight: 800, padding: '1px 4px' }}>{notifCount}</span>}
          </div>
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: 10, overflowX: 'auto', scrollbarWidth: 'none', paddingBottom: 16, borderBottom: `20px solid ${C.maroon}`, borderRadius: '0 0 24px 24px', position: 'relative', zIndex: 2 }}>
        {[
          { icon: '🍔', label: 'Food', active: true },
          { icon: '🛒', label: 'Instamart', active: false, badge: '15 mins' },
          { icon: '🍽️', label: 'Dineout', active: false },
          { icon: '🎪', label: 'Scenes', active: false },
          { icon: '🎁', label: 'Giftable', active: false }
        ].map((item, i) => (
          <div key={i} style={{ 
            background: item.active ? C.maroonLight : 'rgba(255,255,255,0.1)', 
            borderRadius: 16, padding: '10px 14px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, minWidth: 70, position: 'relative'
          }}>
            {item.badge && <div style={{ position: 'absolute', top: -8, background: '#0F65FF', color: '#fff', fontSize: 9, fontWeight: 800, padding: '2px 6px', borderRadius: 4, whiteSpace: 'nowrap' }}>{item.badge}</div>}
            <span style={{ fontSize: 24 }}>{item.icon}</span>
            <span style={{ fontSize: 12, fontWeight: 700, fontFamily: font }}>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ── Search ──''',
    content,
    flags=re.DOTALL
)

# 3. Replace SearchBar
content = re.sub(
    r'function SearchBar.*?/\* ── Banner Carousel ──',
    '''function SearchBar({ onSearch }) {
  const [q, setQ] = useState('')
  const submit = (e) => { e.preventDefault(); if (q.trim()) onSearch(q.trim()) }
  return (
    <form onSubmit={submit} style={{ padding: '0 16px', position: 'relative', zIndex: 10, marginTop: -10 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: '#fff', borderRadius: 16, padding: '0 14px', height: 56, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <span style={{ fontSize: 20, color: C.muted }}>🔍</span>
        <input
          value={q} onChange={e => setQ(e.target.value)}
          placeholder="Search for 'Sweets'"
          style={{ flex: 1, background: 'none', border: 'none', outline: 'none', fontSize: 15, color: C.charcoal, fontFamily: font }}
        />
        <span style={{ fontSize: 20, color: C.saffron, borderRight: `1px solid ${C.border}`, paddingRight: 10 }}>🎙️</span>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <span style={{ fontSize: 9, fontWeight: 800, color: C.sage, fontFamily: font }}>VEG</span>
          <div style={{ width: 24, height: 12, borderRadius: 12, background: C.sand, position: 'relative' }}>
             <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#fff', border: `1px solid ${C.sage}`, position: 'absolute', top: 1, left: 1 }} />
          </div>
        </div>
      </div>
    </form>
  )
}

/* ── Banner Carousel ──''',
    content,
    flags=re.DOTALL
)

# 4. Replace Banner Carousel + Services + Offers
content = re.sub(
    r'function BannerCarousel.*?/\* ── Category Pills ──',
    '''function WelcomeSection() {
  return (
    <div style={{ background: C.maroonLight, padding: '40px 16px 20px', marginTop: -30 }}>
      <div style={{ fontSize: 28, fontWeight: 900, color: '#fff', fontFamily: font, marginBottom: 16, display: 'flex', alignItems: 'baseline', gap: 6 }}>
        Welcome, <span style={{ fontFamily: "'Dancing Script', cursive", color: C.amber, fontSize: 32 }}>foodie!</span>
      </div>
      <div style={{ display: 'flex', gap: 12, overflowX: 'auto', scrollbarWidth: 'none' }}>
        <div style={{ minWidth: 140, background: C.maroon, borderRadius: 16, padding: '12px', display: 'flex', flexDirection: 'column', gap: 4, position: 'relative', overflow: 'hidden' }}>
          <div style={{ fontSize: 18, fontWeight: 900, color: C.amber, fontFamily: font }}>99 store</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', fontFamily: font }}>Meals At ₹99</div>
          <img src="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=200&h=200&fit=crop" style={{ position: 'absolute', right: -20, bottom: -20, width: 90, height: 90, objectFit: 'cover', borderRadius: '50%' }} alt="burger" />
        </div>
        <div style={{ minWidth: 140, background: C.maroon, borderRadius: 16, padding: '12px', display: 'flex', flexDirection: 'column', gap: 4, position: 'relative', overflow: 'hidden' }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: '#fff', fontFamily: font }}>Flat</div>
          <div style={{ fontSize: 18, fontWeight: 900, color: C.amber, fontFamily: font }}>₹200 OFF</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', fontFamily: font }}>& More</div>
          <img src="https://images.unsplash.com/photo-1513104890138-7c749659a591?w=200&h=200&fit=crop" style={{ position: 'absolute', right: -20, bottom: -20, width: 90, height: 90, objectFit: 'cover', borderRadius: '50%' }} alt="pizza" />
        </div>
        <div style={{ minWidth: 140, background: C.maroon, borderRadius: 16, padding: '12px', display: 'flex', flexDirection: 'column', gap: 4, position: 'relative', overflow: 'hidden' }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: '#fff', fontFamily: font }}>Get</div>
          <div style={{ fontSize: 18, fontWeight: 900, color: C.amber, fontFamily: font }}>60% OFF</div>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', fontFamily: font }}>+ Cashback</div>
          <img src="https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?w=200&h=200&fit=crop" style={{ position: 'absolute', right: -20, bottom: -20, width: 90, height: 90, objectFit: 'cover', borderRadius: '50%' }} alt="biryani" />
        </div>
      </div>
    </div>
  )
}

function DominoBanner() {
  return (
    <div style={{ padding: '16px' }}>
      <div style={{ background: '#F0F5FA', borderRadius: 16, overflow: 'hidden', display: 'flex', position: 'relative', border: '1px solid #E2E8F0' }}>
        <div style={{ padding: '16px', flex: 1, zIndex: 2 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#64748B', fontFamily: font }}>Domino's Pizza</div>
          <div style={{ fontSize: 20, fontWeight: 900, color: '#0F172A', fontFamily: font, lineHeight: 1.2, marginTop: 4 }}>Get items at ₹59*</div>
          <div style={{ fontSize: 12, color: '#64748B', fontFamily: font, marginTop: 4 }}>Exclusively on CraveHub!</div>
          <button style={{ background: '#1E293B', color: '#fff', border: 'none', borderRadius: 20, padding: '6px 16px', fontSize: 11, fontWeight: 800, fontFamily: font, marginTop: 12 }}>ORDER NOW</button>
        </div>
        <div style={{ width: 140, position: 'relative' }}>
           <img src="https://images.unsplash.com/photo-1573821663912-569905455b1c?w=300&h=200&fit=crop" style={{ position: 'absolute', right: -20, top: 10, width: 160, height: 120, objectFit: 'cover', borderRadius: 12 }} alt="dominos" />
        </div>
      </div>
      {/* Filter Chips */}
      <div style={{ display: 'flex', gap: 10, marginTop: 16, overflowX: 'auto', scrollbarWidth: 'none' }}>
        <div style={{ border: `1px solid ${C.border}`, borderRadius: 20, padding: '8px 16px', fontSize: 12, fontWeight: 800, color: C.saffron, fontFamily: font, whiteSpace: 'nowrap' }}>MIN Rs. 100 OFF</div>
        <div style={{ border: `1px solid ${C.border}`, borderRadius: 20, padding: '8px 16px', fontSize: 12, fontWeight: 800, color: C.charcoal, fontFamily: font, whiteSpace: 'nowrap' }}>FAST DELIVERY</div>
        <div style={{ border: `1px solid ${C.border}`, borderRadius: 20, padding: '8px 16px', fontSize: 12, fontWeight: 800, color: C.charcoal, fontFamily: font, whiteSpace: 'nowrap' }}>RATING 4.0+</div>
      </div>
    </div>
  )
}

/* ── Category Pills ──''',
    content,
    flags=re.DOTALL
)

# 5. Replace CategoryRow
content = re.sub(
    r'function CategoryRow.*?/\* ── Restaurant Card ──',
    '''function CategoryRow({ categories, loading, onSelect }) {
  const items = categories.length > 0 ? categories : [
    { name: 'Biryani', image: 'https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=200&h=200&fit=crop' },
    { name: 'Pizza', image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=200&h=200&fit=crop' },
    { name: 'Burgers', image: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=200&h=200&fit=crop' },
    { name: 'Chinese', image: 'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=200&h=200&fit=crop' },
    { name: 'South Indian', image: 'https://images.unsplash.com/photo-1610192244261-3f33de3f55e4?w=200&h=200&fit=crop' }
  ];

  return (
    <Section>
      <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font, padding: '16px 16px 12px' }}>What's on your mind?</div>
      <div style={{ display: 'flex', gap: 16, padding: '0 16px 16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
        {items.map((c, i) => (
          <div key={i} onClick={() => onSelect?.(c)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, cursor: 'pointer', minWidth: 72 }}>
            <div style={{ width: 72, height: 72, borderRadius: '50%', overflow: 'hidden', background: C.sand }}>
              <img src={c.image || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=200&h=200&fit=crop'} alt={c.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            </div>
            <span style={{ fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, whiteSpace: 'nowrap' }}>{c.name}</span>
          </div>
        ))}
      </div>
    </Section>
  )
}

/* ── Restaurant Card ──''',
    content,
    flags=re.DOTALL
)

# 6. Replace RestaurantCard
content = re.sub(
    r'function RestaurantCard.*?/\* ── Offer Strip ──',
    '''function RestaurantCard({ r, compact = false, onClick }) {
  const ratingColor = parseFloat(r.rating) >= 4 ? C.sage : C.saffron;
  return (
    <div onClick={() => onClick?.(r)} style={{ width: compact ? 260 : '100%', flexShrink: compact ? 0 : undefined, marginBottom: compact ? 0 : 20, cursor: 'pointer' }}>
      <div style={{ position: 'relative', borderRadius: 20, overflow: 'hidden', height: compact ? 160 : 200, background: C.sand, marginBottom: 12 }}>
        <img src={r.cover_image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&h=300&fit=crop'} alt={r.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, transparent 50%)' }} />
        <div style={{ position: 'absolute', top: 12, right: 12, width: 28, height: 28, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 16 }}>🤍</div>
        <div style={{ position: 'absolute', bottom: 12, left: 12, color: '#fff', fontSize: 20, fontWeight: 900, fontFamily: font, textShadow: '0 2px 8px rgba(0,0,0,0.5)' }}>% Items at ₹49</div>
        <div style={{ position: 'absolute', bottom: 12, right: 12, background: '#fff', color: C.charcoal, fontSize: 11, fontWeight: 800, padding: '4px 8px', borderRadius: 8, fontFamily: font }}>{r.average_delivery_time} mins</div>
      </div>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: C.charcoal, fontFamily: font, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.name}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 3, background: ratingColor, borderRadius: 12, padding: '2px 6px', color: '#fff' }}>
            <span style={{ fontSize: 10 }}>★</span>
            <span style={{ fontSize: 11, fontWeight: 800, fontFamily: font }}>{r.rating}</span>
          </div>
          <span style={{ fontSize: 13, color: C.muted, fontFamily: font }}>• 30-35 mins</span>
        </div>
        <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r.categories?.[0]?.name || 'Indian'}, {r.categories?.[1]?.name || 'Fast Food'}</div>
        <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 2 }}>📍 {r.address?.city || 'City Center'} • ₹300 for two</div>
      </div>
    </div>
  )
}

/* ── Offer Strip ──''',
    content,
    flags=re.DOTALL
)

# 7. Modify CraveHubDashboard render elements
content = re.sub(
    r'<BannerCarousel banners=\{banners\} loading=\{loading\} />.*?<div style=\{\{ height: 8, background: C\.bg \}\} />',
    '''<WelcomeSection />
            <DominoBanner />''',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'<ServiceHub sectors=\{sectors\}.*?background: C\.bg \}\} />',
    ''' ''',
    content,
    flags=re.DOTALL
)

content = re.sub(
    r'<OfferStrip offers=\{offers\} loading=\{loading\} />.*?<MoodBar onMood=\{\(m\) => handleSearch\(m\.label\)\} />.*?<div style=\{\{ height: 8, background: C\.bg \}\} />',
    '''<div style={{ display: 'flex', gap: 10, padding: '16px', overflowX: 'auto', scrollbarWidth: 'none', borderBottom: `1px solid ${C.border}` }}>
              <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, display: 'flex', alignItems: 'center', gap: 6 }}><span style={{fontSize:14}}>⚙️</span> Filter</div>
              <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font, display: 'flex', alignItems: 'center', gap: 6 }}>Sort by <span style={{fontSize:10}}>▼</span></div>
              <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>99 Store</div>
              <div style={{ border: `1px solid ${C.border}`, borderRadius: 12, padding: '8px 12px', fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Offers</div>
            </div>''',
    content,
    flags=re.DOTALL
)

# 8. Bottom Nav
content = re.sub(
    r'function BottomNav.*?/\* ── Profile Sub View ──',
    '''function BottomNav({ active, onChange }) {
  const tabs = [
    { id: 'home', icon: '🍲', label: 'Food' },
    { id: 'search', icon: '🏪', label: '99 store' },
    { id: 'orders', icon: '🥗', label: 'EatRight' },
    { id: 'profile', icon: '🛒', label: 'Reorder' },
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

/* ── Profile Sub View ──''',
    content,
    flags=re.DOTALL
)


with open('src/pages/CraveHubDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactoring complete.")
