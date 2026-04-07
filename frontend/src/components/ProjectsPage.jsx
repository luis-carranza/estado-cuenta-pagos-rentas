import { useState, useEffect } from 'react';
import { Plus, Pencil, Trash2, Building2, ChevronRight } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { getProjects, createProject, updateProject, deleteProject } from '../services/api';
import ProjectModal from './ProjectModal';

export default function ProjectsPage({ onSelectProject }) {
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
        {projects.map(p => (
          <div key={p.id} className="project-card">
            <div className="project-card-header">
              <span className="project-name">{p.name}</span>
              <div className="card-actions">
                <button className="action-btn edit-btn" onClick={() => setModal(p)}><Pencil size={14}/></button>
                <button className="action-btn delete-btn" onClick={() => handleDelete(p.id, p.name)}><Trash2 size={14}/></button>
              </div>
            </div>
            {p.address    && <p className="project-meta">📍 {p.address}</p>}
            {p.description && <p className="project-desc">{p.description}</p>}
            <div className="project-stats">
              <span className="stat-pill total">{p.unit_count || 0} unidades</span>
              <span className="stat-pill avail">{p.available_units || 0} disponibles</span>
            </div>
            <button className="btn-outline full-width mt-8" onClick={() => onSelectProject(p)}>
              Ver unidades <ChevronRight size={14}/>
            </button>
          </div>
        ))}
      </div>

      {modal && <ProjectModal project={modal === 'new' ? null : modal}
        onClose={() => setModal(null)} onSave={handleSave} />}
    </div>
  );
}
