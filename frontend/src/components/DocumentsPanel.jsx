import { useState, useEffect, useRef } from 'react';
import { X, Upload, Trash2, Download, FileText, File } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getDocuments, uploadDocument, deleteDocument } from '../services/api';

const DOC_TYPES = ['CONTRATO','IDENTIFICACION','COMPROBANTE_DOMICILIO','COMPROBANTE_INGRESOS',
                   'PAGARE','AVAL','FOTO','PLANO','RECIBO','OTRO'];

const fmtSize = b => b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`;

export default function DocumentsPanel({ relatedType, relatedId, title, onClose }) {
  const [docs, setDocs]       = useState([]);
  const [uploading, setUpl]   = useState(false);
  const [docName, setDocName] = useState('');
  const [docType, setDocType] = useState('CONTRATO');
  const [file, setFile]       = useState(null);
  const inputRef = useRef();

  const load = () => getDocuments({ related_type: relatedType, related_id: relatedId })
    .then(setDocs).catch(() => toast.error('Error cargando documentos'));
  useEffect(() => { load(); }, [relatedType, relatedId]);

  const handleUpload = async e => {
    e.preventDefault();
    if (!file) return toast.error('Selecciona un archivo');
    if (!docName.trim()) return toast.error('Ingresa un nombre');
    const fd = new FormData();
    fd.append('related_type', relatedType);
    fd.append('related_id', String(relatedId));
    fd.append('name', docName.trim());
    fd.append('document_type', docType);
    fd.append('file', file);
    setUpl(true);
    try {
      await uploadDocument(fd);
      toast.success('Documento subido');
      setDocName(''); setFile(null); if(inputRef.current) inputRef.current.value='';
      load();
    } catch { toast.error('Error subiendo documento'); }
    finally { setUpl(false); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`¿Eliminar "${name}"?`)) return;
    try { await deleteDocument(id); toast.success('Documento eliminado'); load(); }
    catch { toast.error('Error eliminando documento'); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box wide" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <span><FileText size={16}/> {title}</span>
          <button className="modal-close" onClick={onClose}><X size={18}/></button>
        </div>
        <div className="docs-container">
          {/* Upload form */}
          <form onSubmit={handleUpload} className="upload-form">
            <div className="upload-row">
              <input className="upload-name" placeholder="Nombre del documento *" value={docName}
                onChange={e => setDocName(e.target.value)} required/>
              <select className="upload-type" value={docType} onChange={e => setDocType(e.target.value)}>
                {DOC_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="upload-row">
              <label className="file-picker">
                <input type="file" ref={inputRef} style={{display:'none'}}
                  onChange={e => { setFile(e.target.files[0]); if(!docName) setDocName(e.target.files[0]?.name.replace(/\.[^.]+$/,'')||''); }}/>
                <Upload size={14}/> {file ? file.name : 'Seleccionar archivo...'}
              </label>
              <button type="submit" className="btn-primary" disabled={uploading||!file}>
                {uploading ? 'Subiendo...' : <><Upload size={14}/> Subir</>}
              </button>
            </div>
          </form>

          {/* Documents list */}
          <div className="docs-list">
            {docs.length === 0 && <div className="empty-state-sm">No hay documentos subidos.</div>}
            {docs.map(d => (
              <div key={d.id} className="doc-row">
                <File size={16} className="doc-icon"/>
                <div className="doc-info">
                  <span className="doc-name">{d.name}</span>
                  <span className="doc-meta">{d.document_type} · {fmtSize(d.file_size||0)} · {d.uploaded_at?.slice(0,10)}</span>
                </div>
                <div className="doc-actions">
                  <a href={`/api/documents/${d.id}/download`} target="_blank" rel="noreferrer"
                    className="action-btn edit-btn" title="Descargar"><Download size={13}/></a>
                  <button className="action-btn delete-btn" onClick={() => handleDelete(d.id, d.name)}
                    title="Eliminar"><Trash2 size={13}/></button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
