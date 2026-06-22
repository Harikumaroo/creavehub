import React, { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'

const C = {
  purple: '#673076',
  purpleLight: '#F5EBF7',
  textMain: '#1A1A1A',
  textSec: '#666666',
  bg: '#FFFFFF',
  green: '#0C8354',
  greenLight: '#E6F4EA',
  border: '#E8E8E8',
}

const font = "'Inter', 'Outfit', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return <div style={{ width: w, height: h, borderRadius: r, marginBottom: mb, background: `linear-gradient(90deg,#f0f0f0 25%,#fafafa 50%,#f0f0f0 75%)`, backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />
}

export default function GiftsPage({ goHome }) {
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [data, setData] = useState({ categories: [], products: [] })
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('giftables')
  
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [isSearching, setIsSearching] = useState(false)
  
  const [cart, setCart] = useState(null)
  const [cartOpen, setCartOpen] = useState(false)
  const [cartLoading, setCartLoading] = useState(false)
  const [checkoutState, setCheckoutState] = useState('cart') // cart, recipient, message, schedule, review, processing, success
  const [selectedCategory, setSelectedCategory] = useState(null)

  // Gift Checkout State
  const [recipient, setRecipient] = useState({ name: '', mobile: '', address: '', email: '' })
  const [giftMsg, setGiftMsg] = useState({ text: '', type: 'text' }) // type: text, card, video, voice
  const [schedule, setSchedule] = useState({ type: 'now', time: '' }) // now, scheduled, midnight, anniversary
  const [payMode, setPayMode] = useState('cod')

  const loadCart = () => {
    dashboardApi.getInstamartCart().then(r => setCart(r.data?.data)).catch(console.error)
  }

  useEffect(() => {
    loadCart()
    dashboardApi.getInstamart()
      .then(r => {
        const payload = r.data?.data || r.data
        if (payload) {
          let prods = payload.all_products || payload.featured_products || []
          let cats = payload.categories || []
          let stores = payload.stores || []
          setData({ categories: cats, products: prods, stores })
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  let searchTimeout = null
  const handleSearch = (e) => {
    const q = e.target.value
    setSearchQuery(q)
    if (!q.trim()) {
      setSearchResults([])
      return
    }
    setIsSearching(true)
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      dashboardApi.searchInstamartProducts(q)
        .then(r => setSearchResults(r.data?.data || []))
        .catch(console.error)
        .finally(() => setIsSearching(false))
    }, 500)
  }

  const handleAddToCart = (productId) => {
    if (!productId) return
    setCartLoading(true)
    dashboardApi.addInstamartToCart({ product_id: productId, quantity: 1 })
      .then(() => {
        loadCart()
        setCartOpen(true)
      })
      .catch(console.error)
      .finally(() => setCartLoading(false))
  }

  const handleUpdateCart = (id, quantity) => {
    dashboardApi.updateInstamartCartItem(id, { quantity }).then(loadCart).catch(console.error)
  }

  const handlePlaceOrder = () => {
    setCheckoutState('processing')
    dashboardApi.placeInstamartOrder({
      cartTotal: cart.grand_total,
      cartSubtotal: cart.subtotal,
      payMode: payMode,
      deliveryFee: cart.delivery_fee,
      tax: cart.tax,
      items: cart.items.map(i => ({ id: i.product_id, quantity: i.quantity, name: i.name, effective_price: i.price })),
      is_gift: true,
      recipient_name: recipient.name,
      recipient_mobile: recipient.mobile,
      recipient_email: recipient.email,
      gift_message: giftMsg.text,
      delivery_schedule_type: schedule.type,
      scheduled_delivery_time: schedule.time || null,
      deliveryAddress: recipient.address || "Mock Address, Chennai"
    }).then(() => {
      setCheckoutState('success')
      dashboardApi.clearInstamartCart()
      setTimeout(() => {
        setCheckoutState('cart')
        setCartOpen(false)
        loadCart()
      }, 3000)
    }).catch(e => {
      console.error(e)
      alert("Failed to place order.")
      setCheckoutState('cart')
    })
  }

  const budgetCards = [
    { title: 'UNDER', price: '₹500', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹1000', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹1500', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹2000', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹2500', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹3000', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
    { title: 'UNDER', price: '₹5000', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
  ]
  const mockProducts = {
    florist: [
      { id: 'f1', name: 'Pink Roses Bouquet', brand: 'FNP Cakes By Ferns N Petals', price: 499, oldPrice: null, off: null, time: '35 MINS', rating: 4.3, img: 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=400&q=80', description: 'A beautiful bouquet of freshly picked pink roses wrapped elegantly. Perfect for expressing love and admiration.' },
      { id: 'f2', name: 'Mixed Lilies & Orchids', brand: 'Interflora', price: 899, oldPrice: 1200, off: '25% OFF', time: '45 MINS', rating: 4.8, img: 'https://images.unsplash.com/photo-1563241527-3004b7be023c?w=400&q=80', description: 'Stunning mixed flowers to brighten up any occasion. Hand-tied by expert florists.' },
      { id: 'f3', name: 'Premium Red Roses Box', brand: 'IGP', price: 1499, oldPrice: 1999, off: '25% OFF', time: '60 MINS', rating: 4.9, img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=400&q=80', description: 'Classic premium red roses arranged beautifully in a luxury signature box.' }
    ],
    cakes: [
      { id: 'c1', name: 'Black Forest Cake', brand: 'Bakingo', price: 600, oldPrice: null, off: null, time: '25 MINS', rating: 4.5, img: 'https://images.unsplash.com/photo-1557308536-ee471ef2c390?w=400&q=80', description: 'Freshly baked black forest cake layered with chocolate sponge and cherries.' },
      { id: 'c2', name: 'Red Velvet Heart Cake', brand: 'SMOOR', price: 850, oldPrice: 1000, off: '15% OFF', time: '30 MINS', rating: 4.7, img: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80', description: 'Delicious heart-shaped red velvet cake with cream cheese frosting.' },
      { id: 'c3', name: 'Pineapple Delight', brand: 'Monginis', price: 450, oldPrice: null, off: null, time: '20 MINS', rating: 4.2, img: 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400&q=80', description: 'Juicy pineapple bits embedded in soft vanilla sponge cake.' }
    ],
    mostGifted: [
      { id: 'm1', name: 'Eggless Choco Truffle Cake (500g)', brand: 'SMOOR', price: 729, oldPrice: null, off: null, time: '20 MINS', rating: 4.7, img: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400&q=80', description: 'A decadent chocolate truffle cake, completely eggless and incredibly moist.' },
      { id: 'm2', name: 'Ferrero Rocher Box', brand: 'Ferrero', price: 899, oldPrice: 1100, off: '18% OFF', time: '15 MINS', rating: 4.8, img: 'https://images.unsplash.com/photo-1548883354-94cb1f0ab971?w=400&q=80', description: 'Premium hazelnut chocolates wrapped in elegant gold foil.' },
      { id: 'm3', name: 'Custom Photo Mug', brand: 'Printo', price: 299, oldPrice: 499, off: '40% OFF', time: '40 MINS', rating: 4.4, img: 'https://images.unsplash.com/photo-1514066558159-fc8c737ef25f?w=400&q=80', description: 'Personalized coffee mug with high-quality photo print.' }
    ],
    uniqueFinds: [
      { id: 'u1', name: 'Bartique Stainless Steel Home ...', brand: 'Bartique', price: 2049, oldPrice: 2299, off: '10% OFF', time: '30 MINS', rating: null, img: 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=400&q=80', description: 'A sleek and modern stainless steel bar set for your home.' },
      { id: 'u2', name: 'Aromatic Candles Set', brand: 'Yankee Candle', price: 1299, oldPrice: 1599, off: '18% OFF', time: '25 MINS', rating: 4.6, img: 'https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=400&q=80', description: 'Set of 3 premium scented candles to create a relaxing ambiance.' },
      { id: 'u3', name: 'Vintage Desk Clock', brand: 'Titan', price: 1850, oldPrice: 2100, off: '11% OFF', time: '35 MINS', rating: 4.5, img: 'https://images.unsplash.com/photo-1508057198894-247b23fe5278?w=400&q=80', description: 'Classic analog desk clock with a brass finish.' }
    ],
    jewels: [
      { id: 'j1', name: "NVR Women's Gold-Plated Minimalist...", brand: 'NVR', price: 99, oldPrice: 999, off: '90% OFF', time: '14 MINS', rating: 4, img: 'https://images.unsplash.com/photo-1599643478524-fb66f70d00f8?w=400&q=80', description: 'Elegant and minimalist gold-plated necklace for daily wear.' },
      { id: 'j2', name: "Swarovski Crystal Earrings", brand: 'Swarovski', price: 3499, oldPrice: 4999, off: '30% OFF', time: '50 MINS', rating: 4.9, img: 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400&q=80', description: 'Stunning crystal drop earrings that catch the light beautifully.' },
      { id: 'j3', name: "Silver Charm Bracelet", brand: 'Pandora', price: 2999, oldPrice: 3500, off: '14% OFF', time: '40 MINS', rating: 4.7, img: 'https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=400&q=80', description: 'Sterling silver bracelet with customizable charms.' }
    ]
  }

  const getFilteredProducts = (filterStr) => {
    let list = []
    if (filterStr.startsWith("Budget: ")) {
      const maxPrice = parseInt(filterStr.split(" ")[1])
      list = data.products.filter(p => (p.discount_price || p.price) <= maxPrice)
    } else if (filterStr === "Offers") {
      list = data.products.filter(p => p.discount_price && p.discount_price < p.price)
    } else {
      const catObj = data.categories.find(c => c.name === filterStr)
      if (catObj) {
        list = data.products.filter(p => p.category === catObj.id || p.category?.id === catObj.id || p.category?.name === filterStr)
      } else {
        list = data.products.filter(p => p.category?.name === filterStr || p.category === filterStr)
      }
    }
    return list.map(p => ({
        name: p.name,
        brand: p.description || 'Premium',
        price: p.discount_price || p.price,
        oldPrice: p.discount_price ? p.price : null,
        off: p.discount_price ? `${Math.round(((p.price - p.discount_price)/p.price)*100)}% OFF` : null,
        time: '30 MINS',
        rating: 4.5,
        img: p.image,
        id: p.id
    }))
  }

  const normalizeApiProducts = (catName, mockList) => {
    const apiList = getFilteredProducts(catName)
    if (apiList.length > 0) return apiList
    return mockList || []
  }

  const floristProducts = normalizeApiProducts("From the Florist", mockProducts.florist)
  const cakeProducts = normalizeApiProducts("Cakes for Celebrations", mockProducts.cakes)
  const giftedProducts = normalizeApiProducts("Most Gifted", mockProducts.mostGifted)
  const uniqueProducts = normalizeApiProducts("Unique Finds", mockProducts.uniqueFinds)
  const jewelProducts = normalizeApiProducts("Chains & Necklaces", mockProducts.jewels)

  const SectionTitle = ({ children, onBack }) => (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, margin: '32px 0 20px', position: 'relative' }}>
      {onBack && <button onClick={onBack} style={{position: 'absolute', left: 16, background: 'none', border: 'none', fontSize: 20, cursor: 'pointer'}}>←</button>}
      <svg width="24" height="12" viewBox="0 0 24 12" fill="none"><path d="M6 6C6 6 8.5 2 12 2C15.5 2 18 6 18 6" stroke="#CCC" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M6 6C6 6 8.5 10 12 10C15.5 10 18 6 18 6" stroke="#CCC" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><circle cx="3" cy="6" r="1.5" fill="#CCC"/><circle cx="21" cy="6" r="1.5" fill="#CCC"/></svg>
      <h2 style={{ fontSize: 20, fontWeight: 900, color: C.textMain, margin: 0, letterSpacing: '-0.5px' }}>{children}</h2>
      <svg width="24" height="12" viewBox="0 0 24 12" fill="none"><path d="M6 6C6 6 8.5 2 12 2C15.5 2 18 6 18 6" stroke="#CCC" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M6 6C6 6 8.5 10 12 10C15.5 10 18 6 18 6" stroke="#CCC" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><circle cx="3" cy="6" r="1.5" fill="#CCC"/><circle cx="21" cy="6" r="1.5" fill="#CCC"/></svg>
    </div>
  )

  const ProductCard = ({ p }) => (
    <div onClick={() => setSelectedProduct(p)} style={{ minWidth: 160, width: 160, display: 'flex', flexDirection: 'column', cursor: 'pointer' }}>
      <div style={{ height: 180, borderRadius: 16, background: '#f5f5f5', backgroundImage: `url(${p.img})`, backgroundSize: 'cover', backgroundPosition: 'center', position: 'relative', marginBottom: 12 }}>
        {data.stores?.[0]?.is_currently_open === false ? (
          <div style={{ position: 'absolute', bottom: 8, right: 8, borderRadius: 8, background: '#FFF3F3', border: `1px solid #FFCDCD`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#D94F2B', fontSize: 10, fontWeight: 900, padding: '4px 8px' }}>CLOSED</div>
        ) : (
          <button onClick={(e) => { e.stopPropagation(); handleAddToCart(p.id); }} style={{ position: 'absolute', bottom: 8, right: 8, width: 32, height: 32, borderRadius: 8, background: '#fff', border: `1.5px solid ${C.green}`, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: C.green, fontSize: 20, fontWeight: 600, boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>+</button>
        )}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6, fontSize: 11, fontWeight: 700, color: C.textSec }}>
        <span>{p.time}</span>
        {p.rating && <span style={{ color: C.green, display: 'flex', alignItems: 'center', gap: 2 }}>★ {p.rating}</span>}
      </div>
      <div style={{ fontSize: 13, fontWeight: 700, color: C.textMain, lineHeight: 1.3, marginBottom: 4, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 12, height: 12, border: '1px solid #1c833f', borderRadius: 2, marginRight: 6 }}>
          <span style={{ width: 6, height: 6, background: '#1c833f', borderRadius: '50%' }}></span>
        </span>
        {p.name}
      </div>
      <div style={{ fontSize: 11, color: C.textSec, marginBottom: 6, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.brand}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
        {p.off && <span style={{ fontSize: 11, fontWeight: 800, color: C.green }}>{p.off}</span>}
        <span style={{ fontSize: 14, fontWeight: 800, color: C.textMain }}>₹{p.price}</span>
        {p.oldPrice && <span style={{ fontSize: 11, color: '#999', textDecoration: 'line-through' }}>₹{p.oldPrice}</span>}
      </div>
    </div>
  )

  const ProductRow = ({ items }) => (
    <div style={{ display: 'flex', gap: 16, overflowX: 'auto', padding: '0 16px', paddingBottom: 16, scrollbarWidth: 'none', msOverflowStyle: 'none', '::-webkit-scrollbar': { display: 'none' } }}>
      {items.map((it, i) => <ProductCard key={i} p={it} />)}
    </div>
  )

  const ViewAllBtn = ({cat}) => (
    <div style={{ padding: '0 16px', marginTop: -8 }}>
      <button onClick={() => setSelectedCategory(cat)} style={{ width: '100%', padding: '14px', background: C.purpleLight, color: C.purple, border: 'none', borderRadius: 12, fontSize: 15, fontWeight: 800, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, cursor: 'pointer' }}>
        View all items <span style={{ background: C.purple, color: '#fff', borderRadius: '50%', width: 18, height: 18, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>›</span>
      </button>
    </div>
  )

  const cartDrawerContent = !cartOpen ? null : (
      <>
        <div onClick={() => setCartOpen(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000 }} />
        <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderRadius: '24px 24px 0 0', zIndex: 1001, padding: 24, paddingBottom: 100, maxHeight: '90vh', overflowY: 'auto' }}>
          {checkoutState === 'success' ? (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <div style={{ fontSize: 64, marginBottom: 16 }}>🎉</div>
              <h3 style={{ fontSize: 24, fontWeight: 800, color: C.green, marginBottom: 8 }}>Order Placed!</h3>
              <p style={{ color: C.textSec }}>Gift Order ID: #{Math.floor(100000 + Math.random() * 900000)}<br/>Tracking ID: TRK{Math.floor(1000 + Math.random() * 9000)}<br/><br/>Your recipient will be notified soon.</p>
            </div>
          ) : checkoutState === 'processing' ? (
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <Skel w={100} h={100} r="50%" mb={24} style={{ margin: '0 auto' }} />
              <h3 style={{ fontSize: 20, fontWeight: 800 }}>Processing Payment...</h3>
            </div>
          ) : (
            <>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h3 style={{ margin: 0, fontSize: 20, fontWeight: 900 }}>
                  {checkoutState === 'cart' && "🛒 Your Gift Cart"}
                  {checkoutState === 'recipient' && "👤 Recipient Details"}
                  {checkoutState === 'message' && "💌 Personal Message"}
                  {checkoutState === 'schedule' && "📅 Delivery Schedule"}
                  {checkoutState === 'review' && "🧾 Review Order"}
                  {checkoutState === 'payment' && "💳 Payment"}
                </h3>
                <button onClick={() => setCartOpen(false)} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer' }}>×</button>
              </div>

              {checkoutState === 'cart' && (
                (!cart || cart.item_count === 0 ? (
                  <div style={{ textAlign: 'center', padding: 40, color: C.textSec }}>Your cart is empty</div>
                ) : (
                  <>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 24 }}>
                      {cart.items.map(item => (
                        <div key={item.id} style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                          <div style={{ width: 60, height: 60, borderRadius: 8, background: '#f5f5f5', backgroundImage: `url(${item.image})`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
                          <div style={{ flex: 1 }}>
                            <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>{item.name}</div>
                            <div style={{ fontSize: 14, fontWeight: 800, color: C.textMain }}>₹{item.price}</div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 12, background: C.greenLight, borderRadius: 8, padding: '4px 8px' }}>
                            <button onClick={() => handleUpdateCart(item.id, item.quantity - 1)} style={{ background: 'none', border: 'none', color: C.green, fontWeight: 800, fontSize: 18, cursor: 'pointer' }}>-</button>
                            <span style={{ fontWeight: 800, fontSize: 14, color: C.green }}>{item.quantity}</span>
                            <button onClick={() => handleUpdateCart(item.id, item.quantity + 1)} style={{ background: 'none', border: 'none', color: C.green, fontWeight: 800, fontSize: 18, cursor: 'pointer' }}>+</button>
                          </div>
                        </div>
                      ))}
                    </div>
                    <button onClick={() => setCheckoutState('recipient')} style={{ width: '100%', padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Proceed to Recipient Details</button>
                  </>
                ))
              )}

              {checkoutState === 'recipient' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <input placeholder="Recipient Name" value={recipient.name} onChange={e => setRecipient({...recipient, name: e.target.value})} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15 }} />
                  <input placeholder="Mobile Number" value={recipient.mobile} onChange={e => setRecipient({...recipient, mobile: e.target.value})} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15 }} />
                  <input placeholder="Delivery Address" value={recipient.address} onChange={e => setRecipient({...recipient, address: e.target.value})} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15 }} />
                  <input placeholder="Optional Email" type="email" value={recipient.email} onChange={e => setRecipient({...recipient, email: e.target.value})} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15 }} />
                  <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                    <button onClick={() => setCheckoutState('cart')} style={{ flex: 1, padding: 16, background: '#f5f5f5', color: C.textMain, border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Back</button>
                    <button onClick={() => setCheckoutState('message')} style={{ flex: 2, padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Next</button>
                  </div>
                </div>
              )}

              {checkoutState === 'message' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <textarea placeholder="Example: Happy Birthday! Hope you have a wonderful day 🎉" value={giftMsg.text} onChange={e => setGiftMsg({...giftMsg, text: e.target.value})} rows={4} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15, fontFamily: 'inherit', resize: 'none' }} />
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8 }}>Optional Media:</div>
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                      {['text', 'card', 'video', 'voice'].map(t => (
                        <div key={t} onClick={() => setGiftMsg({...giftMsg, type: t})} style={{ padding: '8px 16px', borderRadius: 20, border: `1px solid ${giftMsg.type === t ? C.green : C.border}`, background: giftMsg.type === t ? C.greenLight : '#fff', color: giftMsg.type === t ? C.green : C.textSec, cursor: 'pointer', fontWeight: 600, fontSize: 14, textTransform: 'capitalize' }}>
                          {t === 'text' ? 'None' : t}
                        </div>
                      ))}
                    </div>
                    {giftMsg.type !== 'text' && <div style={{ marginTop: 12, padding: 16, background: '#f9f9f9', borderRadius: 12, fontSize: 13, color: C.textSec, textAlign: 'center', border: '1px dashed #ccc' }}>📸 Media upload functionality placeholder</div>}
                  </div>
                  <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                    <button onClick={() => setCheckoutState('recipient')} style={{ flex: 1, padding: 16, background: '#f5f5f5', color: C.textMain, border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Back</button>
                    <button onClick={() => setCheckoutState('schedule')} style={{ flex: 2, padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Next</button>
                  </div>
                </div>
              )}

              {checkoutState === 'schedule' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {[
                    {id: 'now', label: 'Deliver Now', desc: 'Typically within 30-45 mins'},
                    {id: 'scheduled', label: 'Scheduled Delivery', desc: 'Choose a specific date and time'},
                    {id: 'midnight', label: 'Birthday Midnight Delivery', desc: 'Delivered exactly between 11:45 PM - 12:15 AM'},
                    {id: 'anniversary', label: 'Anniversary Delivery', desc: 'Special careful handling and greeting'}
                  ].map(s => (
                    <div key={s.id} onClick={() => setSchedule({...schedule, type: s.id})} style={{ padding: 16, borderRadius: 12, border: `1.5px solid ${schedule.type === s.id ? C.green : C.border}`, background: schedule.type === s.id ? C.greenLight : '#fff', cursor: 'pointer' }}>
                      <div style={{ fontSize: 16, fontWeight: 800, color: schedule.type === s.id ? C.green : C.textMain, marginBottom: 4 }}>{s.label}</div>
                      <div style={{ fontSize: 13, color: schedule.type === s.id ? '#0A6E44' : C.textSec }}>{s.desc}</div>
                    </div>
                  ))}
                  {['scheduled', 'midnight', 'anniversary'].includes(schedule.type) && (
                    <input type="datetime-local" value={schedule.time} onChange={e => setSchedule({...schedule, time: e.target.value})} style={{ padding: 16, borderRadius: 12, border: `1px solid ${C.border}`, fontSize: 15, marginTop: 8 }} />
                  )}
                  <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                    <button onClick={() => setCheckoutState('message')} style={{ flex: 1, padding: 16, background: '#f5f5f5', color: C.textMain, border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Back</button>
                    <button onClick={() => setCheckoutState('review')} style={{ flex: 2, padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Review Order</button>
                  </div>
                </div>
              )}

              {checkoutState === 'review' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <div style={{ background: '#f5f5f5', padding: 16, borderRadius: 12 }}>
                    <div style={{ fontSize: 14, fontWeight: 800, marginBottom: 8, color: C.textMain }}>Items: {cart.item_count}</div>
                    <div style={{ fontSize: 14, fontWeight: 800, marginBottom: 8, color: C.textMain }}>To: {recipient.name || 'Not provided'} ({recipient.mobile})</div>
                    <div style={{ fontSize: 14, color: C.textSec, marginBottom: 8 }}>{recipient.address || 'No address provided'}</div>
                    <div style={{ fontSize: 14, fontWeight: 800, marginBottom: 8, color: C.textMain }}>Schedule: <span style={{textTransform: 'capitalize'}}>{schedule.type}</span></div>
                    {giftMsg.text && <div style={{ fontSize: 13, fontStyle: 'italic', color: C.textSec, background: '#fff', padding: 8, borderRadius: 8 }}>"{giftMsg.text}"</div>}
                  </div>

                  <div style={{ borderTop: `1px dashed ${C.border}`, paddingTop: 16, marginBottom: 8 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, color: C.textSec, fontSize: 14 }}><span>Item Total</span><span>₹{cart.subtotal}</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, color: C.textSec, fontSize: 14 }}><span>Delivery & Handling</span><span>₹{cart.delivery_fee}</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, color: C.textSec, fontSize: 14 }}><span>Taxes</span><span>₹{cart.tax}</span></div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16, color: C.textMain, fontSize: 18, fontWeight: 900 }}><span>To Pay</span><span>₹{cart.grand_total}</span></div>
                  </div>

                  <div style={{ display: 'flex', gap: 12 }}>
                    <button onClick={() => setCheckoutState('schedule')} style={{ flex: 1, padding: 16, background: '#f5f5f5', color: C.textMain, border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Back</button>
                    <button onClick={() => setCheckoutState('payment')} style={{ flex: 2, padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Select Payment</button>
                  </div>
                </div>
              )}

              {checkoutState === 'payment' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <div style={{ fontSize: 18, fontWeight: 900, marginBottom: 8, textAlign: 'center' }}>Amount to Pay: ₹{cart.grand_total}</div>
                  {['UPI', 'Credit/Debit Card', 'Net Banking', 'Wallets', 'Cash on Delivery'].map(m => (
                    <div key={m} onClick={() => setPayMode(m)} style={{ padding: 16, borderRadius: 12, border: `1.5px solid ${payMode === m ? C.green : C.border}`, background: payMode === m ? C.greenLight : '#fff', cursor: 'pointer', fontWeight: 700, color: payMode === m ? C.green : C.textMain, display: 'flex', justifyContent: 'space-between' }}>
                      {m}
                      {payMode === m && <span>✓</span>}
                    </div>
                  ))}
                  <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
                    <button onClick={() => setCheckoutState('review')} style={{ flex: 1, padding: 16, background: '#f5f5f5', color: C.textMain, border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Back</button>
                    <button onClick={() => handlePlaceOrder(payMode)} style={{ flex: 2, padding: 16, background: C.green, color: '#fff', border: 'none', borderRadius: 12, fontSize: 16, fontWeight: 800, cursor: 'pointer' }}>Pay & Place Order</button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </>
    )

  return (
    <div style={{ background: C.bg, minHeight: '100vh', fontFamily: font, paddingBottom: 100 }}>
      {cartLoading && <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: 3, background: C.green, zIndex: 1100 }} />}
      
      {/* Search Bar */}
      <div style={{ position: 'sticky', top: 0, background: '#fff', zIndex: 50, padding: '16px', borderBottom: `1px solid ${C.border}` }}>
        <div style={{ background: '#F8F8F8', border: `1px solid ${C.border}`, borderRadius: 12, padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 18, color: '#888' }}>🔍</span>
          <input value={searchQuery} onChange={handleSearch} placeholder="Let's find a gift they'll love..." style={{ border: 'none', background: 'transparent', width: '100%', fontSize: 15, outline: 'none', color: C.textMain }} />
        </div>
      </div>

      {searchQuery ? (
        <div style={{ padding: '20px 16px' }}>
          <h3 style={{ fontSize: 18, fontWeight: 800, marginBottom: 16 }}>Search Results</h3>
          {isSearching ? <Skel h={100} mb={10} r={12} /> : searchResults.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              {searchResults.map(p => (
                <ProductCard key={p.id} p={{
                  id: p.id, name: p.name, brand: p.brand || p.description,
                  price: p.discount_price || p.price, oldPrice: p.discount_price ? p.price : null,
                  off: p.discount_price ? `${Math.round(((p.price - p.discount_price)/p.price)*100)}% OFF` : null,
                  time: '30 MINS', rating: 4.5, img: p.image
                }} />
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: 40, color: C.textSec }}>No products found for "{searchQuery}"</div>
          )}
        </div>
      ) : (
        <div style={{ paddingBottom: 40, display: selectedCategory ? 'none' : 'block' }}>
          {/* Gifts by Budget */}
          <SectionTitle>Gifts by Budget</SectionTitle>
          <div style={{ display: 'flex', gap: 12, overflowX: 'auto', padding: '0 16px', scrollbarWidth: 'none' }}>
            {budgetCards.map((b, i) => (
              <div onClick={() => setSelectedCategory(`Budget: ${b.price.replace('₹', '')}`)} key={i} style={{ minWidth: 100, height: 130, background: '#FFF7ED', border: '1px solid #FFE4C4', borderRadius: '60px 60px 16px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px 8px 0', position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: C.textSec, letterSpacing: 0.5 }}>{b.title}</div>
                <div style={{ fontSize: 20, fontWeight: 900, color: C.textMain }}>{b.price}</div>
                <div style={{ position: 'absolute', bottom: -10, width: '90%', height: 60, backgroundImage: `url(${b.img})`, backgroundSize: 'contain', backgroundRepeat: 'no-repeat', backgroundPosition: 'bottom center' }} />
              </div>
            ))}
          </div>

          <SectionTitle>Deals & Offers</SectionTitle>
          <div style={{ padding: '0 16px', display: 'flex', gap: 12, overflowX: 'auto', scrollbarWidth: 'none' }}>
            <div onClick={() => setSelectedCategory('Offers')} style={{ flex: '1 0 auto', minWidth: 280, maxWidth: 350, height: 140, borderRadius: 16, background: 'linear-gradient(135deg, #4A148C 0%, #7B1FA2 100%)', color: '#fff', padding: 20, position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
              <div style={{ fontSize: 24, fontWeight: 900, marginBottom: 4 }}>Flat 50% Off</div>
              <div style={{ fontSize: 14, opacity: 0.9 }}>On Premium Chocolates & Cakes</div>
              <div style={{ position: 'absolute', right: -20, bottom: -20, fontSize: 100, opacity: 0.1 }}>%</div>
            </div>
            <div onClick={() => setSelectedCategory('Offers')} style={{ flex: '1 0 auto', minWidth: 280, maxWidth: 350, height: 140, borderRadius: 16, background: 'linear-gradient(135deg, #00695C 0%, #00897B 100%)', color: '#fff', padding: 20, position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
              <div style={{ fontSize: 24, fontWeight: 900, marginBottom: 4 }}>Special Offers</div>
              <div style={{ fontSize: 14, opacity: 0.9 }}>Explore all discounted gifts</div>
              <div style={{ position: 'absolute', right: -20, bottom: -20, fontSize: 100, opacity: 0.1 }}>🎁</div>
            </div>
            <div onClick={() => setSelectedCategory('Offers')} style={{ flex: '1 0 auto', minWidth: 280, maxWidth: 350, height: 140, borderRadius: 16, background: 'linear-gradient(135deg, #C2185B 0%, #E91E63 100%)', color: '#fff', padding: 20, position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
              <div style={{ fontSize: 24, fontWeight: 900, marginBottom: 4 }}>Clearance Sale</div>
              <div style={{ fontSize: 14, opacity: 0.9 }}>Up to 70% Off on selected items</div>
              <div style={{ position: 'absolute', right: -20, bottom: -20, fontSize: 100, opacity: 0.1 }}>🔥</div>
            </div>
            <div onClick={() => setSelectedCategory('Offers')} style={{ flex: '1 0 auto', minWidth: 280, maxWidth: 350, height: 140, borderRadius: 16, background: 'linear-gradient(135deg, #E65100 0%, #F57C00 100%)', color: '#fff', padding: 20, position: 'relative', overflow: 'hidden', cursor: 'pointer' }}>
              <div style={{ fontSize: 24, fontWeight: 900, marginBottom: 4 }}>Festive Combos</div>
              <div style={{ fontSize: 14, opacity: 0.9 }}>Save big on festive bundles</div>
              <div style={{ position: 'absolute', right: -20, bottom: -20, fontSize: 100, opacity: 0.1 }}>🎊</div>
            </div>
          </div>

          <SectionTitle>From the Florist</SectionTitle>
          <ProductRow items={floristProducts} />
          <ViewAllBtn cat="From the Florist" />

          <SectionTitle>Cakes for Celebrations</SectionTitle>
          <ProductRow items={cakeProducts} />

          <SectionTitle>Most Gifted</SectionTitle>
          <ProductRow items={giftedProducts} />
          <ViewAllBtn cat="Most Gifted" />

          <SectionTitle>Unique Finds</SectionTitle>
          <ProductRow items={uniqueProducts} />

          <SectionTitle>For Every Occasion</SectionTitle>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, padding: '0 16px' }}>
            {[
              { t: 'Birthday Party', img: 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=200&q=80' },
              { t: 'For Your Partner', img: 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80' },
              { t: 'Baby Shower', img: 'https://images.unsplash.com/photo-1519689680058-324335c77eba?w=200&q=80' },
              { t: 'House Warming', img: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=200&q=80' },
            ].map((o, i) => (
              <div key={i} style={{ background: '#FFF9ED', borderRadius: 16, height: 100, padding: 16, position: 'relative', overflow: 'hidden' }}>
                <div style={{ fontSize: 15, fontWeight: 800, width: '70%', lineHeight: 1.2 }}>{o.t}</div>
                <div style={{ color: '#D97706', fontSize: 18, marginTop: 12 }}>→</div>
                <div style={{ position: 'absolute', right: -10, bottom: -10, width: 80, height: 80, backgroundImage: `url(${o.img})`, backgroundSize: 'cover', borderRadius: '50%' }} />
              </div>
            ))}
          </div>

          <SectionTitle>Gifting Favourites</SectionTitle>
          <div style={{ columnCount: 2, columnGap: 12, padding: '0 16px' }}>
            {[
              { cat: "Cakes for Celebrations", t: 'Chocolates & Cakes', h: 180, bg: '#E3F2FD', img: 'https://images.unsplash.com/photo-1548883354-94cb1f0ab971?w=400&q=80' },
              { cat: "Electronics & Gadgets", t: 'Gadgets', h: 240, bg: '#E0F2F1', img: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80' },
              { cat: "From the Florist", t: 'Flowers & Plants', h: 220, bg: '#FCE4EC', img: 'https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?w=400&q=80' },
              { cat: "Home Decor", t: 'Home Decor', h: 190, bg: '#F1F8E9', img: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=400&q=80' },
            ].map((c, i) => (
              <div onClick={() => setSelectedCategory(c.cat)} key={i} style={{ height: c.h, background: c.bg, borderRadius: 16, marginBottom: 12, padding: 16, position: 'relative', overflow: 'hidden', backgroundImage: `url(${c.img})`, backgroundSize: 'cover', backgroundPosition: 'center', cursor: 'pointer' }}>
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(0,0,0,0.6) 0%, transparent 50%, rgba(0,0,0,0.4) 100%)' }} />
                <div style={{ position: 'relative', color: '#fff', fontSize: 16, fontWeight: 900, textShadow: '0 2px 4px rgba(0,0,0,0.3)' }}>{c.t}</div>
              </div>
            ))}
          </div>

          <SectionTitle>For Your Loved Ones</SectionTitle>
          <div style={{ display: 'flex', gap: 12, padding: '0 16px', overflowX: 'auto' }}>
            {['Her', 'Him', 'Kids'].map((t, i) => (
              <div key={i} style={{ minWidth: 120, height: 140, borderRadius: 16, background: '#F8F3ED', position: 'relative', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '12px 16px', fontSize: 16, fontWeight: 900, color: C.textMain }}>{t}</div>
                <div style={{ flex: 1, backgroundImage: `url(https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=200&q=80)`, backgroundSize: 'cover', backgroundPosition: 'center' }} />
              </div>
            ))}
          </div>

          <SectionTitle>Jewels For Someone Special</SectionTitle>
          <ProductRow items={jewelProducts} />
          <ViewAllBtn cat="Chains & Necklaces" />

        </div>
      )}

      {selectedCategory && (
        <div style={{ position: 'fixed', inset: 0, background: C.bg, zIndex: 60, overflowY: 'auto', paddingBottom: 100 }}>
          <div style={{ position: 'sticky', top: 0, background: '#fff', padding: '16px', zIndex: 61, borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', gap: 16 }}>
            <button onClick={() => setSelectedCategory(null)} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer' }}>←</button>
            <h2 style={{ fontSize: 20, fontWeight: 900, margin: 0 }}>{selectedCategory}</h2>
          </div>
          <div style={{ padding: '20px 16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              {normalizeApiProducts(selectedCategory, []).map(p => (
                <ProductCard key={p.id} p={p} />
              ))}
            </div>
          </div>
        </div>
      )}

      {cart && cart.item_count > 0 && !cartOpen && (
        <div onClick={() => setCartOpen(true)} style={{ position: 'fixed', bottom: 80, right: 16, background: C.green, color: '#fff', width: 60, height: 60, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, boxShadow: '0 4px 12px rgba(12, 131, 84, 0.4)', zIndex: 90, cursor: 'pointer' }}>
          🛒
          <span style={{ position: 'absolute', top: -5, right: -5, background: '#E8621A', color: '#fff', fontSize: 12, fontWeight: 800, width: 22, height: 22, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{cart.item_count}</span>
        </div>
      )}

      {cartDrawerContent}

      {selectedProduct && (
        <div style={{ position: 'fixed', inset: 0, background: '#fff', zIndex: 1002, overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
          <div style={{ position: 'relative', width: '100%', height: 350, background: '#f5f5f5', backgroundImage: `url(${selectedProduct.img})`, backgroundSize: 'cover', backgroundPosition: 'center' }}>
            <button onClick={() => setSelectedProduct(null)} style={{ position: 'absolute', top: 16, left: 16, width: 40, height: 40, borderRadius: '50%', background: 'rgba(255,255,255,0.8)', border: 'none', fontSize: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>←</button>
          </div>
          <div style={{ padding: '24px 20px', flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <h1 style={{ fontSize: 24, fontWeight: 900, color: C.textMain, margin: '0 0 8px', lineHeight: 1.2 }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 14, height: 14, border: '1px solid #1c833f', borderRadius: 3, marginRight: 8, verticalAlign: 'middle' }}>
                    <span style={{ width: 8, height: 8, background: '#1c833f', borderRadius: '50%' }}></span>
                  </span>
                  {selectedProduct.name}
                </h1>
                <div style={{ fontSize: 14, color: C.textSec, fontWeight: 600 }}>{selectedProduct.brand}</div>
              </div>
              {selectedProduct.rating && <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: '#E8F5E9', color: C.green, padding: '4px 8px', borderRadius: 8, fontWeight: 800, fontSize: 14 }}>★ {selectedProduct.rating}</div>}
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 28, fontWeight: 900, color: C.textMain }}>₹{selectedProduct.price}</span>
              {selectedProduct.oldPrice && <span style={{ fontSize: 18, color: '#999', textDecoration: 'line-through', fontWeight: 600 }}>₹{selectedProduct.oldPrice}</span>}
              {selectedProduct.off && <span style={{ fontSize: 14, fontWeight: 800, color: '#fff', background: C.green, padding: '4px 8px', borderRadius: 4 }}>{selectedProduct.off}</span>}
            </div>

            <div style={{ marginBottom: 32 }}>
              <h3 style={{ fontSize: 16, fontWeight: 800, marginBottom: 8, color: C.textMain }}>Description</h3>
              <p style={{ fontSize: 15, color: C.textSec, lineHeight: 1.6, margin: 0 }}>
                {selectedProduct.description || "Premium quality product carefully sourced to provide the best experience. Handled with care and delivered fresh to your door in " + selectedProduct.time + "."}
              </p>
            </div>
          </div>
          <div style={{ padding: '16px 20px', background: '#fff', borderTop: `1px solid ${C.border}`, position: 'sticky', bottom: 0 }}>
            {data.stores?.[0]?.is_currently_open === false ? (
              <button disabled style={{ width: '100%', padding: '16px', background: '#FFF3F3', color: '#D94F2B', border: '1px solid #FFCDCD', borderRadius: 16, fontSize: 18, fontWeight: 800, cursor: 'not-allowed' }}>Gifts Store is Closed</button>
            ) : (
              <button onClick={() => { handleAddToCart(selectedProduct.id); setSelectedProduct(null); }} style={{ width: '100%', padding: '16px', background: C.green, color: '#fff', border: 'none', borderRadius: 16, fontSize: 18, fontWeight: 800, cursor: 'pointer', boxShadow: '0 4px 12px rgba(12, 131, 84, 0.3)' }}>Add Item to Cart • ₹{selectedProduct.price}</button>
            )}
          </div>
        </div>
      )}

      {/* Bottom Nav */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderTop: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-around', padding: '12px 0 20px', zIndex: 100, boxShadow: '0 -4px 12px rgba(0,0,0,0.03)' }}>
        <button onClick={() => goHome()} style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}>
          <span style={{ fontSize: 24, filter: 'grayscale(100%)', opacity: 0.5 }}>🏠</span>
          <span style={{ fontSize: 11, fontWeight: 600, color: C.textSec }}>Home</span>
        </button>
        <button onClick={() => setActiveTab('giftables')} style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={activeTab === 'giftables' ? '#E8621A' : C.textSec} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 12 20 22 4 22 4 12"></polyline><rect x="2" y="7" width="20" height="5"></rect><line x1="12" y1="22" x2="12" y2="7"></line><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"></path><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"></path></svg>
          <span style={{ fontSize: 11, fontWeight: activeTab === 'giftables' ? 800 : 600, color: activeTab === 'giftables' ? '#E8621A' : C.textSec }}>Giftables</span>
        </button>
        <button onClick={() => setActiveTab('categories')} style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={activeTab === 'categories' ? '#E8621A' : C.textSec} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          <span style={{ fontSize: 11, fontWeight: activeTab === 'categories' ? 800 : 600, color: activeTab === 'categories' ? '#E8621A' : C.textSec }}>All Categories</span>
        </button>
      </div>
    </div>
  )
}
