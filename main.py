from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
import os, sqlite3, shutil, uuid
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DB_FILE    = BASE_DIR / "app.db"
UPLOADS    = BASE_DIR / "uploads"
EXCEL_FILE = BASE_DIR / "edo cuenta pagos rentas Final.xlsx"
UPLOADS.mkdir(exist_ok=True)

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Estado de Cuenta API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174",
                   "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# ── Database ─────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT NOT NULL,
        description  TEXT,
        address      TEXT,
        latitude     REAL,
        longitude    REAL,
        total_budget REAL,
        budget_notes TEXT,
        created_at   TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS units (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id   INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        unit_number  TEXT NOT NULL,
        unit_type    TEXT DEFAULT 'DEPTO',
        purpose      TEXT DEFAULT 'RENTA',
        floor        INTEGER,
        area_sqm     REAL,
        rent_price   REAL,
        sale_price   REAL,
        is_available INTEGER DEFAULT 1,
        notes        TEXT
    );
    CREATE TABLE IF NOT EXISTS contracts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id      INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
        tenant_name  TEXT NOT NULL,
        tenant_email TEXT,
        tenant_phone TEXT,
        start_date   TEXT,
        end_date     TEXT,
        monthly_rent REAL,
        deposit      REAL,
        payment_day  INTEGER DEFAULT 1,
        status       TEXT DEFAULT 'ACTIVO',
        notes        TEXT,
        created_at   TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS documents (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        related_type  TEXT NOT NULL,
        related_id    INTEGER NOT NULL,
        name          TEXT NOT NULL,
        document_type TEXT DEFAULT 'OTRO',
        file_name     TEXT NOT NULL,
        file_size     INTEGER,
        mime_type     TEXT,
        uploaded_at   TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS pagos (
        consecutivo         INTEGER PRIMARY KEY,
        fecha               TEXT,
        ubicacion           TEXT,
        desarrollo          TEXT,
        mes_correspondiente TEXT,
        cliente             TEXT,
        concepto            TEXT,
        monto               REAL DEFAULT 0,
        forma_de_pago       TEXT,
        semana_fiscal       INTEGER,
        project_id          INTEGER REFERENCES projects(id),
        month               INTEGER,
        year                INTEGER
    );
    """)
    # Migrate existing DB – add new columns if they don't exist yet
    for col, dfn in [
        ("latitude",     "REAL"),
        ("longitude",    "REAL"),
        ("total_budget", "REAL"),
        ("budget_notes", "TEXT"),
    ]:
        try:
            conn.execute(f"ALTER TABLE projects ADD COLUMN {col} {dfn}")
        except Exception:
            pass   # column already exists
    conn.commit()

    # Seed pagos from Excel if table is empty
    if conn.execute("SELECT COUNT(*) FROM pagos").fetchone()[0] == 0:
        _seed_from_excel(conn)
    conn.close()

def _seed_from_excel(conn):
    if not EXCEL_FILE.exists():
        return
    try:
        df = pd.read_excel(EXCEL_FILE, header=None)
        for _, row in df.iloc[11:].iterrows():
            raw_id = row[0]
            if raw_id is None or (isinstance(raw_id, float) and pd.isna(raw_id)):
                continue
            try:
                consecutivo = int(raw_id)
            except (ValueError, TypeError):
                continue
            fecha = row[1].strftime("%Y-%m-%d") if isinstance(row[1], datetime) else str(row[1]) if pd.notna(row[1]) else None
            conn.execute("""INSERT OR IGNORE INTO pagos
                (consecutivo,fecha,ubicacion,desarrollo,mes_correspondiente,
                 cliente,concepto,monto,forma_de_pago,semana_fiscal,month,year)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", (
                consecutivo, fecha,
                str(row[2]).strip() if pd.notna(row[2]) else None,
                str(row[3]).strip() if pd.notna(row[3]) else None,
                str(row[4]).strip() if pd.notna(row[4]) else None,
                str(row[5]).strip() if pd.notna(row[5]) else None,
                str(row[6]).strip() if pd.notna(row[6]) else None,
                float(row[7]) if pd.notna(row[7]) else 0.0,
                str(row[8]).strip() if pd.notna(row[8]) else None,
                int(row[9]) if pd.notna(row[9]) else None,
                3, 2026,
            ))
    except Exception as e:
        print(f"Excel seed warning: {e}")
    conn.commit()

init_db()

# ── Helpers ──────────────────────────────────────────────────────────────────
def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ── Pydantic Models ──────────────────────────────────────────────────────────
class ProjectIn(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_budget: Optional[float] = None
    budget_notes: Optional[str] = None

class UnitIn(BaseModel):
    unit_number: str
    unit_type: Optional[str] = "DEPTO"
    purpose: Optional[str] = "RENTA"
    floor: Optional[int] = None
    area_sqm: Optional[float] = None
    rent_price: Optional[float] = None
    sale_price: Optional[float] = None
    is_available: Optional[bool] = True
    notes: Optional[str] = None

class ContractIn(BaseModel):
    tenant_name: str
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    monthly_rent: Optional[float] = None
    deposit: Optional[float] = None
    payment_day: Optional[int] = 1
    status: Optional[str] = "ACTIVO"
    notes: Optional[str] = None

class PagoIn(BaseModel):
    fecha: Optional[str] = None
    ubicacion: Optional[str] = None
    desarrollo: Optional[str] = None
    mes_correspondiente: Optional[str] = None
    cliente: Optional[str] = None
    concepto: Optional[str] = None
    monto: float = 0.0
    forma_de_pago: Optional[str] = None
    semana_fiscal: Optional[int] = None
    project_id: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None

# ── Routes: Root ─────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"message": "Estado de Cuenta API v2 — running"}

# ── Routes: Estado de Cuenta (summary from DB) ───────────────────────────────
@app.get("/api/estado-cuenta")
def get_estado_cuenta(month: Optional[int] = None, year: Optional[int] = None,
                      project_id: Optional[int] = None):
    conn = get_db()
    where, params = [], []
    if month:    where.append("month=?");      params.append(month)
    if year:     where.append("year=?");       params.append(year)
    if project_id: where.append("project_id=?"); params.append(project_id)
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    rows = conn.execute(f"SELECT * FROM pagos {clause}", params).fetchall()
    pagos = rows_to_list(rows)

    efectivo = sum(p["monto"] for p in pagos if p.get("forma_de_pago","").upper() == "EFECTIVO")
    transf   = sum(p["monto"] for p in pagos if p.get("forma_de_pago","").upper() != "EFECTIVO")
    servicios= sum(p["monto"] for p in pagos if p.get("concepto") and
                   any(k in p["concepto"].upper() for k in ("AGUA","SERVICIO","LUZ","GAS")))

    # Read header info from Excel if available
    header = {"periodo": f"{year or 2026}-{month or 3:02d}-01",
              "desarrollo": "Intercity / Condesa 1", "fecha_reporte": datetime.now().strftime("%Y-%m-%d")}
    if EXCEL_FILE.exists() and not month and not project_id:
        try:
            df = pd.read_excel(EXCEL_FILE, header=None)
            def _d(v): return v.strftime("%Y-%m-%d") if isinstance(v, datetime) else str(v)
            header = {"periodo": _d(df.iloc[1,2]), "desarrollo": str(df.iloc[2,2]),
                      "fecha_reporte": _d(df.iloc[3,2])}
        except: pass

    conn.close()
    return {"header": header,
            "resumen": {"total_efectivo": efectivo, "total_transferencias": transf,
                        "gran_total": efectivo + transf, "pago_servicios": servicios,
                        "pago_renta": (efectivo + transf) - servicios}}

# ── Routes: Pagos ─────────────────────────────────────────────────────────────
@app.get("/api/pagos")
def get_pagos(forma_pago: Optional[str]=None, semana_fiscal: Optional[int]=None,
              search: Optional[str]=None, project_id: Optional[int]=None,
              month: Optional[int]=None, year: Optional[int]=None):
    conn = get_db()
    where, params = [], []
    if forma_pago:   where.append("UPPER(forma_de_pago) LIKE ?"); params.append(f"%{forma_pago.upper()}%")
    if semana_fiscal: where.append("semana_fiscal=?");             params.append(semana_fiscal)
    if project_id:   where.append("project_id=?");                params.append(project_id)
    if month:        where.append("month=?");                     params.append(month)
    if year:         where.append("year=?");                      params.append(year)
    if search:
        s = f"%{search.upper()}%"
        where.append("(UPPER(cliente) LIKE ? OR UPPER(concepto) LIKE ? OR UPPER(ubicacion) LIKE ?)")
        params += [s, s, s]
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    rows = conn.execute(f"SELECT * FROM pagos {clause} ORDER BY consecutivo", params).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/pagos/{consecutivo}")
def get_pago(consecutivo: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM pagos WHERE consecutivo=?", (consecutivo,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Pago no encontrado")
    return row_to_dict(row)

@app.post("/api/pagos", status_code=201)
def create_pago(pago: PagoIn):
    conn = get_db()
    max_id = conn.execute("SELECT MAX(consecutivo) FROM pagos").fetchone()[0] or 0
    new_id = max_id + 1
    conn.execute("""INSERT INTO pagos (consecutivo,fecha,ubicacion,desarrollo,mes_correspondiente,
        cliente,concepto,monto,forma_de_pago,semana_fiscal,project_id,month,year)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (new_id, pago.fecha, pago.ubicacion, pago.desarrollo, pago.mes_correspondiente,
         pago.cliente, pago.concepto, pago.monto, pago.forma_de_pago, pago.semana_fiscal,
         pago.project_id, pago.month, pago.year))
    conn.commit()
    row = conn.execute("SELECT * FROM pagos WHERE consecutivo=?", (new_id,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/pagos/{consecutivo}")
def update_pago(consecutivo: int, pago: PagoIn):
    conn = get_db()
    conn.execute("""UPDATE pagos SET fecha=?,ubicacion=?,desarrollo=?,mes_correspondiente=?,
        cliente=?,concepto=?,monto=?,forma_de_pago=?,semana_fiscal=?,project_id=?,month=?,year=?
        WHERE consecutivo=?""",
        (pago.fecha, pago.ubicacion, pago.desarrollo, pago.mes_correspondiente,
         pago.cliente, pago.concepto, pago.monto, pago.forma_de_pago, pago.semana_fiscal,
         pago.project_id, pago.month, pago.year, consecutivo))
    conn.commit()
    row = conn.execute("SELECT * FROM pagos WHERE consecutivo=?", (consecutivo,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Pago no encontrado")
    return row_to_dict(row)

@app.delete("/api/pagos/{consecutivo}")
def delete_pago(consecutivo: int):
    conn = get_db()
    conn.execute("DELETE FROM pagos WHERE consecutivo=?", (consecutivo,))
    conn.commit(); conn.close()
    return {"message": "Pago eliminado", "consecutivo": consecutivo}

# ── Routes: Projects ──────────────────────────────────────────────────────────
@app.get("/api/projects")
def get_projects():
    conn = get_db()
    rows = conn.execute("""
        SELECT p.*,
               COUNT(u.id) as unit_count,
               SUM(CASE WHEN u.is_available=1 THEN 1 ELSE 0 END) as available_units,
               SUM(CASE WHEN u.is_available=0 THEN u.rent_price ELSE 0 END) as monthly_income
        FROM projects p LEFT JOIN units u ON u.project_id=p.id
        GROUP BY p.id ORDER BY p.name""").fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/projects/{pid}")
def get_project(pid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Proyecto no encontrado")
    return row_to_dict(row)

@app.get("/api/projects/{pid}/budget")
def get_project_budget(pid: int):
    conn = get_db()
    proj = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    if not proj: raise HTTPException(404, "Proyecto no encontrado")

    units = conn.execute("SELECT * FROM units WHERE project_id=?", (pid,)).fetchall()
    total_units    = len(units)
    occupied_units = sum(1 for u in units if not u["is_available"])
    rent_potential = sum((u["rent_price"] or 0) for u in units)
    rent_actual    = sum((u["rent_price"] or 0) for u in units if not u["is_available"])

    contracts = conn.execute("""
        SELECT c.monthly_rent, c.status, c.tenant_name, c.start_date, c.end_date,
               u.unit_number
        FROM contracts c JOIN units u ON u.id=c.unit_id
        WHERE u.project_id=?""", (pid,)).fetchall()
    active_contracts  = [c for c in contracts if c["status"] == "ACTIVO"]
    contract_income   = sum(c["monthly_rent"] or 0 for c in active_contracts)

    payments = conn.execute(
        "SELECT SUM(monto) as total FROM pagos WHERE project_id=?", (pid,)).fetchone()
    total_collected = payments["total"] or 0

    # breakdown by unit_type
    breakdown = {}
    for u in units:
        t = u["unit_type"] or "OTRO"
        if t not in breakdown:
            breakdown[t] = {"total": 0, "occupied": 0, "rent_sum": 0}
        breakdown[t]["total"] += 1
        if not u["is_available"]:
            breakdown[t]["occupied"] += 1
            breakdown[t]["rent_sum"] += (u["rent_price"] or 0)

    conn.close()
    return {
        "project": row_to_dict(proj),
        "total_units": total_units,
        "occupied_units": occupied_units,
        "available_units": total_units - occupied_units,
        "occupancy_rate": round(occupied_units / total_units * 100, 1) if total_units else 0,
        "monthly_rent_potential": rent_potential,
        "monthly_rent_actual": rent_actual,
        "contract_income": contract_income,
        "active_contracts": len(active_contracts),
        "total_payments_collected": total_collected,
        "user_budget": proj["total_budget"] or 0,
        "budget_notes": proj["budget_notes"],
        "unit_type_breakdown": breakdown,
        "contracts": [dict(c) for c in active_contracts],
    }

@app.post("/api/projects", status_code=201)
def create_project(p: ProjectIn):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO projects (name,description,address,latitude,longitude,total_budget,budget_notes) VALUES (?,?,?,?,?,?,?)",
        (p.name, p.description, p.address, p.latitude, p.longitude, p.total_budget, p.budget_notes))
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/projects/{pid}")
def update_project(pid: int, p: ProjectIn):
    conn = get_db()
    conn.execute(
        "UPDATE projects SET name=?,description=?,address=?,latitude=?,longitude=?,total_budget=?,budget_notes=? WHERE id=?",
        (p.name, p.description, p.address, p.latitude, p.longitude, p.total_budget, p.budget_notes, pid))
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Proyecto no encontrado")
    return row_to_dict(row)

@app.delete("/api/projects/{pid}")
def delete_project(pid: int):
    conn = get_db()
    conn.execute("DELETE FROM projects WHERE id=?", (pid,))
    conn.commit(); conn.close()
    return {"message": "Proyecto eliminado", "id": pid}

# ── Routes: Units ─────────────────────────────────────────────────────────────
@app.get("/api/projects/{pid}/units")
def get_units(pid: int):
    conn = get_db()
    rows = conn.execute("""
        SELECT u.*, COUNT(c.id) as contract_count,
               (SELECT c2.tenant_name FROM contracts c2 WHERE c2.unit_id=u.id AND c2.status='ACTIVO' LIMIT 1) as current_tenant
        FROM units u LEFT JOIN contracts c ON c.unit_id=u.id
        WHERE u.project_id=? GROUP BY u.id ORDER BY u.unit_number""", (pid,)).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/units/{uid}")
def get_unit(uid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM units WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Unidad no encontrada")
    return row_to_dict(row)

@app.post("/api/projects/{pid}/units", status_code=201)
def create_unit(pid: int, u: UnitIn):
    conn = get_db()
    cur = conn.execute("""INSERT INTO units (project_id,unit_number,unit_type,purpose,floor,
        area_sqm,rent_price,sale_price,is_available,notes) VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (pid, u.unit_number, u.unit_type, u.purpose, u.floor, u.area_sqm,
         u.rent_price, u.sale_price, 1 if u.is_available else 0, u.notes))
    conn.commit()
    row = conn.execute("SELECT * FROM units WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/units/{uid}")
def update_unit(uid: int, u: UnitIn):
    conn = get_db()
    conn.execute("""UPDATE units SET unit_number=?,unit_type=?,purpose=?,floor=?,
        area_sqm=?,rent_price=?,sale_price=?,is_available=?,notes=? WHERE id=?""",
        (u.unit_number, u.unit_type, u.purpose, u.floor, u.area_sqm,
         u.rent_price, u.sale_price, 1 if u.is_available else 0, u.notes, uid))
    conn.commit()
    row = conn.execute("SELECT * FROM units WHERE id=?", (uid,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Unidad no encontrada")
    return row_to_dict(row)

@app.delete("/api/units/{uid}")
def delete_unit(uid: int):
    conn = get_db()
    conn.execute("DELETE FROM units WHERE id=?", (uid,))
    conn.commit(); conn.close()
    return {"message": "Unidad eliminada", "id": uid}

# ── Routes: Contracts ─────────────────────────────────────────────────────────
@app.get("/api/units/{uid}/contracts")
def get_contracts(uid: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM contracts WHERE unit_id=? ORDER BY created_at DESC", (uid,)).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.get("/api/contracts/{cid}")
def get_contract(cid: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM contracts WHERE id=?", (cid,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Contrato no encontrado")
    return row_to_dict(row)

@app.post("/api/units/{uid}/contracts", status_code=201)
def create_contract(uid: int, c: ContractIn):
    conn = get_db()
    cur = conn.execute("""INSERT INTO contracts (unit_id,tenant_name,tenant_email,tenant_phone,
        start_date,end_date,monthly_rent,deposit,payment_day,status,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, c.tenant_name, c.tenant_email, c.tenant_phone, c.start_date, c.end_date,
         c.monthly_rent, c.deposit, c.payment_day, c.status, c.notes))
    # Mark unit as unavailable if contract is active
    if c.status == "ACTIVO":
        conn.execute("UPDATE units SET is_available=0 WHERE id=?", (uid,))
    conn.commit()
    row = conn.execute("SELECT * FROM contracts WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/contracts/{cid}")
def update_contract(cid: int, c: ContractIn):
    conn = get_db()
    old = conn.execute("SELECT unit_id FROM contracts WHERE id=?", (cid,)).fetchone()
    conn.execute("""UPDATE contracts SET tenant_name=?,tenant_email=?,tenant_phone=?,
        start_date=?,end_date=?,monthly_rent=?,deposit=?,payment_day=?,status=?,notes=?
        WHERE id=?""",
        (c.tenant_name, c.tenant_email, c.tenant_phone, c.start_date, c.end_date,
         c.monthly_rent, c.deposit, c.payment_day, c.status, c.notes, cid))
    if old:
        uid = old["unit_id"]
        active = conn.execute("SELECT COUNT(*) FROM contracts WHERE unit_id=? AND status='ACTIVO'", (uid,)).fetchone()[0]
        conn.execute("UPDATE units SET is_available=? WHERE id=?", (0 if active else 1, uid))
    conn.commit()
    row = conn.execute("SELECT * FROM contracts WHERE id=?", (cid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.delete("/api/contracts/{cid}")
def delete_contract(cid: int):
    conn = get_db()
    row = conn.execute("SELECT unit_id FROM contracts WHERE id=?", (cid,)).fetchone()
    conn.execute("DELETE FROM contracts WHERE id=?", (cid,))
    if row:
        uid = row["unit_id"]
        active = conn.execute("SELECT COUNT(*) FROM contracts WHERE unit_id=? AND status='ACTIVO'", (uid,)).fetchone()[0]
        conn.execute("UPDATE units SET is_available=? WHERE id=?", (1 if not active else 0, uid))
    conn.commit(); conn.close()
    return {"message": "Contrato eliminado", "id": cid}

# ── Routes: Documents ─────────────────────────────────────────────────────────
@app.get("/api/documents")
def get_documents(related_type: Optional[str]=None, related_id: Optional[int]=None):
    conn = get_db()
    where, params = [], []
    if related_type: where.append("related_type=?"); params.append(related_type)
    if related_id:   where.append("related_id=?");   params.append(related_id)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    rows = conn.execute(f"SELECT * FROM documents {clause} ORDER BY uploaded_at DESC", params).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.post("/api/documents/upload", status_code=201)
async def upload_document(
    related_type: str = Form(...),
    related_id: int = Form(...),
    name: str = Form(...),
    document_type: str = Form("OTRO"),
    file: UploadFile = File(...),
):
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOADS / unique_name
    content = await file.read()
    dest.write_bytes(content)
    conn = get_db()
    cur = conn.execute("""INSERT INTO documents (related_type,related_id,name,document_type,
        file_name,file_size,mime_type) VALUES (?,?,?,?,?,?,?)""",
        (related_type, related_id, name, document_type, unique_name,
         len(content), file.content_type))
    conn.commit()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.get("/api/documents/{did}/download")
def download_document(did: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (did,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "Documento no encontrado")
    path = UPLOADS / row["file_name"]
    if not path.exists(): raise HTTPException(404, "Archivo no encontrado")
    return FileResponse(path, media_type=row["mime_type"] or "application/octet-stream",
                        filename=row["name"] + Path(row["file_name"]).suffix)

@app.delete("/api/documents/{did}")
def delete_document(did: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM documents WHERE id=?", (did,)).fetchone()
    if row:
        path = UPLOADS / row["file_name"]
        if path.exists(): path.unlink()
        conn.execute("DELETE FROM documents WHERE id=?", (did,))
        conn.commit()
    conn.close()
    return {"message": "Documento eliminado", "id": did}
