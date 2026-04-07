import { Building2, Calendar, FileText } from 'lucide-react';

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' });
}

export default function Header({ header, activeProject }) {
  return (
    <div className="card mb-6">
      <div className="section-header">
        <span className="section-title">ESTADO DE CUENTA</span>
        {activeProject && (
          <span className="project-filter-badge">
            <Building2 size={12}/> {activeProject}
          </span>
        )}
      </div>
      <div className="header-info">
        <div className="header-row">
          <div className="header-item">
            <Calendar className="header-icon" size={16} />
            <span className="header-label">Periodo:</span>
            <span className="header-value">{formatDate(header?.periodo)}</span>
          </div>
          <div className="header-item">
            <Building2 className="header-icon" size={16} />
            <span className="header-label">Desarrollo:</span>
            <span className="header-value">{header?.desarrollo || '—'}</span>
          </div>
          <div className="header-item">
            <FileText className="header-icon" size={16} />
            <span className="header-label">Fecha Generación Reporte:</span>
            <span className="header-value">{formatDate(header?.fecha_reporte)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
