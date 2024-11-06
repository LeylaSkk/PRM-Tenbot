/** @type {import('tailwindcss').Config} */

module.exports ={
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'playfair': ['Playfair', 'sans-serif'],
      },
      colors: {
        customBlue: '#4BBCEF',
      },
    },
  },
  variants: {
    extend: {
      brightness: ['hover', 'group-hover'],
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'), // Add the typography plugin

  ],
};