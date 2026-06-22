import { createContext, useContext, useReducer, useEffect } from 'react'
import { TOKEN_KEYS } from '../constants'

const AuthCtx = createContext(null)

const init = { user: null, accessToken: null, refreshToken: null, isAuthenticated: false, loading: true }

function reducer(state, { type, payload }) {
  switch (type) {
    case 'HYDRATE':
    case 'LOGIN':
      return { ...state, ...payload, isAuthenticated: true, loading: false }
    case 'LOGOUT':
      return { ...init, loading: false }
    case 'UPDATE_USER':
      return { ...state, user: { ...state.user, ...payload } }
    case 'READY':
      return { ...state, loading: false }
    default:
      return state
  }
}

export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, init)

  /* Rehydrate from localStorage on mount */
  useEffect(() => {
    const access  = localStorage.getItem(TOKEN_KEYS.ACCESS)
    const refresh = localStorage.getItem(TOKEN_KEYS.REFRESH)
    const raw     = localStorage.getItem(TOKEN_KEYS.USER)
    if (access && refresh && raw) {
      try {
        dispatch({ type: 'HYDRATE', payload: { accessToken: access, refreshToken: refresh, user: JSON.parse(raw) } })
      } catch { dispatch({ type: 'READY' }) }
    } else {
      dispatch({ type: 'READY' })
    }
  }, [])

  const login = (data) => {
    /* data shape from backend: { access_token, refresh_token, user: {...} } */
    localStorage.setItem(TOKEN_KEYS.ACCESS,  data.access_token)
    localStorage.setItem(TOKEN_KEYS.REFRESH, data.refresh_token)
    localStorage.setItem(TOKEN_KEYS.USER,    JSON.stringify(data.user))
    dispatch({ type: 'LOGIN', payload: { accessToken: data.access_token, refreshToken: data.refresh_token, user: data.user } })
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEYS.ACCESS)
    localStorage.removeItem(TOKEN_KEYS.REFRESH)
    localStorage.removeItem(TOKEN_KEYS.USER)
    dispatch({ type: 'LOGOUT' })
  }

  const updateUser = (fields) => {
    const updated = { ...state.user, ...fields }
    localStorage.setItem(TOKEN_KEYS.USER, JSON.stringify(updated))
    dispatch({ type: 'UPDATE_USER', payload: fields })
  }

  return (
    <AuthCtx.Provider value={{ ...state, login, logout, updateUser }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuthCtx = () => {
  const ctx = useContext(AuthCtx)
  if (!ctx) throw new Error('useAuthCtx must be inside <AuthProvider>')
  return ctx
}
