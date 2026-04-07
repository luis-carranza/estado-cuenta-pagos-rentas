import { useState, useEffect } from 'react';
import {
  ChevronLeft, Building2, DollarSign, Home, MapPin, FolderOpen,
  TrendingUp, Users, Percent, ArrowUpRight, FileText, Download, Trash2
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getProjectBudget, getDocuments, deleteDocument, uploadDocument } from '../services/api';
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

// ── Main component ───────────────────────────────────────────────────────────
const TABS = [
  { id: 'budget',    label: 'Presupuesto', icon: DollarSign },
  { id: 'units',     label: 'Unidades',    icon: Home        },
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









