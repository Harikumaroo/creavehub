import api from './axiosInstance'

export const supportApi = {
  // FAQs
  getFAQCategories: () => api.get('/api/v1/support/faq-categories/'),
  getFAQs: () => api.get('/api/v1/support/faqs/'),

  // Tickets
  getTickets: () => api.get('/api/v1/support/tickets/'),
  getTicket: (id) => api.get(`/api/v1/support/tickets/${id}/`),
  createTicket: (data) => api.post('/api/v1/support/tickets/', data),
  addTicketMessage: (id, data) => api.post(`/api/v1/support/tickets/${id}/add_message/`, data),

  // Refunds
  getRefunds: () => api.get('/api/v1/support/refunds/'),
}
