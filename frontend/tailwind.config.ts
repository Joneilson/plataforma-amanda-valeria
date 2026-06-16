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
    },
  },
  plugins: [],
};

export default config;
