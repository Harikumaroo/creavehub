import api from './axiosInstance'

export const dashboardApi = {
  // Dashboard
  getHome:           ()        => api.get('/api/v1/dashboard/'),

  // Profile
  updateProfile:     (data)    => api.put('/api/profile/update/', data),

  // Restaurants & Menu
  getRestaurants:    ()        => api.get('/api/v1/restaurants/'),
  getRestaurant:     (id)      => api.get(`/api/v1/restaurants/${id}/`),
  getMenu:           (id)      => api.get(`/api/v1/restaurants/${id}/menu/`),
  searchMenu:        (q)       => api.get(`/api/v1/menu/search/?q=${encodeURIComponent(q)}`),
  filterMenu:        (p)       => api.get('/api/v1/menu/items/', { params: p }),
  getMenuItem:       (id)      => api.get(`/api/v1/menu/items/${id}/`),

  // Cart
  getCart:           ()        => api.get('/api/v1/cart/'),
  addToCart:         (data)    => api.post('/api/v1/cart/add/', data),
  updateCartItem:    (id, d)   => api.put(`/api/v1/cart/item/${id}/`, d),
  removeCartItem:    (id)      => api.delete(`/api/v1/cart/item/${id}/delete/`),
  clearCart:         ()        => api.delete('/api/v1/cart/clear/'),

  // Orders
  placeOrder:        (data)    => api.post('/api/v1/orders/place/', data),
  getOrders:         ()        => api.get('/api/v1/orders/'),
  getOrder:          (id)      => api.get(`/api/v1/orders/${id}/`),
  cancelOrder:       (id, d)   => api.post(`/api/v1/orders/${id}/cancel/`, d),

  // Payments (Razorpay)
  initiatePayment:   (data)    => api.post('/api/v1/payments/initiate/', data),
  verifyPayment:     (data)    => api.post('/api/v1/payments/verify/', data),
  getPaymentHistory: ()        => api.get('/api/v1/payments/history/'),

  // Tracking
  getTracking:       (id)      => api.get(`/api/v1/tracking/orders/${id}/`),

  // Notifications
  getNotifications:  ()        => api.get('/api/v1/notifications/'),
  markAllRead:       ()        => api.post('/api/v1/notifications/mark-all-read/'),

  // Search
  search:            (q, lat, lng) => api.get(`/api/v1/search/`, { params: { q, lat, lng } }),
  getSuggestions:    (q)       => api.get(`/api/v1/search/suggestions/?q=${encodeURIComponent(q)}`),

  // AI — Full Groq Integration
  getRecommendations:    ()        => api.get('/api/v1/ai/recommendations/?context=home'),
  sendChatMessage:       (data)    => api.post('/api/v1/ai/chat/', data),
  sendAgentMessage:      (data)    => api.post('/api/v1/ai/agent/', data),
  getMoodFood:           (mood)    => api.get(`/api/v1/ai/mood/?mood=${encodeURIComponent(mood)}`),
  smartSearch:           (data)    => api.post('/api/v1/ai/smart-search/', data),
  getReorderPredictions: ()        => api.get('/api/v1/ai/reorder/'),
  generateCombo:         (data)    => api.post('/api/v1/ai/combo/', data),
  getPersonalizedOffer:  ()        => api.get('/api/v1/ai/offer/'),
  getNutritionInfo:      (item)    => api.get(`/api/v1/ai/nutrition/?item=${encodeURIComponent(item)}`),
  getWeatherFood:        (lat, lng)=> api.get('/api/v1/ai/weather-food/', { params: { lat, lng } }),

  // Instamart
  getInstamart:      ()        => api.get('/api/v1/instamart/'),
  getStoreProducts:  (id, p)   => api.get(`/api/v1/instamart/stores/${id}/products/`, { params: p }),
  getInstamartOrders:()        => api.get('/api/v1/instamart/orders/'),
  placeInstamartOrder:(data)   => api.post('/api/v1/instamart/orders/place/', data),
  getInstamartCart:  ()        => api.get('/api/v1/instamart/cart/'),
  addInstamartToCart: (data)   => api.post('/api/v1/instamart/cart/add/', data),
  updateInstamartCartItem: (id, d) => api.put(`/api/v1/instamart/cart/item/${id}/`, d),
  removeInstamartCartItem: (id) => api.delete(`/api/v1/instamart/cart/item/${id}/delete/`),
  clearInstamartCart: ()       => api.delete('/api/v1/instamart/cart/clear/'),
  searchInstamartProducts: (q) => api.get(`/api/v1/instamart/search/?q=${encodeURIComponent(q)}`),

  // Dining
  getDiningVenues:   (p)       => api.get('/api/v1/dining/venues/', { params: p }),
  getDiningVenue:    (id)      => api.get(`/api/v1/dining/venues/${id}/`),
  createReservation: (data)    => api.post('/api/v1/dining/reservations/', data),
  getMyReservations: ()        => api.get('/api/v1/dining/my-reservations/'),

  // Gifts
  getGiftCards:      ()        => api.get('/api/v1/gifts/cards/'),
  sendGift:          (data)    => api.post('/api/v1/gifts/send/', data),

  // Party Orders
  getPartyPackages:  ()        => api.get('/api/v1/parties/packages/'),
  createPartyBooking:(data)    => api.post('/api/v1/parties/bookings/', data),
  getMyPartyBookings:()        => api.get('/api/v1/parties/my-bookings/'),

  // Catering
  getCateringMenus:  ()        => api.get('/api/v1/catering/menus/'),
  createCateringInquiry:(data) => api.post('/api/v1/catering/inquiries/', data),

  // Reviews
  createReview:      (id, d)   => api.post(`/api/v1/reviews/restaurants/${id}/`, d),

  // Offers
  getOffers:         ()        => api.get('/api/v1/offers/'),
}

