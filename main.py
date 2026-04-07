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
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        description TEXT,
        address     TEXT,
        created_at  TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS units (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id      INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        unit_number     TEXT NOT NULL,
        unit_type       TEXT DEFAULT 'DEPTO',
        purpose         TEXT DEFAULT 'RENTA',
        floor           INTEGER,
        area_sqm        REAL,
        rent_price      REAL,
        sale_price      REAL,
        is_available    INTEGER DEFAULT 1,
        current_tenant  TEXT,
        notes           TEXT
    );
    CREATE TABLE IF NOT EXISTS unit_services (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id      INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
        service_name TEXT NOT NULL,
        status       TEXT DEFAULT 'PENDIENTE',
        amount       REAL,
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
    conn.commit()

    # Seed pagos from Excel if table is empty
    if conn.execute("SELECT COUNT(*) FROM pagos").fetchone()[0] == 0:
        _seed_from_excel(conn)
    # Seed project + units if empty
    if conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
        _seed_project_and_units(conn)
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

UNITS_SEED = [
    # (unit_number, unit_type, client_name, rent_price)
    ("L-102B",      "LOCAL",  "MA GUADALUPE RAMOS AGUILAR",       12000.00),
    ("L-100A",      "LOCAL",  "LUCERO OLVERA",                    28500.00),
    ("L-105A",      "LOCAL",  "FRANCIS DOS SANTOS GARCIA",        25000.00),
    ("L-108A",      "LOCAL",  "MARIO DOMINGO HERNANDEZ",          26250.00),
    ("L-111A",      "LOCAL",  "LAURA YADIRA CALDERON",            26000.00),
    ("DEPTO 437E",  "DEPTO",  "EVA HORTENSIA DAVILA PEREZ",        8500.00),
    ("DEPTO 328D",  "DEPTO",  "ARMANDO GONZALEZ MARTINEZ",         9000.00),
    ("DEPTO 430E",  "DEPTO",  "DAVID RENE GOZNALEZ ROJAS",         8500.00),
    ("DEPTO 211A",  "DEPTO",  "SIDARTHA MONCADA SORIANO",         15000.00),
    ("DEPTO 130E",  "DEPTO",  "JORGE MANUEL GARDUÑO RIVERA",       9500.00),
    ("DEPTO 209A",  "DEPTO",  "MK GAON FOOD",                    15000.00),
    ("DEPTO 208A",  "DEPTO",  "MONIKA IVONNE ZEPEDA",            15000.00),
    ("DEPTO 429E",  "DEPTO",  "IVAN OMAR BERNAL ALCALA",         17850.00),
    ("DEPTO 438E",  "DEPTO",  "FREDDY CABAÑAS HERNANDEZ",         8900.00),
    ("DEPTO 327D",  "DEPTO",  "LISSETTE REYES GABRIEL",           9500.00),
    ("DEPTO 406A",  "DEPTO",  "DIEGO MARTINEZ MORENO",           10500.00),
    ("DEPTO 138E",  "DEPTO",  "MARIANA MEDINA ARAÑA",             9500.00),
    ("DEPTO 239E",  "DEPTO",  "DIEGO OMAR CAREAGA GOMEZ",         8500.00),
    ("DEPTO 203A",  "DEPTO",  "OSCAR ROSAS PANDURA",             12000.00),
    ("DEPTO 409A",  "DEPTO",  "MA CONCEPCION ORTEGA",            13000.00),
    ("DEPTO 200A",  "DEPTO",  "NORMA SILVIA LAGUNA CASSO",       14000.00),
    ("LOCAL 102A",  "LOCAL",  "LUIS ANTONIO MARTINEZ",           12500.00),
    ("LOCAL 112A",  "LOCAL",  "RAUL FLORENTINO",                 28087.00),
    ("DEPTO 202A",  "DEPTO",  "J JESUS CASTAÑEDA RAMIREZ",       14000.00),
    ("DEPTO 413A",  "DEPTO",  "ANEL NAVA FUENTES",               13650.00),
    ("DEPTO 400A",  "DEPTO",  "OSCAR MANCADA SERVIN",            14150.00),
    ("OXXO",        "COMERCIAL","OXXO",                           1898.55),
    ("DEPTO 140E",  "DEPTO",  "JOSE LEONARDO VAZQUEZ",            9500.00),
    ("DEPTO 402A",  "DEPTO",  "CARLOS A HERNANDEZ HERNANDEZ",    14000.00),
    ("DEPTO 105E",  "DEPTO",  "INQUILINO 30",                     9000.00),
    ("DEPTO 315D",  "DEPTO",  "INQUILINO 31",                     9500.00),
    ("DEPTO 501A",  "DEPTO",  "INQUILINO 32",                    13000.00),
]

DEFAULT_SERVICES = ["AGUA", "LUZ", "BASURA"]

def _seed_project_and_units(conn):
    cur = conn.execute(
        "INSERT INTO projects (name, description, address) VALUES (?,?,?)",
        ("Intercity / Condesa 1", "Desarrollo residencial y comercial", "Ciudad de México")
    )
    pid = cur.lastrowid
    for unit_number, unit_type, client, rent in UNITS_SEED:
        uc = conn.execute(
            """INSERT INTO units (project_id, unit_number, unit_type, purpose,
               rent_price, is_available, current_tenant)
               VALUES (?,?,?,'RENTA',?,0,?)""",
            (pid, unit_number, unit_type, rent, client)
        )
        uid = uc.lastrowid
        for svc in DEFAULT_SERVICES:
            conn.execute(
                "INSERT INTO unit_services (unit_id, service_name, status) VALUES (?,?,?)",
                (uid, svc, "PENDIENTE")
            )
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

class UnitIn(BaseModel):
    unit_number: str
    unit_type: Optional[str] = "DEPTO"
    purpose: Optional[str] = "RENTA"
    floor: Optional[int] = None
    area_sqm: Optional[float] = None
    rent_price: Optional[float] = None
    sale_price: Optional[float] = None
    is_available: Optional[bool] = True
    current_tenant: Optional[str] = None
    notes: Optional[str] = None

class UnitServiceIn(BaseModel):
    service_name: str
    status: Optional[str] = "PENDIENTE"
    amount: Optional[float] = None
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
        SELECT p.*, COUNT(u.id) as unit_count,
               SUM(CASE WHEN u.is_available=1 THEN 1 ELSE 0 END) as available_units
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

@app.post("/api/projects", status_code=201)
def create_project(p: ProjectIn):
    conn = get_db()
    cur = conn.execute("INSERT INTO projects (name,description,address) VALUES (?,?,?)",
                       (p.name, p.description, p.address))
    conn.commit()
    row = conn.execute("SELECT * FROM projects WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/projects/{pid}")
def update_project(pid: int, p: ProjectIn):
    conn = get_db()
    conn.execute("UPDATE projects SET name=?,description=?,address=? WHERE id=?",
                 (p.name, p.description, p.address, pid))
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
        SELECT u.*,
               COUNT(DISTINCT c.id) as contract_count,
               COALESCE(
                   (SELECT c2.tenant_name FROM contracts c2 WHERE c2.unit_id=u.id AND c2.status='ACTIVO' LIMIT 1),
                   u.current_tenant
               ) as display_tenant
        FROM units u LEFT JOIN contracts c ON c.unit_id=u.id
        WHERE u.project_id=? GROUP BY u.id ORDER BY u.unit_number""", (pid,)).fetchall()
    units = rows_to_list(rows)
    # Attach services to each unit
    for unit in units:
        svc_rows = conn.execute(
            "SELECT * FROM unit_services WHERE unit_id=? ORDER BY service_name",
            (unit["id"],)
        ).fetchall()
        unit["services"] = rows_to_list(svc_rows)
        unit["current_tenant"] = unit.pop("display_tenant", unit.get("current_tenant"))
    conn.close()
    return units

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
        area_sqm,rent_price,sale_price,is_available,current_tenant,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (pid, u.unit_number, u.unit_type, u.purpose, u.floor, u.area_sqm,
         u.rent_price, u.sale_price, 1 if u.is_available else 0, u.current_tenant, u.notes))
    uid = cur.lastrowid
    # Seed default services for new unit
    for svc in DEFAULT_SERVICES:
        conn.execute("INSERT INTO unit_services (unit_id, service_name, status) VALUES (?,?,?)",
                     (uid, svc, "PENDIENTE"))
    conn.commit()
    row = conn.execute("SELECT * FROM units WHERE id=?", (uid,)).fetchone()
    unit = row_to_dict(row)
    svc_rows = conn.execute("SELECT * FROM unit_services WHERE unit_id=? ORDER BY service_name", (uid,)).fetchall()
    unit["services"] = rows_to_list(svc_rows)
    conn.close()
    return unit

@app.put("/api/units/{uid}")
def update_unit(uid: int, u: UnitIn):
    conn = get_db()
    conn.execute("""UPDATE units SET unit_number=?,unit_type=?,purpose=?,floor=?,
        area_sqm=?,rent_price=?,sale_price=?,is_available=?,current_tenant=?,notes=? WHERE id=?""",
        (u.unit_number, u.unit_type, u.purpose, u.floor, u.area_sqm,
         u.rent_price, u.sale_price, 1 if u.is_available else 0, u.current_tenant, u.notes, uid))
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

# ── Routes: Unit Services ──────────────────────────────────────────────────────
@app.get("/api/units/{uid}/services")
def get_unit_services(uid: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM unit_services WHERE unit_id=? ORDER BY service_name", (uid,)).fetchall()
    conn.close()
    return rows_to_list(rows)

@app.post("/api/units/{uid}/services", status_code=201)
def create_unit_service(uid: int, s: UnitServiceIn):
    conn = get_db()
    unit = conn.execute("SELECT id FROM units WHERE id=?", (uid,)).fetchone()
    if not unit: raise HTTPException(404, "Unidad no encontrada")
    cur = conn.execute(
        "INSERT INTO unit_services (unit_id, service_name, status, amount, notes) VALUES (?,?,?,?,?)",
        (uid, s.service_name.upper(), s.status, s.amount, s.notes)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM unit_services WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.put("/api/unit-services/{sid}")
def update_unit_service(sid: int, s: UnitServiceIn):
    conn = get_db()
    existing = conn.execute("SELECT id FROM unit_services WHERE id=?", (sid,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(404, "Servicio no encontrado")
    conn.execute(
        "UPDATE unit_services SET service_name=?, status=?, amount=?, notes=? WHERE id=?",
        (s.service_name.upper(), s.status, s.amount, s.notes, sid)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM unit_services WHERE id=?", (sid,)).fetchone()
    conn.close()
    return row_to_dict(row)

@app.delete("/api/unit-services/{sid}")
def delete_unit_service(sid: int):
    conn = get_db()
    conn.execute("DELETE FROM unit_services WHERE id=?", (sid,))
    conn.commit(); conn.close()
    return {"message": "Servicio eliminado", "id": sid}

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
