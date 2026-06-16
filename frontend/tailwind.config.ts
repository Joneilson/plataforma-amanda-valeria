import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Paleta extraída da logo (ameixa/lilás + bege)
        plum: {
          DEFAULT: "#5E4E66",
          700: "#5E4E66",
          600: "#7A6B82",
          400: "#A99BB0",
          200: "#D8CEDB",
        },
        sand: {
          DEFAULT: "#E8E1D9",
          light: "#F7F4F0",
        },
        ink: "#3B3340",
        // Funcionais (estados)
        success: "#8B9A86",
        warning: "#C9A36B",
        danger: "#B5736E",
      },
      fontFamily: {
        display: ["var(--font-cormorant)", "Georgia", "serif"],
        brand: ["var(--font-montserrat)", "system-ui", "sans-serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 2px 10px rgba(94, 78, 102, 0.06)",
        card: "0 6px 20px rgba(94, 78, 102, 0.08)",
        lift: "0 12px 28px rgba(94, 78, 102, 0.14)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.45s ease-out both",
        "fade-in": "fade-in 0.4s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
