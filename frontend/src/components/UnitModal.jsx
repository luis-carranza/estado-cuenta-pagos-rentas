import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const empty = { unit_number:'', unit_type:'DEPTO', purpose:'RENTA', floor:'', area_sqm:'',
                rent_price:'', sale_price:'', is_available:true, notes:'' };
const TYPES = ['DEPTO','LOCAL','OFICINA','BODEGA','CASA','COMERCIAL','OTRO'];

export default function UnitModal({ unit, onClose, onSave }) {
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  useEffect(() => { setForm(unit ? { ...empty, ...unit, floor: unit.floor??'', area_sqm: unit.area_sqm??'',
    rent_price: unit.rent_price??'', sale_price: unit.sale_price??'', is_available: !!unit.is_available } : empty); }, [unit]);

  const set = e => { const {name, value, type, checked} = e.target; setForm(f => ({...f, [name]: type==='checkbox' ? checked : value})); };
  const submit = async e => { e.preventDefault(); setSaving(true);
    try { await onSave({ ...form, floor: form.floor||null, area_sqm: form.area_sqm||null,
      rent_price: form.rent_price||null, sale_price: form.sale_price||null }); }
    finally { setSaving(false); }
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
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>{saving?'Guardando...':'Guardar'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
