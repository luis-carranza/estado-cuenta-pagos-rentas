"""
seed_all.py — Master seed script for AWS deployment.
Creates the project, units, contracts and bank statement from scratch.
Run this ONCE on a fresh database:
    python seed_all.py
"""
import sqlite3, os
from pathlib import Path
from datetime import date

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
    from dateutil.relativedelta import relativedelta

DB_FILE = Path(os.environ.get("DB_FILE", Path(__file__).parent / "app.db"))

# ── helpers ───────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def contract_dates(mes_str, ref_year=2026, ref_month=3):
    """Derive 12-month contract start/end from 'N DE 12' notation."""
    if not mes_str:
        return None, None
    s = str(mes_str).strip().upper()
    try:
        if "Y" in s:
            n = int(s.split("Y")[0].strip().split()[0])
        elif "DE 12" in s:
            n = int(s.split("DE")[0].strip())
        else:
            return None, None
        ref   = date(ref_year, ref_month, 1)
        start = ref - relativedelta(months=n - 1)
        end   = start + relativedelta(months=12) - relativedelta(days=1)
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
    except Exception:
        return None, None

# ══════════════════════════════════════════════════════════════════════════════
# 1. PROJECT
# ══════════════════════════════════════════════════════════════════════════════
PROJECT = dict(
    name="Intercity Condesa",
    description="Proyecto piloto",
    address="Av. Insurgentes Sur 1234",
)

# ══════════════════════════════════════════════════════════════════════════════
# 2. UNITS + CONTRACTS (March 2026 data from Excel)
# ══════════════════════════════════════════════════════════════════════════════
UNITS = [
    # ── Locales ──────────────────────────────────────────────────────────────
    dict(unit_number="L-100A",     unit_type="LOCAL", floor=1, monthly_rent=28500,   mes_str="7 DE 12",  tenant="LUCERO OLVERA",                  notes="Sushi"),
    dict(unit_number="L-102A",     unit_type="LOCAL", floor=1, monthly_rent=12500,   mes_str="9 DE 12",  tenant="LUIS ANTONIO MARTINEZ",          notes="Tanque Oxigeno"),
    dict(unit_number="L-102B",     unit_type="LOCAL", floor=1, monthly_rent=12000,   mes_str="9 DE 12",  tenant="MA GUADALUPE RAMOS AGUILAR",     notes="Ezotenia"),
    dict(unit_number="L-105A",     unit_type="LOCAL", floor=1, monthly_rent=25000,   mes_str="12 DE 12", tenant="FRANCIS DOS SANTOS GARCIA",      notes="Papelería"),
    dict(unit_number="L-108A",     unit_type="LOCAL", floor=1, monthly_rent=26250,   mes_str="2 DE 12",  tenant="MARIO DOMINGO HERNANDEZ",        notes="Estética"),
    dict(unit_number="L-111A",     unit_type="LOCAL", floor=1, monthly_rent=26000,   mes_str="2 DE 12",  tenant="LAURA YADIRA CALDERON",          notes="Helados"),
    dict(unit_number="L-112A",     unit_type="LOCAL", floor=1, monthly_rent=28087,   mes_str="7 DE 12",  tenant="RAUL FLORENTINO",               notes="Bendito Bocado"),
    dict(unit_number="L-201B",     unit_type="LOCAL", floor=2, monthly_rent=10500,   mes_str="2 DE 12",  tenant="OSCAR HUGO MORALES GARCIA",      notes="Spa"),
    dict(unit_number="OXXO",       unit_type="LOCAL", floor=1, monthly_rent=1898.55, mes_str=None,       tenant="OXXO",                           notes="Primer pago OXXO"),
    # ── Departamentos Torre A ─────────────────────────────────────────────────
    dict(unit_number="DEPTO-200A", unit_type="DEPTO", floor=2, monthly_rent=14000,   mes_str="9 DE 12",  tenant="NORMA SILVIA LAGUNA CASSO"),
    dict(unit_number="DEPTO-201A", unit_type="DEPTO", floor=2, monthly_rent=14000,   mes_str="8 DE 12",  tenant="RAUL IRAGORRI"),
    dict(unit_number="DEPTO-202A", unit_type="DEPTO", floor=2, monthly_rent=14000,   mes_str="9 DE 12",  tenant="J JESUS CASTAÑEDA RAMIREZ"),
    dict(unit_number="DEPTO-203A", unit_type="DEPTO", floor=2, monthly_rent=12000,   mes_str="9 DE 12",  tenant="OSCAR ROSAS PANDURA"),
    dict(unit_number="DEPTO-208A", unit_type="DEPTO", floor=2, monthly_rent=15000,   mes_str="4 DE 12",  tenant="MONIKA IVONNE ZEPEDA"),
    dict(unit_number="DEPTO-209A", unit_type="DEPTO", floor=2, monthly_rent=15000,   mes_str="2 DE 12",  tenant="MK GAON FOOD"),
    dict(unit_number="DEPTO-211A", unit_type="DEPTO", floor=2, monthly_rent=15000,   mes_str="9 DE 12",  tenant="SIDARTHA MONCADA SORIANO"),
    dict(unit_number="DEPTO-400A", unit_type="DEPTO", floor=4, monthly_rent=14150,   mes_str="4 DE 12",  tenant="OSCAR MANCADA SERVIN"),
    dict(unit_number="DEPTO-402A", unit_type="DEPTO", floor=4, monthly_rent=14000,   mes_str="8 DE 12",  tenant="CARLOS A HERNANDEZ HERNANDEZ"),
    dict(unit_number="DEPTO-406A", unit_type="DEPTO", floor=4, monthly_rent=10500,   mes_str="7 DE 12",  tenant="DIEGO MARTINEZ MORENO"),
    dict(unit_number="DEPTO-409A", unit_type="DEPTO", floor=4, monthly_rent=13000,   mes_str="8 DE 12",  tenant="MA CONCEPCION ORTEGA"),
    dict(unit_number="DEPTO-413A", unit_type="DEPTO", floor=4, monthly_rent=13650,   mes_str="9 DE 12",  tenant="ANEL NAVA FUENTES"),
    # ── Departamentos Torre D ─────────────────────────────────────────────────
    dict(unit_number="DEPTO-327D", unit_type="DEPTO", floor=3, monthly_rent=9500,    mes_str=None,       tenant="LISSETTE REYES GABRIEL"),
    dict(unit_number="DEPTO-328D", unit_type="DEPTO", floor=3, monthly_rent=9000,    mes_str="10 DE 12", tenant="ARMANDO GONZALEZ MARTINEZ"),
    # ── Departamentos Torre E ─────────────────────────────────────────────────
    dict(unit_number="DEPTO-130E", unit_type="DEPTO", floor=1, monthly_rent=9500,    mes_str="9 DE 12",  tenant="JORGE MANUEL GARDUÑO RIVERA"),
    dict(unit_number="DEPTO-138E", unit_type="DEPTO", floor=1, monthly_rent=9500,    mes_str="8 DE 12",  tenant="MARIANA MEDINA ARAÑA"),
    dict(unit_number="DEPTO-140E", unit_type="DEPTO", floor=1, monthly_rent=9500,    mes_str="9 DE 12",  tenant="JOSE LEONARDO VAZQUEZ"),
    dict(unit_number="DEPTO-239E", unit_type="DEPTO", floor=2, monthly_rent=8500,    mes_str="9 DE 12",  tenant="DIEGO OMAR CAREAGA GOMEZ"),
    dict(unit_number="DEPTO-429E", unit_type="DEPTO", floor=4, monthly_rent=8925,    mes_str="2 DE 12",  tenant="IVAN OMAR BERNAL ALCALA"),
    dict(unit_number="DEPTO-430E", unit_type="DEPTO", floor=4, monthly_rent=8500,    mes_str="9 DE 12",  tenant="DAVID RENE GONZALEZ ROJAS"),
    dict(unit_number="DEPTO-437E", unit_type="DEPTO", floor=4, monthly_rent=8500,    mes_str="8 DE 12",  tenant="EVA HORTENSIA DAVILA PEREZ"),
    dict(unit_number="DEPTO-438E", unit_type="DEPTO", floor=4, monthly_rent=8900,    mes_str="3 DE 12",  tenant="FREDDY CABAS HERNANDEZ"),
]

# ══════════════════════════════════════════════════════════════════════════════
# 3. BANK STATEMENT — BBVA March 2026
# ══════════════════════════════════════════════════════════════════════════════
BANK_TRANSACTIONS = [
    ("2026-03-09","CFE Electricidad","GUIA:4966393 REF:01077221058758260308 CIE:0578869",2424.00,"DEBITO",None,"Pago CFE bimestral"),
    ("2026-03-09","BNET Carpetería Lefort","BNET 0465496950 CARPETAR LEFORT",0.00,"DEBITO",None,"Monto no legible en estado"),
    ("2026-03-09","Depósito efectivo PRACTIC MAROQ","PRAC E121 FOLIO:8607 203-A",200.00,"CREDITO",None,"Depósito efectivo sucursal PRACTIC dpto 203-A"),
    ("2026-03-10","Renta Marzo dpto 210-A","BNET 0488656509 rentaMar210A",15000.00,"CREDITO",None,"PAGO CUENTA DE TERCERO/0016785916 — renta unidad 210-A"),
    ("2026-03-11","SPEI Recibido Santander — FT.N.920570A23559","SPEI RECIBIDOSANTANDER/0194698778 014",56000.00,"CREDITO",2395004.07,"Ingreso Santander"),
    ("2026-03-11","SPEI Enviado Banregio — Pago terreno 7","SPEI ENVIADO BANREGIO/0046213255 058",193930.41,"DEBITO",None,"Pago terreno 7"),
    ("2026-03-11","SPEI Enviado Banregio — Pago LTE 5 Alberto","SPEI ENVIADO BANREGIO/0046213940 058",574499.27,"DEBITO",None,"Pago lote 5 Alberto"),
    ("2026-03-11","BNET FA B4018 Ajuste chapa","BNET 1512784421 FA B4018 AJUSTE CH",0.00,"DEBITO",None,"Ajuste chapa — monto no legible"),
    ("2026-03-11","BNET OQM Intercity","BNET 0465496950 OQM INTERCITY",12818.00,"DEBITO",None,"Servicio OQM Intercity"),
    ("2026-03-11","BNET Extintor — FA 6074","BNET 0118109699 FA 6074 EXTINTOR C",1080.01,"DEBITO",None,"Recarga/mantenimiento extintores"),
    ("2026-03-11","BNET Dpto 308-A","BNET 0144686055 308A",843.00,"DEBITO",None,"Servicio/mantenimiento unidad 308-A"),
    ("2026-03-12","Depósito efectivo PRACTIC — Intercity Marzo D745","DEPOSITO EFECTIVO PRACTIC/******6172 FOLIO:9529",0.00,"CREDITO",None,"Depósito en sucursal PRACTIC — unidad 206-2 — monto no legible"),
    ("2026-03-12","SPEI Recibido Inbursa — Renta Marzo Marcos Vancini","SPEI RECIBIDOINBURSA/0101499058 036",24000.00,"CREDITO",None,"Renta Marcos Vancini unidad 410-A (aprox.)"),
    ("2026-03-13","BNET FA 2611 Mantenimiento Condesa","BNET 5749913900 FA 2611 MTTOS COND",0.00,"DEBITO",None,"Mantenimiento Condesa — monto no legible"),
    ("2026-03-13","BNET FA 97 Pintura dpto 227-D","BNET 0486207979 FA 97 PINTURA 227D",5000.00,"DEBITO",None,"Pintura departamento 227-D"),
    ("2026-03-13","SPEI Recibido Santander","SPEI RECIBIDOSANTANDER/0107095069 014",3498.52,"CREDITO",1643587.97,"Pago Santander"),
    ("2026-03-13","Predial Municipio de Querétaro","MUNICIPIO DE QUERETA/GUIA:7326930",19033.00,"DEBITO",1629474.97,"Pago predial"),
    ("2026-03-13","BNET FA B7 Miguel Vega","BNET 4508309053 FA B7 MIGUEL VEGA G",8000.00,"DEBITO",1615474.97,"Pago a Miguel Vega"),
    ("2026-03-13","BNET FA E7F17 Contador Arce","BNET 2861320963 FA E7F17 CONTA ARC",20200.00,"DEBITO",None,"Honorarios contador Arce"),
    ("2026-03-13","Depósito efectivo PRACTIC — Renta E094","DEPOSITO EFECTIVO PRACTIC/******6172 RENTA E094",9000.00,"CREDITO",None,"Depósito renta E094"),
    ("2026-03-14","SPEI Recibido HSBC — Alberto Danilo Romero Pérez","SPEI RECIBIDOHSBC/0115109371 021",0.00,"CREDITO",None,"Transferencia propia dpto 483-A — monto no legible"),
    ("2026-03-14","Depósito efectivo PRACTIC — DRO DBA FOLIO:2857","DEPOSITO EFECTIVO PRACTIC/******6172 PRAC 9918",2200.00,"CREDITO",None,"Depósito efectivo"),
    ("2026-03-14","Depósito efectivo PRACTIC — MAR14","DEPOSITO EFECTIVO PRACTIC/******6172 MAR14",45000.00,"CREDITO",1631254.97,"Depósito grande sucursal PRACTIC"),
    ("2026-03-14","SPEI Recibido HSBC — Intercity E338","SPEI RECIBIDOHSBC/0116399384 021",0.00,"CREDITO",None,"Intercity E338 dpto 338-A — monto no legible"),
    ("2026-03-14","SPEI Recibido Bancoppel — Condesa 309-A","SPEI RECIBIDOBANCOPPEL/0117832396 137",0.00,"CREDITO",None,"Pago condesa unidad 309-A — monto no legible"),
    ("2026-03-16","SPEI Recibido Nu Mexico — Transferencia","SPEI RECIBIDONU MEXICO/0130869577 638",8900.00,"CREDITO",1678654.97,"Transferencia Nu Mexico"),
    ("2026-03-17","SPEI Recibido Inbursa — 9603171304","SPEI RECIBIDOINBURSA/0132405954 036",14000.00,"CREDITO",1692654.97,"Depósito Inbursa"),
    ("2026-03-17","BNET — Transferencia Intercity 497","73797 2TRANSFERENCIA INTERCITY 497 BUE-D",8500.00,"DEBITO",1701184.97,"Transferencia Intercity unidad BUE-D"),
    ("2026-03-19","SPEI Recibido Inbursa — Renta Marzo 2026 depto Condesa","SPEI RECIBIDO 036 — rco5z6",19000.00,"CREDITO",None,"Renta Condesa marzo 2026"),
    ("2026-03-20","REF CIE-0624101 — Cargo servicio","REF-030041200663717260 CIE-0624101",20148.46,"DEBITO",1870131.64,"Cargo automático"),
    ("2026-03-20","BNET FA49 Líneas hidráulicas","BNET 0477813058 FA49 LINEASHIDRA",981.36,"DEBITO",1590697.70,"Líneas hidráulicas"),
    ("2026-03-20","SPEI Recibido Bancoppel — Transf. Alberto Danilo","SPEI RECIBIDOBANCOPPEL/0149750609 137",10000.00,"CREDITO",None,"Transferencia Bancoppel"),
    ("2026-03-21","PAGO — unidad YOS-A","PAGO CUENTA DE TERCERO YOS-A",10500.00,"CREDITO",1589319.64,"Depósito renta unidad Yos-A"),
    ("2026-03-22","BNET OQM DROAS Condesa","BNET 0465496950 OQM DROAS CONDESA",9500.00,"DEBITO",1598819.64,"Servicio OQM Condesa"),
    ("2026-03-23","Depósito / Transferencia dpto 203-A","BRO 203-A",12000.00,"CREDITO",1580776.62,"Renta unidad 203-A"),
    ("2026-03-24","Depósito en efectivo — dpto 407-A","DEPOSITO EN EFECTIVO/0005554 407-A",13000.00,"CREDITO",1593776.62,"Renta unidad 407-A"),
    ("2026-03-24","BNET Depósito dpto 200-A","BNET 2661997855 depto 200A",14000.00,"CREDITO",1607776.62,"Renta unidad 200-A"),
    ("2026-03-25","Depósito en efectivo — dpto 202-A","DEPOSITO EN EFECTIVO/00055560202 202-A",14000.00,"CREDITO",1621776.62,"Renta unidad 202-A"),
    ("2026-03-25","SPEI Recibido STP — 9040086","SPEI RECIBIDOSTP/0178206834 646",15850.00,"CREDITO",None,"Transferencia STP"),
    ("2026-03-26","SPEI Recibido Scotiabank — Transferencia a Riscos","SPEI RECIBIDOSCOTIABANK/0186286533 044",0.00,"CREDITO",None,"Transferencia Scotiabank a Riscos — monto no legible"),
    ("2026-03-26","SPEI Recibido Scotiabank — Transferencia a Riscos (2)","SPEI RECIBIDOSCOTIABANK/0186292623 044",0.00,"CREDITO",None,"Segunda transferencia Scotiabank — monto no legible"),
    ("2026-03-26","BNET Agua 440-E Intercity","BNET 0125434882 AGUA 440E INTER",879.00,"DEBITO",None,"Pago agua unidad 440-E"),
    ("2026-03-26","SPEI Enviado Inbursa — Term Obra L29","SPEI ENVIADO INBURSA/0095071212 036",0.00,"DEBITO",None,"Terminación obra lote 29 — monto no legible"),
    ("2026-03-27","BNET FA51 Mantenimiento dpto 43","BNET 0477813058 FA 51 MTTO DPTO 43",0.00,"DEBITO",None,"Mantenimiento dpto 43 — monto no legible"),
    ("2026-03-27","BNET FA52 Puerta 307-A","BNET 0477813058 FA 52 PUERTA 307A",3758.40,"DEBITO",1643621.62,"Reparación puerta dpto 307-A"),
    ("2026-03-27","SPEI Enviado Bancoppel — Riego Condesa","SPEI ENVIADO BANCOPPEL/0025245084 137",1992.00,"DEBITO",1625629.00,"Servicio riego Condesa"),
    ("2026-03-27","SPEI Enviado Mercado Pago — Pintura dpto 307-A","SPEI ENVIADO Mercado Pago/0025211964 722",0.00,"DEBITO",None,"Pintura dpto 307-A — monto no legible"),
    ("2026-03-27","SPEI Enviado Citi Mexico — Inmueble 24","SPEI ENVIADO CITI MEXICO/0025208903 124",0.00,"DEBITO",None,"Pago inmueble 24 — monto no legible"),
    ("2026-03-27","BNET FA B4018 Ajuste chapa dpto","BNET 0477813058 FA 52/51 AJUSTE",0.00,"DEBITO",None,"Ajuste chapa — monto no legible"),
    ("2026-03-27","SPEI Recibido Santander — Pago Inmobiliaria 78","SPEI RECIBIDOSANTANDER/0190506781 014",1898.55,"CREDITO",1665170.55,"Pago inmobiliaria 78"),
    ("2026-03-27","BNET FA 2612 Mantenimientos varios","BNET 2712913992 FA 2612 MTTOS VARI",8236.00,"DEBITO",None,"Mantenimientos varios"),
    ("2026-03-27","BNET FA ES6BF Chapa dpto 211","BNET 1512784421 FA ES6BF CHAPA 211",1064.00,"DEBITO",None,"Chapa departamento 211"),
    ("2026-03-30","BNET Telmex casa Lic. Al.","BNET 0465496950 TELMEX CASA LIC AL",0.00,"DEBITO",1663908.55,"Pago Telmex — monto no legible"),
    ("2026-03-30","BNET Local 102-B","BNET 0477780990 local 102 B",8480.40,"DEBITO",None,"Cargo local 102-B"),
    ("2026-03-30","SPEI Recibido Banamex — Dpto 140-E","SPEI RECIBIDOBANAMEX/0106530680 002",9500.00,"CREDITO",1673858.95,"Renta unidad 140-E"),
    ("2026-03-30","SPEI Recibido HSBC — 402-A V0","SPEI RECIBIDOHSBC/0107033356 021",14000.00,"CREDITO",1687858.95,"Renta unidad 402-A"),
    ("2026-03-30","BNET FA 4028D Jabón Manor","BNET 1145096197 FA 4028D JABON MAN",812.00,"DEBITO",1687046.95,"Jabonera Manor — suministro"),
    ("2026-03-30","SPEI Recibido Banamex — Transferencia BDI-A","SPEI RECIBIDOBANAMEX/0107850688 002",14000.00,"CREDITO",1701046.95,"Renta / transferencia BDI-A"),
]


# ══════════════════════════════════════════════════════════════════════════════
def main():
    print(f"Database: {DB_FILE}")
    conn = get_db()

    # ── Schema (in case this runs before main.py) ─────────────────────────────
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        description TEXT, address TEXT, latitude REAL, longitude REAL,
        total_budget REAL, budget_notes TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
        unit_number TEXT NOT NULL, unit_type TEXT DEFAULT 'DEPTO',
        purpose TEXT DEFAULT 'RENTA', floor INTEGER, area_sqm REAL,
        rent_price REAL, sale_price REAL, is_available INTEGER DEFAULT 1, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unit_id INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
        tenant_name TEXT NOT NULL, tenant_email TEXT, tenant_phone TEXT,
        start_date TEXT, end_date TEXT, monthly_rent REAL, deposit REAL,
        payment_day INTEGER DEFAULT 1, status TEXT DEFAULT 'ACTIVO', notes TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS pagos (
        consecutivo INTEGER PRIMARY KEY, fecha TEXT, ubicacion TEXT,
        desarrollo TEXT, mes_correspondiente TEXT, cliente TEXT,
        concepto TEXT, monto REAL DEFAULT 0, forma_de_pago TEXT,
        semana_fiscal INTEGER, project_id INTEGER REFERENCES projects(id),
        month INTEGER, year INTEGER
    );
    CREATE TABLE IF NOT EXISTS bank_statements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
        bank_name TEXT, account_number TEXT, account_alias TEXT,
        period_month INTEGER, period_year INTEGER, description TEXT,
        total_credits REAL DEFAULT 0, total_debits REAL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS bank_statement_lines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        statement_id INTEGER NOT NULL REFERENCES bank_statements(id) ON DELETE CASCADE,
        line_date TEXT, description TEXT, reference TEXT,
        amount REAL DEFAULT 0, transaction_type TEXT DEFAULT 'CREDITO',
        balance REAL, is_matched INTEGER DEFAULT 0, notes TEXT
    );
    CREATE TABLE IF NOT EXISTS statement_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_id INTEGER NOT NULL REFERENCES bank_statement_lines(id) ON DELETE CASCADE,
        unit_id INTEGER REFERENCES units(id) ON DELETE SET NULL,
        contract_id INTEGER REFERENCES contracts(id) ON DELETE SET NULL,
        pago_id INTEGER REFERENCES pagos(consecutivo) ON DELETE SET NULL,
        match_notes TEXT, matched_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # ── 1. Project ────────────────────────────────────────────────────────────
    existing_proj = conn.execute("SELECT id FROM projects WHERE name=?", (PROJECT["name"],)).fetchone()
    if existing_proj:
        project_id = existing_proj["id"]
        print(f"Project already exists (id={project_id})")
    else:
        cur = conn.execute(
            "INSERT INTO projects (name,description,address) VALUES (?,?,?)",
            (PROJECT["name"], PROJECT["description"], PROJECT["address"])
        )
        project_id = cur.lastrowid
        print(f"Created project id={project_id}: {PROJECT['name']}")

    # ── 2. Units + Contracts ──────────────────────────────────────────────────
    existing_units = {r["unit_number"] for r in
                      conn.execute("SELECT unit_number FROM units WHERE project_id=?",
                                   (project_id,)).fetchall()}
    u_created = c_created = 0
    for u in UNITS:
        if u["unit_number"] in existing_units:
            continue
        cur = conn.execute(
            "INSERT INTO units (project_id,unit_number,unit_type,purpose,floor,rent_price,is_available,notes) VALUES (?,?,?,?,?,?,0,?)",
            (project_id, u["unit_number"], u["unit_type"], "RENTA",
             u.get("floor"), u["monthly_rent"], u.get("notes"))
        )
        unit_id = cur.lastrowid
        start_d, end_d = contract_dates(u.get("mes_str"))
        conn.execute(
            "INSERT INTO contracts (unit_id,tenant_name,start_date,end_date,monthly_rent,deposit,payment_day,status) VALUES (?,?,?,?,?,?,1,'ACTIVO')",
            (unit_id, u["tenant"], start_d, end_d, u["monthly_rent"], u["monthly_rent"])
        )
        u_created += 1; c_created += 1
        print(f"  + {u['unit_number']:20s}  {u['tenant'][:40]:<40}  ${u['monthly_rent']:>10,.2f}")

    print(f"Units created: {u_created}  |  Contracts created: {c_created}")

    # ── 3. Bank Statement — BBVA March 2026 ──────────────────────────────────
    existing_bs = conn.execute(
        "SELECT id FROM bank_statements WHERE account_number='0481236172' AND period_month=3 AND period_year=2026"
    ).fetchone()
    if existing_bs:
        print(f"Bank statement already exists (id={existing_bs['id']})")
    else:
        cur = conn.execute(
            "INSERT INTO bank_statements (project_id,bank_name,account_number,account_alias,period_month,period_year,description) VALUES (?,?,?,?,?,?,?)",
            (project_id, "BBVA", "0481236172", "Cuenta Principal BBVA", 3, 2026,
             "Estado de cuenta BBVA — Marzo 2026 — ROMERO PEREZ ALBERTO DANILO")
        )
        sid = cur.lastrowid
        for tx in BANK_TRANSACTIONS:
            conn.execute(
                "INSERT INTO bank_statement_lines (statement_id,line_date,description,reference,amount,transaction_type,balance,notes) VALUES (?,?,?,?,?,?,?,?)",
                (sid, tx[0], tx[1], tx[2], tx[3], tx[4], tx[5], tx[6])
            )
        r = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN transaction_type='CREDITO' THEN amount ELSE 0 END),0) as c, COALESCE(SUM(CASE WHEN transaction_type='DEBITO' THEN amount ELSE 0 END),0) as d FROM bank_statement_lines WHERE statement_id=?",
            (sid,)
        ).fetchone()
        conn.execute("UPDATE bank_statements SET total_credits=?,total_debits=? WHERE id=?", (r["c"], r["d"], sid))
        count = conn.execute("SELECT COUNT(*) FROM bank_statement_lines WHERE statement_id=?", (sid,)).fetchone()[0]
        print(f"Bank statement created id={sid} — {count} lines  |  Credits: ${r['c']:,.2f}  Debits: ${r['d']:,.2f}")

    conn.commit()
    conn.close()
    print("\n✅ Seed complete.")


if __name__ == "__main__":
    main()

