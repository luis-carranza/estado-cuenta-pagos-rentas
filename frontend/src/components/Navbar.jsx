import { Building2, FileText, Home, BookOpen, FolderOpen } from 'lucide-react';

const TABS = [
  { key: 'estado',    label: 'Estado de Cuenta', icon: Home },
  { key: 'projects',  label: 'Proyectos',         icon: Building2 },
  { key: 'units',     label: 'Unidades',           icon: BookOpen },
  { key: 'contracts', label: 'Contratos',          icon: FileText },
  { key: 'documents', label: 'Documentos',         icon: FolderOpen },
];

export default function Navbar({ active, onChange }) {
  // treat project-details as part of the projects section
  const effectiveActive = active === 'project-details' ? 'projects' : active;
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Building2 size={22} /> RISKOS DIVISION RENTAS
      </div>
      <div className="navbar-tabs">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button key={tab.key} className={`nav-tab ${effectiveActive === tab.key ? 'active' : ''}`}
              onClick={() => onChange(tab.key)}>
              <Icon size={15} /> {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
