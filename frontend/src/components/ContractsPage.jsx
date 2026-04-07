import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, ChevronLeft, FileText } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getContracts, createContract, updateContract, deleteContract } from '../services/api';
import ContractModal from './ContractModal';
import DocumentsPanel from './DocumentsPanel';

const fmt = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : '—';

const STATUS_COLOR = { ACTIVO:'badge-activo', VENCIDO:'badge-vencido', CANCELADO:'badge-cancelado' };

export default function ContractsPage({ unit, project, onBack }) {
  const [contracts, setContracts] = useState([]);
  const [modal, setModal]         = useState(null);
  const [docsContract, setDocs]   = useState(null);

  const load = () => getContracts(unit.id).then(setContracts).catch(() => toast.error('Error cargando contratos'));
  useEffect(() => { load(); }, [unit.id]);

  const handleSave = async (data) => {
    try {
      if (modal?.id) { await updateContract(modal.id, data); toast.success('Contrato actualizado'); }
      else           { await createContract(unit.id, data);  toast.success('Contrato creado'); }
      setModal(null); load();
    } catch { toast.error('Error guardando contrato'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este contrato?')) return;
    try { await deleteContract(id); toast.success('Contrato eliminado'); load(); }
    catch { toast.error('Error eliminando contrato'); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="breadcrumb">
          <button className="btn-back" onClick={onBack}><ChevronLeft size={16}/> {project?.name}</button>
          <span className="breadcrumb-sep">/</span>
          <h2 className="page-title"><FileText size={18}/> {unit.unit_number} — Contratos</h2>
        </div>
        <button className="btn-primary" onClick={() => setModal('new')}><Plus size={14}/> Nuevo Contrato</button>
      </div>

      <div className="contracts-list">
        {contracts.length === 0 && <div className="empty-state">No hay contratos para esta unidad.</div>}
        {contracts.map(c => (
          <div key={c.id} className="contract-card">
            <div className="contract-header">
              <div>
                <span className="tenant-name">{c.tenant_name}</span>
                <span className={`badge ${STATUS_COLOR[c.status] || 'badge-trans'}`}>{c.status}</span>
              </div>
              <div className="card-actions">
                <button className="btn-sm-outline" onClick={() => setDocs(c)}><FileText size={13}/> Documentos</button>
                <button className="action-btn edit-btn" onClick={() => setModal(c)}><Pencil size={14}/></button>
                <button className="action-btn delete-btn" onClick={() => handleDelete(c.id)}><Trash2 size={14}/></button>
              </div>
            </div>
            <div className="contract-details">
              {c.tenant_email && <span>✉️ {c.tenant_email}</span>}
              {c.tenant_phone && <span>📞 {c.tenant_phone}</span>}
              {c.start_date && <span>📅 {c.start_date} → {c.end_date || '...'}</span>}
              {c.monthly_rent && <span>💰 {fmt(c.monthly_rent)}/mes</span>}
              {c.deposit && <span>🔒 Depósito: {fmt(c.deposit)}</span>}
              {c.payment_day && <span>📆 Pago día {c.payment_day}</span>}
            </div>
            {c.notes && <p className="contract-notes">{c.notes}</p>}
          </div>
        ))}
      </div>

      {modal && <ContractModal contract={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
      {docsContract && <DocumentsPanel relatedType="contract" relatedId={docsContract.id}
        title={`Docs contrato — ${docsContract.tenant_name}`} onClose={() => setDocs(null)} />}
    </div>
  );
}
