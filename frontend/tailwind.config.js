/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // --- Environment (deep purple-black) ---
        obsidian: '#08050D', // app background
        surface: '#0D0814', // cards / panels
        elevated: '#120A1C', // raised surfaces / table headers
        'purple-deep': '#160D24',
        'purple-mid': '#211034',
        'purple-high': '#2A1542',

        // --- Brand: pink / purple accent (NO blue, cyan or teal) ---
        // Clean semantic tokens. Prefer these in new code.
        primary: '#FF2DAA', // brand primary pink -> text-primary/bg-primary/border-primary
        'primary-soft': '#FF4FD8', // electric pink (highlights, focus)
        accent: '#9B5CFF', // purple accent
        pink: '#FF2DAA',
        'pink-electric': '#FF4FD8',
        'pink-soft': '#FF8BE8',
        'purple-accent': '#9B5CFF',
        'purple-accent-soft': '#6F6278',

        // --- Security status semantics (unchanged meaning) ---
        'security-green': '#35E0A1', // healthy
        success: '#35E0A1',
        warning: '#FFB84D', // high / warning
        critical: '#FF3B6B', // critical
        // --- Text ---
        text: '#F8F3FA',
        'text-secondary': '#C9BFD0',
        muted: '#8E8298',

        // --- Layered border system ---
        // Borders communicate hierarchy, not decoration.
        border: 'rgba(255, 255, 255, 0.06)', // default 1px hairline
        'border-strong': 'rgba(255, 255, 255, 0.10)',
        'border-primary': 'rgba(255, 45, 170, 0.16)', // brand emphasis
        'border-accent': 'rgba(155, 92, 255, 0.16)', // purple emphasis
        'border-critical': 'rgba(255, 59, 107, 0.20)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      boxShadow: {
        // Restrained elevation. Cards use subtle layering, not glow.
        'card': '0 1px 2px rgba(8, 5, 13, 0.4)',
        'card-hover': '0 2px 8px rgba(8, 5, 13, 0.5)',
        'panel': '0 4px 20px rgba(8, 5, 13, 0.5)',
        'popover': '0 8px 28px rgba(8, 5, 13, 0.6)',
        // Pink atmospheric glow - intentionally very subtle, for selected/emphasis only.
        'glow-sm': '0 0 8px rgba(255, 45, 170, 0.10)',
        'glow': '0 0 16px rgba(255, 45, 170, 0.14)',
        'glow-lg': '0 0 30px rgba(255, 45, 170, 0.16)',
        'glow-critical': '0 0 16px rgba(255, 59, 107, 0.18)',
        'glow-green': '0 0 16px rgba(53, 224, 161, 0.18)',
      },
      borderRadius: {
        card: '0.75rem', // 12px
        panel: '1rem', // 16px
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #FF2DAA, #9B5CFF)',
        'brand-gradient-soft': 'linear-gradient(135deg, rgba(255,45,170,0.16), rgba(155,92,255,0.08))',
      },
    },
  },
  plugins: [],
}