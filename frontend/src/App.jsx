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
