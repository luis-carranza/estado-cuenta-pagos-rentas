import { useState, useEffect, useCallback } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Navbar         from './components/Navbar';
import Header         from './components/Header';
import ResumenPagos   from './components/ResumenPagos';
import PagosTable     from './components/PagosTable';
import PagoModal      from './components/PagoModal';
import ProjectsPage   from './components/ProjectsPage';
import UnitsPage      from './components/UnitsPage';
import ContractsPage  from './components/ContractsPage';
import { getEstadoCuenta, getPagos, createPago, updatePago, deletePago } from './services/api';
import './App.css';

export default function App() {
  const [tab, setTab]           = useState('estado');
  const [selProject, setProj]   = useState(null);  // for Units page
  const [selUnit, setUnit]       = useState(null);   // for Contracts page

  // Estado de Cuenta state
  const [estadoCuenta, setEC]   = useState(null);
  const [pagos, setPagos]        = useState([]);
  const [loading, setLoading]    = useState(true);
  const [error, setError]        = useState(null);
  const [modalOpen, setModal]    = useState(false);
  const [editPago, setEditPago]  = useState(null);

  // Filters
  const [filterMonth, setMonth]  = useState('');
  const [filterYear, setYear]    = useState('');
  const [filterProject, setFP]   = useState('');

  const fetchAll = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterMonth)   params.month = filterMonth;
      if (filterYear)    params.year  = filterYear;
      if (filterProject) params.project_id = filterProject;
      const [ec, ps] = await Promise.all([getEstadoCuenta(params), getPagos(params)]);
      setEC(ec); setPagos(ps); setError(null);
    } catch { setError('No se pudo conectar con el servidor (http://localhost:8000)'); }
    finally { setLoading(false); }
  }, [filterMonth, filterYear, filterProject]);

  useEffect(() => { if (tab === 'estado') fetchAll(); }, [tab, fetchAll]);

  const handleSavePago = async (data) => {
    try {
      if (editPago) { await updatePago(editPago.consecutivo, data); toast.success('Pago actualizado'); }
      else          { await createPago(data);                        toast.success('Pago creado'); }
      setModal(false); setEditPago(null); fetchAll();
    } catch { toast.error('Error guardando pago'); }
  };

  const handleDeletePago = async (id) => {
    if (!window.confirm(`¿Eliminar pago #${id}?`)) return;
    try { await deletePago(id); toast.success(`Pago #${id} eliminado`); fetchAll(); }
    catch { toast.error('Error eliminando pago'); }
  };

  // Navigate to units when project selected from ProjectsPage
  const handleSelectProject = (p) => { setProj(p); setTab('units'); };
  // Navigate to contracts when unit selected from UnitsPage
  const handleSelectUnit    = (u) => { setUnit(u); setTab('contracts'); };

  return (
    <div className="app-wrapper">
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
      <Navbar active={tab} onChange={t => { setTab(t);
        if (t !== 'units' && t !== 'contracts') { setProj(null); setUnit(null); }
      }} />

      <main className="app-container">

        {/* ── Estado de Cuenta ── */}
        {tab === 'estado' && (
          <>
            {/* Month / Year / Project filter bar */}
            <div className="periodo-bar card mb-6">
              <span className="periodo-label">Filtrar por:</span>
              <select value={filterMonth} onChange={e => setMonth(e.target.value)}>
                <option value="">Todos los meses</option>
                {Array.from({length:12},(_,i)=>i+1).map(m =>
                  <option key={m} value={m}>{new Date(2000,m-1).toLocaleString('es-MX',{month:'long'})}</option>)}
              </select>
              <select value={filterYear} onChange={e => setYear(e.target.value)}>
                <option value="">Todos los años</option>
                {[2024,2025,2026,2027].map(y => <option key={y} value={y}>{y}</option>)}
              </select>
              <button className="btn-primary btn-sm" onClick={fetchAll}>Aplicar</button>
              {(filterMonth||filterYear||filterProject) &&
                <button className="btn-clear" onClick={() => { setMonth(''); setYear(''); setFP(''); }}>Limpiar</button>}
            </div>

            {loading && <div className="loading-overlay"><div className="spinner"/><span>Cargando...</span></div>}
            {error   && <div className="error-banner">⚠️ {error}<button onClick={fetchAll} className="retry-btn">Reintentar</button></div>}
            {!loading && !error && (
              <>
                <Header header={estadoCuenta?.header} />
                <ResumenPagos resumen={estadoCuenta?.resumen} />
                <PagosTable pagos={pagos}
                  onNew={() => { setEditPago(null); setModal(true); }}
                  onEdit={p  => { setEditPago(p);   setModal(true); }}
                  onDelete={handleDeletePago} />
              </>
            )}
            {modalOpen && <PagoModal pago={editPago}
              onClose={() => { setModal(false); setEditPago(null); }} onSave={handleSavePago} />}
          </>
        )}

        {/* ── Proyectos ── */}
        {tab === 'projects' && (
          <ProjectsPage onSelectProject={handleSelectProject} />
        )}

        {/* ── Unidades ── */}
        {tab === 'units' && selProject && (
          <UnitsPage project={selProject}
            onBack={() => setTab('projects')}
            onSelectUnit={handleSelectUnit} />
        )}
        {tab === 'units' && !selProject && (
          <div className="empty-state">Selecciona un proyecto desde la pestaña Proyectos.</div>
        )}

        {/* ── Contratos ── */}
        {tab === 'contracts' && selUnit && (
          <ContractsPage unit={selUnit} project={selProject}
            onBack={() => { setTab('units'); }} />
        )}
        {tab === 'contracts' && !selUnit && (
          <div className="empty-state">Selecciona una unidad desde la pestaña Unidades.</div>
        )}

        {/* ── Documentos (global view) ── */}
        {tab === 'documents' && (
          <div className="page-header"><h2 className="page-title">📁 Documentos</h2>
            <p style={{color:'#666',marginTop:'8px'}}>Accede a los documentos desde una unidad o contrato específico usando el botón "Docs".</p>
          </div>
        )}
      </main>
    </div>
  );
}
