import { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'
import RestaurantView from '../components/RestaurantView'

const C = {
  charcoal: '#1C1410', sand: '#F0E0CC', border: '#F0E4D4',
  muted: '#9B7B60', bg: '#FAF3EC',
}
const font = "'Poppins', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return <div style={{ width: w, height: h, borderRadius: r, marginBottom: mb, background: `linear-gradient(90deg,${C.sand} 25%,#FDE8CC 50%,${C.sand} 75%)`, backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />
}

export default function PartiesPage({ goHome }) {
  const [packages, setPackages] = useState([])
  const [loading, setLoading] = useState(true)
  const [partyTab, setPartyTab] = useState('party')
  const [selectedPkg, setSelectedPkg] = useState(null)
  const [viewingPkg, setViewingPkg] = useState(null)
  const [form, setForm] = useState({ date: '', time: '', guests: 10, requests: '' })
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    dashboardApi.getPartyPackages()
      .then(r => setPackages(r.data?.results || r.data?.data || r.data || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const handleBook = async () => {
    if (!form.date || !form.time) return
    try {
      await dashboardApi.createPartyBooking({
        package: selectedPkg.id,
        event_date: form.date,
        event_time: form.time,
        guest_count: form.guests,
        special_requests: form.requests
      })
      setSuccess(true)
      setTimeout(() => { setSuccess(false); setSelectedPkg(null) }, 3000)
    } catch {
      alert('Could not book party. Please try again.')
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
      <div style={{ background: 'linear-gradient(135deg, #00838F, #00BCD4)', padding: '20px 16px 16px', color: '#fff' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
          <span style={{ fontSize: 28 }}>🥳</span>
          <div>
            <div style={{ fontSize: 20, fontWeight: 900, fontFamily: font }}>Party Orders</div>
            <div style={{ fontSize: 12, opacity: 0.85, fontFamily: font }}>Bulk orders for your celebrations</div>
          </div>
        </div>
      </div>

      <div style={{ padding: '20px 16px' }}>
        {packages.map(p => {
          const isClosed = p.restaurant_is_currently_open === false;
          const isSoldOut = p.stock_status === 'sold_out';
          const isUnavailable = isClosed || isSoldOut;

          return (
            <div key={p.id} onClick={() => !isUnavailable && setViewingPkg(p)} style={{ background: '#fff', borderRadius: 16, marginBottom: 16, border: `1px solid ${C.border}`, overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,0.05)', padding: '16px', opacity: isUnavailable ? 0.7 : 1, filter: isUnavailable ? 'grayscale(30%)' : 'none', position: 'relative', cursor: isUnavailable ? 'default' : 'pointer' }}>
              {isUnavailable && (
                <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.6)', backdropFilter: 'blur(1px)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', zIndex: 10 }}>
                  <span style={{ color: '#C62828', fontSize: 16, fontWeight: 900, letterSpacing: 1, background: '#FFEBEE', padding: '6px 12px', borderRadius: 8, border: '1px solid #FFCDD2' }}>
                    {isSoldOut ? 'SOLD OUT' : 'RESTAURANT CLOSED'}
                  </span>
                  {isClosed && !isSoldOut && <span style={{ color: C.charcoal, fontSize: 11, fontWeight: 700, marginTop: 8 }}>{p.restaurant_formatted_hours}</span>}
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 10, padding: '2px 6px', borderRadius: 4, background: p.is_veg ? '#FFF7ED' : '#FFEBEE', color: p.is_veg ? '#FC8019' : '#C62828', fontWeight: 800, fontFamily: font, border: `1px solid ${p.is_veg ? '#FDBA74' : '#FFCDD2'}` }}>
                      {p.is_veg ? 'VEG' : 'NON-VEG'}
                    </span>
                    <span style={{ fontSize: 15, fontWeight: 900, color: C.charcoal, fontFamily: font }}>{p.name}</span>
                  </div>
                  <div style={{ fontSize: 12, color: C.muted, fontFamily: font }}>{p.restaurant_name || p.restaurant?.name || 'Restaurant'}</div>
                </div>
                <div style={{ fontSize: 16, fontWeight: 900, color: '#00838F', fontFamily: font }}>₹{p.price_per_person}<span style={{ fontSize: 10, color: C.muted }}>/pax</span></div>
              </div>
              
              <div style={{ fontSize: 12, color: C.charcoal, fontFamily: font, lineHeight: 1.4, marginBottom: 12 }}>{p.description}</div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: `1px dashed ${C.border}`, paddingTop: 12 }}>
                <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>👥 {p.min_guests} - {p.max_guests} guests</div>
                <button onClick={(e) => { e.stopPropagation(); !isUnavailable && setSelectedPkg(p); }} disabled={isUnavailable} style={{ background: isUnavailable ? '#F5F5F5' : '#E0F7FA', border: `1px solid ${isUnavailable ? C.border : '#00BCD4'}`, borderRadius: 10, padding: '6px 16px', color: isUnavailable ? '#9E9E9E' : '#00838F', fontSize: 12, fontWeight: 800, cursor: isUnavailable ? 'not-allowed' : 'pointer', fontFamily: font }}>
                  {isUnavailable ? 'Unavailable' : 'Book Now'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Package Detail View Overlay */}
      {viewingPkg && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 400, background: C.bg, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ position: 'relative', height: 260, flexShrink: 0, background: C.sand }}>
            <img src={viewingPkg.restaurant?.cover_image || viewingPkg.restaurant?.logo || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200'} alt="cover" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 40%, rgba(0,0,0,0.8) 100%)' }} />
            
            <button onClick={() => setViewingPkg(null)} style={{ position: 'absolute', top: 40, left: 16, width: 40, height: 40, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.4)', color: '#fff', fontSize: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
              ←
            </button>

            <div style={{ position: 'absolute', bottom: -20, left: 16, right: 16, background: '#fff', borderRadius: 20, padding: '20px', boxShadow: '0 8px 30px rgba(92,42,15,0.12)', border: `1px solid ${C.border}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h1 style={{ fontSize: 22, fontWeight: 900, color: C.charcoal, fontFamily: font, margin: '0 0 4px 0' }}>{viewingPkg.restaurant_name || viewingPkg.restaurant?.name || 'Restaurant'}</h1>
                  <div style={{ fontSize: 13, color: C.muted, fontFamily: font }}>{viewingPkg.restaurant?.categories?.join(', ') || 'Party Venue'}</div>
                </div>
                <div style={{ background: viewingPkg.is_veg ? '#FFF7ED' : '#FFEBEE', color: viewingPkg.is_veg ? '#FC8019' : '#C62828', padding: '4px 8px', borderRadius: 8, fontSize: 12, fontWeight: 800, fontFamily: font, border: `1px solid ${viewingPkg.is_veg ? '#FDBA74' : '#FFCDD2'}` }}>
                  {viewingPkg.is_veg ? 'PURE VEG' : 'NON-VEG'}
                </div>
              </div>
            </div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '40px 16px', display: 'flex', flexDirection: 'column' }}>
            <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>{viewingPkg.name}</h2>
            <div style={{ fontSize: 28, fontWeight: 900, color: '#00838F', fontFamily: font, marginBottom: 20 }}>
              ₹{viewingPkg.price_per_person}<span style={{ fontSize: 14, color: C.muted, fontWeight: 500 }}>/person</span>
            </div>

            <div style={{ background: '#fff', borderRadius: 16, padding: 16, border: `1px solid ${C.border}`, marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 8 }}>Package Details</h3>
              <p style={{ fontSize: 14, color: C.muted, fontFamily: font, lineHeight: 1.6, margin: 0 }}>
                {viewingPkg.description}
              </p>
            </div>

            <div style={{ background: '#fff', borderRadius: 16, padding: 16, border: `1px solid ${C.border}`, marginBottom: 20 }}>
              <h3 style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 8 }}>Guidelines</h3>
              <div style={{ display: 'flex', gap: 12, flexDirection: 'column' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: C.charcoal, fontFamily: font }}>
                  <span>👥</span> Minimum {viewingPkg.min_guests} to Maximum {viewingPkg.max_guests} guests allowed
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: C.charcoal, fontFamily: font }}>
                  <span>⏱️</span> Bookings must be made in advance
                </div>
              </div>
            </div>

            <div style={{ marginTop: 'auto', paddingTop: 20 }}>
              <button 
                onClick={() => { setSelectedPkg(viewingPkg); setViewingPkg(null); }} 
                style={{ width: '100%', background: 'linear-gradient(135deg, #00838F, #00BCD4)', border: 'none', borderRadius: 16, padding: '16px', color: '#fff', fontSize: 16, fontWeight: 900, cursor: 'pointer', fontFamily: font, boxShadow: '0 8px 24px rgba(0,188,212,0.3)' }}
              >
                Proceed to Book
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedPkg && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 500 }}>
          <div onClick={() => setSelectedPkg(null)} style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(4px)' }} />
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: '#fff', borderRadius: '20px 20px 0 0', padding: '20px', maxHeight: '75vh', overflowY: 'auto' }}>
            {success ? (
              <div style={{ textAlign: 'center', padding: '40px 0' }}>
                <div style={{ fontSize: 52, marginBottom: 12 }}>🥳</div>
                <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font }}>Party Booked!</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 6 }}>The restaurant will contact you soon.</div>
              </div>
            ) : (
              <>
                <div style={{ textAlign: 'center', marginBottom: 4 }}><div style={{ width: 36, height: 4, borderRadius: 99, background: C.sand, margin: '0 auto' }} /></div>
                <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 4, marginTop: 12 }}>Book {selectedPkg.name}</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginBottom: 16 }}>Est. Total: ₹{selectedPkg.price_per_person * form.guests}</div>
                
                <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Date</label>
                    <input type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginTop: 4, boxSizing: 'border-box' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Time</label>
                    <input type="time" value={form.time} onChange={e => setForm(p => ({ ...p, time: e.target.value }))} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginTop: 4, boxSizing: 'border-box' }} />
                  </div>
                </div>
                
                <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Number of Guests</label>
                <input type="number" min={selectedPkg.min_guests} max={selectedPkg.max_guests} value={form.guests} onChange={e => setForm(p => ({ ...p, guests: parseInt(e.target.value) || 0 }))} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 14, fontFamily: font, marginBottom: 12, marginTop: 4, boxSizing: 'border-box' }} />

                <label style={{ fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>Special Requests</label>
                <textarea value={form.requests} onChange={e => setForm(p => ({ ...p, requests: e.target.value }))} placeholder="Any specific requirements..." rows={2} style={{ width: '100%', padding: '12px', borderRadius: 12, border: `1.5px solid ${C.border}`, fontSize: 13, fontFamily: font, marginBottom: 16, marginTop: 4, resize: 'none', boxSizing: 'border-box' }} />
                
                <button onClick={handleBook} style={{ width: '100%', background: 'linear-gradient(135deg, #00838F, #00BCD4)', border: 'none', borderRadius: 14, padding: '14px', color: '#fff', fontSize: 15, fontWeight: 800, cursor: 'pointer', fontFamily: font, boxShadow: '0 4px 20px rgba(0,188,212,0.3)' }}>
                  Confirm Party Booking
                </button>
              </>
            )}
          </div>
        </div>
      )}
      {/* Custom Party Bottom Navigation */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderTop: `1px solid #F0F0F5`, display: 'flex', justifyContent: 'space-around', padding: '10px 0 16px', zIndex: 100 }}>
        {[
          { id: 'hub', icon: '🏠', label: 'Hub' },
          { id: 'party', icon: '🎉', label: 'Party' },
          { id: 'packages', icon: '📦', label: 'Packages' },
          { id: 'my_events', icon: '📅', label: 'My Events' },
        ].map(t => (
          <button 
            key={t.id} 
            onClick={() => {
              if (t.id === 'hub') goHome()
              else setPartyTab(t.id)
            }} 
            style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}
          >
            <span style={{ fontSize: 24, opacity: partyTab === t.id || t.id === 'hub' ? 1 : 0.5, filter: partyTab === t.id || t.id === 'hub' ? 'none' : 'grayscale(100%)' }}>{t.icon}</span>
            <span style={{ fontSize: 10, fontWeight: 800, color: partyTab === t.id ? '#00838F' : '#02060C99', fontFamily: font }}>{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  )

  const renderPackages = () => (
    <div style={{ background: '#fff', minHeight: '100vh', padding: '20px 16px 100px', fontFamily: font }}>
      <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, marginBottom: 24 }}>Party Packages</h2>
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📦</div>
        <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, marginBottom: 8 }}>Explore curated packages</div>
        <div style={{ fontSize: 14, color: C.muted }}>Browse through exclusive deals for large groups.</div>
        <button onClick={() => setPartyTab('party')} style={{ marginTop: 24, background: '#00838F', color: '#fff', padding: '12px 24px', borderRadius: 12, border: 'none', fontWeight: 800, cursor: 'pointer' }}>View All Options</button>
      </div>
    </div>
  )

  const renderEvents = () => (
    <div style={{ background: '#fff', minHeight: '100vh', padding: '20px 16px 100px', fontFamily: font }}>
      <h2 style={{ fontSize: 24, fontWeight: 900, color: C.charcoal, marginBottom: 24 }}>My Events</h2>
      <div style={{ textAlign: 'center', padding: '60px 0' }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📅</div>
        <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, marginBottom: 8 }}>No upcoming events</div>
        <div style={{ fontSize: 14, color: C.muted }}>You haven't booked any parties yet.</div>
        <button onClick={() => setPartyTab('party')} style={{ marginTop: 24, background: '#00838F', color: '#fff', padding: '12px 24px', borderRadius: 12, border: 'none', fontWeight: 800, cursor: 'pointer' }}>Book a Party</button>
      </div>
    </div>
  )

  return (
    <>
      {partyTab === 'party' && renderDashboard()}
      {partyTab === 'packages' && renderPackages()}
      {partyTab === 'my_events' && renderEvents()}
    </>
  )
}
