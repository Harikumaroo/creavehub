import React, { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'

const C = {
  saffron: '#E8621A', amber: '#F5A623', tomato: '#D94F2B',
  cream: '#FDF6EE',   warm: '#FFF8F2', charcoal: '#1C1410',
  bark: '#3D2B1F',    mocha: '#7C4D2F', sand: '#F0E0CC',
  sage: '#5C7A4E',    cardBg: '#FFFFFF', border: '#F0E4D4',
  muted: '#9B7B60',   bg: '#FAF3EC',
}
const font = "'Poppins', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: r, marginBottom: mb,
      background: `linear-gradient(90deg,${C.sand} 25%,#FDE8CC 50%,${C.sand} 75%)`,
      backgroundSize: '400% 100%', animation: 'shimmer 1.5s infinite',
    }} />
  )
}

export default function RestaurantView({ restaurantId, highlightItemId, onClose, onAdd, favRestIds, favItemIds, onToggleFavRest, onToggleFavItem }) {
  const [rest, setRest] = useState(null)
  const [menu, setMenu] = useState([])
  const [loading, setLoading] = useState(true)
  const [addingItem, setAddingItem] = useState(null)

  const handleAdd = (id) => {
    setAddingItem(id)
    onAdd(id)
    setTimeout(() => setAddingItem(null), 1000)
  }

  useEffect(() => {
    setLoading(true)
    Promise.all([
      dashboardApi.getRestaurant(restaurantId).catch(() => null),
      dashboardApi.getMenu(restaurantId).catch(() => null)
    ]).then(([rRes, mRes]) => {
      if (rRes?.data?.success) setRest(rRes.data.data)
      if (mRes?.data?.success) setMenu(mRes.data.data)
      setLoading(false)
    })
  }, [restaurantId])

  useEffect(() => {
    if (!loading && highlightItemId) {
      setTimeout(() => {
        const el = document.getElementById(`menu-item-${highlightItemId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 300);
    }
  }, [loading, highlightItemId])

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 400, background: C.bg, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header / Hero */}
      <div style={{ position: 'relative', height: 260, flexShrink: 0, background: C.sand }}>
        {loading ? <Skel h={260} r={0} /> : (
          <img src={rest?.cover_image || rest?.logo || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1200'} alt="cover" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        )}
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to bottom, rgba(0,0,0,0.4) 0%, transparent 40%, rgba(0,0,0,0.8) 100%)' }} />
        
        {/* Back Button */}
        <button onClick={onClose} style={{ position: 'absolute', top: 40, left: 16, width: 40, height: 40, borderRadius: '50%', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.4)', color: '#fff', fontSize: 20, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
          ←
        </button>

        {/* Info Card Overlay */}
        {!loading && rest && (
          <div style={{ position: 'absolute', bottom: -20, left: 16, right: 16, background: C.cardBg, borderRadius: 20, padding: '20px', boxShadow: '0 8px 30px rgba(92,42,15,0.12)', border: `1px solid ${C.border}` }}>
            <div style={{ position: 'absolute', top: -16, right: 16, width: 44, height: 44, background: '#fff', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', cursor: 'pointer', zIndex: 10, transition: 'transform 0.2s' }} onClick={(e) => { e.stopPropagation(); onToggleFavRest?.(rest) }} onMouseEnter={e => e.currentTarget.style.transform='scale(1.1)'} onMouseLeave={e => e.currentTarget.style.transform='scale(1)'}>
              <span style={{ fontSize: 22, color: (favRestIds && favRestIds.has(rest.id)) ? '#E25E1A' : '#D1D5DB' }}>{(favRestIds && favRestIds.has(rest.id)) ? '❤️' : '🤍'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h1 style={{ fontSize: 22, fontWeight: 900, color: C.charcoal, fontFamily: font, margin: '0 0 4px 0' }}>{rest.name}</h1>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font }}>{rest.categories?.join(', ') || 'Various Cuisines'}</div>
              </div>
              <div style={{ background: C.saffron, color: '#fff', padding: '4px 8px', borderRadius: 8, fontSize: 14, fontWeight: 800, fontFamily: font }}>
                ★ {rest.rating}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 16, marginTop: 16, borderTop: `1px dashed ${C.border}`, paddingTop: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>
                ⏱️ {rest.average_delivery_time} mins
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>
                🛵 ₹{Number(rest.delivery_fee).toFixed(0)}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 700, color: C.charcoal, fontFamily: font }}>
                {rest.is_pure_veg ? '🟢 Pure Veg' : '🍽️ Mix'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Spacer for overlay card */}
      <div style={{ height: 40, flexShrink: 0 }} />

      {/* Menu List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px 40px' }}>
        {loading ? (
          <div style={{ marginTop: 20 }}>
            {[...Array(5)].map((_, i) => <Skel key={i} h={120} r={16} mb={16} />)}
          </div>
        ) : menu.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: C.muted, fontFamily: font }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🍽️</div>
            No menu items available
          </div>
        ) : (
          menu.map(category => (
            <div key={category.id} style={{ marginBottom: 24 }}>
              <h2 style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 16 }}>{category.name}</h2>
              {category.items?.map(item => (
                <div id={`menu-item-${item.id}`} key={item.id} style={{ display: 'flex', gap: 12, background: highlightItemId === item.id ? '#FFF8ED' : C.cardBg, borderRadius: 16, padding: '12px', marginBottom: 12, border: `1px solid ${highlightItemId === item.id ? C.saffron : C.border}`, transition: 'all 0.3s', opacity: item.stock_status === 'sold_out' ? 0.6 : 1 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span style={{ fontSize: 10 }}>{item.is_veg ? '🟢' : '🔴'}</span>
                        <span style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{item.name}</span>
                      </div>
                      <div onClick={(e) => { e.preventDefault(); e.stopPropagation(); alert('Click registered!'); onToggleFavItem?.(item); }} style={{ cursor: 'pointer', padding: 4, transition: 'transform 0.2s', position: 'relative', zIndex: 50 }} onMouseEnter={e => e.currentTarget.style.transform='scale(1.2)'} onMouseLeave={e => e.currentTarget.style.transform='scale(1)'}>
                        <span style={{ fontSize: 18, textShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>{(favItemIds && favItemIds.has(item.id)) ? '❤️' : '🤍'}</span>
                      </div>
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font, marginBottom: 6 }}>
                      ₹{Number(item.effective_price).toFixed(2)}
                      {item.discounted_price && <span style={{ fontSize: 12, color: C.muted, textDecoration: 'line-through', marginLeft: 6 }}>₹{Number(item.price).toFixed(2)}</span>}
                    </div>
                    <div style={{ fontSize: 11, color: C.muted, fontFamily: font, lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {item.description}
                    </div>
                  </div>
                  
                  <div style={{ width: 100, flexShrink: 0, position: 'relative' }}>
                    <div style={{ width: '100%', height: 100, borderRadius: 12, background: C.sand, overflow: 'hidden' }}>
                      {item.image ? (
                        <img src={item.image} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      ) : (
                        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>🍽️</div>
                      )}
                    </div>
                    {item.stock_status === 'sold_out' ? (
                      <div style={{
                        position: 'absolute', bottom: -10, left: '50%', transform: 'translateX(-50%)',
                        background: '#F5F5F5', border: `1px solid #E0E0E0`, color: '#9E9E9E',
                        fontSize: 10, fontWeight: 900, fontFamily: font, padding: '6px 8px',
                        borderRadius: 8, whiteSpace: 'nowrap',
                      }}>
                        SOLD OUT
                      </div>
                    ) : rest?.is_currently_open === false ? (
                      <div style={{
                        position: 'absolute', bottom: -10, left: '50%', transform: 'translateX(-50%)',
                        background: '#FFF3F3', border: `1px solid #FFCDCD`, color: '#D94F2B',
                        fontSize: 10, fontWeight: 900, fontFamily: font, padding: '6px 8px',
                        borderRadius: 8, whiteSpace: 'nowrap',
                      }}>
                        CLOSED
                      </div>
                    ) : (
                      <button 
                        onClick={() => handleAdd(item.id)}
                        disabled={addingItem === item.id}
                        style={{ 
                          position: 'absolute', bottom: -10, left: '50%', transform: 'translateX(-50%)', 
                          background: addingItem === item.id ? C.sage : '#fff', 
                          border: `1px solid ${addingItem === item.id ? C.sage : C.saffron}`, 
                          color: addingItem === item.id ? '#fff' : C.saffron, 
                          fontSize: 12, fontWeight: 900, fontFamily: font, padding: '6px 16px', 
                          borderRadius: 8, cursor: 'pointer', 
                          boxShadow: '0 4px 12px rgba(232,98,26,0.15)',
                          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                          transformOrigin: 'center'
                        }}
                      >
                        {addingItem === item.id ? 'ADDED ✓' : 'ADD'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
