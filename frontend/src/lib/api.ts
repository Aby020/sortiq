import axios from 'axios';

/** Local desktop runtime: no auth is required. All endpoints use AllowAny. */
export const apiClient = axios.create({ baseURL: '/api/v1' });

/** Local desktop runtime: all endpoints use AllowAny. */
export const serviceClient = axios.create({ baseURL: '/service' });

