/** Detective-noir theme: deep navy/charcoal + amber accents. */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        noir: {
          950: '#0a0e1a',
          900: '#0f1526',
          800: '#161d33',
          700: '#1f2942',
          600: '#2b3757',
        },
        amber: {
          glow: '#f5a623',
        },
        evidence: '#e8d9b5',
      },
      fontFamily: {
        display: ['"Special Elite"', 'ui-monospace', 'monospace'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        pin: '0 4px 12px rgba(0,0,0,0.5)',
        glow: '0 0 20px rgba(245,166,35,0.4)',
      },
      keyframes: {
        'flip-in': {
          '0%': { transform: 'rotateY(90deg)', opacity: '0' },
          '100%': { transform: 'rotateY(0)', opacity: '1' },
        },
        'pulse-ring': {
          '0%,100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        'fly-to-board': {
          '0%': { transform: 'translateY(40px) scale(0.8)', opacity: '0' },
          '100%': { transform: 'translateY(0) scale(1)', opacity: '1' },
        },
      },
      animation: {
        'flip-in': 'flip-in 0.6s ease-out',
        'pulse-ring': 'pulse-ring 1s ease-in-out infinite',
        'fly-to-board': 'fly-to-board 0.5s ease-out',
      },
    },
  },
  plugins: [],
}
