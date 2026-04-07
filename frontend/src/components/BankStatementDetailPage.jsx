import { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, Plus, Pencil, Trash2, X, Link2, CheckCircle2, Circle,
         RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';
import { toast } from 'react-hot-toast';
import {
  getStatementLines, createStatementLine, updateStatementLine, deleteStatementLine,
} from '../services/api';
import LineMatchModal from './LineMatchModal';

const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                 'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

const fmt = v => v != null
  ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(v)
  : '—';

const EMPTY_LINE = {
  line_date: '', description: '', reference: '',
  amount: '', transaction_type: 'CREDITO', balance: '', notes: '',
};

// ── Line Modal ───────────────────────────────────────────────────────────────
function LineModal({ line, onClose, onSave }) {
  const [form, setForm] = useState(line ? { ...line } : { ...EMPTY_LINE });
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async e => {
    e.preventDefault();
    await onSave({
      ...form,
      amount:  parseFloat(form.amount)  || 0,
      balance: form.balance !== '' ? parseFloat(form.balance) : null,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>{line ? 'Editar línea' : 'Nueva línea de estado'}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <form className="modal-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Fecha</label>
              <input type="date" value={form.line_date} onChange={e => set('line_date', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Tipo</label>
              <select value={form.transaction_type} onChange={e => set('transaction_type', e.target.value)}>
                <option value="CREDITO">Crédito (ingreso)</option>
                <option value="DEBITO">Débito (cargo)</option>
              </select>
            </div>
            <div className="form-group full-width">
              <label>Descripción</label>
              <input value={form.description} onChange={e => set('description', e.target.value)}
                placeholder="Descripción del movimiento" required />
            </div>
            <div className="form-group">
              <label>Referencia / Núm. operación</label>
              <input value={form.reference} onChange={e => set('reference', e.target.value)}
                placeholder="ej. 123456789" />
            </div>
            <div className="form-group">
              <label>Monto (MXN)</label>
              <input type="number" step="0.01" min="0" value={form.amount}
                onChange={e => set('amount', e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Saldo (opcional)</label>
              <input type="number" step="0.01" value={form.balance}
                onChange={e => set('balance', e.target.value)}
                placeholder="saldo tras movimiento" />
            </div>
            <div className="form-group full-width">
              <label>Notas</label>
              <textarea rows={2} value={form.notes}
                onChange={e => set('notes', e.target.value)} />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn-primary">{line ? 'Guardar' : 'Agregar línea'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Bulk Import Paste Modal ──────────────────────────────────────────────────
function BulkImportModal({ statementId, onClose, onDone }) {
  const [raw, setRaw] = useState('');
  const [parsed, setParsed] = useState([]);
  const [step, setStep] = useState(1); // 1=paste, 2=review
  const [saving, setSaving] = useState(false);

  // Try to parse pasted text: each line = date | description | reference | amount | type
  // Also supports tab-separated or comma-separated
  const handleParse = () => {
    const lines = raw.trim().split('\n').filter(l => l.trim());
    const rows = lines.map((l, i) => {
      const parts = l.split(/\t|,\s*|\s{2,}/);
      // Heuristic: detect if a field looks like a date
      const tryDate = s => {
        if (!s) return '';
        const d = new Date(s);
        return isNaN(d.getTime()) ? '' : d.toISOString().slice(0,10);
      };
      const tryAmt = s => {
        if (!s) return 0;
        const n = parseFloat(s.replace(/[$,\s]/g,''));
        return isNaN(n) ? 0 : Math.abs(n);
      };
      return {
        _key: i,
        line_date: tryDate(parts[0]),
        description: parts[1] || `Línea ${i+1}`,
        reference: parts[2] || '',
        amount: tryAmt(parts[3] || parts[1]),
        transaction_type: (parts[4] || 'CREDITO').toUpperCase().includes('DEB') ? 'DEBITO' : 'CREDITO',
        balance: tryAmt(parts[5]) || null,
        notes: '',
      };
    });
    setParsed(rows);
    setStep(2);
  };

  const setField = (i, k, v) => setParsed(p => p.map((r, idx) => idx === i ? {...r, [k]: v} : r));

  const handleSave = async () => {
    setSaving(true);
    try {
      const { bulkCreateLines } = await import('../services/api');
      await bulkCreateLines(statementId, parsed.map(r => {
        const { _key: _k, ...rest } = r; return rest;
      }));
      toast.success(`${parsed.length} líneas importadas`);
      onDone();
    } catch { toast.error('Error importando líneas'); }
    finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" style={{maxWidth:840}} onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span>📋 Importar líneas (pegar desde banco)</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <div className="modal-form">
          {step === 1 && (
            <>
              <p style={{color:'#555',marginBottom:12,fontSize:13}}>
                Copia y pega las líneas de tu estado de cuenta (desde Excel, PDF o banca en línea).<br/>
                Formato esperado por columna: <b>Fecha · Descripción · Referencia · Monto · Tipo (CREDITO/DEBITO) · Saldo</b>
              </p>
              <textarea rows={12} style={{width:'100%',padding:10,border:'1px solid #d0d9e8',
                borderRadius:6,fontSize:12,fontFamily:'monospace'}}
                placeholder={'01/03/2026\tPago renta depto 101\tREF123\t5500\tCREDITO\t12000\n02/03/2026\tServicio agua\t\t350\tDEBITO\t11650\n…'}
                value={raw} onChange={e => setRaw(e.target.value)} />
              <div className="modal-actions">
                <button className="btn-secondary" onClick={onClose}>Cancelar</button>
                <button className="btn-primary" onClick={handleParse} disabled={!raw.trim()}>
                  Analizar → revisar
                </button>
              </div>
            </>
          )}
          {step === 2 && (
            <>
              <p style={{color:'#555',marginBottom:10,fontSize:13}}>
                Revisa y corrige los datos antes de guardar ({parsed.length} líneas):
              </p>
              <div style={{overflowX:'auto',maxHeight:380,overflowY:'auto'}}>
                <table style={{width:'100%',borderCollapse:'collapse',fontSize:12}}>
                  <thead>
                    <tr style={{background:'#1a3a6b',color:'#fff'}}>
                      {['Fecha','Descripción','Referencia','Monto','Tipo','Saldo'].map(h =>
                        <th key={h} style={{padding:'7px 8px',textAlign:'left',fontWeight:700}}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {parsed.map((r, i) => (
                      <tr key={r._key} style={{background: i%2?'#f5f8fd':'#fff'}}>
                        <td style={{padding:'4px 6px'}}>
                          <input type="date" value={r.line_date} style={{width:130,padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'line_date',e.target.value)} />
                        </td>
                        <td style={{padding:'4px 6px'}}>
                          <input value={r.description} style={{width:200,padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'description',e.target.value)} />
                        </td>
                        <td style={{padding:'4px 6px'}}>
                          <input value={r.reference} style={{width:100,padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'reference',e.target.value)} />
                        </td>
                        <td style={{padding:'4px 6px'}}>
                          <input type="number" value={r.amount} style={{width:90,padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'amount',parseFloat(e.target.value)||0)} />
                        </td>
                        <td style={{padding:'4px 6px'}}>
                          <select value={r.transaction_type} style={{padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'transaction_type',e.target.value)}>
                            <option value="CREDITO">CREDITO</option>
                            <option value="DEBITO">DEBITO</option>
                          </select>
                        </td>
                        <td style={{padding:'4px 6px'}}>
                          <input type="number" value={r.balance ?? ''} style={{width:90,padding:'3px 5px',border:'1px solid #d0d9e8',borderRadius:4,fontSize:12}}
                            onChange={e => setField(i,'balance', e.target.value ? parseFloat(e.target.value) : null)} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setStep(1)}>← Volver</button>
                <button className="btn-primary" onClick={handleSave} disabled={saving}>
                  {saving ? 'Guardando…' : `Guardar ${parsed.length} líneas`}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main Detail Page ─────────────────────────────────────────────────────────
export default function BankStatementDetailPage({ statement, onBack }) {
  const [lines,     setLines]     = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [lineModal, setLineModal] = useState(false);
  const [editLine,  setEditLine]  = useState(null);
  const [matchLine, setMatchLine] = useState(null);
  const [bulkModal, setBulkModal] = useState(false);
  const [filterType, setFilterType] = useState('');
  const [filterMatch, setFilterMatch] = useState('');
  const [search, setSearch]       = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const ls = await getStatementLines(statement.id);
      setLines(ls);
    } catch { toast.error('Error cargando líneas'); }
    finally { setLoading(false); }
  }, [statement.id]);

  useEffect(() => { load(); }, [load]);

  const handleSaveLine = async data => {
    try {
      if (editLine) { await updateStatementLine(editLine.id, data); toast.success('Línea actualizada'); }
      else          { await createStatementLine(statement.id, data); toast.success('Línea agregada'); }
      setLineModal(false); setEditLine(null); load();
    } catch { toast.error('Error guardando línea'); }
  };

  const handleDeleteLine = async l => {
    if (!window.confirm(`¿Eliminar línea "${l.description}"?`)) return;
    try { await deleteStatementLine(l.id); toast.success('Línea eliminada'); load(); }
    catch { toast.error('Error eliminando línea'); }
  };

  const periodStr = statement.period_month
    ? `${MONTHS[statement.period_month-1]} ${statement.period_year}`
    : (statement.period_year || '—');

  const filtered = lines.filter(l => {
    if (filterType && l.transaction_type !== filterType) return false;
    if (filterMatch === 'matched'   && !l.is_matched) return false;
    if (filterMatch === 'unmatched' &&  l.is_matched) return false;
    if (search) {
      const s = search.toLowerCase();
      const inDesc = (l.description || '').toLowerCase().includes(s);
      const inRef  = (l.reference  || '').toLowerCase().includes(s);
      if (!inDesc && !inRef) return false;
    }
    return true;
  });

  const totalCredits  = lines.filter(l => l.transaction_type === 'CREDITO').reduce((a,l) => a + l.amount, 0);
  const totalDebits   = lines.filter(l => l.transaction_type === 'DEBITO').reduce((a,l)  => a + l.amount, 0);
  const matchedCount  = lines.filter(l => l.is_matched).length;

  return (
    <div>
      {/* ── Breadcrumb ── */}
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ArrowLeft size={15}/> Bancos</button>
          <span className="breadcrumb-sep">/</span>
          <span style={{fontWeight:700,color:'#1a3a6b'}}>
            {statement.bank_name || 'Estado'} — {periodStr}
          </span>
        </div>
        <div style={{display:'flex',gap:8}}>
          <button className="btn-outline" onClick={() => setBulkModal(true)}>
            📋 Importar líneas
          </button>
          <button className="btn-primary" onClick={() => { setEditLine(null); setLineModal(true); }}>
            <Plus size={14}/> Nueva línea
          </button>
        </div>
      </div>

      {/* ── Summary cards ── */}
      <div className="kpi-grid mb-6">
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e8f5e9'}}><TrendingUp size={20} color="#2e7d32"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#2e7d32'}}>{fmt(totalCredits)}</div>
            <div className="kpi-label">Total créditos</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#fce4ec'}}><TrendingDown size={20} color="#c62828"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#c62828'}}>{fmt(totalDebits)}</div>
            <div className="kpi-label">Total débitos</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#e3f2fd'}}><Link2 size={20} color="#1565c0"/></div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#1565c0'}}>{matchedCount}/{lines.length}</div>
            <div className="kpi-label">Líneas conciliadas</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon" style={{background:'#f3e8ff'}}>
            <span style={{fontSize:18,fontWeight:700,color:'#6a1b9a'}}>
              {lines.length > 0 ? Math.round(matchedCount/lines.length*100) : 0}%
            </span>
          </div>
          <div className="kpi-body">
            <div className="kpi-value" style={{color:'#6a1b9a'}}>
              {fmt(totalCredits - totalDebits)}
            </div>
            <div className="kpi-label">Balance neto</div>
          </div>
        </div>
      </div>

      {/* ── Filters ── */}
      <div className="card mb-6">
        <div className="filters-bar">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input placeholder="Buscar descripción o referencia…"
              value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <div className="filter-group">
            <span>Tipo:</span>
            <select value={filterType} onChange={e => setFilterType(e.target.value)}>
              <option value="">Todos</option>
              <option value="CREDITO">Créditos</option>
              <option value="DEBITO">Débitos</option>
            </select>
          </div>
          <div className="filter-group">
            <span>Estado:</span>
            <select value={filterMatch} onChange={e => setFilterMatch(e.target.value)}>
              <option value="">Todos</option>
              <option value="matched">Conciliados</option>
              <option value="unmatched">Sin conciliar</option>
            </select>
          </div>
          <button className="btn-outline" onClick={load}><RefreshCw size={13}/> Recargar</button>
          {(filterType || filterMatch || search) &&
            <button className="btn-clear" onClick={() => { setFilterType(''); setFilterMatch(''); setSearch(''); }}>Limpiar</button>}
        </div>
      </div>

      {/* ── Lines table ── */}
      {loading ? (
        <div className="loading-overlay"><div className="spinner"/><span>Cargando…</span></div>
      ) : (
        <div className="card">
          {filtered.length === 0 ? (
            <div className="empty-state">
              {lines.length === 0
                ? 'Sin líneas. Agrega la primera o importa desde banco.'
                : 'Sin resultados con los filtros aplicados.'}
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="pagos-table">
                <thead>
                  <tr>
                    <th style={{width:32}}>Estado</th>
                    <th>Fecha</th>
                    <th>Descripción</th>
                    <th>Referencia</th>
                    <th style={{textAlign:'right'}}>Monto</th>
                    <th style={{textAlign:'right'}}>Saldo</th>
                    <th>Unidad asignada</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((l, idx) => (
                    <tr key={l.id} className={idx%2===0?'row-even':'row-odd'}>
                      <td className="text-center">
                        {l.is_matched
                          ? <CheckCircle2 size={16} color="#43a047" title="Conciliado"/>
                          : <Circle size={16} color="#bbb" title="Sin conciliar"/>}
                      </td>
                      <td style={{whiteSpace:'nowrap'}}>{l.line_date || '—'}</td>
                      <td className="concepto-cell">
                        <div style={{fontWeight:500}}>{l.description || '—'}</div>
                        {l.notes && <div style={{fontSize:11,color:'#888',fontStyle:'italic'}}>{l.notes}</div>}
                      </td>
                      <td style={{fontSize:12,color:'#666'}}>{l.reference || '—'}</td>
                      <td className="monto-cell">
                        <span className={l.transaction_type === 'CREDITO' ? 'credit-val' : 'debit-val'}>
                          {l.transaction_type === 'DEBITO' ? '-' : '+'}{fmt(l.amount)}
                        </span>
                        <div style={{fontSize:10,color:'#999'}}>{l.transaction_type}</div>
                      </td>
                      <td className="text-right" style={{color:'#555',fontSize:12}}>
                        {l.balance != null ? fmt(l.balance) : '—'}
                      </td>
                      <td>
                        {l.matched_unit
                          ? <span className="badge badge-activo">Unidad {l.matched_unit}{l.matched_tenant ? ` · ${l.matched_tenant}` : ''}</span>
                          : <span style={{color:'#bbb',fontSize:11}}>Sin asignar</span>}
                      </td>
                      <td>
                        <div className="actions-cell">
                          <button className="action-btn" title="Asignar unidad"
                            style={{background:'#f3e8ff',color:'#6a1b9a'}}
                            onClick={() => setMatchLine(l)}>
                            <Link2 size={14}/>
                          </button>
                          <button className="action-btn edit-btn" title="Editar"
                            onClick={() => { setEditLine(l); setLineModal(true); }}>
                            <Pencil size={14}/>
                          </button>
                          <button className="action-btn delete-btn" title="Eliminar"
                            onClick={() => handleDeleteLine(l)}>
                            <Trash2 size={14}/>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="total-footer">
                    <td colSpan={4} className="footer-label">Total ({filtered.length} líneas)</td>
                    <td className="footer-total">
                      <div style={{color:'#2e7d32'}}>{fmt(filtered.filter(l=>l.transaction_type==='CREDITO').reduce((a,l)=>a+l.amount,0))}</div>
                      <div style={{color:'#c62828',fontSize:12}}>{fmt(filtered.filter(l=>l.transaction_type==='DEBITO').reduce((a,l)=>a+l.amount,0))}</div>
                    </td>
                    <td colSpan={3}></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Modals ── */}
      {lineModal && (
        <LineModal line={editLine}
          onClose={() => { setLineModal(false); setEditLine(null); }}
          onSave={handleSaveLine} />
      )}
      {matchLine && (
        <LineMatchModal line={matchLine}
          onClose={() => setMatchLine(null)}
          onMatchChanged={() => { load(); }} />
      )}
      {bulkModal && (
        <BulkImportModal statementId={statement.id}
          onClose={() => setBulkModal(false)}
          onDone={() => { setBulkModal(false); load(); }} />
      )}
    </div>
  );
}










