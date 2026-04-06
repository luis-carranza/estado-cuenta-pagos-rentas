#!/usr/bin/env python3
"""Generates all React frontend source files for the Estado de Cuenta system."""

import os

BASE = "/Users/luiscarranza/PycharmProjects/FastAPIProject/frontend/src"

files = {}

# ── ResumenPagos.jsx ────────────────────────────────────────────────────────
files["components/ResumenPagos.jsx"] = r"""
const fmt = (n) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(n ?? 0);

export default function ResumenPagos({ resumen }) {
  return (
    <div className="card mb-6">
      <div className="section-header">
        <span className="section-title">RESUMEN DE PAGOS</span>
      </div>
      <div className="resumen-grid">
        <div className="resumen-left">
          <div className="resumen-row">
            <span className="resumen-label">Total Efectivo:</span>
            <span className="resumen-value efectivo">{fmt(resumen?.total_efectivo)}</span>
          </div>
          <div className="resumen-row">
            <span className="resumen-label">Total Transferencias:</span>
            <span className="resumen-value transferencia">{fmt(resumen?.total_transferencias)}</span>
          </div>
          <div className="resumen-row total-row">
            <span className="resumen-label">Gran Total:</span>
            <span className="resumen-value total">{fmt(resumen?.gran_total)}</span>
          </div>
        </div>
        <div className="resumen-right">
          <div className="resumen-row">
            <span className="resumen-label">Pago Servicios:</span>
            <span className="resumen-value servicios">{fmt(resumen?.pago_servicios)}</span>
          </div>
          <div className="resumen-row">
            <span className="resumen-label">Pago Renta:</span>
            <span className="resumen-value renta">{fmt(resumen?.pago_renta)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
""".lstrip()

# ── PagoModal.jsx ───────────────────────────────────────────────────────────
files["components/PagoModal.jsx"] = r"""
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
""".lstrip()

# ── PagosTable.jsx ──────────────────────────────────────────────────────────
files["components/PagosTable.jsx"] = r"""
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
""".lstrip()

# ── App.jsx ─────────────────────────────────────────────────────────────────
files["App.jsx"] = r"""
import { useState, useEffect, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import ResumenPagos from './components/ResumenPagos';
import PagosTable from './components/PagosTable';
import PagoModal from './components/PagoModal';
import { getEstadoCuenta, getPagos, createPago, updatePago, deletePago } from './services/api';
import './App.css';

export default function App() {
  const [estadoCuenta, setEstadoCuenta] = useState(null);
  const [pagos, setPagos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPago, setEditingPago] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const [ec, ps] = await Promise.all([getEstadoCuenta(), getPagos()]);
      setEstadoCuenta(ec);
      setPagos(ps);
      setError(null);
    } catch (err) {
      setError('No se pudo conectar con el servidor. Asegúrate que el backend esté corriendo en http://localhost:8000');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleNew = () => { setEditingPago(null); setModalOpen(true); };
  const handleEdit = (pago) => { setEditingPago(pago); setModalOpen(true); };
  const handleClose = () => { setModalOpen(false); setEditingPago(null); };

  const handleSave = async (data) => {
    try {
      if (editingPago) {
        await updatePago(editingPago.consecutivo, data);
        toast.success('Pago actualizado correctamente');
      } else {
        await createPago(data);
        toast.success('Pago creado correctamente');
      }
      handleClose();
      fetchAll();
    } catch (err) {
      toast.error('Error al guardar el pago');
    }
  };

  const handleDelete = async (consecutivo) => {
    if (!window.confirm(`¿Eliminar el pago #${consecutivo}?`)) return;
    try {
      await deletePago(consecutivo);
      toast.success(`Pago #${consecutivo} eliminado`);
      fetchAll();
    } catch (err) {
      toast.error('Error al eliminar el pago');
    }
  };

  return (
    <div className="app-container">
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />

      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
          <span>Cargando datos...</span>
        </div>
      )}

      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={fetchAll} className="retry-btn">Reintentar</button>
        </div>
      )}

      {!loading && !error && (
        <>
          <Header header={estadoCuenta?.header} />
          <ResumenPagos resumen={estadoCuenta?.resumen} />
          <PagosTable
            pagos={pagos}
            onNew={handleNew}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </>
      )}

      {modalOpen && (
        <PagoModal
          pago={editingPago}
          onClose={handleClose}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
""".lstrip()

# ── App.css ─────────────────────────────────────────────────────────────────
files["App.css"] = r"""
/* ── Reset / Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Segoe UI', Arial, sans-serif;
  background: #f0f4f8;
  color: #1a1a2e;
  font-size: 13px;
}

/* ── Layout ── */
.app-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px;
}
.mb-6 { margin-bottom: 24px; }

/* ── Card ── */
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  overflow: hidden;
}

/* ── Section Header (blue bar) ── */
.section-header {
  background: #1a3a6b;
  color: #fff;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-title {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* ── Header info ── */
.header-info { padding: 16px 20px; }
.header-row {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
}
.header-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.header-icon { color: #1a3a6b; }
.header-label {
  font-weight: 600;
  color: #444;
}
.header-value {
  color: #1a1a2e;
  font-weight: 500;
}

/* ── Resumen ── */
.resumen-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  padding: 16px 20px;
}
.resumen-left, .resumen-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.resumen-right { padding-left: 40px; border-left: 2px solid #e8edf5; }
.resumen-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.total-row { border-top: 1px solid #d0d9e8; padding-top: 8px; margin-top: 4px; }
.resumen-label { font-weight: 600; color: #333; min-width: 170px; }
.resumen-value { font-weight: 700; font-size: 15px; }
.resumen-value.efectivo  { color: #2e7d32; }
.resumen-value.transferencia { color: #1565c0; }
.resumen-value.total     { color: #1a3a6b; font-size: 17px; }
.resumen-value.servicios { color: #e65100; }
.resumen-value.renta     { color: #6a1b9a; }

/* ── Filters bar ── */
.filters-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 12px 16px;
  background: #f7f9fc;
  border-bottom: 1px solid #e3e9f0;
}
.search-box {
  position: relative;
  flex: 1;
  min-width: 200px;
}
.search-box .search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #888;
}
.search-box input {
  width: 100%;
  padding: 7px 10px 7px 34px;
  border: 1px solid #d0d9e8;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  background: #fff;
}
.search-box input:focus { border-color: #1a3a6b; }
.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
}
.filter-group select {
  padding: 7px 10px;
  border: 1px solid #d0d9e8;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
  background: #fff;
  cursor: pointer;
}
.filter-group select:focus { border-color: #1a3a6b; }
.btn-clear {
  background: none;
  border: 1px solid #bbb;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  color: #555;
}
.btn-clear:hover { background: #f0f0f0; }

/* ── Table ── */
.table-wrapper {
  overflow-x: auto;
}
.pagos-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
}
.pagos-table thead tr {
  background: #1a3a6b;
  color: #fff;
}
.pagos-table th {
  padding: 10px 8px;
  text-align: left;
  font-weight: 700;
  font-size: 11px;
  letter-spacing: 0.3px;
  white-space: nowrap;
}
.pagos-table td {
  padding: 8px 8px;
  border-bottom: 1px solid #eef0f5;
  vertical-align: middle;
}
.row-even { background: #fff; }
.row-odd  { background: #f5f8fd; }
.pagos-table tbody tr:hover { background: #e8f0fb; }
.text-center { text-align: center; }
.text-right  { text-align: right;  }
.font-bold   { font-weight: 700;   }
.client-cell { font-weight: 500; max-width: 180px; }
.concepto-cell { max-width: 240px; }
.monto-cell {
  text-align: right;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #1a3a6b;
  white-space: nowrap;
}
.empty-row {
  text-align: center;
  padding: 32px;
  color: #888;
  font-style: italic;
}
/* badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2px;
  white-space: nowrap;
}
.badge-efectivo { background: #e8f5e9; color: #2e7d32; }
.badge-trans    { background: #e3f2fd; color: #1565c0; }

/* Actions */
.actions-cell { display: flex; gap: 4px; align-items: center; }
.action-btn {
  border: none;
  cursor: pointer;
  border-radius: 5px;
  padding: 5px;
  display: flex;
  align-items: center;
  transition: background 0.15s;
}
.edit-btn   { background: #e3f2fd; color: #1565c0; }
.edit-btn:hover { background: #bbdefb; }
.delete-btn { background: #fce4ec; color: #c62828; }
.delete-btn:hover { background: #f8bbd0; }

/* Tfoot */
.total-footer { background: #f0f4fb; }
.footer-label {
  font-weight: 700;
  font-size: 13px;
  padding-right: 12px;
  color: #333;
}
.footer-total {
  font-weight: 700;
  font-size: 15px;
  color: #1a3a6b;
  text-align: right;
  white-space: nowrap;
}

/* ── Buttons ── */
.btn-primary {
  background: #1a3a6b;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background 0.15s;
}
.btn-primary:hover { background: #0d2447; }
.btn-primary:disabled { background: #9ab; cursor: not-allowed; }
.btn-sm { padding: 5px 12px; font-size: 12px; }
.btn-secondary {
  background: #fff;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}
.btn-secondary:hover { background: #f5f5f5; }

/* ── Modal ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}
.modal-box {
  background: #fff;
  border-radius: 10px;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
}
.modal-header {
  background: #1a3a6b;
  color: #fff;
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 14px;
  border-radius: 10px 10px 0 0;
}
.modal-close {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  opacity: 0.8;
  padding: 0;
  display: flex;
}
.modal-close:hover { opacity: 1; }
.modal-form { padding: 20px; }
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 16px;
}
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-group.full-width { grid-column: 1 / -1; }
.form-group label { font-weight: 600; font-size: 12px; color: #444; }
.form-group input,
.form-group select {
  padding: 8px 10px;
  border: 1px solid #d0d9e8;
  border-radius: 6px;
  font-size: 13px;
  outline: none;
}
.form-group input:focus,
.form-group select:focus { border-color: #1a3a6b; }
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* ── Loading / Error ── */
.loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 80px 0;
  color: #555;
}
.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #d0d9e8;
  border-top-color: #1a3a6b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.error-banner {
  background: #fff3cd;
  border: 1px solid #f0ad4e;
  border-radius: 8px;
  padding: 14px 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #7a4500;
}
.retry-btn {
  margin-left: auto;
  background: #f0ad4e;
  border: none;
  border-radius: 5px;
  padding: 6px 14px;
  cursor: pointer;
  font-weight: 600;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .resumen-grid { grid-template-columns: 1fr; }
  .resumen-right { padding-left: 0; border-left: none; border-top: 2px solid #e8edf5; padding-top: 12px; }
  .form-grid { grid-template-columns: 1fr; }
  .header-row { flex-direction: column; gap: 12px; }
}
""".lstrip()

# ── index.css ────────────────────────────────────────────────────────────────
files["index.css"] = r"""
body {
  margin: 0;
  min-height: 100vh;
  background: #f0f4f8;
}
""".lstrip()

# ── Write all files ──────────────────────────────────────────────────────────
for rel_path, content in files.items():
    full_path = os.path.join(BASE, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {rel_path}")

print("\nAll files generated successfully!")

