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
