import { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'

const C = {
  charcoal: '#1C1410', sand: '#F0E0CC', border: '#F0E4D4',
  muted: '#9B7B60', bg: '#FAF3EC',
}
const font = "'Poppins', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return <div style={{ width: w, height: h, borderRadius: r, marginBottom: mb, background: `linear-gradient(90deg,${C.sand} 25%,#FDE8CC 50%,${C.sand} 75%)`, backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />
}

export default function CateringPage({ goHome }) {
  const [menus, setMenus] = useState([])
  const [loading, setLoading] = useState(true)
  const [caterTab, setCaterTab] = useState('catering')
  const [selectedMenu, setSelectedMenu] = useState(null)
  const [viewingMenu, setViewingMenu] = useState(null)
  const [form, setForm] = useState({ date: '', guests: 50, venue: '', budget: '', requests: '' })
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    dashboardApi.getCateringMenus()
      .then(r => setMenus(r.data?.results || r.data?.data || r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleInquire = async () => {
    if (!form.date || !form.venue) return
    try {
      await dashboardApi.createCateringInquiry({
        catering_menu: selectedMenu.id,
        event_date: form.date,
        guest_count: form.guests,
        venue_address: form.venue,
        budget: form.budget || null,
        special_requests: form.requests
      })
      setSuccess(true)
      setTimeout(() => { setSuccess(false); setSelectedMenu(null) }, 3000)
    } catch {
      alert('Could not submit inquiry. Please try again.')
    }
  }

  if (loading) return (
    <div style={{ padding: 16 }}>
      <Skel h={60} r={16} mb={16} />
      {[...Array(5)].map((_, i) => <Skel key={i} h={120} r={16} mb={12} />)}
    </div>
  )

  const renderDashboard = () => (
    <div style={{ background: C.bg, minHeight: '100vh', paddingBottom: 80 }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg, #1565C0, #1976D2)', padding: '20px 16px 16px', color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <span style={{ fontSize: 28 }}>🍱</span>
          <div>
            <div style={{ fontSize: 20, fontWeight: 900, fontFamily: font }}>Catering Services</div>
            <div style={{ fontSize: 12, opacity: 0.85, fontFamily: font }}>Premium catering for your events</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '20px 16px' }}>
        {menus.map(m => {
          const isSoldOut = m.stock_status === 'sold_out';
          
          return (
            <div key={m.id} onClick={() => !isSoldOut && setViewingMenu(m)} style={{ background: '#fff', borderRadius: 16, marginBottom: 16, border: `1px solid ${C.border}`, overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', padding: '16px', opacity: isSoldOut ? 0.7 : 1, filter: isSoldOut ? 'grayscale(30%)' : 'none', position: 'relative', cursor: isSoldOut ? 'default' : 'pointer' }}>
              {isSoldOut && (
                <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.6)', backdropFilter: 'blur(1px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 10 }}>
                  <span style={{ color: '#C62828', fontSize: 16, fontWeight: 900, letterSpacing: 1, background: '#FFEBEE', padding: '6px 12px', borderRadius: 8, border: '1px solid #FFCDD2' }}>
                    UNAVAILABLE
                  </span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: m.is_veg ? '#FFF7ED' : '#FFEBEE', color: m.is_veg ? '#FC8019' : '#C62828', fontWeight: 800, fontFamily: font, border: `1px solid ${m.is_veg ? '#FDBA74' : '#FFCDD2'}` }}>
                      {m.is_veg ? 'VEG' : 'NON-VEG'}
                    </span>
                    <span style={{ fontSize: 15, fontWeight: 900, color: C.charcoal, fontFamily: font }}>{m.name}</span>
                  </div>
                  <div style={{ fontSize: 12, color: C.muted, fontFamily: font }}>{m.restaurant_name || m.restaurant?.name || 'Restaurant'}</div>
                </div>
                <div style={{ fontSize: 16, fontWeight: 900, color: '#1565C0', fontFamily: font }}>₹{m.price_per_plate}<span style={{ fontSize: 10, color: C.muted }}>/plate</span></div>
              </div>
              
              <div style={{ fontSize: 12, color: C.charcoal, fontFamily: font, lineHeight: 1.4, marginBottom: 8 }}>{m.description}</div>
              {m.cuisine_type && <div style={{ fontSize: 11, color: '#1976D2', fontWeight: 700, fontFamily: font, marginBottom: 12 }}>{m.cuisine_type}</div>}
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: `1px dashed ${C.border}`, paddingTop: 12 }}>
                <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Min. {m.min_plates} plates</div>
                <button onClick={(e) => { e.stopPropagation(); !isSoldOut && setSelectedMenu(m); }} disabled={isSoldOut} style={{ background: isSoldOut ? '#F5F5F5' : '#E3F2FD', border: `1px solid ${isSoldOut ? C.border : '#1976D2'}`, borderRadius: 10, padding: '6px 16px', color: isSoldOut ? '#9E9E9E' : '#1565C0', fontSize: 12, fontWeight: 800, cursor: isSoldOut ? 'not-allowed' : 'pointer', fontFamily: font }}>
                  {isSoldOut ? 'Sold Out' : 'Inquire Now'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Detail View Overlay */}
      {viewingMenu && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 400, background: C.bg, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ position: 'relative', height: 260, flexShrink: 0, background: C.sand }}>
            <img src={viewingMenu.restaurant?.cover_image || viewingMenu.restaurant?.logo || 'https://images.unsplash.com/photo-1555244162-803834f70033?w=1200'} alt="cover" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 40%, rgba(0,0,0,0.8) 100%)' }} />
            
            <button onClick={() => setViewingMenu(null)} style={{ position: 'absolute', top: 40, left: 16, width: 40, height: 40, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.4)', color: '#fff', fontSize: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
              ←
            </button>

            <div style={{ position: 'absolute', bottom: -20, left: 16, right: 16, background: '#fff', borderRadius: 20, padding: '20px', boxShadow: '0 8px 30px rgba(92,42,15,0.12)', border: `1px solid ${C.border}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h1 style={{ fontSize: 22, fontWeight: 900, color: C.charcoal, fontFamily: font, margin: '0 0 4px 0' }}>{viewingMenu.restaurant_name || viewingMenu.restaurant?.name || 'Caterer'}</h1>
                  <div style={{ fontSize: 13, color: C.muted, fontFamily: font }}>{viewingMenu.cuisine_type || 'Various Cuisines'}</div>
                </div>
                <div style={{ background: viewingMenu.is_veg ? '#FFF7ED' : '#FFEBEE', color: viewingMenu.is_veg ? '#FC8019' : '#C62828', padding: '4px 8px', borderRadius: 8, fontSize: 12, fontWeight: 800, fontFamily: font, border: `1px solid ${viewingMenu.is_veg ? '#FDBA74' : '#FFCDD2'}` }}>
                  {viewingMenu.is_veg ? 'PURE VEG' : 'NON-VEG'}
                </div>
              </div>
            </div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '40px 16px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>{viewingMenu.name}</h2>
            <div style={{ fontSize: 28, fontWeight: 900, color: '#1565C0', fontFamily: font, marginBottom: 20 }}>
              ₹{viewingMenu.price_per_plate}<span style={{ fontSize: 14, color: C.muted, fontWeight: 500 }}>/plate</span>
            </div>

            <div style={{ background: '#fff', borderRadius: 16, padding: 16, border: `1px solid ${C.border}`, marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 8 }}>Menu Details</h3>
              <p style={{ fontSize: 14, color: C.muted, fontFamily: font, lineHeight: 1.6, margin: 0 }}>
                {viewingMenu.description}
              </p>
            </div>

            <div style={{ background: '#fff', borderRadius: 16, padding: 16, border: `1px solid ${C.border}`, marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 8 }}>Service Guidelines</h3>
              <div style={{ display: 'flex', gap: 12, flexDirection: 'column' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: C.charcoal, fontFamily: font }}>
                  <span>🍽️</span> Minimum requirement: {viewingMenu.min_plates} plates
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: C.charcoal, fontFamily: font }}>
                  <span>🚚</span> Includes delivery and basic setup
                </div>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: 20 }}>
              <button 
                onClick={() => { setSelectedMenu(viewingMenu); setViewingMenu(null); }} 
                style={{ width: '100%', background: 'linear-gradient(135deg, #1565C0, #1976D2)', border: 'none', borderRadius: 16, padding: '16px', color: '#fff', fontSize: 16, fontWeight: 900, cursor: 'pointer', fontFamily: font, boxShadow: '0 8px 24px rgba(21,101,192,0.3)' }}
              >
                Inquire Now
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedMenu && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 500 }}>
          <div onClick={() => setSelectedMenu(null)} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)' }} />
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: '#fff', borderRadius: '20px 20px 0 0', padding: '20px', maxHeight: '80vh', overflowY: 'auto' }}>
            {success ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ fontSize: 52, marginBottom: 12 }}>✅</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font }}>Inquiry Submitted!</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 6 }}>The catering team will contact you soon to finalize details.</div>
              </div>
            ) : (
              <>
                <div style={{ textAlign: 'center', marginBottom: 4 }}><div style={{ width: 36, height: 4, borderRadius: 99, background: C.sand, margin: '0 auto' }} /></div>
                <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 4, marginTop: 12 }}>Catering Inquiry</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginBottom: 16 }}>{selectedMenu.name} (Min {selectedMenu.min_plates} plates)</div>
                
                <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Event Date</label>
                    <input type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginTop: 4, boxSizing: 'border-box' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Est. Guests</label>
                    <input type="number" min={selectedMenu.min_plates} value={form.guests} onChange={e => setForm(p => ({ ...p, guests: parseInt(e.target.value) || 0 }))} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginTop: 4, boxSizing: 'border-box' }} />
                  </div>
                </div>
                
                <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Venue Address</label>
                <textarea value={form.venue} onChange={e => setForm(p => ({ ...p, venue: e.target.value }))} placeholder="Where is the event taking place?" rows={2} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 13, fontFamily: font, marginBottom: 12, marginTop: 4, resize: 'none', boxSizing: 'border-box' }} />

                <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Total Budget (₹)</label>
                <input type="number" value={form.budget} onChange={e => setForm(p => ({ ...p, budget: e.target.value }))} placeholder="Optional" style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginBottom: 12, marginTop: 4, boxSizing: 'border-box' }} />

                <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Special Requests</label>
                <textarea value={form.requests} onChange={e => setForm(p => ({ ...p, requests: e.target.value }))} placeholder="Any specific requirements..." rows={2} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 13, fontFamily: font, marginBottom: 16, marginTop: 4, resize: 'none', boxSizing: 'border-box' }} />
                
                <button onClick={handleInquire} style={{ width: '100%', background: 'linear-gradient(135deg, #1565C0, #1976D2)', border: 'none', borderRadius: 14, padding: '14px', color: '#fff', fontSize: 15, fontWeight: 800, cursor: 'pointer', fontFamily: font, boxShadow: '0 4px 20px rgba(21,101,192,0.3)' }}>
                  Submit Inquiry
                </button>
              </>
            )}
          </div>
        </div>
      )}
      {/* Custom Catering Bottom Navigation */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderTop: `1px solid #F0F0F5`, display: 'flex', justifyContent: 'space-around', padding: '10px 0 16px', zIndex: 100 }}>
        {[
          { id: 'hub', icon: '🏠', label: 'Hub' },
          { id: 'catering', icon: '👨‍🍳', label: 'Catering' },
          { id: 'menus', icon: '📋', label: 'Menus' },
          { id: 'inquiries', icon: '📞', label: 'Inquiries' },
        ].map(t => (
          <button 
            key={t.id} 
            onClick={() => {
              if (t.id === 'hub') goHome()
              else setCaterTab(t.id)
            }} 
            style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}
          >
            <span style={{ fontSize: 24, opacity: caterTab === t.id || t.id === 'hub' ? 1 : 0.5, filter: caterTab === t.id || t.id === 'hub' ? 'none' : 'grayscale(100%)' }}>{t.icon}</span>
            <span style={{ fontSize: 10, fontWeight: 800, color: caterTab === t.id ? '#1565C0' : '#02060C99', fontFamily: font }}>{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  )

  const renderMenus = () => (
    <div style={{ background: '#fff', minHeight: '100vh', padding: '20px 16px 100px', fontFamily: font }}>
      <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, marginBottom: 24 }}>Catering Menus</h2>
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
        <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, marginBottom: 8 }}>Explore custom menus</div>
        <div style={{ fontSize: 14, color: C.muted }}>Find the perfect spread for your next big event.</div>
        <button onClick={() => setCaterTab('catering')} style={{ marginTop: 24, background: '#1565C0', color: '#fff', padding: '12px 24px', borderRadius: 12, border: 'none', fontWeight: 800, cursor: 'pointer' }}>View Caterers</button>
      </div>
    </div>
  )

  const renderInquiries = () => (
    <div style={{ background: '#fff', minHeight: '100vh', padding: '20px 16px 100px', fontFamily: font }}>
      <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, marginBottom: 24 }}>My Inquiries</h2>
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📞</div>
        <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, marginBottom: 8 }}>No recent inquiries</div>
        <div style={{ fontSize: 14, color: C.muted }}>You haven't requested any catering quotes yet.</div>
      </div>
    </div>
  )

  return (
    <>
      {caterTab === 'catering' && renderDashboard()}
      {caterTab === 'menus' && renderMenus()}
      {caterTab === 'inquiries' && renderInquiries()}
    </>
  )
}
