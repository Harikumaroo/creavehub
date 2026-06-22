import React, { createContext, useContext, useEffect, useState } from 'react';
import { profileApi } from '../api/profileApi';
import { useAuthCtx } from '../store/authStore';

const SettingsContext = createContext();

export const SettingsProvider = ({ children }) => {
  const { isAuthenticated, loading } = useAuthCtx();
  const [settings, setSettings] = useState({
    dark_mode: false,
    language: 'en',
    push_notifications: false,
    email_notifications: false,
    sms_notifications: false,
    whatsapp_notifications: false,
  });

  // Fetch settings only after user is authenticated
  useEffect(() => {
    // Don't fetch if still loading auth state or user not authenticated
    if (loading || !isAuthenticated) return;

    const fetchSettings = async () => {
      try {
        const res = await profileApi.getSettings();
        if (res.data) {
          setSettings(res.data);
        }
      } catch (err) {
        // Failed to fetch settings, use defaults
        console.error('Failed to fetch settings:', err);
      }
    };
    
    fetchSettings();
  }, [isAuthenticated, loading]);

  // Update HTML class for dark mode
  useEffect(() => {
    if (settings.dark_mode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [settings.dark_mode]);

  // Dictionary for translations
  const dict = {
    en: {
      'Good Evening': 'Good Evening',
      'What are you craving today?': 'What are you craving today?',
      'Search food, restaurants, groceries, cuisines...': 'Search food, restaurants, groceries, cuisines...',
      'My Orders': 'My Orders',
      'Saved Addresses': 'Saved Addresses',
      'Payment Methods': 'Payment Methods',
      'Favourites': 'Favourites',
      'Offers & Coupons': 'Offers & Coupons',
      'Settings': 'Settings',
      'Help & Support': 'Help & Support',
    },
    hi: {
      'Good Evening': 'शुभ संध्या',
      'What are you craving today?': 'आज आप क्या खाना चाहते हैं?',
      'Search food, restaurants, groceries, cuisines...': 'भोजन, रेस्तरां, किराना, व्यंजन खोजें...',
      'My Orders': 'मेरे आदेश',
      'Saved Addresses': 'सहेजे गए पते',
      'Payment Methods': 'भुगतान की विधि',
      'Favourites': 'पसंदीदा',
      'Offers & Coupons': 'ऑफर और कूपन',
      'Settings': 'समायोजन',
      'Help & Support': 'मदद और समर्थन',
    },
    te: {
      'Good Evening': 'శుభ సాయంత్రం',
      'What are you craving today?': 'ఈరోజు మీరు ఏమి తినాలనుకుంటున్నారు?',
      'Search food, restaurants, groceries, cuisines...': 'ఆహారం, రెస్టారెంట్లు, కిరాణా, వంటకాలు శోధించండి...',
      'My Orders': 'నా ఆర్డర్లు',
      'Saved Addresses': 'సేవ్ చేసిన చిరునామాలు',
      'Payment Methods': 'చెల్లింపు పద్ధతులు',
      'Favourites': 'ఇష్టమైనవి',
      'Offers & Coupons': 'ఆఫర్లు & కూపన్లు',
      'Settings': 'సెట్టింగులు',
      'Help & Support': 'సహాయం & మద్దతు',
    },
    es: {
      'Good Evening': 'Buenas tardes',
      'What are you craving today?': '¿Qué se te antoja hoy?',
      'Search food, restaurants, groceries, cuisines...': 'Buscar comida, restaurantes, supermercados...',
      'My Orders': 'Mis pedidos',
      'Saved Addresses': 'Direcciones guardadas',
      'Payment Methods': 'Métodos de pago',
      'Favourites': 'Favoritos',
      'Offers & Coupons': 'Ofertas y Cupones',
      'Settings': 'Ajustes',
      'Help & Support': 'Ayuda y Soporte',
    }
  };

  const t = (text) => {
    const lang = settings.language || 'en';
    if (dict[lang] && dict[lang][text]) {
      return dict[lang][text];
    }
    return text; // fallback to english/default
  };

  // Dynamic Theme Colors
  // We use this to replace `const C = {...}` in CraveHubDashboard
  const C = {
    saffron: '#FC8019',
    amber: '#FF9E2A',
    tomato: '#E25E1A',
    cream: settings.dark_mode ? '#1A1A1A' : '#FDF6EE',
    warm: settings.dark_mode ? '#2A2A2A' : '#FFFFFF',
    charcoal: settings.dark_mode ? '#FFFFFF' : '#02060C',
    bark: settings.dark_mode ? '#E0E0E0' : '#02060C99',
    mocha: settings.dark_mode ? '#FFFFFF' : '#02060CEB',
    sand: settings.dark_mode ? '#333333' : '#F0F0F5',
    sage: '#118C4F',
    muted: settings.dark_mode ? '#999999' : '#02060C99',
    bg: settings.dark_mode ? '#121212' : '#F0F0F5',
    cardBg: settings.dark_mode ? '#1E1E1E' : '#FFFFFF',
    border: settings.dark_mode ? '#333333' : '#EEEEEE',
  };

  const updateSetting = async (key, value) => {
    const oldSettings = { ...settings };
    setSettings({ ...settings, [key]: value });
    try {
      await profileApi.updateSettings({ [key]: value });
    } catch (e) {
      setSettings(oldSettings); // revert
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSetting, t, C, setSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => useContext(SettingsContext);
