import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Bind to all network interfaces
    port: 5173,      // Specify the port (optional if you're already using 5173)
    allowedHosts: ['Frontend', 'oliver.dailybruin.com'],
  },
  preview: {
    allowedHosts: ['Frontend', 'oliver.dailybruin.com'],
  },
});