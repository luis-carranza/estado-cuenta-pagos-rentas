import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Building2, ChevronRight, DollarSign } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getProjects, createProject, updateProject, deleteProject } from '../services/api';
import ProjectModal from './ProjectModal';

const fmt = n => n != null ? new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(n) : null;

export default function ProjectsPage({ onSelectProject, onViewDetails }) {
  const [projects, setProjects] = useState([]);
  const [modal, setModal] = useState(null); // null | 'new' | project obj

  const load = () => getProjects().then(setProjects).catch(() => toast.error('Error cargando proyectos'));
  useEffect(() => { load(); }, []);

  const handleSave = async (data) => {
    try {
      if (modal?.id) { await updateProject(modal.id, data); toast.success('Proyecto actualizado'); }
      else           { await createProject(data);            toast.success('Proyecto creado');     }
      setModal(null); load();
    } catch { toast.error('Error guardando proyecto'); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`¿Eliminar proyecto "${name}" y todas sus unidades?`)) return;
    try { await deleteProject(id); toast.success('Proyecto eliminado'); load(); }
    catch { toast.error('Error eliminando proyecto'); }
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title"><Building2 size={20}/> Proyectos</h2>
        <button className="btn-primary" onClick={() => setModal('new')}>
          <Plus size={14}/> Nuevo Proyecto
        </button>
      </div>

      <div className="projects-grid">
        {projects.length === 0 && (
          <div className="empty-state">No hay proyectos aún. Crea el primero.</div>
        )}
        {projects.map(p => {
          const income = p.monthly_income || 0;
          const occ    = p.unit_count > 0
            ? Math.round((p.unit_count - (p.available_units||0)) / p.unit_count * 100)
            : 0;
          return (
            <div key={p.id} className="project-card">
              <div className="project-card-header">
                <span className="project-name">{p.name}</span>
                <div className="card-actions">
                  <button className="action-btn edit-btn"   onClick={() => setModal(p)}><Pencil size={14}/></button>
                  <button className="action-btn delete-btn" onClick={() => handleDelete(p.id, p.name)}><Trash2 size={14}/></button>
                </div>
              </div>
              {p.address     && <p className="project-meta">📍 {p.address}</p>}
              {p.description && <p className="project-desc">{p.description}</p>}

              <div className="project-stats">
                <span className="stat-pill total">{p.unit_count || 0} unidades</span>
                <span className="stat-pill avail">{p.available_units || 0} libres</span>
                <span className="stat-pill occ">{occ}% ocupación</span>
              </div>

              {/* Budget summary */}
              {income > 0 && (
                <div className="project-budget-row">
                  <DollarSign size={13} style={{color:'#6a1b9a'}}/>
                  <span className="project-budget-label">Ingreso mensual:</span>
                  <span className="project-budget-value">{fmt(income)}</span>
                </div>
              )}
              {p.total_budget > 0 && (
                <div className="project-budget-row" style={{opacity:0.7}}>
                  <span className="project-budget-label" style={{paddingLeft:17}}>Presupuesto:</span>
                  <span className="project-budget-value">{fmt(p.total_budget)}</span>
                </div>
              )}

              <div className="project-card-actions">
                <button className="btn-primary btn-sm flex-1" onClick={() => onViewDetails(p)}>
                  <Building2 size={13}/> Ver detalles
                </button>
                <button className="btn-outline flex-1" onClick={() => onSelectProject(p)}>
                  Unidades <ChevronRight size={13}/>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {modal && <ProjectModal project={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
    </div>
  );
}
