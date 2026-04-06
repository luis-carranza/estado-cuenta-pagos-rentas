import { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const emptyForm = {
  fecha: '',
  ubicacion: '',
  desarrollo: '',
  mes_correspondiente: '',
  cliente: '',
  concepto: '',
  monto: '',
  forma_de_pago: 'TRANSFERENCIA',
  semana_fiscal: '',
};

export default function PagoModal({ pago, onClose, onSave }) {
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (pago) {
      setForm({
        fecha: pago.fecha || '',
        ubicacion: pago.ubicacion || '',
        desarrollo: pago.desarrollo || '',
        mes_correspondiente: pago.mes_correspondiente || '',
        cliente: pago.cliente || '',
        concepto: pago.concepto || '',
        monto: pago.monto ?? '',
        forma_de_pago: pago.forma_de_pago || 'TRANSFERENCIA',
        semana_fiscal: pago.semana_fiscal ?? '',
      });
    } else {
      setForm(emptyForm);
    }
  }, [pago]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({
        ...form,
        monto: parseFloat(form.monto) || 0,
        semana_fiscal: form.semana_fiscal ? parseInt(form.semana_fiscal) : null,
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <span>{pago ? `Editar Pago #${pago.consecutivo}` : 'Nuevo Pago'}</span>
          <button className="modal-close" onClick={onClose}><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-grid">
            <div className="form-group">
              <label>Fecha</label>
              <input type="date" name="fecha" value={form.fecha} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Ubicación</label>
              <input type="text" name="ubicacion" value={form.ubicacion} onChange={handleChange} placeholder="Ej: DEPTO 437E" />
            </div>
            <div className="form-group">
              <label>Desarrollo</label>
              <input type="text" name="desarrollo" value={form.desarrollo} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Mes Correspondiente</label>
              <input type="text" name="mes_correspondiente" value={form.mes_correspondiente} onChange={handleChange} placeholder="Ej: 9 DE 12" />
            </div>
            <div className="form-group full-width">
              <label>Cliente *</label>
              <input required type="text" name="cliente" value={form.cliente} onChange={handleChange} />
            </div>
            <div className="form-group full-width">
              <label>Concepto *</label>
              <input required type="text" name="concepto" value={form.concepto} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Monto *</label>
              <input required type="number" step="0.01" min="0" name="monto" value={form.monto} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Forma de Pago *</label>
              <select required name="forma_de_pago" value={form.forma_de_pago} onChange={handleChange}>
                <option value="EFECTIVO">EFECTIVO</option>
                <option value="TRANSFERENCIA">TRANSFERENCIA</option>
              </select>
            </div>
            <div className="form-group">
              <label>Semana Fiscal</label>
              <input type="number" name="semana_fiscal" value={form.semana_fiscal} onChange={handleChange} min="1" max="53" />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
