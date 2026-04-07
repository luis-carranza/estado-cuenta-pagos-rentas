"""
Seed script – populates units + contracts from the xlsx payment register.
Run once:  python seed_units.py
"""
import sqlite3
from datetime import date
from dateutil.relativedelta import relativedelta

DB_FILE = "app.db"
PROJECT_ID = 1        # "Intercity Condesa" already in DB
REPORT_YEAR = 2026
REPORT_MONTH = 3      # March 2026 is the period of the Excel

# ---------------------------------------------------------------------------
# Helper: derive contract start/end from "N DE 12" string
# March 2026 is payment #N → start was March - (N-1) months ago
# ---------------------------------------------------------------------------
def contract_dates(mes_str):
    if not mes_str:
        return None, None
    s = str(mes_str).strip().upper()
    # Handle "2 Y 3 DE 12" (two months paid together – take the lower N)
    if "Y" in s:
        parts = s.split("Y")
        try:
            n = int(parts[0].strip().split()[0])
        except Exception:
            return None, None
    elif "DE 12" in s:
        try:
            n = int(s.split("DE")[0].strip())
        except Exception:
            return None, None
    else:
        return None, None

    ref = date(REPORT_YEAR, REPORT_MONTH, 1)
    start = ref - relativedelta(months=n - 1)
    end   = start + relativedelta(months=12) - relativedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Unit data derived from Excel rows (unique ubicaciones)
# Fields: unit_number, unit_type, floor, tenant, monthly_rent, mes_str
# ---------------------------------------------------------------------------
UNITS = [
    # ---- Locales (ground-floor commercial) --------------------------------
    dict(unit_number="L-100A",      unit_type="LOCAL", floor=1,
         tenant="LUCERO OLVERA",                    monthly_rent=28500,  mes_str="7 DE 12",
         notes="Sushi"),
    dict(unit_number="L-102A",      unit_type="LOCAL", floor=1,
         tenant="LUIS ANTONIO MARTINEZ",            monthly_rent=12500,  mes_str="9 DE 12",
         notes="Tanque Oxigeno"),
    dict(unit_number="L-102B",      unit_type="LOCAL", floor=1,
         tenant="MA GUADALUPE RAMOS AGUILAR",       monthly_rent=12000,  mes_str="9 DE 12",
         notes="Ezotenia"),
    dict(unit_number="L-105A",      unit_type="LOCAL", floor=1,
         tenant="FRANCIS DOS SANTOS GARCIA",        monthly_rent=25000,  mes_str="12 DE 12",
         notes="Papelería"),
    dict(unit_number="L-108A",      unit_type="LOCAL", floor=1,
         tenant="MARIO DOMINGO HERNANDEZ",          monthly_rent=26250,  mes_str="2 DE 12",
         notes="Estética"),
    dict(unit_number="L-111A",      unit_type="LOCAL", floor=1,
         tenant="LAURA YADIRA CALDERON",            monthly_rent=26000,  mes_str="2 DE 12",
         notes="Helados"),
    dict(unit_number="L-112A",      unit_type="LOCAL", floor=1,
         tenant="RAUL FLORENTINO",                  monthly_rent=28087,  mes_str="7 DE 12",
         notes="Bendito Bocado"),
    dict(unit_number="L-201B",      unit_type="LOCAL", floor=2,
         tenant="OSCAR HUGO MORALES GARCIA",        monthly_rent=10500,  mes_str="2 DE 12",
         notes="Spa"),
    dict(unit_number="OXXO",        unit_type="LOCAL", floor=1,
         tenant="OXXO",                             monthly_rent=1898.55, mes_str=None,
         notes="Primer pago OXXO"),
    # ---- Departamentos – Torre A ------------------------------------------
    dict(unit_number="DEPTO-200A",  unit_type="DEPTO", floor=2,
         tenant="NORMA SILVIA LAGUNA CASSO",        monthly_rent=14000,  mes_str="9 DE 12"),
    dict(unit_number="DEPTO-201A",  unit_type="DEPTO", floor=2,
         tenant="RAUL IRAGORRI",                    monthly_rent=14000,  mes_str="8 DE 12"),
    dict(unit_number="DEPTO-202A",  unit_type="DEPTO", floor=2,
         tenant="J JESUS CASTAÑEDA RAMIREZ",        monthly_rent=14000,  mes_str="9 DE 12"),
    dict(unit_number="DEPTO-203A",  unit_type="DEPTO", floor=2,
         tenant="OSCAR ROSAS PANDURA",              monthly_rent=12000,  mes_str="9 DE 12"),
    dict(unit_number="DEPTO-208A",  unit_type="DEPTO", floor=2,
         tenant="MONIKA IVONNE ZEPEDA",             monthly_rent=15000,  mes_str="4 DE 12"),
    dict(unit_number="DEPTO-209A",  unit_type="DEPTO", floor=2,
         tenant="MK GAON FOOD",                     monthly_rent=15000,  mes_str="2 DE 12"),
    dict(unit_number="DEPTO-211A",  unit_type="DEPTO", floor=2,
         tenant="SIDARTHA MONCADA SORIANO",         monthly_rent=15000,  mes_str="9 DE 12"),
    dict(unit_number="DEPTO-400A",  unit_type="DEPTO", floor=4,
         tenant="OSCAR MANCADA SERVIN",             monthly_rent=14150,  mes_str="4 DE 12"),
    dict(unit_number="DEPTO-402A",  unit_type="DEPTO", floor=4,
         tenant="CARLOS A HERNANDEZ HERNANDEZ",     monthly_rent=14000,  mes_str="8 DE 12"),
    dict(unit_number="DEPTO-406A",  unit_type="DEPTO", floor=4,
         tenant="DIEGO MARTINEZ MORENO",            monthly_rent=10500,  mes_str="7 DE 12"),
    dict(unit_number="DEPTO-409A",  unit_type="DEPTO", floor=4,
         tenant="MA CONCEPCION ORTEGA",             monthly_rent=13000,  mes_str="8 DE 12"),
    dict(unit_number="DEPTO-413A",  unit_type="DEPTO", floor=4,
         tenant="ANEL NAVA FUENTES",                monthly_rent=13650,  mes_str="9 DE 12"),
    # ---- Departamentos – Torre D ------------------------------------------
    dict(unit_number="DEPTO-327D",  unit_type="DEPTO", floor=3,
         tenant="LISSETTE REYES GABRIEL",           monthly_rent=9500,   mes_str=None),
    dict(unit_number="DEPTO-328D",  unit_type="DEPTO", floor=3,
         tenant="ARMANDO GONZALEZ MARTINEZ",        monthly_rent=9000,   mes_str="10 DE 12"),
    # ---- Departamentos – Torre E ------------------------------------------
    dict(unit_number="DEPTO-130E",  unit_type="DEPTO", floor=1,
         tenant="JORGE MANUEL GARDUÑO RIVERA",      monthly_rent=9500,   mes_str="9 DE 12"),
    dict(unit_number="DEPTO-138E",  unit_type="DEPTO", floor=1,
         tenant="MARIANA MEDINA ARAÑA",             monthly_rent=9500,   mes_str="8 DE 12"),
    dict(unit_number="DEPTO-140E",  unit_type="DEPTO", floor=1,
         tenant="JOSE LEONARDO VAZQUEZ",            monthly_rent=9500,   mes_str="9 DE 12"),
    dict(unit_number="DEPTO-239E",  unit_type="DEPTO", floor=2,
         tenant="DIEGO OMAR CAREAGA GOMEZ",         monthly_rent=8500,   mes_str="9 DE 12"),
    dict(unit_number="DEPTO-429E",  unit_type="DEPTO", floor=4,
         tenant="IVAN OMAR BERNAL ALCALA",          monthly_rent=8925,   mes_str="2 DE 12"),
    dict(unit_number="DEPTO-430E",  unit_type="DEPTO", floor=4,
         tenant="DAVID RENE GONZALEZ ROJAS",        monthly_rent=8500,   mes_str="9 DE 12"),
    dict(unit_number="DEPTO-437E",  unit_type="DEPTO", floor=4,
         tenant="EVA HORTENSIA DAVILA PEREZ",       monthly_rent=8500,   mes_str="8 DE 12"),
    dict(unit_number="DEPTO-438E",  unit_type="DEPTO", floor=4,
         tenant="FREDDY CABAS HERNANDEZ",           monthly_rent=8900,   mes_str="3 DE 12"),
]

# ---------------------------------------------------------------------------
def run():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    existing_units = {r["unit_number"] for r in
                      conn.execute("SELECT unit_number FROM units WHERE project_id=?",
                                   (PROJECT_ID,)).fetchall()}
    print(f"Already existing units: {len(existing_units)}")

    created_units = 0
    created_contracts = 0

    for u in UNITS:
        unit_num = u["unit_number"]
        if unit_num in existing_units:
            print(f"  SKIP (already exists): {unit_num}")
            continue

        # Insert unit (marked as NOT available = occupied/rented)
        cur = conn.execute(
            """INSERT INTO units
               (project_id, unit_number, unit_type, purpose, floor,
                rent_price, is_available, notes)
               VALUES (?,?,?,?,?,?,0,?)""",
            (PROJECT_ID, unit_num, u["unit_type"], "RENTA",
             u.get("floor"), u["monthly_rent"], u.get("notes"))
        )
        unit_id = cur.lastrowid
        created_units += 1

        # Insert active contract
        start_date, end_date = contract_dates(u.get("mes_str"))
        conn.execute(
            """INSERT INTO contracts
               (unit_id, tenant_name, start_date, end_date,
                monthly_rent, deposit, payment_day, status)
               VALUES (?,?,?,?,?,?,1,'ACTIVO')""",
            (unit_id, u["tenant"], start_date, end_date,
             u["monthly_rent"], u["monthly_rent"])   # deposit = 1 month's rent as default
        )
        created_contracts += 1
        print(f"  + {unit_num:20s}  {u['tenant'][:40]}  ${u['monthly_rent']:>10,.2f}")

    conn.commit()
    conn.close()
    print(f"\nDone – created {created_units} units and {created_contracts} contracts.")

if __name__ == "__main__":
    try:
        from dateutil.relativedelta import relativedelta
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dateutil"])
        from dateutil.relativedelta import relativedelta
    run()

