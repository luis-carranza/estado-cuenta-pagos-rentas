import { useState } from 'react';
import { Pencil, Trash2, Plus, Search, Filter } from 'lucide-react';

const fmt = (n) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(n ?? 0);

function fmtDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function PagosTable({ pagos, onNew, onEdit, onDelete }) {
  const [search, setSearch] = useState('');
  const [filterForma, setFilterForma] = useState('');
  const [filterSemana, setFilterSemana] = useState('');

  const semanas = [...new Set(pagos.map(p => p.semana_fiscal).filter(Boolean))].sort((a, b) => a - b);

  const filtered = pagos.filter(p => {
    const s = search.toLowerCase();
    const matchSearch = !s || [p.cliente, p.concepto, p.ubicacion, p.forma_de_pago]
      .some(f => f && f.toLowerCase().includes(s));
    const matchForma = !filterForma || (p.forma_de_pago && p.forma_de_pago.toUpperCase() === filterForma);
    const matchSemana = !filterSemana || p.semana_fiscal === parseInt(filterSemana);
    return matchSearch && matchForma && matchSemana;
  });

  const total = filtered.reduce((acc, p) => acc + (p.monto || 0), 0);

  return (
    <div className="card">
      <div className="section-header">
        <span className="section-title">DETALLE DE PAGOS ({filtered.length} registros)</span>
        <button className="btn-primary btn-sm" onClick={onNew}>
          <Plus size={14} /> Nuevo Pago
        </button>
      </div>

      {/* Filters bar */}
      <div className="filters-bar">
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            placeholder="Buscar cliente, concepto, ubicación..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <Filter size={16} />
          <select value={filterForma} onChange={e => setFilterForma(e.target.value)}>
            <option value="">Todas las formas</option>
            <option value="EFECTIVO">Efectivo</option>
            <option value="TRANSFERENCIA">Transferencia</option>
          </select>
        </div>
        <div className="filter-group">
          <select value={filterSemana} onChange={e => setFilterSemana(e.target.value)}>
            <option value="">Todas las semanas</option>
            {semanas.map(s => (
              <option key={s} value={s}>Semana {s}</option>
            ))}
          </select>
        </div>
        {(search || filterForma || filterSemana) && (
          <button className="btn-clear" onClick={() => { setSearch(''); setFilterForma(''); setFilterSemana(''); }}>
            Limpiar filtros
          </button>
        )}
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="pagos-table">
          <thead>
            <tr>
              <th>CONSEC.</th>
              <th>FECHA</th>
              <th>UBICACIÓN</th>
              <th>DESARROLLO</th>
              <th>MES CORRESP.</th>
              <th>CLIENTE</th>
              <th>CONCEPTO</th>
              <th>MONTO</th>
              <th>FORMA PAGO</th>
              <th>SEM. FISCAL</th>
              <th>ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr><td colSpan={11} className="empty-row">No se encontraron registros</td></tr>
            ) : (
              filtered.map((p, idx) => (
                <tr key={p.consecutivo} className={idx % 2 === 0 ? 'row-even' : 'row-odd'}>
                  <td className="text-center font-bold">{p.consecutivo}</td>
                  <td>{fmtDate(p.fecha)}</td>
                  <td>{p.ubicacion || '—'}</td>
                  <td>{p.desarrollo || '—'}</td>
                  <td className="text-center">{p.mes_correspondiente || '—'}</td>
                  <td className="client-cell">{p.cliente || '—'}</td>
                  <td className="concepto-cell">{p.concepto || '—'}</td>
                  <td className="monto-cell">{fmt(p.monto)}</td>
                  <td className="text-center">
                    <span className={`badge ${p.forma_de_pago?.toUpperCase() === 'EFECTIVO' ? 'badge-efectivo' : 'badge-trans'}`}>
                      {p.forma_de_pago || '—'}
                    </span>
                  </td>
                  <td className="text-center">{p.semana_fiscal ?? '—'}</td>
                  <td className="actions-cell">
                    <button className="action-btn edit-btn" title="Editar" onClick={() => onEdit(p)}>
                      <Pencil size={14} />
                    </button>
                    <button className="action-btn delete-btn" title="Eliminar" onClick={() => onDelete(p.consecutivo)}>
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
          <tfoot>
            <tr className="total-footer">
              <td colSpan={7} className="text-right footer-label">TOTAL FILTRADO:</td>
              <td className="monto-cell footer-total">{fmt(total)}</td>
              <td colSpan={3}></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
