import React, { useState, useCallback, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { profileApi } from '../api/profileApi';

const font = "'Proxima Nova', 'Inter', system-ui, sans-serif";
const C = {
  saffron: '#FC8019', charcoal: '#02060C', muted: '#02060C99',
  border: '#F0F0F5', cardBg: '#FFFFFF', warm: '#FFFFFF', sand: '#F0F0F5',
  green: '#2E8B57', red: '#D94F2B', maroon: '#6B0B22'
};

const defaultCenter = [13.0827, 80.2707]; // Chennai default

const BLANK_FORM = {
  label: 'Home',
  flat_no: '',
  building_name: '',
  street: '',
  landmark: '',
  city: '',
  state: '',
  pincode: '',
  full_address: '',
  latitude: null,
  longitude: null
};

/* ── Fixed Center Pin Map Event Listener ── */
function MapEventsHandler({ onMoveEnd }) {
  const map = useMapEvents({
    moveend() {
      const center = map.getCenter();
      onMoveEnd(center.lat, center.lng);
    }
  });

  // Try to locate user on mount
  useEffect(() => {
    map.locate().on('locationfound', function (e) {
      map.flyTo(e.latlng, map.getZoom());
    });
  }, [map]);

  return null;
}

export default function LocationDrawer({ open, onClose, onSelectAddress }) {
  const [view, setView] = useState('LIST');
  const [loading, setLoading] = useState(false);
  const [geocoding, setGeocoding] = useState(false);
  const [addresses, setAddresses] = useState([]);
  const [fetchError, setFetchError] = useState(null);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  const [markerPosition, setMarkerPosition] = useState(defaultCenter);
  const [formData, setFormData] = useState(BLANK_FORM);

  useEffect(() => {
    if (open && view === 'LIST') {
      setFetchError(null);
      profileApi.getAddresses()
        .then(r => {
          const data = r.data?.data || r.data?.results || r.data || [];
          setAddresses(Array.isArray(data) ? data : []);
        })
        .catch(e => {
          console.error('Fetch addresses error:', e);
          setFetchError('Could not load addresses. Please try again.');
        });
    }
  }, [open, view]);

  // Reverse Geocoding via Nominatim
  const performGeocoding = async (lat, lng) => {
    setGeocoding(true);
    setMarkerPosition([lat, lng]);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
      );
      const data = await response.json();

      setFormData(prev => ({
        ...prev,
        full_address: data.display_name || '',
        street: data.address?.road || data.address?.suburb || '',
        city: data.address?.city || data.address?.town || data.address?.village || data.address?.county || '',
        state: data.address?.state || '',
        pincode: data.address?.postcode || '',
        latitude: parseFloat(lat.toFixed(7)),
        longitude: parseFloat(lng.toFixed(7))
      }));
    } catch (error) {
      console.error('Reverse geocoding error:', error);
    } finally {
      setGeocoding(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaveError(null);
    setSaveSuccess(false);
    setLoading(true);
    try {
      const res = await profileApi.addAddress(formData);
      if (res.status === 201 || res.status === 200) {
        setSaveSuccess(true);
        setFormData(BLANK_FORM);
        setTimeout(() => {
          setSaveSuccess(false);
          setView('LIST');
        }, 1000);
      } else {
        setSaveError('Unexpected response. Please try again.');
      }
    } catch (err) {
      console.error('Save address error:', err);
      const resData = err?.response?.data;
      if (resData && resData.success === false) {
        if (resData.errors && typeof resData.errors === 'object' && Object.keys(resData.errors).length > 0) {
          const firstKey = Object.keys(resData.errors)[0];
          setSaveError(`${firstKey}: ${resData.errors[firstKey]}`);
        } else {
          setSaveError(resData.message || 'Failed to save address.');
        }
      } else if (resData && typeof resData === 'object') {
        const firstKey = Object.keys(resData)[0];
        setSaveError(`${firstKey}: ${resData[firstKey]}`);
      } else {
        setSaveError('Failed to save address. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const goToAdd = () => {
    setSaveError(null);
    setSaveSuccess(false);
    setFormData(BLANK_FORM);
    setView('ADD');
  };

  if (!open) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 400 }}>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{ position: 'absolute', inset: 0, background: 'rgba(2,6,12,0.55)', backdropFilter: 'blur(3px)' }}
      />

      {/* Sheet */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0,
        maxWidth: 600, margin: '0 auto',
        background: C.cardBg, borderRadius: '24px 24px 0 0',
        maxHeight: '95vh', display: 'flex', flexDirection: 'column',
        boxShadow: '0 -8px 40px rgba(0,0,0,0.18)'
      }}>
        {/* Handle */}
        <div style={{ padding: '12px 0 0', display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: 40, height: 4, borderRadius: 99, background: C.border }} />
        </div>

        {/* Header */}
        <div style={{
          padding: '14px 20px 14px', borderBottom: `1px solid ${C.border}`,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {view === 'ADD' && (
              <button
                onClick={() => setView('LIST')}
                style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', padding: 0, lineHeight: 1 }}
              >←</button>
            )}
            <div style={{ fontSize: 17, fontWeight: 900, color: C.charcoal, fontFamily: font }}>
              {view === 'LIST' ? '📍 Select Location' : '➕ Add New Address'}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: C.sand, border: `1px solid ${C.border}`, borderRadius: 10,
              width: 32, height: 32, cursor: 'pointer', fontSize: 14,
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800
            }}
          >✕</button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }}>

          {/* ── LIST VIEW ── */}
          {view === 'LIST' && (
            <>
              {fetchError && (
                <div style={{ background: '#FFF0EE', border: '1px solid #F5C0B8', borderRadius: 12, padding: '12px 16px', color: C.red, fontFamily: font, fontSize: 13, marginBottom: 16 }}>
                  ⚠️ {fetchError}
                </div>
              )}

              {addresses.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 0, marginBottom: 20 }}>
                  {addresses.map((a, i) => (
                    <div
                      key={a.id}
                      onClick={() => { onSelectAddress(a); }}
                      style={{
                        display: 'flex', alignItems: 'flex-start', gap: 14,
                        padding: '16px 4px', cursor: 'pointer',
                        borderBottom: i < addresses.length - 1 ? `1px solid ${C.border}` : 'none',
                      }}
                    >
                      <div style={{
                        width: 38, height: 38, borderRadius: 12, flexShrink: 0,
                        background: `${C.saffron}18`, display: 'flex',
                        alignItems: 'center', justifyContent: 'center', fontSize: 18
                      }}>
                        {a.label?.toLowerCase().includes('work') ? '🏢' : a.label?.toLowerCase().includes('other') ? '📌' : '🏠'}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>
                          {a.label}
                          {a.is_default && (
                            <span style={{ marginLeft: 8, fontSize: 10, background: `${C.saffron}20`, color: C.saffron, borderRadius: 6, padding: '2px 7px', fontWeight: 700 }}>DEFAULT</span>
                          )}
                        </div>
                        <div style={{ fontSize: 12, color: C.muted, fontFamily: font, marginTop: 3, lineHeight: 1.5 }}>
                          {a.full_address || [a.flat_no, a.building_name, a.street, a.city, a.state, a.pincode].filter(Boolean).join(', ')}
                        </div>
                      </div>
                      <span style={{ color: C.muted, fontSize: 18, alignSelf: 'center' }}>›</span>
                    </div>
                  ))}
                </div>
              ) : !fetchError ? (
                <div style={{ textAlign: 'center', padding: '40px 0 24px', fontFamily: font }}>
                  <div style={{ fontSize: 40, marginBottom: 10 }}>🗺️</div>
                  <div style={{ fontSize: 15, fontWeight: 700, color: C.charcoal }}>No saved addresses</div>
                  <div style={{ fontSize: 13, color: C.muted, marginTop: 6 }}>Add your first delivery address below</div>
                </div>
              ) : null}

              <button
                onClick={goToAdd}
                style={{
                  width: '100%', background: `${C.saffron}12`,
                  border: `1.5px dashed ${C.saffron}`, borderRadius: 16,
                  padding: '16px', color: C.saffron, fontSize: 14, fontWeight: 800,
                  cursor: 'pointer', fontFamily: font,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8
                }}
              >
                <span style={{ fontSize: 20 }}>+</span> Add New Address
              </button>
            </>
          )}

          {/* ── ADD VIEW ── */}
          {view === 'ADD' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>

              {/* Swiggy-Style Map with Fixed Center Pin */}
              <div style={{ position: 'relative', borderRadius: '16px 16px 0 0', overflow: 'hidden', height: 260, border: `1px solid ${C.border}`, borderBottom: 'none' }}>
                <MapContainer
                  center={markerPosition}
                  zoom={16}
                  style={{ width: '100%', height: '100%' }}
                  zoomControl={false}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  />
                  <MapEventsHandler onMoveEnd={performGeocoding} />
                </MapContainer>
                
                {/* Fixed Center Pin */}
                <div style={{
                  position: 'absolute', top: '50%', left: '50%',
                  transform: 'translate(-50%, -100%)', zIndex: 400,
                  fontSize: 40, pointerEvents: 'none', filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))'
                }}>
                  📍
                </div>

                {geocoding && (
                  <div style={{
                    position: 'absolute', top: 12, left: '50%', transform: 'translateX(-50%)',
                    background: '#fff', padding: '6px 16px', borderRadius: 20, zIndex: 400,
                    fontSize: 12, fontWeight: 700, fontFamily: font, boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    display: 'flex', alignItems: 'center', gap: 6, color: C.saffron
                  }}>
                    <div className="spinner" style={{ width: 12, height: 12, border: `2px solid ${C.saffron}`, borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                    Fetching address...
                  </div>
                )}
              </div>

              {/* Selected Location Display */}
              <div style={{ background: '#FFF7F0', border: `1px solid ${C.saffron}30`, borderRadius: '0 0 16px 16px', padding: '16px', marginBottom: 20 }}>
                <div style={{ fontSize: 13, fontWeight: 800, color: C.saffron, fontFamily: font, marginBottom: 4 }}>SELECTED LOCATION</div>
                <div style={{ fontSize: 14, color: C.charcoal, fontFamily: font, lineHeight: 1.5, fontWeight: 600 }}>
                  {formData.full_address || 'Move map to select location...'}
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {/* Label picker */}
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: C.muted, fontFamily: font, marginBottom: 8 }}>SAVE ADDRESS AS</div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    {['Home', 'Work', 'Other'].map(label => (
                      <button
                        key={label}
                        type="button"
                        onClick={() => setFormData(f => ({ ...f, label: label }))}
                        style={{
                          padding: '8px 16px', borderRadius: 20, border: `1.5px solid`,
                          borderColor: formData.label === label ? C.saffron : C.border,
                          background: formData.label === label ? `${C.saffron}15` : C.warm,
                          color: formData.label === label ? C.saffron : C.muted,
                          fontFamily: font, fontSize: 13, fontWeight: 700, cursor: 'pointer'
                        }}
                      >
                        {label === 'Home' ? '🏠' : label === 'Work' ? '🏢' : '📌'} {label}
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <input
                    required
                    placeholder="Flat / House No. *"
                    value={formData.flat_no}
                    onChange={e => setFormData(f => ({ ...f, flat_no: e.target.value }))}
                    style={inputStyle}
                  />
                  <input
                    placeholder="Building Name / Apartment"
                    value={formData.building_name}
                    onChange={e => setFormData(f => ({ ...f, building_name: e.target.value }))}
                    style={inputStyle}
                  />
                  <input
                    placeholder="Street / Area / Colony"
                    value={formData.street}
                    onChange={e => setFormData(f => ({ ...f, street: e.target.value }))}
                    style={inputStyle}
                  />
                  <input
                    placeholder="Landmark (Optional)"
                    value={formData.landmark}
                    onChange={e => setFormData(f => ({ ...f, landmark: e.target.value }))}
                    style={inputStyle}
                  />
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                    <input
                      required
                      placeholder="City *"
                      value={formData.city}
                      onChange={e => setFormData(f => ({ ...f, city: e.target.value }))}
                      style={inputStyle}
                    />
                    <input
                      required
                      placeholder="State *"
                      value={formData.state}
                      onChange={e => setFormData(f => ({ ...f, state: e.target.value }))}
                      style={inputStyle}
                    />
                  </div>
                  <input
                    required
                    placeholder="Pincode *"
                    value={formData.pincode}
                    onChange={e => setFormData(f => ({ ...f, pincode: e.target.value }))}
                    style={{ ...inputStyle, width: '50%' }}
                  />
                </div>

                {/* Error & Success */}
                {saveError && (
                  <div style={{ background: '#FFF0EE', border: '1px solid #F5C0B8', borderRadius: 12, padding: '12px 16px', color: C.red, fontFamily: font, fontSize: 13 }}>
                    ❌ {saveError}
                  </div>
                )}
                {saveSuccess && (
                  <div style={{ background: '#F0FFF6', border: '1px solid #A7F3D0', borderRadius: 12, padding: '12px 16px', color: C.green, fontFamily: font, fontSize: 13, fontWeight: 700 }}>
                    ✅ Address saved successfully!
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || geocoding || !formData.full_address}
                  style={{
                    background: (loading || geocoding || !formData.full_address) ? '#ccc' : C.saffron,
                    color: '#fff', border: 'none', borderRadius: 14,
                    padding: '16px', fontSize: 15, fontWeight: 900,
                    cursor: (loading || geocoding || !formData.full_address) ? 'not-allowed' : 'pointer',
                    fontFamily: font, marginTop: 4,
                    transition: 'background 0.2s'
                  }}
                >
                  {loading ? '⏳ Saving...' : '💾 Save Address'}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
      
      {/* CSS for Spinner */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

const inputStyle = {
  background: '#FAFAFA',
  border: '1.5px solid #E8EDF2',
  borderRadius: 12,
  padding: '14px 16px',
  fontSize: 14,
  fontFamily: "'Proxima Nova', 'Inter', system-ui, sans-serif",
  outline: 'none',
  width: '100%',
  boxSizing: 'border-box',
  color: '#02060C'
};
