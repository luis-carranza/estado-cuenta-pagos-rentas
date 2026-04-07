#!/usr/bin/env python3
"""Generates NEW feature components: Projects, Units, Contracts, Documents + updated App."""
import os
BASE = "/Users/luiscarranza/PycharmProjects/FastAPIProject/frontend/src"
files = {}

# ── services/api.js ──────────────────────────────────────────────────────────
files["services/api.js"] = r"""
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

export const getUnitServices    = (uid)    => api.get(`/api/units/${uid}/services`).then(r=>r.data);
export const createUnitService  = (uid, d) => api.post(`/api/units/${uid}/services`, d).then(r=>r.data);
export const updateUnitService  = (sid, d) => api.put(`/api/unit-services/${sid}`, d).then(r=>r.data);
export const deleteUnitService  = (sid)    => api.delete(`/api/unit-services/${sid}`).then(r=>r.data);

export const getContracts    = (uid)  => api.get(`/api/units/${uid}/contracts`).then(r=>r.data);
export const createContract  = (uid,d)=> api.post(`/api/units/${uid}/contracts`, d).then(r=>r.data);
export const updateContract  = (id,d) => api.put(`/api/contracts/${id}`, d).then(r=>r.data);
export const deleteContract  = (id)   => api.delete(`/api/contracts/${id}`).then(r=>r.data);

export const getDocuments    = (p={}) => api.get('/api/documents', { params: p }).then(r=>r.data);
export const deleteDocument  = (id)   => api.delete(`/api/documents/${id}`).then(r=>r.data);
export const uploadDocument  = (formData) =>
  axios.post('/api/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' }}).then(r=>r.data);
""".lstrip()

# ── components/Navbar.jsx ─────────────────────────────────────────────────────
files["components/Navbar.jsx"] = r"""
import { Building2, FileText, Home, BookOpen, FolderOpen } from 'lucide-react';

const TABS = [
  { key: 'estado',    label: 'Estado de Cuenta', icon: Home },
  { key: 'projects',  label: 'Proyectos',         icon: Building2 },
  { key: 'units',     label: 'Unidades',           icon: BookOpen },
  { key: 'contracts', label: 'Contratos',          icon: FileText },
  { key: 'documents', label: 'Documentos',         icon: FolderOpen },
];

export default function Navbar({ active, onChange }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Building2 size={22} /> Estado de Cuenta
      </div>
      <div className="navbar-tabs">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button key={key} className={`nav-tab ${active === key ? 'active' : ''}`}
            onClick={() => onChange(key)}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>
    </nav>
  );
}
""".lstrip()

# ── components/ProjectsPage.jsx ───────────────────────────────────────────────
files["components/ProjectsPage.jsx"] = r"""
import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Building2, ChevronRight } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getProjects, createProject, updateProject, deleteProject } from '../services/api';
import ProjectModal from './ProjectModal';

export default function ProjectsPage({ onSelectProject }) {
  const [projects, setProjects] = useState([]);
  const [modal, setModal] = useState(null); // null | 'new' | project obj

  const load = () => getProjects().then(setProjects).catch(() => toast.error('Error cargando proyectos'));
  useEffect(() => { load(); }, []);

  const handleSave = async (data) => {
    try {
      if (modal?.id) { await updateProject(modal.id, data); toast.success('Proyecto actualizado'); }
      else           { await createProject(data);            toast.success('Proyecto creado');     }
      setModal(null); load();
    } catch { toast.error('Error guardando proyecto'); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`¿Eliminar proyecto "${name}" y todas sus unidades?`)) return;
    try { await deleteProject(id); toast.success('Proyecto eliminado'); load(); }
    catch { toast.error('Error eliminando proyecto'); }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title"><Building2 size={20}/> Proyectos</h2>
        <button className="btn-primary" onClick={() => setModal('new')}>
          <Plus size={14}/> Nuevo Proyecto
        </button>
      </div>

      <div className="projects-grid">
        {projects.length === 0 && (
          <div className="empty-state">No hay proyectos aún. Crea el primero.</div>
        )}
        {projects.map(p => (
          <div key={p.id} className="project-card">
            <div className="project-card-header">
              <span className="project-name">{p.name}</span>
              <div className="card-actions">
                <button className="action-btn edit-btn" onClick={() => setModal(p)}><Pencil size={14}/></button>
                <button className="action-btn delete-btn" onClick={() => handleDelete(p.id, p.name)}><Trash2 size={14}/></button>
              </div>
            </div>
            {p.address    && <p className="project-meta">📍 {p.address}</p>}
            {p.description && <p className="project-desc">{p.description}</p>}
            <div className="project-stats">
              <span className="stat-pill total">{p.unit_count || 0} unidades</span>
              <span className="stat-pill avail">{p.available_units || 0} disponibles</span>
            </div>
            <button className="btn-outline full-width mt-8" onClick={() => onSelectProject(p)}>
              Ver unidades <ChevronRight size={14}/>
            </button>
          </div>
        ))}
      </div>

      {modal && <ProjectModal project={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
    </div>
  );
}
""".lstrip()

# ── components/ProjectModal.jsx ───────────────────────────────────────────────
files["components/ProjectModal.jsx"] = r"""
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export default function ProjectModal({ project, onClose, onSave }) {
  const [form, setForm] = useState({ name: '', description: '', address: '' });
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    setForm(project ? { name: project.name||'', description: project.description||'', address: project.address||'' }
                    : { name: '', description: '', address: '' });
  }, [project]);

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const submit = async e => { e.preventDefault(); setSaving(true); try { await onSave(form); } finally { setSaving(false); } };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{project ? `Editar: ${project.name}` : 'Nuevo Proyecto'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-group full-width">
            <label>Nombre del Proyecto *</label>
            <input required name="name" value={form.name} onChange={handle} placeholder="Ej: Intercity / Condesa 1"/>
          </div>
          <div className="form-group full-width">
            <label>Dirección</label>
            <input name="address" value={form.address} onChange={handle} placeholder="Calle, número, colonia..."/>
          </div>
          <div className="form-group full-width">
            <label>Descripción</label>
            <textarea name="description" value={form.description} onChange={handle} rows={3} style={{resize:'vertical'}}/>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
""".lstrip()

# ── components/UnitsPage.jsx ──────────────────────────────────────────────────
files["components/UnitsPage.jsx"] = r"""
import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, ChevronLeft, ChevronRight, Home, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getUnits, createUnit, updateUnit, deleteUnit } from '../services/api';
import UnitModal from './UnitModal';
import DocumentsPanel from './DocumentsPanel';

const fmt = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : '—';

const SVC_BADGE = { PAGADO:'svc-pagado', PENDIENTE:'svc-pendiente', VENCIDO:'svc-vencido' };

export default function UnitsPage({ project, onBack, onSelectUnit }) {
  const [units, setUnits] = useState([]);
  const [modal, setModal] = useState(null);
  const [docsUnit, setDocsUnit] = useState(null);

  const load = () => getUnits(project.id).then(setUnits).catch(() => toast.error('Error cargando unidades'));
  useEffect(() => { load(); }, [project.id]);

  const handleSave = async (data) => {
    try {
      if (modal?.id) { await updateUnit(modal.id, data); toast.success('Unidad actualizada'); }
      else           { await createUnit(project.id, data); toast.success('Unidad creada'); }
      setModal(null); load();
    } catch { toast.error('Error guardando unidad'); }
  };

  const handleDelete = async (id, num) => {
    if (!window.confirm(`¿Eliminar unidad "${num}"?`)) return;
    try { await deleteUnit(id); toast.success('Unidad eliminada'); load(); }
    catch { toast.error('Error eliminando unidad'); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ChevronLeft size={16}/> Proyectos</button>
          <span className="breadcrumb-sep">/</span>
          <h2 className="page-title"><Home size={18}/> {project.name} — Unidades</h2>
        </div>
        <button className="btn-primary" onClick={() => setModal('new')}><Plus size={14}/> Nueva Unidad</button>
      </div>

      <div className="units-grid">
        {units.length === 0 && <div className="empty-state">No hay unidades. Agrega la primera.</div>}
        {units.map(u => (
          <div key={u.id} className={`unit-card ${u.is_available ? 'available' : 'occupied'}`}>
            <div className="unit-header">
              <span className="unit-number">{u.unit_number}</span>
              <span className={`purpose-badge ${u.purpose === 'RENTA' ? 'renta' : 'venta'}`}>{u.purpose}</span>
            </div>
            <div className="unit-type-row">
              <span className="unit-type">{u.unit_type}</span>
              {u.floor != null && <span className="unit-floor">Piso {u.floor}</span>}
              {u.area_sqm && <span className="unit-area">{u.area_sqm} m²</span>}
            </div>
            {u.purpose === 'RENTA' && u.rent_price &&
              <div className="unit-price renta">{fmt(u.rent_price)}/mes</div>}
            {u.purpose === 'VENTA' && u.sale_price &&
              <div className="unit-price venta">{fmt(u.sale_price)}</div>}
            <div className={`availability-badge ${u.is_available ? 'free' : 'taken'}`}>
              {u.is_available ? 'Disponible' : `Ocupada${u.current_tenant ? ` — ${u.current_tenant}` : ''}`}
            </div>
            {u.services && u.services.length > 0 && (
              <div className="unit-services">
                {u.services.map(svc => (
                  <span key={svc.id} className={`svc-badge ${SVC_BADGE[svc.status] || 'svc-pendiente'}`}
                        title={svc.service_name}>
                    {svc.service_name.charAt(0)}{svc.service_name.length > 1 ? svc.service_name.slice(1,3).toLowerCase() : ''}
                  </span>
                ))}
              </div>
            )}
            {u.notes && <p className="unit-notes">{u.notes}</p>}
            <div className="unit-actions">
              <button className="btn-outline flex-1" onClick={() => onSelectUnit(u)}>
                <FileText size={13}/> Contratos <ChevronRight size={13}/>
              </button>
              <button className="btn-outline flex-1" onClick={() => setDocsUnit(u)}>
                Docs ({u.contract_count||0})
              </button>
              <button className="action-btn edit-btn" onClick={() => setModal(u)}><Pencil size={13}/></button>
              <button className="action-btn delete-btn" onClick={() => handleDelete(u.id, u.unit_number)}><Trash2 size={13}/></button>
            </div>
          </div>
        ))}
      </div>

      {modal && <UnitModal unit={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
      {docsUnit && <DocumentsPanel relatedType="unit" relatedId={docsUnit.id}
        title={`Docs — ${docsUnit.unit_number}`} onClose={() => setDocsUnit(null)} />}
    </div>
  );
}
""".lstrip()

# ── components/UnitModal.jsx ──────────────────────────────────────────────────
files["components/UnitModal.jsx"] = r"""
import { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getUnitServices, createUnitService, updateUnitService, deleteUnitService } from '../services/api';

const empty = { unit_number:'', unit_type:'DEPTO', purpose:'RENTA', floor:'', area_sqm:'',
                rent_price:'', sale_price:'', is_available:true, current_tenant:'', notes:'' };
const TYPES = ['DEPTO','LOCAL','OFICINA','BODEGA','CASA','COMERCIAL','OTRO'];
const SVC_STATUS = ['PENDIENTE','PAGADO','VENCIDO'];
const STATUS_COLORS = { PAGADO:'svc-pagado', PENDIENTE:'svc-pendiente', VENCIDO:'svc-vencido' };

export default function UnitModal({ unit, onClose, onSave }) {
  const [form, setForm]       = useState(empty);
  const [saving, setSaving]   = useState(false);
  const [services, setServices] = useState([]);
  const [newSvc, setNewSvc]   = useState({ service_name:'', status:'PENDIENTE' });
  const [addingSvc, setAddingSvc] = useState(false);

  useEffect(() => {
    setForm(unit ? {
      ...empty, ...unit,
      floor: unit.floor ?? '',
      area_sqm: unit.area_sqm ?? '',
      rent_price: unit.rent_price ?? '',
      sale_price: unit.sale_price ?? '',
      current_tenant: unit.current_tenant ?? '',
      is_available: !!unit.is_available
    } : empty);
    if (unit?.id) {
      getUnitServices(unit.id).then(setServices).catch(() => {});
    } else {
      setServices([]);
    }
  }, [unit]);

  const set = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const submit = async e => {
    e.preventDefault(); setSaving(true);
    try {
      await onSave({
        ...form,
        floor: form.floor || null,
        area_sqm: form.area_sqm || null,
        rent_price: form.rent_price || null,
        sale_price: form.sale_price || null,
        current_tenant: form.current_tenant || null,
      });
    } finally { setSaving(false); }
  };

  const handleSvcStatusChange = async (svc, newStatus) => {
    try {
      const updated = await updateUnitService(svc.id, { ...svc, status: newStatus });
      setServices(ss => ss.map(s => s.id === svc.id ? updated : s));
    } catch { toast.error('Error actualizando servicio'); }
  };

  const handleAddSvc = async () => {
    if (!newSvc.service_name.trim()) return;
    if (!unit?.id) { toast.error('Guarda la unidad primero para añadir servicios'); return; }
    try {
      const created = await createUnitService(unit.id, { ...newSvc, service_name: newSvc.service_name.trim().toUpperCase() });
      setServices(ss => [...ss, created]);
      setNewSvc({ service_name: '', status: 'PENDIENTE' });
      setAddingSvc(false);
    } catch { toast.error('Error añadiendo servicio'); }
  };

  const handleDeleteSvc = async (sid) => {
    try {
      await deleteUnitService(sid);
      setServices(ss => ss.filter(s => s.id !== sid));
    } catch { toast.error('Error eliminando servicio'); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{unit ? `Editar Unidad: ${unit.unit_number}` : 'Nueva Unidad'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-grid">
            <div className="form-group"><label>Número / Código *</label>
              <input required name="unit_number" value={form.unit_number} onChange={set} placeholder="Ej: DEPTO 437E"/></div>
            <div className="form-group"><label>Tipo</label>
              <select name="unit_type" value={form.unit_type} onChange={set}>
                {TYPES.map(t => <option key={t}>{t}</option>)}</select></div>
            <div className="form-group"><label>Propósito</label>
              <select name="purpose" value={form.purpose} onChange={set}>
                <option value="RENTA">RENTA</option><option value="VENTA">VENTA</option></select></div>
            <div className="form-group"><label>Inquilino / Cliente</label>
              <input name="current_tenant" value={form.current_tenant} onChange={set} placeholder="Nombre del inquilino"/></div>
            <div className="form-group"><label>Piso</label>
              <input type="number" name="floor" value={form.floor} onChange={set}/></div>
            <div className="form-group"><label>Área (m²)</label>
              <input type="number" step="0.01" name="area_sqm" value={form.area_sqm} onChange={set}/></div>
            {form.purpose === 'RENTA' && <div className="form-group"><label>Precio Renta/mes ($)</label>
              <input type="number" step="0.01" name="rent_price" value={form.rent_price} onChange={set}/></div>}
            {form.purpose === 'VENTA' && <div className="form-group"><label>Precio Venta ($)</label>
              <input type="number" step="0.01" name="sale_price" value={form.sale_price} onChange={set}/></div>}
            <div className="form-group" style={{alignSelf:'center'}}>
              <label style={{display:'flex',gap:'8px',alignItems:'center',cursor:'pointer'}}>
                <input type="checkbox" name="is_available" checked={form.is_available} onChange={set}/>
                Disponible
              </label>
            </div>
            <div className="form-group full-width"><label>Notas</label>
              <textarea name="notes" value={form.notes} onChange={set} rows={2} style={{resize:'vertical'}}/></div>
          </div>

          {unit?.id && (
            <div className="services-section">
              <div className="services-header">
                <span className="services-title">Servicios</span>
                <button type="button" className="btn-sm-outline" onClick={() => setAddingSvc(v => !v)}>
                  <Plus size={12}/> Agregar
                </button>
              </div>
              {addingSvc && (
                <div className="svc-add-row">
                  <input
                    className="svc-name-input"
                    placeholder="Nombre del servicio (ej. INTERNET)"
                    value={newSvc.service_name}
                    onChange={e => setNewSvc(v => ({ ...v, service_name: e.target.value }))}
                    onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); handleAddSvc(); } }}
                  />
                  <select
                    value={newSvc.status}
                    onChange={e => setNewSvc(v => ({ ...v, status: e.target.value }))}
                  >
                    {SVC_STATUS.map(s => <option key={s}>{s}</option>)}
                  </select>
                  <button type="button" className="btn-primary btn-sm" onClick={handleAddSvc}>Añadir</button>
                  <button type="button" className="btn-secondary btn-sm" onClick={() => setAddingSvc(false)}>×</button>
                </div>
              )}
              <div className="services-list">
                {services.length === 0 && <span className="svc-empty">Sin servicios registrados</span>}
                {services.map(svc => (
                  <div key={svc.id} className="svc-row">
                    <span className="svc-name">{svc.service_name}</span>
                    <select
                      className={`svc-status-select ${STATUS_COLORS[svc.status] || ''}`}
                      value={svc.status}
                      onChange={e => handleSvcStatusChange(svc, e.target.value)}
                    >
                      {SVC_STATUS.map(s => <option key={s}>{s}</option>)}
                    </select>
                    <button type="button" className="action-btn delete-btn" onClick={() => handleDeleteSvc(svc.id)}>
                      <Trash2 size={12}/>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving?'Guardando...':'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
""".lstrip()

# ── components/ContractsPage.jsx ──────────────────────────────────────────────
files["components/ContractsPage.jsx"] = r"""
import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, ChevronLeft, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getContracts, createContract, updateContract, deleteContract } from '../services/api';
import ContractModal from './ContractModal';
import DocumentsPanel from './DocumentsPanel';

const fmt = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : '—';

const STATUS_COLOR = { ACTIVO:'badge-activo', VENCIDO:'badge-vencido', CANCELADO:'badge-cancelado' };

export default function ContractsPage({ unit, project, onBack }) {
  const [contracts, setContracts] = useState([]);
  const [modal, setModal]         = useState(null);
  const [docsContract, setDocs]   = useState(null);

  const load = () => getContracts(unit.id).then(setContracts).catch(() => toast.error('Error cargando contratos'));
  useEffect(() => { load(); }, [unit.id]);

  const handleSave = async (data) => {
    try {
      if (modal?.id) { await updateContract(modal.id, data); toast.success('Contrato actualizado'); }
      else           { await createContract(unit.id, data);  toast.success('Contrato creado'); }
      setModal(null); load();
    } catch { toast.error('Error guardando contrato'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este contrato?')) return;
    try { await deleteContract(id); toast.success('Contrato eliminado'); load(); }
    catch { toast.error('Error eliminando contrato'); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ChevronLeft size={16}/> {project?.name}</button>
          <span className="breadcrumb-sep">/</span>
          <h2 className="page-title"><FileText size={18}/> {unit.unit_number} — Contratos</h2>
        </div>
        <button className="btn-primary" onClick={() => setModal('new')}><Plus size={14}/> Nuevo Contrato</button>
      </div>

      <div className="contracts-list">
        {contracts.length === 0 && <div className="empty-state">No hay contratos para esta unidad.</div>}
        {contracts.map(c => (
          <div key={c.id} className="contract-card">
            <div className="contract-header">
              <div>
                <span className="tenant-name">{c.tenant_name}</span>
                <span className={`badge ${STATUS_COLOR[c.status] || 'badge-trans'}`}>{c.status}</span>
              </div>
              <div className="card-actions">
                <button className="btn-sm-outline" onClick={() => setDocs(c)}><FileText size={13}/> Documentos</button>
                <button className="action-btn edit-btn" onClick={() => setModal(c)}><Pencil size={14}/></button>
                <button className="action-btn delete-btn" onClick={() => handleDelete(c.id)}><Trash2 size={14}/></button>
              </div>
            </div>
            <div className="contract-details">
              {c.tenant_email && <span>✉️ {c.tenant_email}</span>}
              {c.tenant_phone && <span>📞 {c.tenant_phone}</span>}
              {c.start_date && <span>📅 {c.start_date} → {c.end_date || '...'}</span>}
              {c.monthly_rent && <span>💰 {fmt(c.monthly_rent)}/mes</span>}
              {c.deposit && <span>🔒 Depósito: {fmt(c.deposit)}</span>}
              {c.payment_day && <span>📆 Pago día {c.payment_day}</span>}
            </div>
            {c.notes && <p className="contract-notes">{c.notes}</p>}
          </div>
        ))}
      </div>

      {modal && <ContractModal contract={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
      {docsContract && <DocumentsPanel relatedType="contract" relatedId={docsContract.id}
        title={`Docs contrato — ${docsContract.tenant_name}`} onClose={() => setDocs(null)} />}
    </div>
  );
}
""".lstrip()

# ── components/ContractModal.jsx ──────────────────────────────────────────────
files["components/ContractModal.jsx"] = r"""
import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const empty = { tenant_name:'', tenant_email:'', tenant_phone:'', start_date:'', end_date:'',
                monthly_rent:'', deposit:'', payment_day:'1', status:'ACTIVO', notes:'' };

export default function ContractModal({ contract, onClose, onSave }) {
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  useEffect(() => { setForm(contract ? { ...empty, ...contract,
    monthly_rent: contract.monthly_rent??'', deposit: contract.deposit??'',
    payment_day: contract.payment_day??'1' } : empty); }, [contract]);

  const set = e => setForm(f => ({...f, [e.target.name]: e.target.value}));
  const submit = async e => { e.preventDefault(); setSaving(true);
    try { await onSave({ ...form, monthly_rent: form.monthly_rent||null,
      deposit: form.deposit||null, payment_day: parseInt(form.payment_day)||1 }); }
    finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{contract ? `Editar Contrato` : 'Nuevo Contrato'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-grid">
            <div className="form-group full-width"><label>Nombre del Inquilino *</label>
              <input required name="tenant_name" value={form.tenant_name} onChange={set}/></div>
            <div className="form-group"><label>Correo</label>
              <input type="email" name="tenant_email" value={form.tenant_email} onChange={set}/></div>
            <div className="form-group"><label>Teléfono</label>
              <input name="tenant_phone" value={form.tenant_phone} onChange={set}/></div>
            <div className="form-group"><label>Fecha Inicio</label>
              <input type="date" name="start_date" value={form.start_date} onChange={set}/></div>
            <div className="form-group"><label>Fecha Fin</label>
              <input type="date" name="end_date" value={form.end_date} onChange={set}/></div>
            <div className="form-group"><label>Renta Mensual ($)</label>
              <input type="number" step="0.01" name="monthly_rent" value={form.monthly_rent} onChange={set}/></div>
            <div className="form-group"><label>Depósito ($)</label>
              <input type="number" step="0.01" name="deposit" value={form.deposit} onChange={set}/></div>
            <div className="form-group"><label>Día de Pago</label>
              <input type="number" min="1" max="31" name="payment_day" value={form.payment_day} onChange={set}/></div>
            <div className="form-group"><label>Estatus</label>
              <select name="status" value={form.status} onChange={set}>
                <option value="ACTIVO">ACTIVO</option>
                <option value="VENCIDO">VENCIDO</option>
                <option value="CANCELADO">CANCELADO</option>
              </select></div>
            <div className="form-group full-width"><label>Notas</label>
              <textarea name="notes" value={form.notes} onChange={set} rows={2} style={{resize:'vertical'}}/></div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving?'Guardando...':'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
""".lstrip()

# ── components/DocumentsPanel.jsx ────────────────────────────────────────────
files["components/DocumentsPanel.jsx"] = r"""
import { useState, useEffect, useRef } from 'react';
import { X, Upload, Trash2, Download, FileText, File } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

const DOC_TYPES = ['CONTRATO','IDENTIFICACION','COMPROBANTE_DOMICILIO','COMPROBANTE_INGRESOS',
                   'PAGARE','AVAL','FOTO','PLANO','RECIBO','OTRO'];

const fmtSize = b => b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`;

export default function DocumentsPanel({ relatedType, relatedId, title, onClose }) {
  const [docs, setDocs]       = useState([]);
  const [uploading, setUpl]   = useState(false);
  const [docName, setDocName] = useState('');
  const [docType, setDocType] = useState('CONTRATO');
  const [file, setFile]       = useState(null);
  const inputRef = useRef();

  const load = () => getDocuments({ related_type: relatedType, related_id: relatedId })
    .then(setDocs).catch(() => toast.error('Error cargando documentos'));
  useEffect(() => { load(); }, [relatedType, relatedId]);

  const handleUpload = async e => {
    e.preventDefault();
    if (!file) return toast.error('Selecciona un archivo');
    if (!docName.trim()) return toast.error('Ingresa un nombre');
    const fd = new FormData();
    fd.append('related_type', relatedType);
    fd.append('related_id', String(relatedId));
    fd.append('name', docName.trim());
    fd.append('document_type', docType);
    fd.append('file', file);
    setUpl(true);
    try {
      await uploadDocument(fd);
      toast.success('Documento subido');
      setDocName(''); setFile(null); if(inputRef.current) inputRef.current.value='';
      load();
    } catch { toast.error('Error subiendo documento'); }
    finally { setUpl(false); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`¿Eliminar "${name}"?`)) return;
    try { await deleteDocument(id); toast.success('Documento eliminado'); load(); }
    catch { toast.error('Error eliminando documento'); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span><FileText size={16}/> {title}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <div className="docs-container">
          {/* Upload form */}
          <form onSubmit={handleUpload} className="upload-form">
            <div className="upload-row">
              <input className="upload-name" placeholder="Nombre del documento *" value={docName}
                onChange={e => setDocName(e.target.value)} required/>
              <select className="upload-type" value={docType} onChange={e => setDocType(e.target.value)}>
                {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="upload-row">
              <label className="file-picker">
                <input type="file" ref={inputRef} style={{display:'none'}}
                  onChange={e => { setFile(e.target.files[0]); if(!docName) setDocName(e.target.files[0]?.name.replace(/\.[^.]+$/,'')||''); }}/>
                <Upload size={14}/> {file ? file.name : 'Seleccionar archivo...'}
              </label>
              <button type="submit" className="btn-primary" disabled={uploading||!file}>
                {uploading ? 'Subiendo...' : <><Upload size={14}/> Subir</>}
              </button>
            </div>
          </form>

          {/* Documents list */}
          <div className="docs-list">
            {docs.length === 0 && <div className="empty-state-sm">No hay documentos subidos.</div>}
            {docs.map(d => (
              <div key={d.id} className="doc-row">
                <File size={16} className="doc-icon"/>
                <div className="doc-info">
                  <span className="doc-name">{d.name}</span>
                  <span className="doc-meta">{d.document_type} · {fmtSize(d.file_size||0)} · {d.uploaded_at?.slice(0,10)}</span>
                </div>
                <div className="doc-actions">
                  <a href={`/api/documents/${d.id}/download`} target="_blank" rel="noreferrer"
                    className="action-btn edit-btn" title="Descargar"><Download size={13}/></a>
                  <button className="action-btn delete-btn" onClick={() => handleDelete(d.id, d.name)}
                    title="Eliminar"><Trash2 size={13}/></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
""".lstrip()

# ── Updated App.jsx ────────────────────────────────────────────────────────────
files["App.jsx"] = r"""
import { useState, useEffect, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Navbar         from './components/Navbar';
import Header         from './components/Header';
import ResumenPagos   from './components/ResumenPagos';
import PagosTable     from './components/PagosTable';
import PagoModal      from './components/PagoModal';
import ProjectsPage   from './components/ProjectsPage';
import UnitsPage      from './components/UnitsPage';
import ContractsPage  from './components/ContractsPage';
import { getEstadoCuenta, getPagos, createPago, updatePago, deletePago } from './services/api';
import './App.css';

export default function App() {
  const [tab, setTab]           = useState('estado');
  const [selProject, setProj]   = useState(null);  // for Units page
  const [selUnit, setUnit]       = useState(null);   // for Contracts page

  // Estado de Cuenta state
  const [estadoCuenta, setEC]   = useState(null);
  const [pagos, setPagos]        = useState([]);
  const [loading, setLoading]    = useState(true);
  const [error, setError]        = useState(null);
  const [modalOpen, setModal]    = useState(false);
  const [editPago, setEditPago]  = useState(null);

  // Filters
  const [filterMonth, setMonth]  = useState('');
  const [filterYear, setYear]    = useState('');
  const [filterProject, setFP]   = useState('');

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterMonth)   params.month = filterMonth;
      if (filterYear)    params.year  = filterYear;
      if (filterProject) params.project_id = filterProject;
      const [ec, ps] = await Promise.all([getEstadoCuenta(params), getPagos(params)]);
      setEC(ec); setPagos(ps); setError(null);
    } catch { setError('No se pudo conectar con el servidor (http://localhost:8000)'); }
    finally { setLoading(false); }
  }, [filterMonth, filterYear, filterProject]);

  useEffect(() => { if (tab === 'estado') fetchAll(); }, [tab, fetchAll]);

  const handleSavePago = async (data) => {
    try {
      if (editPago) { await updatePago(editPago.consecutivo, data); toast.success('Pago actualizado'); }
      else          { await createPago(data);                        toast.success('Pago creado'); }
      setModal(false); setEditPago(null); fetchAll();
    } catch { toast.error('Error guardando pago'); }
  };

  const handleDeletePago = async (id) => {
    if (!window.confirm(`¿Eliminar pago #${id}?`)) return;
    try { await deletePago(id); toast.success(`Pago #${id} eliminado`); fetchAll(); }
    catch { toast.error('Error eliminando pago'); }
  };

  // Navigate to units when project selected from ProjectsPage
  const handleSelectProject = (p) => { setProj(p); setTab('units'); };
  // Navigate to contracts when unit selected from UnitsPage
  const handleSelectUnit    = (u) => { setUnit(u); setTab('contracts'); };

  return (
    <div className="app-wrapper">
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
      <Navbar active={tab} onChange={t => { setTab(t);
        if (t !== 'units' && t !== 'contracts') { setProj(null); setUnit(null); }
      }} />

      <main className="app-container">

        {/* ── Estado de Cuenta ── */}
        {tab === 'estado' && (
          <>
            {/* Month / Year / Project filter bar */}
            <div className="periodo-bar card mb-6">
              <span className="periodo-label">Filtrar por:</span>
              <select value={filterMonth} onChange={e => setMonth(e.target.value)}>
                <option value="">Todos los meses</option>
                {Array.from({length:12},(_,i)=>i+1).map(m =>
                  <option key={m} value={m}>{new Date(2000,m-1).toLocaleString('es-MX',{month:'long'})}</option>)}
              </select>
              <select value={filterYear} onChange={e => setYear(e.target.value)}>
                <option value="">Todos los años</option>
                {[2024,2025,2026,2027].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <button className="btn-primary btn-sm" onClick={fetchAll}>Aplicar</button>
              {(filterMonth||filterYear||filterProject) &&
                <button className="btn-clear" onClick={() => { setMonth(''); setYear(''); setFP(''); }}>Limpiar</button>}
            </div>

            {loading && <div className="loading-overlay"><div className="spinner"/><span>Cargando...</span></div>}
            {error   && <div className="error-banner">⚠️ {error}<button onClick={fetchAll} className="retry-btn">Reintentar</button></div>}
            {!loading && !error && (
              <>
                <Header header={estadoCuenta?.header} />
                <ResumenPagos resumen={estadoCuenta?.resumen} />
                <PagosTable pagos={pagos}
                  onNew={() => { setEditPago(null); setModal(true); }}
                  onEdit={p  => { setEditPago(p);   setModal(true); }}
                  onDelete={handleDeletePago} />
              </>
            )}
            {modalOpen && <PagoModal pago={editPago}
              onClose={() => { setModal(false); setEditPago(null); }} onSave={handleSavePago} />}
          </>
        )}

        {/* ── Proyectos ── */}
        {tab === 'projects' && (
          <ProjectsPage onSelectProject={handleSelectProject} />
        )}

        {/* ── Unidades ── */}
        {tab === 'units' && selProject && (
          <UnitsPage project={selProject}
            onBack={() => setTab('projects')}
            onSelectUnit={handleSelectUnit} />
        )}
        {tab === 'units' && !selProject && (
          <div className="empty-state">Selecciona un proyecto desde la pestaña Proyectos.</div>
        )}

        {/* ── Contratos ── */}
        {tab === 'contracts' && selUnit && (
          <ContractsPage unit={selUnit} project={selProject}
            onBack={() => { setTab('units'); }} />
        )}
        {tab === 'contracts' && !selUnit && (
          <div className="empty-state">Selecciona una unidad desde la pestaña Unidades.</div>
        )}

        {/* ── Documentos (global view) ── */}
        {tab === 'documents' && (
          <div className="page-header"><h2 className="page-title">📁 Documentos</h2>
            <p style={{color:'#666',marginTop:'8px'}}>Accede a los documentos desde una unidad o contrato específico usando el botón "Docs".</p>
          </div>
        )}
      </main>
    </div>
  );
}
""".lstrip()

# ── Updated App.css (add new styles) ─────────────────────────────────────────
files["App.css"] = r"""
/* ── Reset / Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f4f8; color: #1a1a2e; font-size: 13px; }

/* ── Wrapper ── */
.app-wrapper { display: flex; flex-direction: column; min-height: 100vh; }
.app-container { max-width: 1400px; margin: 0 auto; padding: 20px 16px; width: 100%; }
.mb-6 { margin-bottom: 20px; }
.mt-8 { margin-top: 8px; }
.flex-1 { flex: 1; }

/* ── Navbar ── */
.navbar { background: #1a3a6b; color: #fff; padding: 0 24px; display: flex; align-items: center; gap: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); position: sticky; top: 0; z-index: 100; }
.navbar-brand { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 16px; padding: 14px 0; white-space: nowrap; }
.navbar-tabs { display: flex; gap: 2px; overflow-x: auto; }
.nav-tab { background: none; border: none; color: rgba(255,255,255,0.7); padding: 14px 14px; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 6px; border-bottom: 3px solid transparent; transition: all 0.15s; white-space: nowrap; }
.nav-tab:hover { color: #fff; background: rgba(255,255,255,0.08); }
.nav-tab.active { color: #fff; border-bottom-color: #5b9bd5; background: rgba(255,255,255,0.1); }

/* ── Card ── */
.card { background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }

/* ── Section Header (blue bar) ── */
.section-header { background: #1a3a6b; color: #fff; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; }
.section-title { font-weight: 700; font-size: 14px; letter-spacing: 0.5px; text-transform: uppercase; }

/* ── Header info ── */
.header-info { padding: 16px 20px; }
.header-row { display: flex; flex-wrap: wrap; gap: 32px; }
.header-item { display: flex; align-items: center; gap: 6px; }
.header-icon { color: #1a3a6b; }
.header-label { font-weight: 600; color: #444; }
.header-value { color: #1a1a2e; font-weight: 500; }

/* ── Periodo bar ── */
.periodo-bar { padding: 10px 16px; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.periodo-label { font-weight: 600; color: #555; }
.periodo-bar select { padding: 6px 10px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 13px; outline: none; background: #fff; }

/* ── Resumen ── */
.resumen-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0; padding: 16px 20px; }
.resumen-left, .resumen-right { display: flex; flex-direction: column; gap: 8px; }
.resumen-right { padding-left: 40px; border-left: 2px solid #e8edf5; }
.resumen-row { display: flex; align-items: center; gap: 12px; }
.total-row { border-top: 1px solid #d0d9e8; padding-top: 8px; margin-top: 4px; }
.resumen-label { font-weight: 600; color: #333; min-width: 170px; }
.resumen-value { font-weight: 700; font-size: 15px; }
.resumen-value.efectivo { color: #2e7d32; }
.resumen-value.transferencia { color: #1565c0; }
.resumen-value.total { color: #1a3a6b; font-size: 17px; }
.resumen-value.servicios { color: #e65100; }
.resumen-value.renta { color: #6a1b9a; }

/* ── Filters bar ── */
.filters-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; padding: 12px 16px; background: #f7f9fc; border-bottom: 1px solid #e3e9f0; }
.search-box { position: relative; flex: 1; min-width: 200px; }
.search-box .search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #888; }
.search-box input { width: 100%; padding: 7px 10px 7px 34px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 13px; outline: none; background: #fff; }
.search-box input:focus { border-color: #1a3a6b; }
.filter-group { display: flex; align-items: center; gap: 6px; color: #666; }
.filter-group select { padding: 7px 10px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 13px; outline: none; background: #fff; cursor: pointer; }

/* ── Table ── */
.table-wrapper { overflow-x: auto; }
.pagos-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.pagos-table thead tr { background: #1a3a6b; color: #fff; }
.pagos-table th { padding: 10px 8px; text-align: left; font-weight: 700; font-size: 11px; letter-spacing: 0.3px; white-space: nowrap; }
.pagos-table td { padding: 8px 8px; border-bottom: 1px solid #eef0f5; vertical-align: middle; }
.row-even { background: #fff; }
.row-odd  { background: #f5f8fd; }
.pagos-table tbody tr:hover { background: #e8f0fb; }
.text-center { text-align: center; }
.text-right  { text-align: right; }
.font-bold   { font-weight: 700; }
.client-cell { font-weight: 500; max-width: 180px; }
.concepto-cell { max-width: 240px; }
.monto-cell { text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; color: #1a3a6b; white-space: nowrap; }
.empty-row { text-align: center; padding: 32px; color: #888; font-style: italic; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.2px; white-space: nowrap; }
.badge-efectivo { background: #e8f5e9; color: #2e7d32; }
.badge-trans    { background: #e3f2fd; color: #1565c0; }
.badge-activo   { background: #e8f5e9; color: #2e7d32; }
.badge-vencido  { background: #fff3e0; color: #e65100; }
.badge-cancelado{ background: #fce4ec; color: #c62828; }
.actions-cell { display: flex; gap: 4px; align-items: center; }
.action-btn { border: none; cursor: pointer; border-radius: 5px; padding: 5px; display: flex; align-items: center; transition: background 0.15s; }
.edit-btn   { background: #e3f2fd; color: #1565c0; }
.edit-btn:hover { background: #bbdefb; }
.delete-btn { background: #fce4ec; color: #c62828; }
.delete-btn:hover { background: #f8bbd0; }
.total-footer { background: #f0f4fb; }
.footer-label { font-weight: 700; font-size: 13px; padding-right: 12px; color: #333; }
.footer-total { font-weight: 700; font-size: 15px; color: #1a3a6b; text-align: right; white-space: nowrap; }

/* ── Buttons ── */
.btn-primary { background: #1a3a6b; color: #fff; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; transition: background 0.15s; }
.btn-primary:hover { background: #0d2447; }
.btn-primary:disabled { background: #9ab; cursor: not-allowed; }
.btn-sm { padding: 5px 12px; font-size: 12px; }
.btn-secondary { background: #fff; color: #333; border: 1px solid #ccc; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 13px; font-weight: 600; }
.btn-secondary:hover { background: #f5f5f5; }
.btn-outline { background: none; border: 1px solid #c0cfe0; border-radius: 6px; padding: 5px 10px; cursor: pointer; font-size: 12px; color: #1a3a6b; display: inline-flex; align-items: center; gap: 4px; transition: all 0.15s; }
.btn-outline:hover { background: #e8f0fb; }
.full-width { width: 100%; justify-content: center; }
.btn-clear { background: none; border: 1px solid #bbb; border-radius: 6px; padding: 6px 12px; font-size: 12px; cursor: pointer; color: #555; }
.btn-clear:hover { background: #f0f0f0; }
.btn-back { background: none; border: none; color: #1a3a6b; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 4px; font-weight: 600; padding: 0; }
.btn-back:hover { color: #0d2447; }
.btn-sm-outline { background: none; border: 1px solid #c0cfe0; border-radius: 5px; padding: 4px 8px; cursor: pointer; font-size: 11px; color: #555; display: flex; align-items: center; gap: 3px; }
.btn-sm-outline:hover { background: #e8f0fb; }

/* ── Page layout ── */
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }
.page-title  { font-size: 18px; font-weight: 700; color: #1a3a6b; display: flex; align-items: center; gap: 8px; }
.breadcrumb  { display: flex; align-items: center; gap: 8px; }
.breadcrumb-sep { color: #999; }
.empty-state { text-align: center; padding: 48px; color: #888; font-style: italic; font-size: 14px; }
.card-actions { display: flex; gap: 6px; }

/* ── Projects grid ── */
.projects-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.project-card { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #e3e9f0; }
.project-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.project-name { font-weight: 700; font-size: 15px; color: #1a3a6b; }
.project-meta { font-size: 12px; color: #666; margin: 4px 0; }
.project-desc { font-size: 12px; color: #555; margin: 6px 0; }
.project-stats { display: flex; gap: 8px; margin: 10px 0; }
.stat-pill { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.stat-pill.total { background: #e3f2fd; color: #1565c0; }
.stat-pill.avail { background: #e8f5e9; color: #2e7d32; }

/* ── Units grid ── */
.units-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.unit-card { background: #fff; border-radius: 10px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border-left: 4px solid #e0e0e0; }
.unit-card.available { border-left-color: #43a047; }
.unit-card.occupied  { border-left-color: #e53935; }
.unit-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.unit-number { font-weight: 700; font-size: 14px; color: #1a3a6b; }
.purpose-badge { font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 20px; }
.purpose-badge.renta { background: #e3f2fd; color: #1565c0; }
.purpose-badge.venta { background: #fff3e0; color: #e65100; }
.unit-type-row { display: flex; gap: 8px; margin-bottom: 4px; }
.unit-type, .unit-floor, .unit-area { font-size: 11px; color: #666; background: #f5f5f5; padding: 1px 6px; border-radius: 4px; }
.unit-price { font-weight: 700; font-size: 14px; margin: 6px 0; }
.unit-price.renta { color: #1565c0; }
.unit-price.venta { color: #e65100; }
.availability-badge { font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 5px; display: inline-block; margin: 6px 0; }
.availability-badge.free  { background: #e8f5e9; color: #2e7d32; }
.availability-badge.taken { background: #fce4ec; color: #c62828; }
.unit-notes { font-size: 11px; color: #777; margin: 4px 0; font-style: italic; }
.unit-actions { display: flex; gap: 6px; margin-top: 10px; align-items: center; }

/* ── Contracts ── */
.contracts-list { display: flex; flex-direction: column; gap: 12px; }
.contract-card { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border: 1px solid #e3e9f0; }
.contract-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
.tenant-name { font-weight: 700; font-size: 15px; color: #1a3a6b; margin-right: 8px; }
.contract-details { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: #555; }
.contract-notes { font-size: 12px; color: #777; margin-top: 8px; font-style: italic; }

/* ── Documents ── */
.docs-container { padding: 16px; }
.upload-form { background: #f7f9fc; border: 1px dashed #c0cfe0; border-radius: 8px; padding: 14px; margin-bottom: 16px; }
.upload-row { display: flex; gap: 10px; margin-bottom: 8px; flex-wrap: wrap; }
.upload-name { flex: 2; min-width: 140px; padding: 7px 10px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 13px; outline: none; }
.upload-type { flex: 1; min-width: 120px; padding: 7px 10px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 12px; outline: none; }
.file-picker { flex: 2; min-width: 160px; padding: 7px 12px; border: 1px solid #d0d9e8; border-radius: 6px; cursor: pointer; font-size: 12px; background: #fff; color: #555; display: flex; align-items: center; gap: 6px; }
.file-picker:hover { background: #e8f0fb; }
.docs-list { display: flex; flex-direction: column; gap: 8px; max-height: 380px; overflow-y: auto; }
.empty-state-sm { text-align: center; color: #aaa; font-style: italic; padding: 24px; font-size: 12px; }
.doc-row { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: #f7f9fc; border-radius: 6px; border: 1px solid #e3e9f0; }
.doc-icon { color: #1a3a6b; flex-shrink: 0; }
.doc-info { flex: 1; min-width: 0; }
.doc-name { font-weight: 600; font-size: 13px; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-meta { font-size: 11px; color: #888; }
.doc-actions { display: flex; gap: 4px; flex-shrink: 0; }

/* ── Modal ── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.45); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 16px; }
.modal-box { background: #fff; border-radius: 10px; width: 100%; max-width: 580px; max-height: 90vh; overflow-y: auto; box-shadow: 0 12px 40px rgba(0,0,0,0.25); }
.modal-box.wide { max-width: 700px; }
.modal-header { background: #1a3a6b; color: #fff; padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; font-weight: 700; font-size: 14px; border-radius: 10px 10px 0 0; position: sticky; top: 0; }
.modal-close { background: none; border: none; color: #fff; cursor: pointer; opacity: 0.8; padding: 0; display: flex; }
.modal-close:hover { opacity: 1; }
.modal-form { padding: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 16px; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group.full-width { grid-column: 1 / -1; }
.form-group label { font-weight: 600; font-size: 12px; color: #444; }
.form-group input, .form-group select, .form-group textarea { padding: 8px 10px; border: 1px solid #d0d9e8; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: #1a3a6b; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

/* ── Loading / Error ── */
.loading-overlay { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 80px 0; color: #555; }
.spinner { width: 40px; height: 40px; border: 4px solid #d0d9e8; border-top-color: #1a3a6b; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.error-banner { background: #fff3cd; border: 1px solid #f0ad4e; border-radius: 8px; padding: 14px 20px; margin-bottom: 16px; display: flex; align-items: center; gap: 12px; color: #7a4500; }
.retry-btn { margin-left: auto; background: #f0ad4e; border: none; border-radius: 5px; padding: 6px 14px; cursor: pointer; font-weight: 600; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .resumen-grid { grid-template-columns: 1fr; }
  .resumen-right { padding-left: 0; border-left: none; border-top: 2px solid #e8edf5; padding-top: 12px; }
  .form-grid { grid-template-columns: 1fr; }
  .header-row { flex-direction: column; gap: 12px; }
  .navbar { flex-direction: column; align-items: flex-start; padding: 8px 16px; }
  .navbar-tabs { width: 100%; }
}
""".lstrip()

files["index.css"] = "body { margin: 0; min-height: 100vh; background: #f0f4f8; }\n"

for rel_path, content in files.items():
    full = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {rel_path}")

print("\nAll feature files generated!")

