import { useState, useEffect, useCallback, useRef } from 'react';
import { ArrowLeft, Plus, Trash2, X, Link2, CheckCircle2, Circle,
         RefreshCw, TrendingUp, TrendingDown, Check, Ban } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  getStatementLines, createStatementLine, bulkCreateLines, updateStatementLine, deleteStatementLine,
} from '../services/api';
import LineMatchModal from './LineMatchModal';

const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                 'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const fmt = v => v != null
  ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(v)
  : '—';

const EMPTY_LINE = {
  line_date:'', description:'', reference:'',
  amount:'', transaction_type:'CREDITO', balance:'', notes:'',
};

// ── Inline editable cell ─────────────────────────────────────────────────────
function EditCell({ value, name, type='text', options, onChange, style={} }) {
  if (options) {
    return (
      <select name={name} value={value??''} onChange={e=>onChange(name,e.target.value)}
        className="ie-select" style={style}>
        {options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    );
  }
  return (
    <input name={name} type={type} value={value??''} onChange={e=>onChange(name,e.target.value)}
      className="ie-input" style={style}
      step={type==='number'?'0.01':undefined}
      min={type==='number'?'0':undefined} />
  );
}

// ── New row appended at bottom ────────────────────────────────────────────────
function NewLineRow({ statementId, onSaved, onCancel }) {
  const [form, setForm] = useState({...EMPTY_LINE});
  const [saving, setSaving] = useState(false);
  const set = (k,v) => setForm(f=>({...f,[k]:v}));

  const handleSave = async () => {
    if (!form.description) { toast.error('La descripción es obligatoria'); return; }
    setSaving(true);
    try {
      const saved = await createStatementLine(statementId, {
        ...form,
        amount:  parseFloat(form.amount)||0,
        balance: form.balance!=='' ? parseFloat(form.balance) : null,
      });
      toast.success('Línea agregada');
      onSaved(saved);
    } catch { toast.error('Error guardando'); }
    finally { setSaving(false); }
  };

  const handleKeyDown = e => {
    if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); handleSave(); }
    if (e.key==='Escape') onCancel();
  };

  return (
    <tr className="ie-new-row" onKeyDown={handleKeyDown}>
      <td className="text-center" style={{color:'#bbb'}}><Circle size={15}/></td>
      <td><EditCell name="line_date" type="date" value={form.line_date} onChange={set} style={{width:130}}/></td>
      <td><EditCell name="description" value={form.description} onChange={set} style={{width:'100%',minWidth:180}}/></td>
      <td><EditCell name="reference" value={form.reference} onChange={set} style={{width:130}}/></td>
      <td style={{textAlign:'right'}}>
        <EditCell name="amount" type="number" value={form.amount} onChange={set} style={{width:100,textAlign:'right'}}/>
      </td>
      <td>
        <EditCell name="transaction_type" value={form.transaction_type} onChange={set}
          options={[{value:'CREDITO',label:'CRÉDITO'},{value:'DEBITO',label:'DÉBITO'}]} style={{width:100}}/>
      </td>
      <td style={{textAlign:'right'}}>
        <EditCell name="balance" type="number" value={form.balance} onChange={set} style={{width:100,textAlign:'right'}}/>
      </td>
      <td><EditCell name="notes" value={form.notes} onChange={set} style={{width:'100%',minWidth:140}}/></td>
      <td/>
      <td>
        <div className="actions-cell">
          <button className="action-btn" style={{background:'#e8f5e9',color:'#2e7d32'}}
            onClick={handleSave} disabled={saving} title="Guardar (Enter)"><Check size={14}/></button>
          <button className="action-btn delete-btn" onClick={onCancel} title="Cancelar (Esc)"><X size={14}/></button>
        </div>
      </td>
    </tr>
  );
}

// ── Editable data row ─────────────────────────────────────────────────────────
function DataRow({ line, idx, onDelete, onMatchClick, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [form,    setForm]    = useState({});
  const [saving,  setSaving]  = useState(false);
  const rowRef = useRef(null);

  const startEdit = () => {
    setForm({
      line_date:        line.line_date        ?? '',
      description:      line.description      ?? '',
      reference:        line.reference        ?? '',
      amount:           line.amount           ?? '',
      transaction_type: line.transaction_type ?? 'CREDITO',
      balance:          line.balance          ?? '',
      notes:            line.notes            ?? '',
    });
    setEditing(true);
    setTimeout(()=>{ rowRef.current?.querySelector('.ie-input')?.focus(); }, 50);
  };

  const set = (k,v) => setForm(f=>({...f,[k]:v}));

  const handleSave = async () => {
    setSaving(true);
    try {
      const saved = await updateStatementLine(line.id, {
        ...form,
        amount:  parseFloat(form.amount)||0,
        balance: form.balance!=='' && form.balance!=null ? parseFloat(form.balance) : null,
      });
      toast.success('Guardado');
      setEditing(false);
      onSaved(saved);
    } catch { toast.error('Error guardando'); }
    finally { setSaving(false); }
  };

  const handleKeyDown = e => {
    if (e.key==='Enter' && !e.shiftKey) { e.preventDefault(); handleSave(); }
    if (e.key==='Escape') setEditing(false);
  };

  const rowBg = idx%2===0 ? 'row-even' : 'row-odd';

  if (editing) {
    return (
      <tr ref={rowRef} className={`${rowBg} ie-editing-row`} onKeyDown={handleKeyDown}>
        <td className="text-center">
          {line.is_matched ? <CheckCircle2 size={16} color="#43a047"/> : <Circle size={16} color="#bbb"/>}
        </td>
        <td><EditCell name="line_date" type="date" value={form.line_date} onChange={set} style={{width:130}}/></td>
        <td><EditCell name="description" value={form.description} onChange={set} style={{width:'100%',minWidth:180}}/></td>
        <td><EditCell name="reference" value={form.reference} onChange={set} style={{width:130}}/></td>
        <td style={{textAlign:'right'}}>
          <EditCell name="amount" type="number" value={form.amount} onChange={set} style={{width:100,textAlign:'right'}}/>
        </td>
        <td>
          <EditCell name="transaction_type" value={form.transaction_type} onChange={set}
            options={[{value:'CREDITO',label:'CRÉDITO'},{value:'DEBITO',label:'DÉBITO'}]} style={{width:100}}/>
        </td>
        <td style={{textAlign:'right'}}>
          <EditCell name="balance" type="number" value={form.balance} onChange={set} style={{width:100,textAlign:'right'}}/>
        </td>
        <td><EditCell name="notes" value={form.notes} onChange={set} style={{width:'100%',minWidth:140}}/></td>
        <td>
          {line.matched_unit
            ? <span className="badge badge-activo">Unidad {line.matched_unit}{line.matched_tenant?` · ${line.matched_tenant}`:''}</span>
            : <span style={{color:'#bbb',fontSize:11}}>Sin asignar</span>}
        </td>
        <td>
          <div className="actions-cell">
            <button className="action-btn" style={{background:'#e8f5e9',color:'#2e7d32'}}
              onClick={handleSave} disabled={saving} title="Guardar (Enter)"><Check size={14}/></button>
            <button className="action-btn" style={{background:'#f5f5f5',color:'#555'}}
              onClick={()=>setEditing(false)} title="Cancelar (Esc)"><Ban size={14}/></button>
          </div>
        </td>
      </tr>
    );
  }

  return (
    <tr ref={rowRef} className={`${rowBg} ie-row`} title="Clic en cualquier celda para editar">
      <td className="text-center">
        {line.is_matched
          ? <CheckCircle2 size={16} color="#43a047" title="Conciliado"/>
          : <Circle size={16} color="#bbb" title="Sin conciliar"/>}
      </td>
      <td className="ie-cell" onClick={startEdit} style={{whiteSpace:'nowrap'}}>{line.line_date||<span className="ie-empty">—</span>}</td>
      <td className="ie-cell concepto-cell" onClick={startEdit}>
        <div style={{fontWeight:500}}>{line.description||<span className="ie-empty">—</span>}</div>
        {line.notes&&<div style={{fontSize:11,color:'#888',fontStyle:'italic'}}>{line.notes}</div>}
      </td>
      <td className="ie-cell" onClick={startEdit} style={{fontSize:12,color:'#666'}}>{line.reference||<span className="ie-empty">—</span>}</td>
      <td className="ie-cell monto-cell" onClick={startEdit}>
        <span className={line.transaction_type==='CREDITO'?'credit-val':'debit-val'}>
          {line.transaction_type==='DEBITO'?'-':'+'}{fmt(line.amount)}
        </span>
        <div style={{fontSize:10,color:'#999'}}>{line.transaction_type}</div>
      </td>
      <td className="ie-cell" onClick={startEdit}>
        <span className={`badge ${line.transaction_type==='CREDITO'?'badge-activo':'badge-cancelado'}`} style={{fontSize:10}}>
          {line.transaction_type==='CREDITO'?'CRÉDITO':'DÉBITO'}
        </span>
      </td>
      <td className="ie-cell text-right" onClick={startEdit} style={{color:'#555',fontSize:12}}>
        {line.balance!=null?fmt(line.balance):<span className="ie-empty">—</span>}
      </td>
      <td className="ie-cell" onClick={startEdit}
        style={{fontSize:11,color:'#777',maxWidth:160,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>
        {line.notes||<span className="ie-empty">sin notas</span>}
      </td>
      <td>
        {line.matched_unit
          ? <span className="badge badge-activo">Unidad {line.matched_unit}{line.matched_tenant?` · ${line.matched_tenant}`:''}</span>
          : <span style={{color:'#bbb',fontSize:11}}>Sin asignar</span>}
      </td>
      <td>
        <div className="actions-cell">
          <button className="action-btn" title="Asignar unidad"
            style={{background:'#f3e8ff',color:'#6a1b9a'}} onClick={()=>onMatchClick(line)}>
            <Link2 size={14}/>
          </button>
          <button className="action-btn delete-btn" title="Eliminar" onClick={()=>onDelete(line)}>
            <Trash2 size={14}/>
          </button>
        </div>
      </td>
    </tr>
  );
}

// ── Bulk Import Modal ─────────────────────────────────────────────────────────
function BulkImportModal({ statementId, onClose, onDone }) {
  const [raw,setRaw]=useState(''); const [parsed,setParsed]=useState([]);
  const [step,setStep]=useState(1); const [saving,setSaving]=useState(false);

  const handleParse = () => {
    const rows = raw.trim().split('\n').filter(l=>l.trim()).map((l,i)=>{
      const p=l.split(/\t|,\s*|\s{2,}/);
      const tryDate=s=>{if(!s)return'';const d=new Date(s);return isNaN(d.getTime())?'':d.toISOString().slice(0,10);};
      const tryAmt=s=>{if(!s)return 0;const n=parseFloat(s.replace(/[$,\s]/g,''));return isNaN(n)?0:Math.abs(n);};
      return {_key:i,line_date:tryDate(p[0]),description:p[1]||`Línea ${i+1}`,reference:p[2]||'',
        amount:tryAmt(p[3]||p[1]),transaction_type:(p[4]||'CREDITO').toUpperCase().includes('DEB')?'DEBITO':'CREDITO',
        balance:tryAmt(p[5])||null,notes:''};
    });
    setParsed(rows); setStep(2);
  };
  const setField=(i,k,v)=>setParsed(p=>p.map((r,idx)=>idx===i?{...r,[k]:v}:r));
  const handleSave=async()=>{
    setSaving(true);
    try{
      await bulkCreateLines(statementId,parsed.map(r=>{const{_key:_k,...rest}=r;return rest;}));
      toast.success(`${parsed.length} líneas importadas`); onDone();
    }catch{toast.error('Error importando');}finally{setSaving(false);}
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{maxWidth:860}} onClick={e=>e.stopPropagation()}>
        <div className="modal-header">
          <span>📋 Importar líneas (pegar desde banco)</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <div className="modal-form">
          {step===1&&(<>
            <p style={{color:'#555',marginBottom:12,fontSize:13}}>
              Pega las líneas de tu estado de cuenta.<br/>
              Columnas: <b>Fecha · Descripción · Referencia · Monto · Tipo (CREDITO/DEBITO) · Saldo</b>
            </p>
            <textarea rows={12} style={{width:'100%',padding:10,border:'1px solid #d0d9e8',borderRadius:6,fontSize:12,fontFamily:'monospace'}}
              placeholder={'01/03/2026\tPago renta 101\tREF123\t5500\tCREDITO\t12000\n…'}
              value={raw} onChange={e=>setRaw(e.target.value)}/>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={onClose}>Cancelar</button>
              <button className="btn-primary" onClick={handleParse} disabled={!raw.trim()}>Analizar → revisar</button>
            </div>
          </>)}
          {step===2&&(<>
            <p style={{color:'#555',marginBottom:10,fontSize:13}}>Revisa y corrige ({parsed.length} líneas):</p>
            <div style={{overflowX:'auto',maxHeight:380,overflowY:'auto'}}>
              <table style={{width:'100%',borderCollapse:'collapse',fontSize:12}}>
                <thead><tr style={{background:'#1a3a6b',color:'#fff'}}>
                  {['Fecha','Descripción','Referencia','Monto','Tipo','Saldo'].map(h=>
                    <th key={h} style={{padding:'7px 8px',textAlign:'left',fontWeight:700}}>{h}</th>)}
                </tr></thead>
                <tbody>{parsed.map((r,i)=>(
                  <tr key={r._key} style={{background:i%2?'#f5f8fd':'#fff'}}>
                    <td style={{padding:'4px 6px'}}><input type="date" value={r.line_date} className="ie-input" style={{width:130}} onChange={e=>setField(i,'line_date',e.target.value)}/></td>
                    <td style={{padding:'4px 6px'}}><input value={r.description} className="ie-input" style={{width:200}} onChange={e=>setField(i,'description',e.target.value)}/></td>
                    <td style={{padding:'4px 6px'}}><input value={r.reference} className="ie-input" style={{width:100}} onChange={e=>setField(i,'reference',e.target.value)}/></td>
                    <td style={{padding:'4px 6px'}}><input type="number" value={r.amount} className="ie-input" style={{width:90,textAlign:'right'}} onChange={e=>setField(i,'amount',parseFloat(e.target.value)||0)}/></td>
                    <td style={{padding:'4px 6px'}}><select value={r.transaction_type} className="ie-select" onChange={e=>setField(i,'transaction_type',e.target.value)}><option value="CREDITO">CREDITO</option><option value="DEBITO">DEBITO</option></select></td>
                    <td style={{padding:'4px 6px'}}><input type="number" value={r.balance??''} className="ie-input" style={{width:90,textAlign:'right'}} onChange={e=>setField(i,'balance',e.target.value?parseFloat(e.target.value):null)}/></td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
            <div className="modal-actions">
              <button className="btn-secondary" onClick={()=>setStep(1)}>← Volver</button>
              <button className="btn-primary" onClick={handleSave} disabled={saving}>
                {saving?'Guardando…':`Guardar ${parsed.length} líneas`}
              </button>
            </div>
          </>)}
        </div>
      </div>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function BankStatementDetailPage({ statement, onBack }) {
  const [lines,       setLines]       = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [showNewRow,  setShowNewRow]  = useState(false);
  const [matchLine,   setMatchLine]   = useState(null);
  const [bulkModal,   setBulkModal]   = useState(false);
  const [filterType,  setFilterType]  = useState('');
  const [filterMatch, setFilterMatch] = useState('');
  const [search,      setSearch]      = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try { setLines(await getStatementLines(statement.id)); }
    catch { toast.error('Error cargando líneas'); }
    finally { setLoading(false); }
  }, [statement.id]);

  useEffect(()=>{ load(); },[load]);

  const updateLineInState = updated =>
    setLines(prev=>prev.map(l=>l.id===updated.id?{...l,...updated}:l));

  const handleNewSaved = newLine => {
    setLines(prev=>[...prev, newLine]);
    setShowNewRow(false);
  };

  const handleDeleteLine = async l => {
    if (!window.confirm(`¿Eliminar "${l.description}"?`)) return;
    try {
      await deleteStatementLine(l.id);
      toast.success('Línea eliminada');
      setLines(prev=>prev.filter(x=>x.id!==l.id));
    } catch { toast.error('Error eliminando'); }
  };

  const periodStr = statement.period_month
    ? `${MONTHS[statement.period_month-1]} ${statement.period_year}`
    : (statement.period_year||'—');

  const filtered = lines.filter(l=>{
    if (filterType && l.transaction_type!==filterType) return false;
    if (filterMatch==='matched'   && !l.is_matched) return false;
    if (filterMatch==='unmatched' &&  l.is_matched) return false;
    if (search) {
      const s=search.toLowerCase();
      if (!(l.description||'').toLowerCase().includes(s) && !(l.reference||'').toLowerCase().includes(s)) return false;
    }
    return true;
  });

  const totalCredits = lines.filter(l=>l.transaction_type==='CREDITO').reduce((a,l)=>a+l.amount,0);
  const totalDebits  = lines.filter(l=>l.transaction_type==='DEBITO').reduce((a,l)=>a+l.amount,0);
  const matchedCount = lines.filter(l=>l.is_matched).length;

  return (
    <div>
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ArrowLeft size={15}/> Bancos</button>
          <span className="breadcrumb-sep">/</span>
          <span style={{fontWeight:700,color:'#1a3a6b'}}>{statement.bank_name||'Estado'} — {periodStr}</span>
        </div>
        <div style={{display:'flex',gap:8}}>
          <button className="btn-outline" onClick={()=>setBulkModal(true)}>📋 Importar líneas</button>
          <button className="btn-primary" onClick={()=>setShowNewRow(true)} disabled={showNewRow}>
            <Plus size={14}/> Nueva línea
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="kpi-grid mb-6">
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e8f5e9'}}><TrendingUp size={20} color="#2e7d32"/></div>
          <div className="kpi-body"><div className="kpi-value" style={{color:'#2e7d32'}}>{fmt(totalCredits)}</div><div className="kpi-label">Total créditos</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#fce4ec'}}><TrendingDown size={20} color="#c62828"/></div>
          <div className="kpi-body"><div className="kpi-value" style={{color:'#c62828'}}>{fmt(totalDebits)}</div><div className="kpi-label">Total débitos</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e3f2fd'}}><Link2 size={20} color="#1565c0"/></div>
          <div className="kpi-body"><div className="kpi-value" style={{color:'#1565c0'}}>{matchedCount}/{lines.length}</div><div className="kpi-label">Líneas conciliadas</div></div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#f3e8ff'}}>
            <span style={{fontSize:18,fontWeight:700,color:'#6a1b9a'}}>{lines.length>0?Math.round(matchedCount/lines.length*100):0}%</span>
          </div>
          <div className="kpi-body"><div className="kpi-value" style={{color:'#6a1b9a'}}>{fmt(totalCredits-totalDebits)}</div><div className="kpi-label">Balance neto</div></div>
        </div>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="filters-bar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input placeholder="Buscar descripción o referencia…" value={search} onChange={e=>setSearch(e.target.value)}/>
          </div>
          <div className="filter-group">
            <span>Tipo:</span>
            <select value={filterType} onChange={e=>setFilterType(e.target.value)}>
              <option value="">Todos</option><option value="CREDITO">Créditos</option><option value="DEBITO">Débitos</option>
            </select>
          </div>
          <div className="filter-group">
            <span>Estado:</span>
            <select value={filterMatch} onChange={e=>setFilterMatch(e.target.value)}>
              <option value="">Todos</option><option value="matched">Conciliados</option><option value="unmatched">Sin conciliar</option>
            </select>
          </div>
          <button className="btn-outline" onClick={load}><RefreshCw size={13}/> Recargar</button>
          {(filterType||filterMatch||search) &&
            <button className="btn-clear" onClick={()=>{setFilterType('');setFilterMatch('');setSearch('');}}>Limpiar</button>}
        </div>
      </div>

      {/* Hint */}
      <div className="ie-hint">
        ✏️ <strong>Edición inline:</strong> haz clic en cualquier celda de la tabla para editar.
        <kbd>Enter</kbd> guarda · <kbd>Esc</kbd> cancela.
      </div>

      {/* Table */}
      {loading ? (
        <div className="loading-overlay"><div className="spinner"/><span>Cargando…</span></div>
      ) : (
        <div className="card">
          {filtered.length===0 && !showNewRow ? (
            <div className="empty-state">
              {lines.length===0 ? 'Sin líneas. Haz clic en "+ Nueva línea" o en "Importar líneas".'
                                : 'Sin resultados con los filtros aplicados.'}
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="pagos-table ie-table">
                <thead>
                  <tr>
                    <th style={{width:28}}></th>
                    <th style={{width:120}}>Fecha</th>
                    <th>Descripción</th>
                    <th style={{width:130}}>Referencia</th>
                    <th style={{textAlign:'right',width:120}}>Monto</th>
                    <th style={{width:100}}>Tipo</th>
                    <th style={{textAlign:'right',width:110}}>Saldo</th>
                    <th>Notas</th>
                    <th style={{width:160}}>Unidad asignada</th>
                    <th style={{width:80}}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((l,idx)=>(
                    <DataRow key={l.id} line={l} idx={idx}
                      onDelete={handleDeleteLine}
                      onMatchClick={setMatchLine}
                      onSaved={updateLineInState}/>
                  ))}
                  {showNewRow && (
                    <NewLineRow statementId={statement.id}
                      onSaved={handleNewSaved}
                      onCancel={()=>setShowNewRow(false)}/>
                  )}
                </tbody>
                <tfoot>
                  <tr className="total-footer">
                    <td colSpan={4} className="footer-label">
                      Total ({filtered.length} líneas{filtered.length!==lines.length?` de ${lines.length}`:''})
                    </td>
                    <td className="footer-total">
                      <div style={{color:'#2e7d32'}}>{fmt(filtered.filter(l=>l.transaction_type==='CREDITO').reduce((a,l)=>a+l.amount,0))}</div>
                      <div style={{color:'#c62828',fontSize:12}}>{fmt(filtered.filter(l=>l.transaction_type==='DEBITO').reduce((a,l)=>a+l.amount,0))}</div>
                    </td>
                    <td colSpan={5}/>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </div>
      )}

      {matchLine && (
        <LineMatchModal line={matchLine} onClose={()=>setMatchLine(null)}
          onMatchChanged={()=>{ setMatchLine(null); load(); }}/>
      )}
      {bulkModal && (
        <BulkImportModal statementId={statement.id}
          onClose={()=>setBulkModal(false)}
          onDone={()=>{ setBulkModal(false); load(); }}/>
      )}
    </div>
  );
}
