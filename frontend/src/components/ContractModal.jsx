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
