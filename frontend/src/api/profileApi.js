import api from './axiosInstance'

export const profileApi = {
  getAddresses: () => api.get('/api/addresses/'),
  addAddress: (data) => api.post('/api/addresses/', data),
  updateAddress: (id, data) => api.patch(`/api/addresses/${id}/`, data),
  deleteAddress: (id) => api.delete(`/api/addresses/${id}/`),

  // Payment Methods
  getPaymentMethods: () => api.get('/api/v1/payments/saved-methods/'),
  addPaymentMethod: (data) => api.post('/api/v1/payments/saved-methods/', data),
  deletePaymentMethod: (id) => api.delete(`/api/v1/payments/saved-methods/${id}/`),

  // Favorites (Restaurants)
  getFavorites: () => api.get('/api/v1/restaurants/favorites/'),
  addFavorite: (data) => api.post('/api/v1/restaurants/favorites/', data),
  deleteFavorite: (id) => api.delete(`/api/v1/restaurants/favorites/${id}/`),

  // Favorites (Items)
  getFavoriteItems: () => api.get('/api/v1/favorites/'),
  addFavoriteItem: (data) => api.post('/api/v1/favorites/', data),
  deleteFavoriteItem: (id) => api.delete(`/api/v1/favorites/${id}/`),

  // Offers
  getSavedOffers: () => api.get('/api/v1/offers/saved/'),

  // Settings
  getSettings: () => api.get('/api/settings/'),
  updateSettings: (data) => api.patch('/api/settings/', data),

  // Support
  getTickets: () => api.get('/api/v1/support/tickets/'),
  createTicket: (data) => api.post('/api/v1/support/tickets/', data),
  addTicketMessage: (id, data) => api.post(`/api/v1/support/tickets/${id}/add_message/`, data),
}
