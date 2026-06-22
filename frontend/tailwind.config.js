/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          saffron: '#FC8019',
          amber: '#FF9E2A',
          tomato: '#E25E1A',
          cream: '#FDF6EE',
          warm: '#FFFFFF',
          charcoal: '#02060C',
          bark: '#02060C99',
          mocha: '#02060CEB',
          sand: '#F0F0F5',
          sage: '#118C4F',
          muted: '#02060C99',
          bg: '#F0F0F5',
          maroon: '#6B0B22',
          maroonLight: '#8A1538',
        }
      },
      fontFamily: {
        sans: ["'Proxima Nova'", "'Inter'", "system-ui", "sans-serif"],
        display: ["'Dancing Script'", "cursive"],
      },
      animation: {
        'marquee': 'marquee 25s linear infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-100%)' },
        }
      }
    },
  },
  plugins: [],
}
