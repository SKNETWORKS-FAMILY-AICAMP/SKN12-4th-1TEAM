/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#141944",
        "chat-bg": {
          from: "rgba(2, 0, 17, 0.8)",
          via: "rgba(23, 31, 65, 0.6)",
          to: "rgba(0, 10, 31, 0.8)",
        },
        secondary: "#864BD8",
        accent: "#EE6D52",
        dark: "#1E2A39",
        "gray-text": "#5C6272",
        "light-gray": "#F5F6F8",
      },
      fontFamily: {
        poppins: ["Poppins", "sans-serif"],
        inter: ["Inter", "sans-serif"],
      },
      spacing: {
        26: "6.5rem", // 104px
        30: "7.5rem", // 120px
      },
    },
  },
  plugins: [],
};
