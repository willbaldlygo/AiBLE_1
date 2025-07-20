/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        able: {
          primary: '#2D5448',     // Deep teal-green background
          cardBg: '#FEFEFE',      // Off-white card background
          cardBorder: '#E8D5B7',  // Warm beige border
          textPrimary: '#000000', // Black primary text
          textSecondary: '#4A4A4A', // Dark gray secondary text
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 4px 12px rgba(0, 0, 0, 0.15)',
      },
      borderRadius: {
        'card': '12px',
      },
    },
  },
  plugins: [],
}