const DEVICE_ID_KEY = 'ch_device_id'

const genId = () =>
  'xxxxxxxx-xxxx-4xxx-yxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })

export const getDeviceId = () => {
  let id = localStorage.getItem(DEVICE_ID_KEY)
  if (!id) { id = genId(); localStorage.setItem(DEVICE_ID_KEY, id) }
  return id
}

export const getDeviceType = () => {
  const ua = navigator.userAgent.toLowerCase()
  if (/iphone|android.*mobile|windows phone/.test(ua)) return 'mobile'
  if (/ipad|android(?!.*mobile)|tablet/.test(ua))      return 'tablet'
  return 'web'
}

export const getDeviceName = () => {
  const ua = navigator.userAgent
  if (/iPhone/.test(ua))       return 'iPhone'
  if (/iPad/.test(ua))         return 'iPad'
  if (/Android/.test(ua))      return 'Android Device'
  if (/Windows NT/.test(ua))   return 'Windows'
  if (/Macintosh/.test(ua))    return 'Mac'
  if (/Linux/.test(ua))        return 'Linux'
  return 'Web Browser'
}

export const getDeviceInfo = () => ({
  device_id:   getDeviceId(),
  device_type: getDeviceType(),
  device_name: getDeviceName(),
})
