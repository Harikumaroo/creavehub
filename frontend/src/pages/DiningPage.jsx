import { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboardApi'

const font = "'Poppins', system-ui, sans-serif"

function Skel({ w = '100%', h = 16, r = 8, mb = 0 }) {
  return <div style={{ width: w, height: h, borderRadius: r, marginBottom: mb, background: `linear-gradient(90deg,#F0E0CC 25%,#FDE8CC 50%,#F0E0CC 75%)`, backgroundSize: '200% 100%', animation: 'shimmer 1.4s infinite' }} />
}

export default function DiningPage({ goHome }) {
  const [venues, setVenues] = useState([])
  const [loading, setLoading] = useState(true)
  const [diningTab, setDiningTab] = useState('dining')
  const [selectedVenue, setSelectedVenue] = useState(null)
  
  // Search
  const [searchQ, setSearchQ] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  
  // Filters
  const [filterNearMe, setFilterNearMe] = useState(false)
  const [filterOffers, setFilterOffers] = useState(false)

  // Booking state
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [bookingForm, setBookingForm] = useState({ date: '', time: '', guest_count: 2, special_requests: '' })
  const [bookingSuccess, setBookingSuccess] = useState(false)

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (filterNearMe) {
      params.lat = '13.0827'
      params.lng = '80.2707'
      params.radius = '10'
    }
    if (filterOffers) {
      params.has_offers = 'true'
    }

    dashboardApi.getDiningVenues(params)
      .then(r => {
        const d = r.data?.data || r.data?.results || r.data
        setVenues(Array.isArray(d) ? d : [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [filterNearMe, filterOffers])

  const handleSearchChange = async (e) => {
    const val = e.target.value
    setSearchQ(val)
    if (val.length >= 1) {
      await new Promise(r => setTimeout(r, 100))
      const query = val.toLowerCase()
      const matches = venues.filter(v => (v.restaurant_name || v.restaurant?.name || '').toLowerCase().includes(query)).map(v => v.restaurant_name || v.restaurant?.name)
      setSuggestions(Array.from(new Set(matches)).slice(0,5))
      setShowDropdown(true)
    } else {
      setSuggestions([])
      setShowDropdown(false)
    }
  }

  const handleSuggestionClick = (sug) => {
    setSearchQ(sug)
    setShowDropdown(false)
    const match = venues.find(v => (v.restaurant_name || v.restaurant?.name) === sug)
    if (match) setSelectedVenue(match)
  }

  const handleBook = async () => {
    if (!bookingForm.date || !bookingForm.time) return
    try {
      await dashboardApi.createReservation({
        venue: selectedVenue.id,
        date: bookingForm.date,
        time: bookingForm.time,
        guest_count: bookingForm.guest_count,
        special_requests: bookingForm.special_requests,
      })
      setBookingSuccess(true)
      setTimeout(() => { 
        setBookingSuccess(false)
        setShowBookingModal(false) 
      }, 3000)
    } catch (err) {
      alert(err.response?.data?.message || 'Could not create reservation. Please try again.')
    }
  }

  if (loading) return (
    <div className="p-4">
      <Skel h={60} r={16} mb={16} />
      {[...Array(5)].map((_, i) => <Skel key={i} h={180} r={16} mb={12} />)}
    </div>
  )

  if (selectedVenue) {
    return (
      <div className="bg-[#f8f9fa] min-h-screen pb-[120px]" style={{ fontFamily: font }}>
        {/* Hero Image */}
        <div className="relative w-full h-[280px]">
          <img src={selectedVenue.restaurant?.cover_image || selectedVenue.restaurant_image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&q=80'} alt="cover" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-transparent" />
          
          {/* Top Actions */}
          <div className="absolute top-4 left-4 right-4 flex justify-between items-center z-10">
            <button onClick={() => setSelectedVenue(null)} className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md text-xl">
              ←
            </button>
            <div className="flex gap-3">
              <button className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md text-xl">♡</button>
              <button className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-md text-xl">🔗</button>
            </div>
          </div>
        </div>

        {/* Floating Info Card */}
        <div className="relative px-4 -mt-16 z-20">
          <div className="bg-white rounded-[24px] shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-[#FFF7ED] px-4 py-2 flex items-center gap-2 border-b border-[#FFEDD5]">
              <span className="bg-[#FFD54F] text-[#5D4037] text-[10px] font-black px-1.5 py-0.5 rounded">2X</span>
              <span className="text-[#FC8019] text-xs font-bold">Earn & Redeem 2X DineCash</span>
            </div>
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <h1 className="text-xl font-black text-gray-900 leading-tight flex-1 pr-4">
                  {selectedVenue.restaurant_name || selectedVenue.restaurant?.name || 'Grand Multicuisine Restaurant'}
                </h1>
                <div className="flex flex-col items-center bg-gray-50 border border-gray-200 rounded-lg p-1.5 min-w-[50px]">
                  <div className="flex items-center text-green-700 font-black text-sm">
                    {selectedVenue.restaurant?.rating || '4.2'} <span className="text-xs ml-0.5">★</span>
                  </div>
                  <div className="text-[9px] text-gray-500 font-bold mt-0.5">100 ratings</div>
                </div>
              </div>
              
              <div className="text-[13px] text-gray-600 font-medium mb-1">
                {selectedVenue.distance_km ? `${selectedVenue.distance_km} km` : '7.1 km'} • {selectedVenue.restaurant?.address?.city || 'Velachery, Chennai'} <span className="text-[#E65100]">▼</span>
              </div>
              <div className="text-[13px] text-gray-500 mb-3">
                {selectedVenue.restaurant?.categories?.map(c=>c.name).join(', ') || 'North Indian, South Indian'} | ₹{selectedVenue.avg_cost_for_two || 600} for two
              </div>
              
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-full px-3 py-1.5">
                  <span className={selectedVenue.restaurant_is_currently_open === false ? "text-red-500 font-bold text-xs" : "text-green-600 font-bold text-xs"}>
                    {selectedVenue.restaurant_is_currently_open === false ? "Closed" : "Open"}
                  </span>
                  <span className="text-gray-500 text-xs">till {selectedVenue.restaurant_formatted_hours?.split('-')[1] || '11:30PM'}</span>
                  <span className="text-gray-400 text-xs ml-1">▼</span>
                </div>
                <button className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 shadow-sm text-sm">📍</button>
                <button className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 shadow-sm text-sm">📞</button>
              </div>
            </div>
          </div>
        </div>

        {/* Offers Section */}
        <div className="mt-6 px-4">
          <h2 className="text-lg font-black text-gray-900 mb-3">Offers for you</h2>
          <div className="flex gap-2 mb-3 bg-gray-100 p-1 rounded-full w-max">
            <button className="bg-gray-900 text-white text-xs font-bold px-4 py-2 rounded-full">Pre-booking offers</button>
            <button className="text-gray-600 text-xs font-bold px-4 py-2 rounded-full">Walk-in offers</button>
          </div>
          <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2">
            {selectedVenue.restaurant?.offers?.length > 0 ? selectedVenue.restaurant.offers.map((offer, idx) => (
              <div key={offer.id || idx} className="flex-shrink-0 w-[280px] bg-white rounded-2xl border border-[#FFCCBC] p-4 shadow-sm relative overflow-hidden">
                <div className="text-[#D84315] text-[10px] font-black uppercase mb-1 tracking-wider">{offer.coupon_code}</div>
                <div className="text-lg font-black text-gray-900">{offer.title} &gt;</div>
                <div className="text-[#D84315] text-xs font-bold mt-1">Discount: {offer.discount_type === 'PERCENTAGE' ? `${offer.discount_value}%` : `₹${offer.discount_value}`}</div>
              </div>
            )) : (
              <div className="flex-shrink-0 w-[280px] bg-white rounded-2xl border border-[#FFCCBC] p-4 shadow-sm relative overflow-hidden">
                <div className="text-[#D84315] text-[10px] font-black uppercase mb-1 tracking-wider">ONE Exclusive</div>
                <div className="text-lg font-black text-gray-900">Flat 20% off on Total Bill &gt;</div>
                <div className="text-[#D84315] text-xs font-bold mt-1">with 1 Month at just ₹1</div>
              </div>
            )}
          </div>
        </div>

        {/* Divider */}
        <div className="my-6 flex items-center justify-center">
          <div className="h-px bg-gray-300 w-12"></div>
          <div className="text-gray-500 text-xs font-black tracking-[0.2em] px-4 uppercase">Useful Bits</div>
          <div className="h-px bg-gray-300 w-12"></div>
        </div>

        {/* Menu Section */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-black text-gray-900 mb-3">Menu</h2>
          <div className="flex gap-4 overflow-x-auto no-scrollbar pb-2">
            <div className="flex-shrink-0 w-[140px]">
              <div className="w-full aspect-[1/1.3] bg-[#FDF5E6] border border-[#E0C097] rounded-xl shadow-md p-2 relative overflow-hidden flex flex-col justify-between">
                <div className="text-center text-[8px] font-serif text-[#8B5A2B] border-b border-[#E0C097] pb-1">FRIED RICE & NOODLES</div>
                <div className="flex-1 opacity-40 flex flex-col gap-1 mt-2">
                   <div className="h-1 bg-[#8B5A2B] rounded w-full"></div>
                   <div className="h-1 bg-[#8B5A2B] rounded w-3/4"></div>
                   <div className="h-1 bg-[#8B5A2B] rounded w-5/6"></div>
                   <div className="h-1 bg-[#8B5A2B] rounded w-full mt-2"></div>
                </div>
              </div>
              <div className="text-center text-sm font-bold text-gray-800 mt-2">Food <span className="text-gray-400 font-normal text-xs">• 7 pages</span></div>
            </div>
            <div className="flex-shrink-0 w-[140px]">
              <div className="w-full aspect-[1/1.3] bg-[#FDF5E6] border border-[#E0C097] rounded-xl shadow-md p-2 relative overflow-hidden flex flex-col justify-between">
                <div className="text-center text-[8px] font-serif text-[#8B5A2B] border-b border-[#E0C097] pb-1">BEVERAGES</div>
                <div className="flex-1 opacity-40 flex flex-col gap-1 mt-2">
                   <div className="h-1 bg-[#8B5A2B] rounded w-3/4"></div>
                   <div className="h-1 bg-[#8B5A2B] rounded w-1/2"></div>
                </div>
              </div>
              <div className="text-center text-sm font-bold text-gray-800 mt-2">Beverage <span className="text-gray-400 font-normal text-xs">• 1 page</span></div>
            </div>
          </div>
        </div>

        {/* Photos Section */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-black text-gray-900 mb-3">Photos</h2>
          <div className="grid grid-cols-3 gap-2">
            <div className="col-span-2 row-span-2 rounded-xl overflow-hidden bg-gray-200">
              <img src="https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&q=80" alt="photo" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-xl overflow-hidden bg-gray-200 aspect-square">
              <img src="https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=200&q=80" alt="photo" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-xl overflow-hidden bg-gray-200 aspect-square">
              <img src="https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=200&q=80" alt="photo" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-xl overflow-hidden bg-gray-200 aspect-square">
              <img src="https://images.unsplash.com/photo-1544148103-0773bf10d330?w=200&q=80" alt="photo" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-xl overflow-hidden bg-gray-200 aspect-square">
              <img src="https://images.unsplash.com/photo-1590846406792-0adc7f928f1e?w=200&q=80" alt="photo" className="w-full h-full object-cover" />
            </div>
            <div className="rounded-xl overflow-hidden bg-gray-800 aspect-square relative">
              <img src="https://images.unsplash.com/photo-1600891964092-4316c288032e?w=200&q=80" alt="photo" className="w-full h-full object-cover opacity-50" />
              <div className="absolute inset-0 flex items-center justify-center text-white font-black text-lg">+1</div>
            </div>
          </div>
        </div>

        {/* Amenities Section */}
        <div className="px-4 mb-6">
          <h2 className="text-lg font-black text-gray-900 mb-3">Amenities (2)</h2>
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-3 text-sm text-gray-700 font-medium">
              <span className="text-gray-400">🅿️</span> Parking available
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-700 font-medium">
              <span className="text-gray-400">💳</span> SwiggyPay accepted
            </div>
          </div>
        </div>

        {/* Fixed Bottom Action Bar */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 p-4 pb-6 z-50 rounded-t-3xl shadow-[0_-10px_40px_rgba(0,0,0,0.05)]">
          <div className="bg-[#FFF7ED] border border-[#FFEDD5] rounded-xl p-2 mb-3 flex items-center justify-center gap-2">
            <span className="bg-[#FFD54F] text-[#5D4037] text-[10px] font-black px-1.5 py-0.5 rounded">2X</span>
            <span className="text-[#FC8019] text-xs font-bold">Earn 20% DineCash on bill payment ⓘ</span>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setShowBookingModal(true)} className="flex-1 bg-[#FFF0E6] text-[#E65100] font-black py-3.5 rounded-xl border border-[#FFCCBC]">
              Book a table
            </button>
            <button className="flex-1 bg-[#E65100] text-white font-black py-3.5 rounded-xl shadow-lg shadow-orange-500/30">
              Pay bill now
            </button>
          </div>
        </div>

        {/* Booking Modal Overlay */}
        {showBookingModal && (
          <div className="fixed inset-0 z-[400]">
            <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowBookingModal(false)} />
            <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-[24px] p-5">
              {bookingSuccess ? (
                <div className="text-center py-10">
                  <div className="text-5xl mb-4">✅</div>
                  <div className="text-xl font-black text-gray-900">Table Reserved!</div>
                  <div className="text-sm text-gray-500 mt-2">You'll receive a confirmation shortly</div>
                </div>
              ) : (
                <>
                  <div className="w-10 h-1.5 bg-gray-200 rounded-full mx-auto mb-4" />
                  <div className="text-xl font-black text-gray-900 mb-1">Book a Table</div>
                  <div className="text-sm text-gray-500 mb-4">{selectedVenue.restaurant_name || 'Restaurant'}</div>
                  
                  <div className="flex gap-3 mb-4">
                    <div className="flex-1">
                      <label className="text-xs font-bold text-gray-700 block mb-1">Date</label>
                      <input type="date" value={bookingForm.date} onChange={e => setBookingForm(p => ({...p, date: e.target.value}))} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:border-orange-500 font-medium" />
                    </div>
                    <div className="flex-1">
                      <label className="text-xs font-bold text-gray-700 block mb-1">Time</label>
                      <input type="time" value={bookingForm.time} onChange={e => setBookingForm(p => ({...p, time: e.target.value}))} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:border-orange-500 font-medium" />
                    </div>
                  </div>
                  
                  <label className="text-xs font-bold text-gray-700 block mb-1">Guests</label>
                  <div className="flex gap-2 mb-4 overflow-x-auto no-scrollbar pb-1">
                    {[1, 2, 3, 4, 5, 6, 8, 10].map(n => (
                      <button key={n} onClick={() => setBookingForm(p => ({ ...p, guest_count: n }))} className={`flex-shrink-0 w-11 h-11 rounded-xl font-black text-sm border ${bookingForm.guest_count === n ? 'border-orange-600 bg-orange-50 text-orange-600' : 'border-gray-200 bg-white text-gray-700'}`}>
                        {n}
                      </button>
                    ))}
                  </div>

                  <label className="text-xs font-bold text-gray-700 block mb-1">Special Requests</label>
                  <textarea value={bookingForm.special_requests} onChange={e => setBookingForm(p => ({...p, special_requests: e.target.value}))} placeholder="Any special requests..." rows={2} className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:border-orange-500 font-medium resize-none mb-6" />
                  
                  <button onClick={handleBook} className="w-full bg-[#E65100] text-white font-black py-4 rounded-xl shadow-lg shadow-orange-500/30 text-base">
                    Confirm Reservation 🎉
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  // --- DASHBOARD VIEW ---
  const renderDashboard = () => (
    <div className="bg-white min-h-screen pb-[100px]" style={{ fontFamily: font }}>
      {/* Top Search Bar */}
      <div className="p-4 flex gap-3 items-center sticky top-0 bg-white/90 backdrop-blur-md z-40">
        <div className="flex-1 bg-white border border-gray-200 rounded-xl flex items-center px-3 h-12 shadow-sm relative">
          <span className="text-gray-400 mr-2 text-lg">🔍</span>
          <input 
            value={searchQ}
            onChange={handleSearchChange}
            onFocus={() => searchQ.length >= 1 && setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
            placeholder="Search for restaurant, area, vib..." 
            className="bg-transparent border-none outline-none text-sm font-medium w-full text-gray-800 placeholder-gray-400"
          />
          {showDropdown && suggestions.length > 0 && (
            <div className="absolute top-[52px] left-0 right-0 bg-white rounded-xl shadow-lg border border-gray-100 z-50 overflow-hidden">
              {suggestions.map((sug, i) => (
                <div key={i} onClick={() => handleSuggestionClick(sug)} className="px-4 py-3 text-[13px] font-bold text-gray-800 border-b border-gray-50 cursor-pointer flex items-center gap-3">
                  <span className="text-gray-400">🔍</span> {sug}
                </div>
              ))}
            </div>
          )}
        </div>
        <button className="bg-[#0B4D3C] text-white h-12 px-4 rounded-xl flex flex-col items-center justify-center font-black leading-tight shadow-sm">
          <span className="text-[10px] text-green-300">₹</span>
          <span className="text-sm">₹0</span>
        </button>
      </div>

      {/* Featured Promo Carousel */}
      <div className="px-4 mb-8">
        <div className="flex gap-4 overflow-x-auto no-scrollbar pb-2 snap-x">
          <div 
            onClick={() => { if(venues.length > 0) setSelectedVenue(venues[0]) }}
            className="flex-shrink-0 w-[280px] h-[160px] bg-[#2E3B2C] rounded-[24px] relative overflow-hidden snap-start shadow-md cursor-pointer"
          >
            <div className="absolute right-0 top-0 bottom-0 w-1/2">
              <img src="https://images.unsplash.com/photo-1552566626-52f8b828add9?w=400&q=80" alt="promo" className="w-full h-full object-cover opacity-80" />
            </div>
            <div className="absolute inset-0 bg-gradient-to-r from-[#2E3B2C] via-[#2E3B2C]/90 to-transparent p-5 flex flex-col justify-center">
              <h2 className="text-white text-xl font-black leading-tight mb-1 w-2/3">Raaj Bhaavan Clarks Inn</h2>
              <div className="text-white/80 text-xs font-medium mb-4">Bask in flavours</div>
              <button className="bg-black/40 border border-white/20 text-white text-[10px] font-black px-3 py-1.5 rounded-full w-max tracking-wide">PREBOOK NOW</button>
            </div>
          </div>
          <div 
            onClick={() => { if(venues.length > 1) setSelectedVenue(venues[1]) }}
            className="flex-shrink-0 w-[280px] h-[160px] bg-[#1E293B] rounded-[24px] relative overflow-hidden snap-start shadow-md cursor-pointer"
          >
             <div className="absolute inset-0 p-5 flex flex-col justify-center">
              <h2 className="text-white text-xl font-black leading-tight mb-1">Call It A Day Restaurant</h2>
              <div className="text-white/80 text-xs font-medium mb-4">A cooler experience</div>
              <button className="bg-black/40 border border-white/20 text-white text-[10px] font-black px-3 py-1.5 rounded-full w-max tracking-wide">PREBOOK NOW</button>
            </div>
          </div>
          <div 
            onClick={() => { if(venues.length > 2) setSelectedVenue(venues[2]) }}
            className="flex-shrink-0 w-[280px] h-[160px] bg-[#662C21] rounded-[24px] relative overflow-hidden snap-start shadow-md cursor-pointer"
          >
             <div className="absolute right-0 top-0 bottom-0 w-1/2">
               <img src="https://images.unsplash.com/photo-1544148103-0773bf10d330?w=400&q=80" alt="promo" className="w-full h-full object-cover opacity-60 mix-blend-overlay" />
             </div>
             <div className="absolute inset-0 bg-gradient-to-r from-[#662C21] via-[#662C21]/90 to-transparent p-5 flex flex-col justify-center">
              <h2 className="text-white text-xl font-black leading-tight mb-1">The Gourmet Table</h2>
              <div className="text-white/80 text-xs font-medium mb-4">A romantic evening</div>
              <button className="bg-[#E65100] border border-orange-400 text-white text-[10px] font-black px-3 py-1.5 rounded-full w-max tracking-wide shadow-md">50% OFF TODAY</button>
            </div>
          </div>
          <div 
            onClick={() => { if(venues.length > 3) setSelectedVenue(venues[3]) }}
            className="flex-shrink-0 w-[280px] h-[160px] bg-[#6B4E0F] rounded-[24px] relative overflow-hidden snap-start shadow-md cursor-pointer"
          >
             <div className="absolute inset-0 p-5 flex flex-col justify-center">
              <h2 className="text-white text-xl font-black leading-tight mb-1">Spice Route</h2>
              <div className="text-white/80 text-xs font-medium mb-4">Authentic Flavors</div>
              <button className="bg-[#10B981] border border-green-400 text-white text-[10px] font-black px-3 py-1.5 rounded-full w-max tracking-wide shadow-md">EARN 3X DINECASH</button>
            </div>
          </div>
        </div>
      </div>

      {/* What's on your mind? */}
      <div className="px-4 mb-6">
        <h2 className="text-xl font-black text-gray-900 mb-4">What's on your mind?</h2>
        <div className="flex gap-3 mb-6">
          <div 
            onClick={() => {
              setFilterNearMe(!filterNearMe)
              document.getElementById('restaurants-section')?.scrollIntoView({ behavior: 'smooth' })
            }}
            className={`flex-1 ${filterNearMe ? 'bg-[#FFD54F]' : 'bg-[#FFF5EE]'} border ${filterNearMe ? 'border-[#FFC107]' : 'border-[#FDE0D0]'} rounded-[20px] p-3 flex items-center justify-between relative overflow-hidden shadow-sm h-[70px] cursor-pointer`}
          >
             <div className="text-sm font-black text-[#5D4037] w-2/3 leading-tight z-10">Restaurants near me</div>
             <span className="text-4xl absolute right-2 bottom-[-5px] z-0">📍</span>
          </div>
          <div 
            onClick={() => {
              setFilterOffers(!filterOffers)
              document.getElementById('restaurants-section')?.scrollIntoView({ behavior: 'smooth' })
            }}
            className={`flex-1 ${filterOffers ? 'bg-[#FFD54F]' : 'bg-[#FFF3E0]'} border ${filterOffers ? 'border-[#FFC107]' : 'border-[#FFE0B2]'} rounded-[20px] p-3 flex items-center justify-between relative overflow-hidden shadow-sm h-[70px] cursor-pointer`}
          >
             <div className="flex flex-col z-10">
               <span className="bg-[#E65100] text-white text-[8px] font-black px-1.5 py-0.5 rounded w-max mb-0.5">ONE</span>
               <div className="text-sm font-black text-[#5D4037] leading-tight">Pre-Book Offers</div>
             </div>
             <span className="text-4xl absolute right-1 bottom-0 z-0">⏳</span>
          </div>
        </div>

        {/* Categories Grid */}
        <div className="grid grid-cols-4 gap-3">
          {[
            { name: 'Cafes', image: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400&q=80' },
            { name: 'Nightlife & Drinks', image: 'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=400&q=80' },
            { name: 'Family Friendly', image: 'https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=400&q=80' },
            { name: 'Events & Experiences', image: 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=400&q=80' },
            { name: 'Rooftop Places', image: 'https://images.unsplash.com/photo-1572116469696-31de0f17cc34?w=400&q=80' },
            { name: 'Buffets', image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&q=80' },
            { name: 'Pure Veg', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80' },
            { name: 'Five-Star Dining', image: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&q=80' },
          ].map((c, i) => (
            <div key={i} onClick={() => {
              if (venues.length === 0) return;
              const match = venues.find(v => {
                const rName = (v.restaurant?.name || '').toLowerCase();
                const cName = c.name.toLowerCase();
                if (rName.includes(cName)) return true;
                const map = {
                  'cafes': 'cafe',
                  'nightlife & drinks': 'lounge',
                  'family friendly': 'happy times',
                  'events & experiences': 'illusionist',
                  'rooftop places': 'sky high',
                  'buffets': 'buffet',
                  'pure veg': 'veg',
                  'five-star dining': 'imperial'
                };
                return map[cName] && rName.includes(map[cName]);
              });
              if (match) {
                setSelectedVenue(match);
                window.scrollTo({ top: 0, behavior: 'smooth' });
              } else {
                alert(`Sorry, no restaurants found for ${c.name} at the moment.`);
              }
            }} className="flex flex-col items-center cursor-pointer">
              <div className="w-full aspect-[4/5] bg-gray-900 rounded-[20px] shadow-sm flex flex-col p-2 relative overflow-hidden transition-transform active:scale-95 hover:shadow-md">
                <img src={c.image} alt={c.name} className="absolute inset-0 w-full h-full object-cover opacity-80" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                <div className="text-[11px] font-black text-center text-white leading-tight z-10 absolute bottom-3 left-1 right-1">{c.name}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Venues List */}
      <div className="px-4" id="restaurants-section">
        <h2 className="text-xl font-black text-gray-900 mb-4">Restaurants near you</h2>
        <div className="flex flex-col gap-4">
          {venues.map(v => {
            const isClosed = v.restaurant_is_currently_open === false;
            return (
              <div 
                key={v.id} 
                onClick={() => setSelectedVenue(v)}
                className={`bg-white rounded-[20px] border border-gray-100 shadow-sm overflow-hidden flex flex-col ${isClosed ? 'opacity-70 grayscale-[30%]' : 'cursor-pointer'}`}
              >
                <div className="h-[160px] relative w-full">
                   <img src={v.restaurant?.cover_image || v.restaurant_image || 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&q=80'} className="w-full h-full object-cover" alt="rest" />
                   {isClosed && (
                     <div className="absolute inset-0 bg-black/60 flex items-center justify-center backdrop-blur-[2px]">
                       <span className="text-white text-lg font-black tracking-wider bg-black/50 px-3 py-1 rounded border border-white/20">CLOSED</span>
                     </div>
                   )}
                   <div className="absolute top-3 right-3 w-8 h-8 bg-white/90 backdrop-blur rounded-full flex items-center justify-center text-gray-400">♡</div>
                </div>
                <div className="p-4">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="text-base font-black text-gray-900 flex-1 truncate pr-2">{v.restaurant_name || v.restaurant?.name || 'Restaurant'}</h3>
                    <div className="bg-green-700 text-white text-[10px] font-bold px-1.5 py-0.5 rounded flex items-center gap-0.5">
                      {v.restaurant?.rating || '4.2'} ★
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 font-medium mb-2 truncate">
                    {v.restaurant?.categories?.map(c=>c.name).join(', ') || 'North Indian, South Indian'}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500 font-bold border-t border-gray-100 pt-3">
                    <span className="flex items-center gap-1">📍 {v.distance_km ? `${v.distance_km} km` : '2.5 km'}</span>
                    <span className="flex items-center gap-1">💰 ₹{v.avg_cost_for_two || 500} for two</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Removed Bottom Fixed Banner (Cashback) */}

      {/* Custom Dining Bottom Navigation */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, background: '#fff', borderTop: `1px solid #F0F0F5`, display: 'flex', justifyContent: 'space-around', padding: '10px 0 16px', zIndex: 100 }}>
        {[
          { id: 'hub', icon: '🏠', label: 'Hub' },
          { id: 'dining', icon: '🍽️', label: 'Dineout' },
          { id: 'reservations', icon: '🔖', label: 'Reservations' },
          { id: 'offers', icon: '🎟️', label: 'Offers' },
        ].map(t => (
          <button 
            key={t.id} 
            onClick={() => {
              if (t.id === 'hub') goHome()
              else setDiningTab(t.id)
            }} 
            style={{ background: 'none', border: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, cursor: 'pointer', padding: '4px 12px' }}
          >
            <span style={{ fontSize: 24, opacity: diningTab === t.id || t.id === 'hub' ? 1 : 0.5, filter: diningTab === t.id || t.id === 'hub' ? 'none' : 'grayscale(100%)' }}>{t.icon}</span>
            <span style={{ fontSize: 10, fontWeight: 800, color: diningTab === t.id ? '#FC8019' : '#02060C99', fontFamily: font }}>{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  )

  const renderReservations = () => (
    <div className="bg-white min-h-screen p-4 pb-[100px]" style={{ fontFamily: font }}>
      <h2 className="text-2xl font-black text-gray-900 mb-6">Your Reservations</h2>
      <div className="text-center py-20">
        <div className="text-5xl mb-4">🍽️</div>
        <div className="text-lg font-bold text-gray-900 mb-2">No upcoming reservations</div>
        <div className="text-sm text-gray-500">Book a table at your favorite restaurant now!</div>
        <button onClick={() => setDiningTab('dining')} className="mt-6 bg-[#FC8019] text-white px-6 py-3 rounded-xl font-bold">Explore Restaurants</button>
      </div>
    </div>
  )

  const renderOffers = () => (
    <div className="bg-white min-h-screen p-4 pb-[100px]" style={{ fontFamily: font }}>
      <h2 className="text-2xl font-black text-gray-900 mb-6">Dineout Offers</h2>
      <div className="bg-[#FFF7ED] rounded-[24px] p-6 text-center border border-[#FFEDD5]">
        <div className="text-4xl mb-4">🎉</div>
        <div className="text-xl font-black text-[#FC8019] mb-2">Flat 20% Off on total bill</div>
        <div className="text-sm text-gray-600 mb-6">Available at 500+ premium restaurants</div>
        <button onClick={() => setDiningTab('dining')} className="bg-[#FC8019] text-white px-6 py-3 rounded-xl font-bold shadow-md shadow-orange-500/30">View Participating Restaurants</button>
      </div>
    </div>
  )

  return (
    <>
      {diningTab === 'dining' && renderDashboard()}
      {diningTab === 'reservations' && renderReservations()}
      {diningTab === 'offers' && renderOffers()}
    </>
  )
}
