/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'company-orange': {
          50: '#fff8f1',
          100: '#ffe9d4',
          200: '#ffd2a9',
          300: '#ffb77d',
          400: '#ff9344',
          500: '#ff7a1a',
          600: '#ff6600',
          700: '#cc5200',
          800: '#a34200',
          900: '#7a3100',
        },
      },
    },
  },
  plugins: [],
};
