/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        // Theme-aware semantic colors
        // These will be overridden in dark mode using Tailwind's dark: variant
        base: {
          DEFAULT: '#F9FAFB', // Light: bg-base
        },
        secondary: {
          DEFAULT: '#FFFFFF', // Light: bg-secondary
        },
        card: {
          DEFAULT: '#FFFFFF', // Light: bg-card
        },
        'border-color': {
          DEFAULT: '#E5E7EB', // Light: border-color
        },
        primary: {
          DEFAULT: '#059669', // Light: primary
          hover: '#10B981', // Light: primary-hover
          active: '#047857', // Light: primary-active
        },
        text: {
          primary: '#111827', // Light: text-primary
          secondary: '#374151', // Light: text-secondary
          muted: '#6B7280', // Light: text-muted
        },
        success: {
          DEFAULT: '#16A34A', // Light: success
        },
        warning: {
          DEFAULT: '#D97706', // Light: warning
        },
        error: {
          DEFAULT: '#DC2626', // Light: error
        },
        info: {
          DEFAULT: '#2563EB', // Light: info
        },
        // Legacy colors (kept for backward compatibility)
        orange: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
          950: '#431407',
        },
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        zinc: {
          50: '#fafafa',
          100: '#f4f4f5',
          200: '#e4e4e7',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
          600: '#52525b',
          700: '#3f3f46',
          800: '#27272a',
          900: '#18181b',
          950: '#09090b',
        }
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gradient': 'gradient 15s ease infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        gradient: {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
      },
    },
  },
  plugins: [],
}
