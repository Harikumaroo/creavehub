import { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'

const C = {
  saffron: '#E8621A', amber: '#F5A623', tomato: '#D94F2B',
  cream: '#FDF6EE', warm: '#FFF8F2', charcoal: '#1C1410',
  bark: '#3D2B1F', mocha: '#7C4D2F', sand: '#F0E0CC',
  sage: '#5C7A4E', cardBg: '#FFFFFF', border: '#F0E4D4',
  muted: '#9B7B60', bg: '#F4F6F9',
  instaBlue: '#0252D8', instaDark: '#003db8', instaLight: '#eef4ff'
}
const font = "'Poppins', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return <div style={{ width: w, height: h, borderRadius: r, marginBottom: mb, background: `linear-gradient(90deg,#e0e0e0 25%,#f5f5f5 50%,#e0e0e0 75%)`, backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />
}

export default function InstamartPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedCat, setSelectedCat] = useState(null)
  const [cart, setCart] = useState({})
  const [searchQ, setSearchQ] = useState('')
  const [cartOpen, setCartOpen] = useState(false)
  const [payMode, setPayMode] = useState('cod')
  const [offers, setOffers] = useState([])
  const [offersLoading, setOffersLoading] = useState(false)
  const [appliedOffer, setAppliedOffer] = useState(null)
  const [manualCode, setManualCode] = useState('')
  const [codeError, setCodeError] = useState('')
  const [checkoutState, setCheckoutState] = useState('cart')
  const [showOffers, setShowOffers] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [instaTab, setInstaTab] = useState('instamart')
  const [pastOrders, setPastOrders] = useState([])
  const [ordersLoading, setOrdersLoading] = useState(false)

  const totalItems = Object.values(cart).reduce((a, b) => a + b, 0)

  useEffect(() => {
    dashboardApi.getInstamart()
      .then(r => { if (r.data?.success) setData(r.data.data) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (instaTab === 'reorder') {
      setOrdersLoading(true)
      dashboardApi.getInstamartOrders()
        .then(r => { if (r.data?.success) setPastOrders(r.data.data) })
        .catch(() => {})
        .finally(() => setOrdersLoading(false))
    }
  }, [instaTab])

  useEffect(() => {
    if (cartOpen && totalItems > 0) {
      setOffersLoading(true)
      dashboardApi.getOffers()
        .then(r => { if (r.data?.success) setOffers(r.data.data || []) })
        .catch(() => {})
        .finally(() => setOffersLoading(false))
      setCheckoutState('cart')
      setAppliedOffer(null)
    }
  }, [cartOpen, totalItems])

  const categories = data?.categories || []
  const stores = data?.stores || []
  const featured = data?.featured_products || []
  
  const allProductsData = data?.all_products || []
  const allProductsRaw = [
    ...stores.flatMap(s => (s.products || []).map(p => ({ ...p, store_name: s.name }))),
    ...featured,
    ...allProductsData
  ]
  
  // Remove duplicates by ID
  const allProducts = Array.from(new Map(allProductsRaw.map(item => [item.id, item])).values())
  
  const filteredProducts = allProducts.filter(p => {
    const matchCat = !selectedCat || p.category === selectedCat
    const matchSearch = !searchQ || p.name.toLowerCase().includes(searchQ.toLowerCase())
    return matchCat && matchSearch
  })

  const handleSearchChange = async (e) => {
    const val = e.target.value
    setSearchQ(val)
    if (val.length >= 1) {
      // Provide async suggestions based on local data for Instamart
      await new Promise(r => setTimeout(r, 100))
      const query = val.toLowerCase()
      const matches = Array.from(new Set(allProducts.filter(p => p.name.toLowerCase().includes(query)).map(p => p.name))).slice(0, 5)
      setSuggestions(matches)
      setShowDropdown(true)
    } else {
      setSuggestions([])
      setShowDropdown(false)
    }
  }

  const handleSuggestionClick = (sug) => {
    setSearchQ(sug)
    setShowDropdown(false)
  }

  const addToCart = (product) => setCart(prev => ({ ...prev, [product.id]: (prev[product.id] || 0) + 1 }))
  const removeFromCart = (product) => setCart(prev => {
    const n = { ...prev }
    if (n[product.id] > 1) n[product.id]--
    else delete n[product.id]
    return n
  })

  const cartItems = Object.entries(cart).map(([id, qty]) => {
    const isPromo = id.toString().startsWith('promo-')
    const realId = isPromo ? id.replace('promo-', '') : id
    const p = allProducts.find(p => p.id === parseInt(realId) || p.id === realId)
    if (!p) return null
    if (isPromo) return { ...p, id, effective_price: 1, price: 1, quantity: 1, name: `${p.name} (₹1 Offer)` }
    return { ...p, quantity: qty }
  }).filter(Boolean)

  const cartSubtotal = cartItems.reduce((acc, item) => acc + ((item.effective_price || item.price) * item.quantity), 0)
  const cartDelivery = cartSubtotal > 500 ? 0 : 35

  let discountAmt = 0
  if (appliedOffer) {
    if (appliedOffer.discount_type === 'PERCENTAGE') {
      discountAmt = (cartSubtotal * Number(appliedOffer.discount_value)) / 100
      if (appliedOffer.maximum_discount && discountAmt > Number(appliedOffer.maximum_discount)) discountAmt = Number(appliedOffer.maximum_discount)
    } else if (appliedOffer.discount_type === 'FLAT') {
      discountAmt = Number(appliedOffer.discount_value)
    } else if (appliedOffer.discount_type === 'FREE_DELIVERY') {
      discountAmt = cartDelivery
    }
  }

  const tax = Math.max(0, ((cartSubtotal - discountAmt) * 0.05))
  const cartTotal = Math.max(0, cartSubtotal + cartDelivery + tax - discountAmt)

  const applyOffer = (offer) => {
    if (cartSubtotal < Number(offer.minimum_order_amount)) {
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

  const handleCheckout = () => {
    setCheckoutState('processing')
    const payload = {
      payMode,
      cartTotal,
      cartSubtotal,
      discountAmt,
      deliveryFee: cartDelivery,
      tax,
      items: cartItems.map(i => ({ id: i.id, quantity: i.quantity, effective_price: i.effective_price || i.price, name: i.name }))
    }
    dashboardApi.placeInstamartOrder(payload).then(r => {
      if (r.data?.success) {
        setCheckoutState('success')
        setTimeout(() => { setCartOpen(false); setCart({}); setCheckoutState('cart') }, 3000)
      } else {
        setCheckoutState('failed')
        setTimeout(() => { setCartOpen(false); setCart({}); setCheckoutState('cart') }, 3000)
      }
    }).catch(() => {
      setCheckoutState('failed')
      setTimeout(() => { setCartOpen(false); setCart({}); setCheckoutState('cart') }, 3000)
    })
  }

  const getCatIcon = (name) => {
    const n = name.toLowerCase()
    if (n.includes('fresh') || n.includes('fruit') || n.includes('veg')) return '🍋'
    if (n.includes('electronic') || n.includes('appliance')) return '🎧'
    if (n.includes('snack') || n.includes('chips')) return '🍿'
    if (n.includes('beverage') || n.includes('drink')) return '🥤'
    if (n.includes('meat') || n.includes('chicken') || n.includes('seafood')) return '🍗'
    if (n.includes('school') || n.includes('stationery')) return '🎒'
    if (n.includes('personal') || n.includes('care')) return '🧴'
    if (n.includes('cleaning') || n.includes('home')) return '🧼'
    return '🛍️'
  }

  if (loading) return (
    <div style={{ padding: 16 }}>
      <Skel h={40} r={12} mb={16} />
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        {[...Array(5)].map((_, i) => <Skel key={i} w={80} h={36} r={20} />)}
      </div>
      {[...Array(6)].map((_, i) => <Skel key={i} h={80} r={12} mb={10} />)}
    </div>
  )

  const renderInstamartHome = () => (
    <>
      {/* Top Blue Section */}
      <div style={{ background: C.instaBlue, paddingTop: 16, paddingBottom: 24 }}>
        {/* Search */}
        <div style={{ margin: '0 16px 16px', display: 'flex', alignItems: 'center', gap: 8, background: '#fff', borderRadius: 12, padding: '0 12px', height: 44, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', position: 'relative' }}>
          <span style={{ fontSize: 16 }}>🔍</span>
          <input
            value={searchQ} onChange={handleSearchChange}
            onFocus={() => searchQ.length >= 1 && setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Search for groceries..."
            style={{ flex: 1, background: 'none', border: 'none', outline: 'none', color: C.charcoal, fontSize: 14, fontFamily: font }}
          />
          {showDropdown && suggestions.length > 0 && (
            <div style={{ position: 'absolute', top: 50, left: 0, right: 0, background: '#fff', borderRadius: 12, boxShadow: '0 4px 12px rgba(0,0,0,0.15)', border: `1px solid ${C.border}`, zIndex: 50, overflow: 'hidden' }}>
              {suggestions.map((sug, i) => (
                <div key={i} onClick={() => handleSuggestionClick(sug)} style={{ padding: '10px 16px', fontSize: 13, fontWeight: 700, color: C.charcoal, fontFamily: font, borderBottom: i < suggestions.length - 1 ? `1px solid ${C.border}` : 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ color: C.muted }}>🔍</span> {sug}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Category Icons Nav */}
        <div style={{ display: 'flex', gap: 16, padding: '0 16px', overflowX: 'auto', scrollbarWidth: 'none', marginBottom: 20 }}>
          <div onClick={() => setSelectedCat(null)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, cursor: 'pointer', flexShrink: 0 }}>
            <div style={{ fontSize: 24 }}>🛍️</div>
            <div style={{ fontSize: 11, color: '#fff', fontWeight: !selectedCat ? 800 : 500, fontFamily: font, borderBottom: !selectedCat ? '2px solid #fff' : 'none', paddingBottom: 2 }}>All</div>
          </div>
          {categories.map(cat => (
            <div key={cat.id} onClick={() => setSelectedCat(cat.id)} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, cursor: 'pointer', flexShrink: 0 }}>
              <div style={{ fontSize: 24 }}>{getCatIcon(cat.name)}</div>
              <div style={{ fontSize: 11, color: '#fff', fontWeight: selectedCat === cat.id ? 800 : 500, fontFamily: font, borderBottom: selectedCat === cat.id ? '2px solid #fff' : 'none', paddingBottom: 2, whiteSpace: 'nowrap' }}>{cat.name}</div>
            </div>
          ))}
        </div>

        {/* Top Products Slider */}
        {!searchQ && !selectedCat && (
          <div style={{ display: 'flex', gap: 12, padding: '0 16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
            {allProducts.map((p, i) => (
              <div key={i} onClick={() => setSearchQ(p.name)} style={{ flexShrink: 0, width: 110, background: '#fff', borderRadius: 16, padding: '12px 8px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', cursor: 'pointer' }}>
                <div style={{ width: 48, height: 48, background: C.bg, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, marginBottom: 8, overflow: 'hidden' }}>
                  {p.image ? <img src={p.image} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : '🛍️'}
                </div>
                <div style={{ fontSize: 11, fontWeight: 800, color: C.instaBlue, fontFamily: font, lineHeight: 1.2, marginBottom: 4, height: 26, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{p.name}</div>
                <div style={{ fontSize: 10, color: C.charcoal, fontFamily: font, fontWeight: 800 }}>₹{p.effective_price || p.price}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ₹1 STORE */}
      {!searchQ && !selectedCat && (
        <div style={{ margin: '16px', background: '#fff', borderRadius: 16, border: `1px solid ${C.border}`, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <div style={{ background: 'linear-gradient(90deg, #F9F9FC, #F1F5FD)', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ background: '#5E35B1', color: '#fff', fontSize: 18, fontWeight: 900, padding: '4px 10px', borderRadius: 8, fontFamily: font }}>₹1</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 16, fontWeight: 900, color: C.charcoal, fontFamily: font }}>Store</div>
              <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>Shop for ₹400 to get up to TWO items at ₹1</div>
            </div>
            <div style={{ fontSize: 24 }}>🍩</div>
          </div>
          
          {/* ₹1 Products */}
          <div style={{ display: 'flex', gap: 12, padding: '16px', overflowX: 'auto', scrollbarWidth: 'none' }}>
            {allProducts.slice(0, 20).map(p => {
              const promoId = `promo-${p.id}`
              const inCart = !!cart[promoId]
              return (
              <div key={promoId} style={{ flexShrink: 0, width: 100, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ width: 80, height: 80, background: C.bg, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, marginBottom: 8, border: `1px solid ${C.border}`, overflow: 'hidden', position: 'relative' }}>
                  {p.image ? <img src={p.image} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : '🛍️'}
                  {inCart && <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>✅</div>}
                </div>
                <div style={{ fontSize: 10, fontWeight: 700, color: C.charcoal, fontFamily: font, textAlign: 'center', height: 28, overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name}</div>
                {inCart ? (
                  <button onClick={() => removeFromCart({ id: promoId })} style={{ marginTop: 8, background: '#f5f5f5', border: `1px solid #ccc`, color: '#666', fontSize: 10, fontWeight: 800, padding: '4px 16px', borderRadius: 14, fontFamily: font, cursor: 'pointer' }}>Remove</button>
                ) : stores[0]?.is_currently_open === false ? (
                  <div style={{ marginTop: 8, background: '#FFF3F3', border: '1px solid #FFCDCD', color: '#D94F2B', fontSize: 10, fontWeight: 800, padding: '4px 16px', borderRadius: 14, fontFamily: font, cursor: 'not-allowed' }}>Closed</div>
                ) : (
                  <button onClick={() => {
                    const currentPromoCount = Object.keys(cart).filter(k => k.toString().startsWith('promo-')).length;
                    if (cartSubtotal < 400) {
                      alert("Add items worth ₹400 or more to unlock the ₹1 offer!")
                    } else if (currentPromoCount >= 2) {
                      alert("You can only select up to 2 items from the ₹1 store!")
                    } else {
                      addToCart({ id: promoId })
                    }
                  }} style={{ marginTop: 8, background: '#fff', border: `1px solid ${C.instaBlue}`, color: C.instaBlue, fontSize: 10, fontWeight: 800, padding: '4px 16px', borderRadius: 14, fontFamily: font, cursor: 'pointer' }}>Select</button>
                )}
              </div>
            )})}
          </div>
        </div>
      )}

      {/* Products List */}
      <div style={{ padding: '0 16px 16px' }}>
        <div style={{ fontSize: 16, fontWeight: 800, color: C.charcoal, fontFamily: font, margin: '16px 0 12px' }}>
          {selectedCat ? categories.find(c => c.id === selectedCat)?.name || 'Products' : searchQ ? `Results for "${searchQ}"` : 'All Products'}
          <span style={{ fontSize: 12, color: C.muted, fontWeight: 500, marginLeft: 8 }}>({filteredProducts.length})</span>
        </div>
        
        {filteredProducts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <div style={{ fontSize: 48, marginBottom: 8 }}>📦</div>
            <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>No products found</div>
          </div>
        ) : filteredProducts.map(p => (
          <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px', background: '#fff', borderRadius: 16, marginBottom: 12, border: `1px solid ${C.border}`, boxShadow: '0 2px 4px rgba(0,0,0,0.02)', opacity: p.stock_status === 'sold_out' ? 0.6 : 1 }}>
            <div style={{ width: 64, height: 64, borderRadius: 12, background: C.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 28, flexShrink: 0 }}>🛍️</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 14, fontWeight: 700, color: C.charcoal, fontFamily: font }}>{p.name}</div>
              <div style={{ fontSize: 12, color: C.muted, fontFamily: font }}>{p.unit} · {p.brand || p.store_name}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
                <span style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font }}>₹{p.effective_price || p.price}</span>
                {p.has_discount && <span style={{ fontSize: 12, color: C.muted, textDecoration: 'line-through' }}>₹{p.price}</span>}
              </div>
            </div>
            <div>
              {p.stock_status === 'sold_out' ? (
                <div style={{ background: '#F5F5F5', border: '1px solid #E0E0E0', borderRadius: 8, padding: '6px 12px', fontSize: 10, fontWeight: 900, color: '#9E9E9E', fontFamily: font, whiteSpace: 'nowrap' }}>SOLD OUT</div>
              ) : stores[0]?.is_currently_open === false ? (
                <div style={{ background: '#FFF3F3', border: '1px solid #FFCDCD', borderRadius: 8, padding: '6px 12px', fontSize: 10, fontWeight: 900, color: '#D94F2B', fontFamily: font, whiteSpace: 'nowrap' }}>CLOSED</div>
              ) : cart[p.id] ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: C.instaLight, borderRadius: 8, border: `1px solid ${C.instaBlue}`, padding: '4px 6px' }}>
                  <button onClick={() => removeFromCart(p)} style={{ width: 24, height: 24, border: 'none', background: 'none', fontSize: 16, fontWeight: 800, color: C.instaBlue, cursor: 'pointer' }}>−</button>
                  <span style={{ fontSize: 13, fontWeight: 800, color: C.instaBlue, minWidth: 16, textAlign: 'center' }}>{cart[p.id]}</span>
                  <button onClick={() => addToCart(p)} style={{ width: 24, height: 24, border: 'none', background: 'none', fontSize: 16, fontWeight: 800, color: C.instaBlue, cursor: 'pointer' }}>+</button>
                </div>
              ) : (
                <button onClick={() => addToCart(p)} style={{ background: '#fff', border: `1.5px solid ${C.instaBlue}`, borderRadius: 8, padding: '6px 16px', fontSize: 12, fontWeight: 800, color: C.instaBlue, cursor: 'pointer', fontFamily: font }}>ADD</button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Floating Cart (Swiggy Blue style) */}
      {totalItems > 0 && !cartOpen && (
        <div style={{ position: 'fixed', bottom: 80, left: 16, right: 16, background: C.instaBlue, borderRadius: 16, padding: '16px', display: 'flex', flexDirection: 'column', zIndex: 90, boxShadow: '0 4px 20px rgba(0,84,255,0.4)' }}>
          {cartSubtotal < 500 && (
            <div style={{ fontSize: 12, color: '#fff', fontWeight: 600, fontFamily: font, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>Add ₹{(500 - cartSubtotal).toFixed(0)} more to unlock <strong style={{ fontWeight: 900 }}>FREE DELIVERY</strong></span>
            </div>
          )}
          {cartSubtotal < 500 && (
            <div style={{ height: 4, background: 'rgba(255,255,255,0.3)', borderRadius: 2, marginBottom: 12, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${Math.min(100, (cartSubtotal/500)*100)}%`, background: '#fff', borderRadius: 2 }} />
            </div>
          )}
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 36, height: 36, background: 'rgba(255,255,255,0.2)', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>🛍️</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 900, color: '#fff', fontFamily: font }}>{totalItems} ITEM{totalItems > 1 ? 'S' : ''}</div>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', fontFamily: font, fontWeight: 500 }}>₹{cartSubtotal.toFixed(2)} plus taxes</div>
              </div>
            </div>
            <button onClick={() => setCartOpen(true)} style={{ background: 'none', border: 'none', fontSize: 14, fontWeight: 900, color: '#fff', cursor: 'pointer', fontFamily: font, display: 'flex', alignItems: 'center', gap: 4 }}>
              VIEW CART <span>→</span>
            </button>
          </div>
        </div>
      )}

      {/* Cart Drawer */}
      {cartOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 500, display: 'flex', flexDirection: 'column' }}>
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }} onClick={() => setCartOpen(false)} />
          
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: C.bg, borderRadius: '24px 24px 0 0', display: 'flex', flexDirection: 'column', maxHeight: '88vh', overflow: 'hidden' }}>
            <div style={{ display: 'flex', justifyContent: 'center', padding: '12px 0 4px' }}>
              <div style={{ width: 40, height: 4, borderRadius: 2, background: '#ccc' }} />
            </div>

            {checkoutState === 'processing' && (
              <div style={{ padding: '80px 20px', textAlign: 'center' }}>
                <div style={{ fontSize: 48, marginBottom: 16, animation: 'pulse 1.5s infinite' }}>🔄</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: C.charcoal, fontFamily: font }}>Processing your order...</div>
                <div style={{ fontSize: 13, color: C.muted, fontFamily: font, marginTop: 8 }}>Please wait while we confirm</div>
              </div>
            )}

            {checkoutState === 'success' && (
              <div style={{ padding: '60px 20px', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ fontSize: 64, marginBottom: 16 }}>🎉</div>
                <div style={{ fontSize: 22, fontWeight: 900, color: C.instaBlue, fontFamily: font, marginBottom: 8 }}>Order Placed!</div>
                <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>Your groceries will arrive in 10-15 minutes.</div>
                {appliedOffer && <div style={{ fontSize: 13, color: C.instaBlue, fontWeight: 700, fontFamily: font, marginTop: 8 }}>🎁 You saved ₹{discountAmt.toFixed(2)}!</div>}
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
                <div style={{ padding: '16px 20px', borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#fff' }}>
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 900, color: C.charcoal, fontFamily: font }}>🛒 Instamart Cart</div>
                    <div style={{ fontSize: 12, color: C.muted, fontFamily: font }}>{totalItems} item{totalItems !== 1 ? 's' : ''}</div>
                  </div>
                  <button onClick={() => setCartOpen(false)} style={{ background: 'none', border: 'none', fontSize: 24, color: C.muted, cursor: 'pointer' }}>×</button>
                </div>

                <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
                  {/* Items */}
                  <div style={{ background: '#fff', borderRadius: 16, padding: '16px', marginBottom: 16, border: `1px solid ${C.border}` }}>
                    {cartItems.map((item, idx) => (
                      <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: idx === cartItems.length - 1 ? 0 : 16 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1 }}>
                          <div style={{ fontSize: 24 }}>🛍️</div>
                          <div>
                            <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{item.name}</div>
                            <div style={{ fontSize: 12, color: C.muted, fontFamily: font }}>₹{item.effective_price || item.price} / {item.unit}</div>
                          </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: C.instaLight, borderRadius: 8, border: `1px solid ${C.instaBlue}`, padding: '4px 8px' }}>
                            <button onClick={() => removeFromCart(item)} style={{ border: 'none', background: 'none', fontSize: 16, fontWeight: 800, color: C.instaBlue, cursor: 'pointer' }}>−</button>
                            <span style={{ fontSize: 13, fontWeight: 800, color: C.instaBlue, minWidth: 16, textAlign: 'center' }}>{item.quantity}</span>
                            <button onClick={() => addToCart(item)} style={{ border: 'none', background: 'none', fontSize: 16, fontWeight: 800, color: C.instaBlue, cursor: 'pointer' }}>+</button>
                          </div>
                          <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, width: 60, textAlign: 'right' }}>
                            ₹{((item.effective_price || item.price) * item.quantity).toFixed(2)}
                          </div>
                        </div>
                      </div>
                    ))}

                    {/* Offers Section */}
                    <div style={{ marginTop: 16, paddingTop: 16, borderTop: `1px solid ${C.border}` }}>
                      {appliedOffer ? (
                        <div style={{ background: C.instaLight, borderRadius: 14, padding: '12px 16px', border: `1px solid ${C.instaBlue}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <div style={{ fontSize: 13, fontWeight: 800, color: C.instaBlue, fontFamily: font }}>🎉 {appliedOffer.coupon_code} applied!</div>
                            <div style={{ fontSize: 11, color: C.instaDark, fontFamily: font }}>You save ₹{discountAmt.toFixed(2)}</div>
                          </div>
                          <button onClick={() => setAppliedOffer(null)} style={{ background: 'none', border: 'none', fontSize: 18, color: C.instaBlue, cursor: 'pointer', fontWeight: 800 }}>×</button>
                        </div>
                      ) : (
                        <div>
                          <button onClick={() => setShowOffers(!showOffers)} style={{
                            width: '100%', padding: '12px 16px', borderRadius: 14,
                            border: `2px dashed ${C.instaBlue}`, background: `${C.instaBlue}10`,
                            cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            fontFamily: font, fontSize: 13, fontWeight: 700, color: C.instaBlue,
                          }}>
                            <span>🏷️ Apply Coupon or Offer</span>
                            <span style={{ fontSize: 18, transform: showOffers ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s' }}>▾</span>
                          </button>

                          {showOffers && (
                            <div style={{ marginTop: 10, background: '#fff', borderRadius: 14, border: `1px solid ${C.border}`, overflow: 'hidden' }}>
                              <div style={{ display: 'flex', gap: 8, padding: '12px' }}>
                                <input
                                  value={manualCode} onChange={e => { setManualCode(e.target.value); setCodeError('') }}
                                  placeholder="Enter coupon code"
                                  style={{ flex: 1, padding: '10px 12px', borderRadius: 10, border: `1px solid ${C.border}`, fontSize: 13, fontFamily: font, outline: 'none', background: C.bg, textTransform: 'uppercase' }}
                                />
                                <button onClick={applyManualCode} style={{
                                  padding: '10px 16px', borderRadius: 10, border: 'none',
                                  background: C.instaBlue, color: '#fff', fontSize: 12, fontWeight: 800, cursor: 'pointer', fontFamily: font
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
                                    border: `1px solid ${C.border}`, background: '#F8FAF8',
                                  }}>
                                    <div style={{ flex: 1 }}>
                                      <div style={{ fontSize: 13, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{offer.coupon_code}</div>
                                      <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>{offer.title}</div>
                                      {Number(offer.minimum_order_amount) > 0 && (
                                        <div style={{ fontSize: 10, color: C.instaBlue, fontFamily: font, marginTop: 2 }}>Min order ₹{offer.minimum_order_amount}</div>
                                      )}
                                    </div>
                                    <button onClick={() => applyOffer(offer)} style={{
                                      padding: '6px 14px', borderRadius: 8, border: `1.5px solid ${C.instaBlue}`, background: 'transparent',
                                      color: C.instaBlue, fontSize: 11, fontWeight: 800, cursor: 'pointer', fontFamily: font,
                                    }}>APPLY</button>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Bill details */}
                  <div style={{ background: '#fff', borderRadius: 16, padding: '16px', border: `1px solid ${C.border}` }}>
                    <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>Bill Details</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: C.muted, fontFamily: font }}>
                      <span>Item Total</span>
                      <span>₹{cartSubtotal.toFixed(2)}</span>
                    </div>
                    {appliedOffer && (
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: C.instaBlue, fontWeight: 700, fontFamily: font }}>
                        <span>Discount ({appliedOffer.coupon_code})</span>
                        <span>-₹{discountAmt.toFixed(2)}</span>
                      </div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13, color: C.muted, fontFamily: font }}>
                      <span>Delivery Fee</span>
                      <span style={{ color: cartDelivery === 0 ? C.instaBlue : C.muted }}>{cartDelivery === 0 ? 'FREE' : `₹${cartDelivery.toFixed(2)}`}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12, fontSize: 13, color: C.muted, fontFamily: font }}>
                      <span>Taxes (5%)</span>
                      <span style={{ color: C.muted }}>₹{tax.toFixed(2)}</span>
                    </div>
                    {cartDelivery > 0 && cartSubtotal < 500 && (
                      <div style={{ fontSize: 11, color: '#D94F2B', fontFamily: font, marginBottom: 12, textAlign: 'right' }}>Add ₹{(500 - cartSubtotal).toFixed(2)} more for FREE delivery</div>
                    )}
                    <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: 12, borderTop: `1px dashed ${C.border}`, fontSize: 15, fontWeight: 900, color: C.charcoal, fontFamily: font }}>
                      <span>To Pay</span>
                      <span style={{ color: C.instaBlue }}>₹{cartTotal.toFixed(2)}</span>
                    </div>

                    {/* Payment mode selector */}
                    <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
                      {[{ id: 'cod', label: '💵 Cash on Delivery' }, { id: 'razorpay', label: '💳 Pay Online' }].map(m => (
                        <button key={m.id} onClick={() => setPayMode(m.id)}
                          style={{ flex: 1, padding: '10px 8px', borderRadius: 12, border: `2px solid ${payMode === m.id ? C.instaBlue : C.border}`, background: payMode === m.id ? C.instaLight : '#fff', cursor: 'pointer', fontSize: 11, fontWeight: 700, color: payMode === m.id ? C.instaBlue : C.charcoal, fontFamily: font, transition: 'all 0.2s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                          {m.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Checkout Footer */}
                <div style={{ background: '#fff', padding: '16px 20px', borderTop: `1px solid ${C.border}`, display: 'flex', gap: 16, alignItems: 'center' }}>
                  <button onClick={handleCheckout} style={{ background: C.instaBlue, border: 'none', borderRadius: 12, padding: '14px 24px', fontSize: 15, fontWeight: 800, color: '#fff', cursor: 'pointer', fontFamily: font, flex: 1, boxShadow: '0 4px 15px rgba(0,84,255,0.3)' }}>
                    {payMode === 'cod' ? `Place Order → ₹${cartTotal.toFixed(2)}` : `Pay ₹${cartTotal.toFixed(2)} Online →`}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  )

  const renderCategories = () => (
    <div style={{ padding: '16px 16px 100px' }}>
      <div style={{ fontSize: 22, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 16 }}>All Categories</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {categories.map(cat => (
          <div key={cat.id} onClick={() => { setSelectedCat(cat.id); setInstaTab('instamart'); }} style={{ background: '#fff', borderRadius: 16, padding: '12px 8px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', cursor: 'pointer', border: `1px solid ${C.border}` }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>{getCatIcon(cat.name)}</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: C.charcoal, fontFamily: font, lineHeight: 1.2 }}>{cat.name}</div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderReorder = () => (
    <div style={{ padding: '16px 16px 100px' }}>
      <div style={{ fontSize: 22, fontWeight: 900, color: C.charcoal, fontFamily: font, marginBottom: 16 }}>Your Past Orders</div>
      {ordersLoading ? (
        <div style={{ padding: 16 }}>{[...Array(3)].map((_, i) => <Skel key={i} h={100} r={12} mb={12} />)}</div>
      ) : pastOrders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🛒</div>
          <div style={{ fontSize: 14, color: C.muted, fontFamily: font }}>No past orders found</div>
        </div>
      ) : pastOrders.map(o => (
        <div key={o.id} style={{ background: '#fff', borderRadius: 16, padding: '16px', marginBottom: 12, border: `1px solid ${C.border}` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>{o.store_name || 'Instamart Store'}</div>
              <div style={{ fontSize: 11, color: C.muted, fontFamily: font }}>{new Date(o.created_at).toLocaleDateString()} · {o.status}</div>
            </div>
            <div style={{ fontSize: 14, fontWeight: 800, color: C.instaBlue, fontFamily: font }}>₹{o.grand_total}</div>
          </div>
          <div style={{ fontSize: 12, color: C.charcoal, fontFamily: font, marginBottom: 12 }}>
            {o.items?.map(i => `${i.quantity}x ${i.name}`).join(', ')}
          </div>
          <button onClick={() => setInstaTab('instamart')} style={{ width: '100%', background: C.instaLight, border: `1px solid ${C.instaBlue}`, borderRadius: 10, padding: '8px', color: C.instaBlue, fontSize: 12, fontWeight: 800, cursor: 'pointer', fontFamily: font }}>
            Browse Instamart to Reorder
          </button>
        </div>
      ))}
    </div>
  )

  const TABS = [
    { id: 'instamart', icon: '🛍️', label: 'Instamart' },
    { id: 'categories', icon: '🔠', label: 'Categories' },
    { id: 'reorder', icon: '🛒', label: 'Reorder' },
  ]

  return (
    <div style={{ background: C.bg, minHeight: '100vh', paddingBottom: 80 }}>
      {instaTab === 'instamart' && renderInstamartHome()}
      {instaTab === 'categories' && renderCategories()}
      {instaTab === 'reorder' && renderReorder()}

      {/* Custom Instamart Bottom Navigation */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderTop: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-around', padding: '10px 0 16px', zIndex: 100 }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setInstaTab(t.id)} style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}>
            <span style={{ fontSize: 24, opacity: instaTab === t.id ? 1 : 0.5, filter: instaTab === t.id ? 'none' : 'grayscale(100%)' }}>{t.icon}</span>
            <span style={{ fontSize: 10, fontWeight: 800, color: instaTab === t.id ? C.instaBlue : C.muted, fontFamily: font }}>{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
