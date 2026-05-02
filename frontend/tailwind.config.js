/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f7f7fb",
          100: "#eeeef6",
          200: "#d8d8e7",
          300: "#b3b3cd",
          400: "#7c7c9c",
          500: "#4f4f70",
          600: "#363552",
          700: "#26253c",
          800: "#181828",
          900: "#0d0d18",
        },
        accent: {
          50: "#fff5f4",
          100: "#ffe5e2",
          200: "#ffc6c1",
          300: "#ff9f95",
          400: "#ff7568",
          500: "#f04e3f",
          600: "#cc382a",
          700: "#a32a20",
          800: "#7a1f17",
          900: "#561610",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ["'Playfair Display'", "ui-serif", "Georgia", "serif"],
      },
      boxShadow: {
        soft: "0 10px 30px -12px rgba(13, 13, 24, 0.18)",
        glow: "0 0 0 4px rgba(240, 78, 63, 0.18)",
      },
      backgroundImage: {
        "hero-radial":
          "radial-gradient(1200px 600px at 80% -10%, rgba(240,78,63,0.20), transparent 60%), radial-gradient(900px 500px at 0% 0%, rgba(99,102,241,0.18), transparent 60%)",
      },
    },
  },
  plugins: [],
};
