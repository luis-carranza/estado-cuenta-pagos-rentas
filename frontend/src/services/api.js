import axios from 'axios';

// Empty base → requests go through the Vite proxy to http://localhost:8000
const BASE_URL = '';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Estado de cuenta (header + resumen)
export const getEstadoCuenta = () => api.get('/api/estado-cuenta').then(r => r.data);

// Pagos
export const getPagos = (params = {}) =>
  api.get('/api/pagos', { params }).then(r => r.data);

export const getPago = (consecutivo) =>
  api.get(`/api/pagos/${consecutivo}`).then(r => r.data);

export const createPago = (data) =>
  api.post('/api/pagos', data).then(r => r.data);

export const updatePago = (consecutivo, data) =>
  api.put(`/api/pagos/${consecutivo}`, data).then(r => r.data);

export const deletePago = (consecutivo) =>
  api.delete(`/api/pagos/${consecutivo}`).then(r => r.data);

