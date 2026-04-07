import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, ChevronLeft, ChevronRight, Home, FileText, LayoutGrid, List } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getUnits, createUnit, updateUnit, deleteUnit } from '../services/api';
import UnitModal from './UnitModal';
import DocumentsPanel from './DocumentsPanel';

const fmt = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : '—';

export default function UnitsPage({ project, onBack, onSelectUnit, hideBackButton = false }) {
  const [units, setUnits]     = useState([]);
  const [modal, setModal]     = useState(null);
  const [docsUnit, setDocsUnit] = useState(null);
  const [viewMode, setViewMode] = useState('card'); // 'card' | 'list'
  const [search, setSearch]   = useState('');

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

  const filtered = units.filter(u => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      u.unit_number?.toLowerCase().includes(q) ||
      u.current_tenant?.toLowerCase().includes(q) ||
      u.unit_type?.toLowerCase().includes(q) ||
      u.notes?.toLowerCase().includes(q)
    );
  });

  return (
    <div>
      {/* ── Header ── */}
      <div className="page-header">
        <div className="breadcrumb">
          {!hideBackButton && (
            <button className="btn-back" onClick={onBack}><ChevronLeft size={16}/> Proyectos</button>
          )}
          {!hideBackButton && <span className="breadcrumb-sep">/</span>}
          <h2 className="page-title"><Home size={18}/> {project.name} — Unidades</h2>
        </div>
        <div className="units-toolbar">
          {/* Search */}
          <input
            className="units-search"
            placeholder="Buscar unidad, inquilino…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {/* View toggle */}
          <div className="view-toggle">
            <button
              className={`view-btn ${viewMode === 'card' ? 'active' : ''}`}
              title="Vista tarjetas"
              onClick={() => setViewMode('card')}
            ><LayoutGrid size={15}/></button>
            <button
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              title="Vista lista"
              onClick={() => setViewMode('list')}
            ><List size={15}/></button>
          </div>
          <button className="btn-primary" onClick={() => setModal('new')}><Plus size={14}/> Nueva Unidad</button>
        </div>
      </div>

      {/* ── Stats bar ── */}
      <div className="units-stats-bar">
        <span className="ustat total">{units.length} unidades</span>
        <span className="ustat occupied">{units.filter(u => !u.is_available).length} ocupadas</span>
        <span className="ustat available">{units.filter(u => u.is_available).length} disponibles</span>
        {search && <span className="ustat filtered">({filtered.length} resultado{filtered.length !== 1 ? 's' : ''})</span>}
      </div>

      {filtered.length === 0 && <div className="empty-state">No se encontraron unidades.</div>}

      {/* ── CARD VIEW ── */}
      {viewMode === 'card' && (
        <div className="units-grid">
          {filtered.map(u => (
            <div key={u.id} className={`unit-card ${u.is_available ? 'available' : 'occupied'}`}>
              <div className="unit-header">
                <span className="unit-number">{u.unit_number}</span>
                <span className={`purpose-badge ${u.purpose === 'RENTA' ? 'renta' : 'venta'}`}>{u.purpose}</span>
              </div>
              <div className="unit-type-row">
                <span className="unit-type">{u.unit_type}</span>
                {u.floor != null && <span className="unit-floor">Piso {u.floor}</span>}
                {u.area_sqm  && <span className="unit-area">{u.area_sqm} m²</span>}
              </div>
              {u.purpose === 'RENTA' && u.rent_price &&
                <div className="unit-price renta">{fmt(u.rent_price)}/mes</div>}
              {u.purpose === 'VENTA' && u.sale_price &&
                <div className="unit-price venta">{fmt(u.sale_price)}</div>}
              <div className={`availability-badge ${u.is_available ? 'free' : 'taken'}`}>
                {u.is_available ? 'Disponible' : `Ocupada${u.current_tenant ? ` — ${u.current_tenant}` : ''}`}
              </div>
              {u.notes && <p className="unit-notes">{u.notes}</p>}
              <div className="unit-actions">
                <button className="btn-outline flex-1" onClick={() => onSelectUnit(u)}>
                  <FileText size={13}/> Contratos <ChevronRight size={13}/>
                </button>
                <button className="btn-outline flex-1" onClick={() => setDocsUnit(u)}>
                  Docs ({u.contract_count||0})
                </button>
                <button className="action-btn edit-btn"   onClick={() => setModal(u)}><Pencil size={13}/></button>
                <button className="action-btn delete-btn" onClick={() => handleDelete(u.id, u.unit_number)}><Trash2 size={13}/></button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── LIST VIEW ── */}
      {viewMode === 'list' && (
        <div className="table-wrapper card">
          <table className="units-table">
            <thead>
              <tr>
                <th>Unidad</th>
                <th>Tipo</th>
                <th>Piso</th>
                <th>Propósito</th>
                <th>Inquilino</th>
                <th className="text-right">Renta / Precio</th>
                <th>Estado</th>
                <th>Notas</th>
                <th className="text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u, i) => (
                <tr key={u.id} className={i % 2 === 0 ? 'row-even' : 'row-odd'}>
                  <td className="ul-unit-num">{u.unit_number}</td>
                  <td><span className="unit-type">{u.unit_type}</span></td>
                  <td className="text-center">{u.floor ?? '—'}</td>
                  <td>
                    <span className={`purpose-badge ${u.purpose === 'RENTA' ? 'renta' : 'venta'}`}>
                      {u.purpose}
                    </span>
                  </td>
                  <td className="ul-tenant">{u.current_tenant || <span className="ul-empty">—</span>}</td>
                  <td className="monto-cell">
                    {u.purpose === 'RENTA' ? fmt(u.rent_price) : fmt(u.sale_price)}
                  </td>
                  <td>
                    <span className={`availability-badge ${u.is_available ? 'free' : 'taken'}`}>
                      {u.is_available ? 'Disponible' : 'Ocupada'}
                    </span>
                  </td>
                  <td className="ul-notes">{u.notes || <span className="ul-empty">—</span>}</td>
                  <td>
                    <div className="actions-cell" style={{justifyContent:'center'}}>
                      <button className="action-btn edit-btn" title="Contratos" onClick={() => onSelectUnit(u)}>
                        <FileText size={13}/>
                      </button>
                      <button className="action-btn" style={{background:'#f3e8ff',color:'#6a1b9a'}} title="Documentos" onClick={() => setDocsUnit(u)}>
                        <span style={{fontSize:11,fontWeight:700}}>{u.contract_count||0}</span>
                      </button>
                      <button className="action-btn edit-btn"   title="Editar"    onClick={() => setModal(u)}><Pencil size={13}/></button>
                      <button className="action-btn delete-btn" title="Eliminar"  onClick={() => handleDelete(u.id, u.unit_number)}><Trash2 size={13}/></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
            {/* Footer totals */}
            {filtered.length > 0 && (
              <tfoot>
                <tr className="total-footer">
                  <td colSpan={5} className="footer-label">
                    Total rentas ({filtered.filter(u=>u.purpose==='RENTA'&&!u.is_available).length} ocupadas)
                  </td>
                  <td className="footer-total">
                    {fmt(filtered.reduce((s,u) => s + (u.purpose==='RENTA' && !u.is_available ? (u.rent_price||0) : 0), 0))}
                  </td>
                  <td colSpan={3}></td>
                </tr>
              </tfoot>
            )}
          </table>
        </div>
      )}

      {modal && <UnitModal unit={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
      {docsUnit && <DocumentsPanel relatedType="unit" relatedId={docsUnit.id}
        title={`Docs — ${docsUnit.unit_number}`} onClose={() => setDocsUnit(null)} />}
    </div>
  );
}
