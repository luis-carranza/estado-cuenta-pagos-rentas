import { useState, useEffect } from 'react';
import {
  ChevronLeft, Building2, DollarSign, Home, MapPin, FolderOpen,
  TrendingUp, Users, Percent, ArrowUpRight, FileText, Download, Trash2,
  Landmark, ChevronDown, ChevronRight, Link2, CheckCircle2, Circle,
  TrendingDown, RefreshCw
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  getProjectBudget, getDocuments, deleteDocument, uploadDocument,
  getProjectBankTransactions,
} from '../services/api';
import UnitsPage from './UnitsPage';

const fmt  = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : '—';
const pct  = n => `${n ?? 0}%`;

// ── KPI card ────────────────────────────────────────────────────────────────
function KpiCard({ label, value, sub, color='#1a3a6b', IconComponent }) {
  return (
    <div className="kpi-card">
      <div className="kpi-icon" style={{ background: color + '18', color }}>
        <IconComponent size={20}/>
      </div>
      <div className="kpi-body">
        <div className="kpi-value" style={{ color }}>{value}</div>
        <div className="kpi-label">{label}</div>
        {sub && <div className="kpi-sub">{sub}</div>}
      </div>
    </div>
  );
}

// ── Occupancy bar ───────────────────────────────────────────────────────────
function OccupancyBar({ value }) {
  const color = value >= 80 ? '#2e7d32' : value >= 50 ? '#e65100' : '#c62828';
  return (
    <div className="occ-bar-wrap">
      <div className="occ-bar-bg">
        <div className="occ-bar-fill" style={{ width: `${value}%`, background: color }}/>
      </div>
      <span className="occ-bar-label" style={{ color }}>{value}%</span>
    </div>
  );
}

// ── Documents tab (per project) ──────────────────────────────────────────────

// ── Documents tab (per project) ──────────────────────────────────────────────
function ProjectDocsTab({ projectId }) {
  const [docs, setDocs]   = useState([]);
  const [uploading, setUL] = useState(false);
  const [form, setForm]   = useState({ name: '', document_type: 'CONTRATO', file: null });

  const load = () => getDocuments({ related_type: 'project', related_id: projectId }).then(setDocs);
  useEffect(() => { load(); }, [projectId]);

  const handleUpload = async e => {
    e.preventDefault();
    if (!form.file || !form.name) return toast.error('Nombre y archivo requeridos');
    const fd = new FormData();
    fd.append('related_type', 'project');
    fd.append('related_id',   projectId);
    fd.append('name',         form.name);
    fd.append('document_type',form.document_type);
    fd.append('file',         form.file);
    setUL(true);
    try { await uploadDocument(fd); toast.success('Documento subido'); setForm({ name:'', document_type:'CONTRATO', file:null }); load(); }
    catch { toast.error('Error subiendo documento'); }
    finally { setUL(false); }
  };

  const handleDelete = async id => {
    if (!window.confirm('¿Eliminar este documento?')) return;
    try { await deleteDocument(id); toast.success('Eliminado'); load(); }
    catch { toast.error('Error eliminando'); }
  };

  const fmtSize = b => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(0)} KB`;

  return (
    <div className="docs-container">
      {/* Upload form */}
      <form className="upload-form" onSubmit={handleUpload}>
        <div className="upload-row">
          <input className="upload-name" placeholder="Nombre del documento" value={form.name}
            onChange={e=>setForm(f=>({...f,name:e.target.value}))}/>
          <select className="upload-type" value={form.document_type}
            onChange={e=>setForm(f=>({...f,document_type:e.target.value}))}>
            {['CONTRATO','PLANO','PERMISO','PRESUPUESTO','FACTURA','FOTO','OTRO'].map(t=>
              <option key={t} value={t}>{t}</option>)}
          </select>
          <label className="file-picker">
            <FolderOpen size={14}/> {form.file ? form.file.name : 'Elegir archivo…'}
            <input type="file" style={{display:'none'}} onChange={e=>setForm(f=>({...f,file:e.target.files[0]}))}/>
          </label>
          <button type="submit" className="btn-primary btn-sm" disabled={uploading}>
            {uploading ? 'Subiendo…' : 'Subir'}
          </button>
        </div>
      </form>

      {/* List */}
      {docs.length === 0 && <div className="empty-state-sm">No hay documentos para este proyecto.</div>}
      <div className="docs-list">
        {docs.map(d => (
          <div key={d.id} className="doc-row">
            <FileText size={18} className="doc-icon"/>
            <div className="doc-info">
              <span className="doc-name">{d.name}</span>
              <span className="doc-meta">{d.document_type} · {fmtSize(d.file_size||0)} · {d.uploaded_at?.slice(0,10)}</span>
            </div>
            <div className="doc-actions">
              <a className="btn-sm-outline" href={`/api/documents/${d.id}/download`} target="_blank" rel="noreferrer">
                <Download size={12}/> Descargar
              </a>
              <button className="action-btn delete-btn" onClick={()=>handleDelete(d.id)}><Trash2 size={13}/></button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Bancos tab (bank statements + lines per project) ─────────────────────────
const MONTHS_ES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                   'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const fmtCur = v => v != null
  ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(v)
  : '—';

function StatementBlock({ statement }) {
  const [open, setOpen] = useState(true);
  const periodStr = statement.period_month
    ? `${MONTHS_ES[statement.period_month-1]} ${statement.period_year}`
    : (statement.period_year || '—');
  const credits = statement.lines.filter(l=>l.transaction_type==='CREDITO').reduce((s,l)=>s+l.amount,0);
  const debits  = statement.lines.filter(l=>l.transaction_type==='DEBITO').reduce((s,l)=>s+l.amount,0);
  const matched = statement.lines.filter(l=>l.is_matched).length;
  const total   = statement.lines.length;
  const pct     = total > 0 ? Math.round(matched/total*100) : 0;

  return (
    <div className="bs-block card mb-6">
      {/* ── Statement header (clickable to collapse) ── */}
      <div className="bs-block-header" onClick={()=>setOpen(o=>!o)}>
        <div className="bs-block-left">
          <div className="bs-bank-icon"><Landmark size={18}/></div>
          <div>
            <div className="bs-title">
              {statement.bank_name || 'Banco'}
              {statement.account_alias && <span className="bs-alias"> — {statement.account_alias}</span>}
            </div>
            <div className="bs-meta">
              {statement.account_number && <span className="bs-chip">•••• {statement.account_number}</span>}
              <span className="bs-chip period">{periodStr}</span>
            </div>
          </div>
        </div>
        <div className="bs-block-stats">
          <div className="bs-stat-item">
            <TrendingUp size={13} color="#2e7d32"/>
            <span className="bs-stat-num credit">{fmtCur(credits)}</span>
            <span className="bs-stat-lbl">créditos</span>
          </div>
          <div className="bs-stat-item">
            <TrendingDown size={13} color="#c62828"/>
            <span className="bs-stat-num debit">{fmtCur(debits)}</span>
            <span className="bs-stat-lbl">débitos</span>
          </div>
          <div className="bs-stat-item">
            <Link2 size={13} color="#1565c0"/>
            <span className="bs-stat-num">{matched}/{total}</span>
            <span className="bs-stat-lbl">conciliadas ({pct}%)</span>
          </div>
        </div>
        <div className="bs-block-toggle">
          {open ? <ChevronDown size={16}/> : <ChevronRight size={16}/>}
        </div>
      </div>

      {/* ── Lines table ── */}
      {open && (
        <div className="table-wrapper" style={{marginTop:0}}>
          {statement.lines.length === 0 ? (
            <div className="empty-state-sm">Sin líneas en este estado.</div>
          ) : (
            <table className="pagos-table" style={{fontSize:12}}>
              <thead>
                <tr>
                  <th style={{width:24}}></th>
                  <th style={{width:100}}>Fecha</th>
                  <th>Descripción</th>
                  <th style={{width:110}}>Referencia</th>
                  <th style={{textAlign:'right',width:110}}>Monto</th>
                  <th style={{width:80}}>Tipo</th>
                  <th style={{width:150}}>Unidad asignada</th>
                </tr>
              </thead>
              <tbody>
                {statement.lines.map((l, idx) => (
                  <tr key={l.id} className={idx%2===0?'row-even':'row-odd'}>
                    <td className="text-center">
                      {l.is_matched
                        ? <CheckCircle2 size={13} color="#43a047" title="Conciliada"/>
                        : <Circle size={13} color="#ccc" title="Sin conciliar"/>}
                    </td>
                    <td style={{whiteSpace:'nowrap'}}>{l.line_date||'—'}</td>
                    <td>
                      <div style={{fontWeight:500,lineHeight:1.3}}>{l.description||'—'}</div>
                      {l.notes && <div style={{fontSize:10,color:'#999',fontStyle:'italic'}}>{l.notes}</div>}
                    </td>
                    <td style={{fontSize:11,color:'#777'}}>{l.reference||'—'}</td>
                    <td style={{textAlign:'right'}}>
                      <span className={l.transaction_type==='CREDITO'?'credit-val':'debit-val'} style={{fontWeight:700}}>
                        {l.transaction_type==='DEBITO'?'-':'+'}{fmtCur(l.amount)}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${l.transaction_type==='CREDITO'?'badge-activo':'badge-cancelado'}`}
                        style={{fontSize:10}}>
                        {l.transaction_type==='CREDITO'?'CRÉDITO':'DÉBITO'}
                      </span>
                    </td>
                    <td>
                      {l.matched_unit
                        ? <span className="badge badge-activo" style={{fontSize:10}}>
                            {l.matched_unit}{l.matched_tenant?` · ${l.matched_tenant}`:''}
                          </span>
                        : <span style={{color:'#ccc',fontSize:11}}>—</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="total-footer">
                  <td colSpan={4} className="footer-label">{total} movimientos</td>
                  <td className="footer-total" style={{textAlign:'right'}}>
                    <div className="credit-val">{fmtCur(credits)}</div>
                    <div className="debit-val" style={{fontSize:11}}>{fmtCur(debits)}</div>
                  </td>
                  <td colSpan={2}/>
                </tr>
              </tfoot>
            </table>
          )}
        </div>
      )}
    </div>
  );
}

function ProjectBancosTab({ projectId }) {
  const [statements, setStatements] = useState([]);
  const [loading, setLoading]       = useState(true);
  const [filterType, setFilterType] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await getProjectBankTransactions(projectId);
      setStatements(data);
    } catch { toast.error('Error cargando estados bancarios'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, [projectId]); // eslint-disable-line

  // Overall KPIs across all statements
  const allLines   = statements.flatMap(s => s.lines);
  const totCredits = allLines.filter(l=>l.transaction_type==='CREDITO').reduce((s,l)=>s+l.amount,0);
  const totDebits  = allLines.filter(l=>l.transaction_type==='DEBITO').reduce((s,l)=>s+l.amount,0);
  const totMatched = allLines.filter(l=>l.is_matched).length;

  // Filter visible lines inside each statement
  const filtered = statements.map(s => ({
    ...s,
    lines: filterType ? s.lines.filter(l=>l.transaction_type===filterType) : s.lines,
  }));

  if (loading) return <div className="loading-overlay"><div className="spinner"/><span>Cargando…</span></div>;

  if (statements.length === 0) return (
    <div className="empty-state">
      <Landmark size={40} style={{margin:'0 auto 12px',color:'#c0cfe0'}}/>
      <p>No hay estados de banco asociados a este proyecto.</p>
      <p style={{fontSize:12,color:'#888',marginTop:6}}>Ve a la sección Bancos para crear uno y asignarlo a este proyecto.</p>
    </div>
  );

  return (
    <div>
      {/* KPIs */}
      <div className="kpi-grid mb-6">
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e8f5e9'}}><TrendingUp size={20} color="#2e7d32"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#2e7d32'}}>{fmtCur(totCredits)}</div>
            <div className="kpi-label">Total créditos</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#fce4ec'}}><TrendingDown size={20} color="#c62828"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#c62828'}}>{fmtCur(totDebits)}</div>
            <div className="kpi-label">Total débitos</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e3f2fd'}}><Landmark size={20} color="#1565c0"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#1565c0'}}>{statements.length}</div>
            <div className="kpi-label">Estados de banco</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#f3e8ff'}}><Link2 size={20} color="#6a1b9a"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#6a1b9a'}}>{totMatched}/{allLines.length}</div>
            <div className="kpi-label">Líneas conciliadas</div>
          </div>
        </div>
      </div>

      {/* Filter bar */}
      <div className="card mb-6">
        <div className="filters-bar">
          <div className="filter-group">
            <span>Tipo:</span>
            <select value={filterType} onChange={e=>setFilterType(e.target.value)}>
              <option value="">Todos</option>
              <option value="CREDITO">Solo créditos</option>
              <option value="DEBITO">Solo débitos</option>
            </select>
          </div>
          <button className="btn-outline" onClick={load}><RefreshCw size={13}/> Recargar</button>
          {filterType && <button className="btn-clear" onClick={()=>setFilterType('')}>Limpiar</button>}
        </div>
      </div>

      {/* Statement blocks */}
      {filtered.map(s => <StatementBlock key={s.id} statement={s}/>)}
    </div>
  );
}

// ── Main component ───────────────────────────────────────────────────────────
const TABS = [
  { id: 'budget',    label: 'Presupuesto', icon: DollarSign },
  { id: 'units',     label: 'Unidades',    icon: Home        },
  { id: 'bancos',    label: 'Banco$',      icon: Landmark    },
  { id: 'location',  label: 'Ubicación',   icon: MapPin      },
  { id: 'documents', label: 'Documentos',  icon: FolderOpen  },
];

export default function ProjectDetailsPage({ project, onBack, onEditProject }) {
  const [activeTab, setActiveTab] = useState('budget');
  const [budget, setBudget]       = useState(null);

  useEffect(() => {
    getProjectBudget(project.id).then(setBudget).catch(() => toast.error('Error cargando presupuesto'));
  }, [project.id]);

  // Build Google Maps embed URL
  const mapSrc = () => {
    if (project.latitude && project.longitude)
      return `https://maps.google.com/maps?q=${project.latitude},${project.longitude}&z=16&output=embed`;
    if (project.address)
      return `https://maps.google.com/maps?q=${encodeURIComponent(project.address)}&z=15&output=embed`;
    return null;
  };

  return (
    <div>
      {/* ── Breadcrumb header ── */}
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ChevronLeft size={16}/> Proyectos</button>
          <span className="breadcrumb-sep">/</span>
          <h2 className="page-title"><Building2 size={18}/> {project.name}</h2>
        </div>
        <button className="btn-outline" onClick={() => onEditProject(project)}>✏️ Editar proyecto</button>
      </div>

      {/* ── Meta row ── */}
      {(project.address || project.description) && (
        <div className="project-detail-meta card mb-6">
          {project.address    && <span><MapPin size={13}/> {project.address}</span>}
          {project.description && <span style={{color:'#555'}}>{project.description}</span>}
        </div>
      )}

      {/* ── Tab bar ── */}
      <div className="detail-tabs mb-6">
        {TABS.map(t => (
          <button key={t.id}
            className={`detail-tab ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}>
            <t.icon size={15}/> {t.label}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════
          TAB: BUDGET
         ══════════════════════════════════════════════════════ */}
      {activeTab === 'budget' && budget && (
        <div>
          {/* KPI row */}
          <div className="kpi-grid mb-6">
            <KpiCard IconComponent={Home}       label="Total Unidades"     value={budget.total_units}
              sub={`${budget.occupied_units} ocupadas`} color="#1565c0"/>
            <KpiCard IconComponent={Percent}    label="Ocupación"          value={pct(budget.occupancy_rate)}
              color={budget.occupancy_rate>=80?'#2e7d32':budget.occupancy_rate>=50?'#e65100':'#c62828'}/>
            <KpiCard IconComponent={TrendingUp} label="Ingreso Mensual Real" value={fmt(budget.monthly_rent_actual)}
              sub="unidades ocupadas" color="#6a1b9a"/>
            <KpiCard IconComponent={DollarSign} label="Potencial Mensual"  value={fmt(budget.monthly_rent_potential)}
              sub="si 100% ocupado" color="#1a3a6b"/>
            <KpiCard IconComponent={Users}      label="Contratos Activos"  value={budget.active_contracts} color="#0277bd"/>
            <KpiCard IconComponent={ArrowUpRight} label="Pagos Cobrados"   value={fmt(budget.total_payments_collected)}
              sub="este proyecto" color="#2e7d32"/>
          </div>

          {/* Occupancy visual */}
          <div className="card mb-6" style={{padding:'16px 20px'}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:10}}>
              <span style={{fontWeight:700,color:'#1a3a6b'}}>Tasa de Ocupación</span>
              <span style={{fontSize:12,color:'#666'}}>{budget.occupied_units} / {budget.total_units} unidades</span>
            </div>
            <OccupancyBar value={budget.occupancy_rate}/>
          </div>

          {/* Unit type breakdown */}
          {Object.keys(budget.unit_type_breakdown).length > 0 && (
            <div className="card mb-6">
              <div className="section-header"><span className="section-title">Desglose por Tipo</span></div>
              <div className="table-wrapper">
                <table className="units-table">
                  <thead><tr>
                    <th>Tipo</th><th className="text-center">Total</th>
                    <th className="text-center">Ocupadas</th><th className="text-center">Disponibles</th>
                    <th className="text-right">Ingreso Mensual</th>
                  </tr></thead>
                  <tbody>
                    {Object.entries(budget.unit_type_breakdown).map(([type, d], i) => (
                      <tr key={type} className={i%2===0?'row-even':'row-odd'}>
                        <td className="ul-unit-num">{type}</td>
                        <td className="text-center">{d.total}</td>
                        <td className="text-center"><span className="availability-badge taken">{d.occupied}</span></td>
                        <td className="text-center"><span className="availability-badge free">{d.total - d.occupied}</span></td>
                        <td className="monto-cell">{fmt(d.rent_sum)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="total-footer">
                      <td className="footer-label">Total</td>
                      <td className="text-center font-bold">{budget.total_units}</td>
                      <td className="text-center font-bold">{budget.occupied_units}</td>
                      <td className="text-center font-bold">{budget.available_units}</td>
                      <td className="footer-total">{fmt(budget.monthly_rent_actual)}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}

          {/* User budget */}
          {(budget.user_budget > 0 || budget.budget_notes) && (
            <div className="card mb-6" style={{padding:'16px 20px'}}>
              <div style={{fontWeight:700,color:'#1a3a6b',marginBottom:10}}>Presupuesto Definido</div>
              {budget.user_budget > 0 && (
                <div style={{display:'flex',gap:40,flexWrap:'wrap'}}>
                  <div>
                    <div style={{fontSize:11,color:'#666',marginBottom:2}}>Presupuesto Total</div>
                    <div style={{fontSize:22,fontWeight:700,color:'#1a3a6b'}}>{fmt(budget.user_budget)}</div>
                  </div>
                  <div>
                    <div style={{fontSize:11,color:'#666',marginBottom:2}}>Ingreso vs Presupuesto</div>
                    <div style={{fontSize:22,fontWeight:700,color: budget.monthly_rent_actual >= budget.user_budget ? '#2e7d32' : '#c62828'}}>
                      {Math.round(budget.monthly_rent_actual / budget.user_budget * 100)}%
                    </div>
                  </div>
                </div>
              )}
              {budget.budget_notes && <p style={{marginTop:10,fontSize:12,color:'#555',fontStyle:'italic'}}>{budget.budget_notes}</p>}
            </div>
          )}

          {/* Active contracts list */}
          {budget.contracts.length > 0 && (
            <div className="card">
              <div className="section-header"><span className="section-title">Contratos Activos ({budget.contracts.length})</span></div>
              <div className="table-wrapper">
                <table className="units-table">
                  <thead><tr>
                    <th>Unidad</th><th>Inquilino</th>
                    <th className="text-right">Renta/mes</th>
                    <th>Inicio</th><th>Vence</th>
                  </tr></thead>
                  <tbody>
                    {budget.contracts.map((c,i)=>(
                      <tr key={i} className={i%2===0?'row-even':'row-odd'}>
                        <td className="ul-unit-num">{c.unit_number}</td>
                        <td className="ul-tenant">{c.tenant_name}</td>
                        <td className="monto-cell">{fmt(c.monthly_rent)}</td>
                        <td>{c.start_date||'—'}</td>
                        <td>{c.end_date||'—'}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr className="total-footer">
                      <td colSpan={2} className="footer-label">Total mensual</td>
                      <td className="footer-total">{fmt(budget.contract_income)}</td>
                      <td colSpan={2}/>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════
          TAB: UNITS
         ══════════════════════════════════════════════════════ */}
      {activeTab === 'units' && (
        <UnitsPage
          project={project}
          onBack={() => setActiveTab('budget')}
          onSelectUnit={() => {}}
          hideBackButton
        />
      )}

      {/* ══════════════════════════════════════════════════════
          TAB: BANCOS$
         ══════════════════════════════════════════════════════ */}
      {activeTab === 'bancos' && (
        <ProjectBancosTab projectId={project.id}/>
      )}

      {/* ══════════════════════════════════════════════════════
          TAB: LOCATION
         ══════════════════════════════════════════════════════ */}
      {activeTab === 'location' && (
        <div className="card">
          <div className="section-header">
            <span className="section-title"><MapPin size={14} style={{marginRight:6}}/>Ubicación — {project.name}</span>
            {project.address && (
              <a className="btn-outline" style={{color:'#fff',borderColor:'rgba(255,255,255,0.4)'}}
                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(project.address)}`}
                target="_blank" rel="noreferrer">
                Abrir en Google Maps ↗
              </a>
            )}
          </div>
          {project.address || (project.latitude && project.longitude) ? (
            <div style={{position:'relative'}}>
              {project.latitude && project.longitude && (
                <div className="map-coords-badge">
                  📍 {Number(project.latitude).toFixed(5)}, {Number(project.longitude).toFixed(5)}
                </div>
              )}
              <iframe
                title="Mapa"
                src={mapSrc()}
                className="project-map"
                allowFullScreen
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
            </div>
          ) : (
            <div className="empty-state">
              Agrega una dirección o coordenadas al proyecto para ver el mapa.
              <br/>
              <button className="btn-primary" style={{marginTop:16}} onClick={() => onEditProject(project)}>
                ✏️ Editar proyecto
              </button>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════════════════════════════════
          TAB: DOCUMENTS
         ══════════════════════════════════════════════════════ */}
      {activeTab === 'documents' && (
        <div className="card">
          <div className="section-header"><span className="section-title">Documentos del Proyecto</span></div>
          <ProjectDocsTab projectId={project.id}/>
        </div>
      )}
    </div>
  );
}









