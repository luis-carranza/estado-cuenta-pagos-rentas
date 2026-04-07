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

          {/* Services section — only shown when editing an existing unit */}
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
