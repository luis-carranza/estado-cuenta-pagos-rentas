import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

export default function ProjectModal({ project, onClose, onSave }) {
  const [form, setForm] = useState({
    name: '', description: '', address: '',
    latitude: '', longitude: '', total_budget: '', budget_notes: ''
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setForm(project ? {
      name:         project.name         || '',
      description:  project.description  || '',
      address:      project.address      || '',
      latitude:     project.latitude     ?? '',
      longitude:    project.longitude    ?? '',
      total_budget: project.total_budget ?? '',
      budget_notes: project.budget_notes || '',
    } : { name: '', description: '', address: '', latitude: '', longitude: '', total_budget: '', budget_notes: '' });
  }, [project]);

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));
  const submit = async e => {
    e.preventDefault(); setSaving(true);
    try {
      await onSave({
        ...form,
        latitude:     form.latitude     !== '' ? parseFloat(form.latitude)     : null,
        longitude:    form.longitude    !== '' ? parseFloat(form.longitude)    : null,
        total_budget: form.total_budget !== '' ? parseFloat(form.total_budget) : null,
      });
    } finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{project ? `Editar: ${project.name}` : 'Nuevo Proyecto'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form onSubmit={submit} className="modal-form">
          <div className="form-grid">
            <div className="form-group full-width">
              <label>Nombre del Proyecto *</label>
              <input required name="name" value={form.name} onChange={handle} placeholder="Ej: Intercity / Condesa 1"/>
            </div>
            <div className="form-group full-width">
              <label>Dirección</label>
              <input name="address" value={form.address} onChange={handle} placeholder="Calle, número, colonia, ciudad…"/>
            </div>
            <div className="form-group">
              <label>Latitud</label>
              <input name="latitude" type="number" step="any" value={form.latitude} onChange={handle} placeholder="19.4326"/>
            </div>
            <div className="form-group">
              <label>Longitud</label>
              <input name="longitude" type="number" step="any" value={form.longitude} onChange={handle} placeholder="-99.1332"/>
            </div>
            <div className="form-group">
              <label>Presupuesto Total (MXN)</label>
              <input name="total_budget" type="number" step="any" min="0" value={form.total_budget} onChange={handle} placeholder="0.00"/>
            </div>
            <div className="form-group">
              <label>Notas de Presupuesto</label>
              <input name="budget_notes" value={form.budget_notes} onChange={handle} placeholder="Notas adicionales…"/>
            </div>
            <div className="form-group full-width">
              <label>Descripción</label>
              <textarea name="description" value={form.description} onChange={handle} rows={3} style={{resize:'vertical'}}/>
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Guardando…' : 'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
