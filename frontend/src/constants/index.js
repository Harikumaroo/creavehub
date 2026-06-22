export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ENDPOINTS = {
  REGISTER_MOBILE:   '/api/register/mobile/',
  REGISTER_VERIFY:   '/api/register/verify-otp/',
  REGISTER_COMPLETE: '/api/register/complete/',
  LOGIN_MOBILE:      '/api/login/mobile/',
  LOGIN_VERIFY:      '/api/login/verify-otp/',
  LOGOUT:            '/api/logout/',
  TOKEN_REFRESH:     '/api/token/refresh/',
  PROFILE:           '/api/profile/',
  PROFILE_UPDATE:    '/api/profile/update/',
  DEVICES:           '/api/devices/',
  DEVICE_LOGOUT:     '/api/devices/logout/',
  DEVICE_LOGOUT_ALL: '/api/devices/logout-all/',

  /* Phase 2 */
  DASHBOARD:      '/api/v1/dashboard/',
  RESTAURANTS:    '/api/v1/restaurants/',
  MENU:           '/api/v1/menu/',
  CART:           '/api/v1/cart/',

  /* Phase 3 */
  ORDERS:         '/api/v1/orders/',
  PAYMENTS:       '/api/v1/payments/',
  REVIEWS:        '/api/v1/reviews/',

  /* Phase 4 */
  NOTIFICATIONS:  '/api/v1/notifications/',
  SEARCH:         '/api/v1/search/',
  AI:             '/api/v1/ai/',
  INSTAMART:      '/api/v1/instamart/',
  TRACKING:       '/api/v1/tracking/',
}

export const TOKEN_KEYS = {
  ACCESS:  'ch_access',
  REFRESH: 'ch_refresh',
  USER:    'ch_user',
}

export const COUNTRY_CODES = [
  { code: '+91',  flag: '🇮🇳', name: 'India',      maxLen: 10 },
  { code: '+1',   flag: '🇺🇸', name: 'USA',         maxLen: 10 },
  { code: '+44',  flag: '🇬🇧', name: 'UK',          maxLen: 10 },
  { code: '+971', flag: '🇦🇪', name: 'UAE',         maxLen: 9  },
  { code: '+65',  flag: '🇸🇬', name: 'Singapore',  maxLen: 8  },
  { code: '+61',  flag: '🇦🇺', name: 'Australia',  maxLen: 9  },
]

export const OTP_LENGTH         = 6
export const OTP_RESEND_SECONDS = 30

export const FOOD_EMOJIS = ['🍕','🍣','🍜','🍔','🥗','🍛','🌮','🍦','🍰','🥩','🍱','🌯','🥙','🍝','🧆','🥘']

/* CraveHub design tokens (mirrors Dashboard C object for use outside JSX) */
export const COLORS = {
  saffron: '#E8621A',
  amber:   '#F5A623',
  tomato:  '#D94F2B',
  cream:   '#FDF6EE',
  warm:    '#FFF8F2',
  charcoal:'#1C1410',
  bark:    '#3D2B1F',
  mocha:   '#7C4D2F',
  sand:    '#F0E0CC',
  sage:    '#5C7A4E',
  bg:      '#FAF3EC',
  border:  '#F0E4D4',
  muted:   '#9B7B60',
}
