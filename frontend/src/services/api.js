import axios from 'axios';
const api = axios.create({ baseURL: '', headers: { 'Content-Type': 'application/json' } });

export const getEstadoCuenta = (p={}) => api.get('/api/estado-cuenta', { params: p }).then(r=>r.data);
export const getPagos        = (p={}) => api.get('/api/pagos', { params: p }).then(r=>r.data);
export const createPago      = (d)    => api.post('/api/pagos', d).then(r=>r.data);
export const updatePago      = (id,d) => api.put(`/api/pagos/${id}`, d).then(r=>r.data);
export const deletePago      = (id)   => api.delete(`/api/pagos/${id}`).then(r=>r.data);

export const getProjects     = ()     => api.get('/api/projects').then(r=>r.data);
export const createProject   = (d)    => api.post('/api/projects', d).then(r=>r.data);
export const updateProject   = (id,d) => api.put(`/api/projects/${id}`, d).then(r=>r.data);
export const deleteProject   = (id)   => api.delete(`/api/projects/${id}`).then(r=>r.data);

export const getUnits        = (pid)  => api.get(`/api/projects/${pid}/units`).then(r=>r.data);
export const createUnit      = (pid,d)=> api.post(`/api/projects/${pid}/units`, d).then(r=>r.data);
export const updateUnit      = (id,d) => api.put(`/api/units/${id}`, d).then(r=>r.data);
export const deleteUnit      = (id)   => api.delete(`/api/units/${id}`).then(r=>r.data);

export const getContracts    = (uid)  => api.get(`/api/units/${uid}/contracts`).then(r=>r.data);
export const createContract  = (uid,d)=> api.post(`/api/units/${uid}/contracts`, d).then(r=>r.data);
export const updateContract  = (id,d) => api.put(`/api/contracts/${id}`, d).then(r=>r.data);
export const deleteContract  = (id)   => api.delete(`/api/contracts/${id}`).then(r=>r.data);

export const getDocuments    = (p={}) => api.get('/api/documents', { params: p }).then(r=>r.data);
export const deleteDocument  = (id)   => api.delete(`/api/documents/${id}`).then(r=>r.data);
export const uploadDocument  = (formData) =>
  axios.post('/api/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' }}).then(r=>r.data);
