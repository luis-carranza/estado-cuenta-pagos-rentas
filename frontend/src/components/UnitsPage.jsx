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
            {/* Service status badges */}
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
