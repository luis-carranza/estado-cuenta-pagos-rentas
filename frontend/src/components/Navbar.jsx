import { Building2, Home, FolderOpen, Landmark } from 'lucide-react';

const TABS = [
  { key: 'estado',    label: 'Estado de Cuenta', icon: Home },
  { key: 'projects',  label: 'Proyectos',         icon: Building2 },
  { key: 'documents', label: 'Documentos',         icon: FolderOpen },
  { key: 'bancos',    label: 'Bancos',             icon: Landmark },
];

export default function Navbar({ active, onChange }) {
  // units / contracts / project-details all belong to the projects section
  // banco-detail belongs to the bancos section
  const effectiveActive = ['project-details','units','contracts'].includes(active) ? 'projects'
                        : active === 'banco-detail' ? 'bancos'
                        : active;
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Building2 size={22} /> Estado de Cuenta
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
