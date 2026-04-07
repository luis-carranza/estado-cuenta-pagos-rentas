import { Building2, FileText, Home, BookOpen, FolderOpen } from 'lucide-react';

const TABS = [
  { key: 'estado',    label: 'Estado de Cuenta', icon: Home },
  { key: 'projects',  label: 'Proyectos',         icon: Building2 },
  { key: 'units',     label: 'Unidades',           icon: BookOpen },
  { key: 'contracts', label: 'Contratos',          icon: FileText },
  { key: 'documents', label: 'Documentos',         icon: FolderOpen },
];

export default function Navbar({ active, onChange }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Building2 size={22} /> Estado de Cuenta
      </div>
      <div className="navbar-tabs">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button key={key} className={`nav-tab ${active === key ? 'active' : ''}`}
            onClick={() => onChange(key)}>
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>
    </nav>
  );
}
