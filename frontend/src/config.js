// Centralized client API base URL. Vite exposes env vars that start with VITE_ to the client.
// Use VITE_API_URL in your .env to set the API base URL (e.g. VITE_API_URL=http://localhost:8000)
export const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || ''

export default API_BASE_URL
