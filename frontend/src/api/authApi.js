import api from './axiosInstance'
import { ENDPOINTS } from '../constants'

export const authApi = {
  /* ── Registration (3 steps) ── */
  registerMobile:   (mobile_number) =>
    api.post(ENDPOINTS.REGISTER_MOBILE, { mobile_number }),

  registerVerifyOtp: (mobile_number, otp) =>
    api.post(ENDPOINTS.REGISTER_VERIFY, { mobile_number, otp }),

  registerComplete: (payload) =>
    /* payload: { mobile_number, full_name, email?, device_id, device_type, device_name } */
    api.post(ENDPOINTS.REGISTER_COMPLETE, payload),

  /* ── Login (2 steps) ── */
  loginMobile:    (mobile_number) =>
    api.post(ENDPOINTS.LOGIN_MOBILE, { mobile_number }),

  loginVerifyOtp: (payload) =>
    /* payload: { mobile_number, otp, device_id, device_type, device_name } */
    api.post(ENDPOINTS.LOGIN_VERIFY, payload),

  /* ── Session ── */
  logout:          (refresh_token) =>
    api.post(ENDPOINTS.LOGOUT, { refresh_token }),

  refreshToken:    (refresh) =>
    api.post(ENDPOINTS.TOKEN_REFRESH, { refresh }),

  /* ── Profile ── */
  getProfile:      () => api.get(ENDPOINTS.PROFILE),
  updateProfile:   (payload) => api.put(ENDPOINTS.PROFILE_UPDATE, payload),

  /* ── Devices ── */
  getDevices:      () => api.get(ENDPOINTS.DEVICES),
  logoutDevice:    (session_id) => api.post(ENDPOINTS.DEVICE_LOGOUT, { session_id }),
  logoutAllDevices:() => api.post(ENDPOINTS.DEVICE_LOGOUT_ALL),
}
