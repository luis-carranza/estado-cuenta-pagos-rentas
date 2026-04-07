import { useState, useEffect } from 'react';
import { X, Link2, Trash2, Search } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getLineMatches, createLineMatch, deleteStatementMatch, getProjects, getUnits } from '../services/api';

const fmt = v => v != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(v) : '—';

export default function LineMatchModal({ line, onClose, onMatchChanged }) {
  const [matches,  setMatches]  = useState([]);
  const [projects, setProjects] = useState([]);
  const [units,    setUnits]    = useState([]);
  const [selProj,  setSelProj]  = useState('');
  const [selUnit,  setSelUnit]  = useState('');
  const [notes,    setNotes]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [unitSearch, setUnitSearch] = useState('');

  const load = async () => {
    try {
      const [m, ps] = await Promise.all([getLineMatches(line.id), getProjects()]);
      setMatches(m); setProjects(ps);
    } catch { toast.error('Error cargando coincidencias'); }
  };

  useEffect(() => { load(); }, []); // eslint-disable-line

  const loadUnits = async pid => {
    if (!pid) { setUnits([]); setSelUnit(''); return; }
    try {
      const us = await getUnits(pid);
      setUnits(us); setSelUnit('');
    } catch { toast.error('Error cargando unidades'); }
  };

  const handleProjChange = e => {
    const v = e.target.value; setSelProj(v); setUnitSearch('');
    loadUnits(v);
  };

  const filteredUnits = units.filter(u =>
    !unitSearch ||
    u.unit_number.toLowerCase().includes(unitSearch.toLowerCase()) ||
    (u.current_tenant || '').toLowerCase().includes(unitSearch.toLowerCase())
  );

  const handleAddMatch = async () => {
    if (!selUnit) { toast.error('Selecciona una unidad'); return; }
    setLoading(true);
    try {
      const unit = units.find(u => String(u.id) === String(selUnit));
      await createLineMatch(line.id, {
        unit_id: Number(selUnit),
        match_notes: notes || null,
      });
      toast.success(`Coincidencia con ${unit?.unit_number} guardada`);
      setSelUnit(''); setNotes(''); setUnitSearch('');
      await load();
      onMatchChanged();
    } catch { toast.error('Error guardando coincidencia'); }
    finally { setLoading(false); }
  };

  const handleRemove = async mid => {
    if (!window.confirm('¿Quitar esta coincidencia?')) return;
    try {
      await deleteStatementMatch(mid);
      toast.success('Coincidencia eliminada');
      await load(); onMatchChanged();
    } catch { toast.error('Error eliminando'); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>🔗 Asignar línea a unidad</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <div className="modal-form">

          {/* Line summary */}
          <div className="match-line-summary">
            <div className="match-line-row">
              <span className="match-line-label">Descripción</span>
              <span className="match-line-val">{line.description || '—'}</span>
            </div>
            <div className="match-line-row">
              <span className="match-line-label">Referencia</span>
              <span className="match-line-val">{line.reference || '—'}</span>
            </div>
            <div className="match-line-row">
              <span className="match-line-label">Fecha</span>
              <span className="match-line-val">{line.line_date || '—'}</span>
            </div>
            <div className="match-line-row">
              <span className="match-line-label">Monto</span>
              <span className={`match-line-val font-bold ${line.transaction_type === 'CREDITO' ? 'credit-val' : 'debit-val'}`}>
                {line.transaction_type === 'DEBITO' ? '-' : '+'}{fmt(line.amount)}
              </span>
            </div>
          </div>

          {/* Existing matches */}
          <div className="match-section-title">Coincidencias actuales</div>
          {matches.length === 0 ? (
            <div className="empty-state-sm">Sin coincidencias — asigna abajo</div>
          ) : (
            <div className="matches-list">
              {matches.map(m => (
                <div key={m.id} className="match-row">
                  <Link2 size={14} className="match-icon"/>
                  <div className="match-row-info">
                    {m.unit_number && <span className="match-unit-num">Unidad {m.unit_number}</span>}
                    {m.tenant_name && <span className="match-tenant">{m.tenant_name}</span>}
                    {m.match_notes && <span className="match-notes-text">{m.match_notes}</span>}
                  </div>
                  <button className="action-btn delete-btn" style={{marginLeft:'auto'}} onClick={() => handleRemove(m.id)}>
                    <Trash2 size={13}/>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add match form */}
          <div className="match-section-title" style={{marginTop:16}}>Agregar coincidencia</div>
          <div className="form-grid" style={{marginTop:8}}>
            <div className="form-group">
              <label>Proyecto</label>
              <select value={selProj} onChange={handleProjChange}>
                <option value="">— seleccionar proyecto —</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            {selProj && (
              <div className="form-group">
                <label>Buscar unidad</label>
                <div style={{position:'relative'}}>
                  <Search size={13} style={{position:'absolute',left:8,top:'50%',transform:'translateY(-50%)',color:'#888'}}/>
                  <input style={{paddingLeft:26}} value={unitSearch}
                    onChange={e => setUnitSearch(e.target.value)}
                    placeholder="número o inquilino…" />
                </div>
              </div>
            )}
            {selProj && (
              <div className="form-group full-width">
                <label>Unidad / Departamento</label>
                <select value={selUnit} onChange={e => setSelUnit(e.target.value)}>
                  <option value="">— seleccionar unidad —</option>
                  {filteredUnits.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.unit_number}
                      {u.current_tenant ? ` — ${u.current_tenant}` : ' (disponible)'}
                      {u.rent_price ? ` — ${fmt(u.rent_price)}/mes` : ''}
                    </option>
                  ))}
                </select>
              </div>
            )}
            <div className="form-group full-width">
              <label>Notas de conciliación (opcional)</label>
              <input value={notes} onChange={e => setNotes(e.target.value)}
                placeholder="ej. Pago de renta marzo 2026…" />
            </div>
          </div>

          <div className="modal-actions">
            <button className="btn-secondary" onClick={onClose}>Cerrar</button>
            <button className="btn-primary" onClick={handleAddMatch} disabled={loading || !selUnit}>
              <Link2 size={14}/> Asignar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

