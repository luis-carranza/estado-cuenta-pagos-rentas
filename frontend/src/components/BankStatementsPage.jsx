import { useState, useEffect } from 'react';
import { Landmark, Plus, Pencil, Trash2, X, ChevronRight, RefreshCw } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  getBankStatements, createBankStatement, updateBankStatement, deleteBankStatement,
  getProjects,
} from '../services/api';

const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                 'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const EMPTY = {
  project_id: '', bank_name: '', account_number: '', account_alias: '',
  period_month: '', period_year: new Date().getFullYear(), description: '',
};

// ── Modal ────────────────────────────────────────────────────────────────────
function StatementModal({ statement, projects, onClose, onSave }) {
  const [form, setForm] = useState(statement
    ? { ...statement, project_id: statement.project_id || '' }
    : { ...EMPTY });

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async e => {
    e.preventDefault();
    const payload = {
      ...form,
      project_id:   form.project_id   ? Number(form.project_id)   : null,
      period_month: form.period_month ? Number(form.period_month) : null,
      period_year:  form.period_year  ? Number(form.period_year)  : null,
    };
    await onSave(payload);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{statement ? 'Editar Estado de Banco' : 'Nuevo Estado de Banco'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Banco</label>
              <input value={form.bank_name} onChange={e => set('bank_name', e.target.value)}
                placeholder="ej. BBVA, Santander…" />
            </div>
            <div className="form-group">
              <label>Alias de cuenta</label>
              <input value={form.account_alias} onChange={e => set('account_alias', e.target.value)}
                placeholder="ej. Cuenta Principal" />
            </div>
            <div className="form-group">
              <label>Número de cuenta</label>
              <input value={form.account_number} onChange={e => set('account_number', e.target.value)}
                placeholder="últimos 4 dígitos…" />
            </div>
            <div className="form-group">
              <label>Proyecto</label>
              <select value={form.project_id} onChange={e => set('project_id', e.target.value)}>
                <option value="">— General (sin proyecto) —</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Mes del estado</label>
              <select value={form.period_month} onChange={e => set('period_month', e.target.value)}>
                <option value="">— seleccionar —</option>
                {MONTHS.map((m,i) => <option key={i+1} value={i+1}>{m}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Año del estado</label>
              <select value={form.period_year} onChange={e => set('period_year', e.target.value)}>
                {[2024,2025,2026,2027].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            <div className="form-group full-width">
              <label>Descripción / notas</label>
              <textarea rows={2} value={form.description}
                onChange={e => set('description', e.target.value)}
                placeholder="Notas opcionales…" />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary">
              {statement ? 'Guardar cambios' : 'Crear estado'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Main Page ────────────────────────────────────────────────────────────────
export default function BankStatementsPage({ onOpenDetail }) {
  const [statements, setStatements] = useState([]);
  const [projects, setProjects]     = useState([]);
  const [loading, setLoading]       = useState(true);
  const [modal, setModal]           = useState(false);
  const [editItem, setEditItem]     = useState(null);

  // filters
  const [fProject, setFProject] = useState('');
  const [fMonth, setFMonth]     = useState('');
  const [fYear, setFYear]       = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const params = {};
      if (fProject) params.project_id  = fProject;
      if (fMonth)   params.period_month = fMonth;
      if (fYear)    params.period_year  = fYear;
      const [ss, ps] = await Promise.all([getBankStatements(params), getProjects()]);
      setStatements(ss); setProjects(ps);
    } catch { toast.error('Error cargando estados de banco'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []); // eslint-disable-line

  const handleSave = async payload => {
    try {
      if (editItem) { await updateBankStatement(editItem.id, payload); toast.success('Estado actualizado'); }
      else          { await createBankStatement(payload);              toast.success('Estado creado'); }
      setModal(false); setEditItem(null); load();
    } catch { toast.error('Error guardando estado'); }
  };

  const handleDelete = async s => {
    if (!window.confirm(`¿Eliminar estado "${s.bank_name || 'sin banco'}" — ${s.period_month ? MONTHS[s.period_month-1] : '?'} ${s.period_year || ''}?`)) return;
    try { await deleteBankStatement(s.id); toast.success('Estado eliminado'); load(); }
    catch { toast.error('Error eliminando'); }
  };

  const fmt = v => v != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(v) : '—';

  return (
    <div>
      {/* ── Header ── */}
      <div className="page-header">
        <h2 className="page-title"><Landmark size={20}/> Estados de Banco</h2>
        <button className="btn-primary" onClick={() => { setEditItem(null); setModal(true); }}>
          <Plus size={15}/> Nuevo estado
        </button>
      </div>

      {/* ── Filters ── */}
      <div className="card mb-6">
        <div className="periodo-bar">
          <span className="periodo-label">Filtrar:</span>
          <select className="project-select" value={fProject} onChange={e => setFProject(e.target.value)}>
            <option value="">Todos los proyectos</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select value={fMonth} onChange={e => setFMonth(e.target.value)}>
            <option value="">Todos los meses</option>
            {MONTHS.map((m,i) => <option key={i+1} value={i+1}>{m}</option>)}
          </select>
          <select value={fYear} onChange={e => setFYear(e.target.value)}>
            <option value="">Todos los años</option>
            {[2024,2025,2026,2027].map(y => <option key={y} value={y}>{y}</option>)}
          </select>
          <button className="btn-primary btn-sm" onClick={load}><RefreshCw size={13}/> Aplicar</button>
          {(fProject || fMonth || fYear) &&
            <button className="btn-clear" onClick={() => { setFProject(''); setFMonth(''); setFYear(''); }}>Limpiar</button>}
        </div>
      </div>

      {/* ── List ── */}
      {loading ? (
        <div className="loading-overlay"><div className="spinner"/><span>Cargando…</span></div>
      ) : statements.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <Landmark size={40} style={{margin:'0 auto 12px',color:'#c0cfe0'}}/>
            <p>No hay estados de banco. Crea el primero.</p>
          </div>
        </div>
      ) : (
        <div className="bs-list">
          {statements.map(s => {
            const matched   = s.matched_count || 0;
            const total     = s.line_count || 0;
            const pct       = total > 0 ? Math.round(matched / total * 100) : 0;
            const periodStr = s.period_month ? `${MONTHS[s.period_month-1]} ${s.period_year}` : (s.period_year || '—');
            return (
              <div key={s.id} className="bs-card card mb-6">
                <div className="bs-card-left">
                  <div className="bs-bank-icon"><Landmark size={22}/></div>
                  <div className="bs-info">
                    <div className="bs-title">
                      {s.bank_name || 'Banco sin nombre'}
                      {s.account_alias && <span className="bs-alias"> — {s.account_alias}</span>}
                    </div>
                    <div className="bs-meta">
                      {s.account_number && <span className="bs-chip">•••• {s.account_number}</span>}
                      <span className="bs-chip period">{periodStr}</span>
                      {s.project_name && <span className="bs-chip project">{s.project_name}</span>}
                    </div>
                    {s.description && <div className="bs-desc">{s.description}</div>}
                  </div>
                </div>

                <div className="bs-card-middle">
                  <div className="bs-stat-row">
                    <span className="bs-stat-label">Créditos</span>
                    <span className="bs-stat-val credit">{fmt(s.total_credits)}</span>
                  </div>
                  <div className="bs-stat-row">
                    <span className="bs-stat-label">Débitos</span>
                    <span className="bs-stat-val debit">{fmt(s.total_debits)}</span>
                  </div>
                  <div className="bs-stat-row">
                    <span className="bs-stat-label">Líneas</span>
                    <span className="bs-stat-val">{total}</span>
                  </div>
                </div>

                <div className="bs-card-right">
                  <div className="bs-match-label">Conciliado</div>
                  <div className="occ-bar-wrap" style={{minWidth:120}}>
                    <div className="occ-bar-bg">
                      <div className="occ-bar-fill"
                        style={{width:`${pct}%`, background: pct===100?'#43a047':'#1a3a6b'}}/>
                    </div>
                    <span className="occ-bar-label" style={{fontSize:13}}>{pct}%</span>
                  </div>
                  <div style={{fontSize:11,color:'#888',marginTop:3}}>{matched}/{total} líneas</div>
                </div>

                <div className="bs-card-actions">
                  <button className="btn-outline" onClick={() => onOpenDetail(s)}>
                    Ver líneas <ChevronRight size={13}/>
                  </button>
                  <button className="action-btn edit-btn" onClick={() => { setEditItem(s); setModal(true); }}>
                    <Pencil size={14}/>
                  </button>
                  <button className="action-btn delete-btn" onClick={() => handleDelete(s)}>
                    <Trash2 size={14}/>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {modal && (
        <StatementModal
          statement={editItem}
          projects={projects}
          onClose={() => { setModal(false); setEditItem(null); }}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

