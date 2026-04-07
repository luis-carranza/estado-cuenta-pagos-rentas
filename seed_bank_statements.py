"""
Seed BBVA bank statement for March 2026 extracted from the 3 screenshot images.
Account: 0481236172 — ROMERO PEREZ ALBERTO DANILO
"""
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "app.db"

# ── All transactions parsed from the 3 OCR'd screenshots ─────────────────────
# Fields: (line_date, description, reference, amount, transaction_type, balance, notes)
# type: CREDITO = incoming / DEBITO = outgoing
TRANSACTIONS = [
    # ── 09 March ──────────────────────────────────────────────────────────────
    ("2026-03-09", "CFE Electricidad",
     "GUIA:4966393 REF:01077221058758260308 CIE:0578869", 2424.00, "DEBITO", None,
     "Pago CFE bimestral"),
    ("2026-03-09", "BNET Carpetería Lefort",
     "BNET 0465496950 CARPETAR LEFORT", 0.00, "DEBITO", None,
     "Monto no legible en estado"),
    ("2026-03-09", "Depósito efectivo PRACTIC MAROQ",
     "PRAC E121 FOLIO:8607 203-A", 200.00, "CREDITO", None,
     "Depósito efectivo sucursal PRACTIC dpto 203-A"),

    # ── 10 March ──────────────────────────────────────────────────────────────
    ("2026-03-10", "Renta Marzo dpto 210-A",
     "BNET 0488656509 rentaMar210A", 15000.00, "CREDITO", None,
     "PAGO CUENTA DE TERCERO/0016785916 — renta unidad 210-A"),

    # ── 11 March ──────────────────────────────────────────────────────────────
    ("2026-03-11", "SPEI Recibido Santander — FT.N.920570A23559",
     "SPEI RECIBIDOSANTANDER/0194698778 014", 56000.00, "CREDITO", 2395004.07,
     "Ingreso Santander"),
    ("2026-03-11", "SPEI Enviado Banregio — Pago terreno 7",
     "SPEI ENVIADO BANREGIO/0046213255 058 — 0110326PAGO 6 TERRENO 7", 193930.41, "DEBITO", None,
     "Pago terreno 7"),
    ("2026-03-11", "SPEI Enviado Banregio — Pago LTE 5 Alberto",
     "SPEI ENVIADO BANREGIO/0046213940 058 — 0110326PAGO 6 LTE 5 ALBERTO", 574499.27, "DEBITO", None,
     "Pago lote 5 Alberto"),
    ("2026-03-11", "BNET FA B4018 Ajuste chapa",
     "BNET 1512784421 FA B4018 AJUSTE CH", 0.00, "DEBITO", None,
     "Ajuste chapa — monto no legible"),
    ("2026-03-11", "BNET OQM Intercity",
     "BNET 0465496950 OQM INTERCITY", 12818.00, "DEBITO", None,
     "Servicio OQM Intercity"),
    ("2026-03-11", "BNET Extintor — FA 6074",
     "BNET 0118109699 FA 6074 EXTINTOR C", 1080.01, "DEBITO", None,
     "Recarga/mantenimiento extintores"),
    ("2026-03-11", "BNET Dpto 308-A",
     "BNET 0144686055 308A", 843.00, "DEBITO", None,
     "Servicio/mantenimiento unidad 308-A"),

    # ── 12 March ──────────────────────────────────────────────────────────────
    ("2026-03-12", "Depósito efectivo PRACTIC — Intercity Marzo D745",
     "DEPOSITO EFECTIVO PRACTIC/******6172 FOLIO:9529 530 E INTER MARZO D745 206-2", 0.00, "CREDITO", None,
     "Depósito en sucursal PRACTIC — unidad 206-2 — monto no legible"),
    ("2026-03-12", "SPEI Recibido Inbursa — Renta Marzo Marcos Vancini",
     "SPEI RECIBIDOINBURSA/0101499058 036 — 2026031Renta marzo Marcos Vancini", 24000.00, "CREDITO", None,
     "Renta Marcos Vancini unidad 410-A (aprox.)"),

    # ── 13 March ──────────────────────────────────────────────────────────────
    ("2026-03-13", "BNET FA 2611 Mantenimiento Condesa",
     "BNET 5749913900 FA 2611 MTTOS COND", 0.00, "DEBITO", None,
     "Mantenimiento Condesa — monto no legible"),
    ("2026-03-13", "BNET FA 97 Pintura dpto 227-D",
     "BNET 0486207979 FA 97 PINTURA 227D", 5000.00, "DEBITO", None,
     "Pintura departamento 227-D"),
    ("2026-03-13", "SPEI Recibido Santander",
     "SPEI RECIBIDOSANTANDER/0107095069 014 — 7994213", 3498.52, "CREDITO", 1643587.97,
     "Pago Santander"),
    ("2026-03-13", "Predial Municipio de Querétaro",
     "MUNICIPIO DE QUERETA/GUIA:7326930 — CIE:0914185", 19033.00, "DEBITO", 1629474.97,
     "Pago predial"),
    ("2026-03-13", "BNET FA B7 Miguel Vega",
     "BNET 4508309053 FA B7 MIGUEL VEGA G", 8000.00, "DEBITO", 1615474.97,
     "Pago a Miguel Vega"),
    ("2026-03-13", "BNET FA E7F17 Contador Arce",
     "BNET 2861320963 FA E7F17 CONTA ARC", 20200.00, "DEBITO", None,
     "Honorarios contador Arce"),
    ("2026-03-13", "Depósito efectivo PRACTIC — Renta E094",
     "DEPOSITO EFECTIVO PRACTIC/******6172 RENTA E094 FOLIO:9232", 9000.00, "CREDITO", None,
     "Depósito renta E094"),

    # ── 14 March ──────────────────────────────────────────────────────────────
    ("2026-03-14", "SPEI Recibido HSBC — Alberto Danilo Romero Pérez",
     "SPEI RECIBIDOHSBC/0115109371 021 — 0000403 ALBERTO DANILO ROMERO PEREZ 483-A", 0.00, "CREDITO", None,
     "Transferencia propia dpto 483-A — monto no legible"),
    ("2026-03-14", "Depósito efectivo PRACTIC — DRO DBA FOLIO:2857",
     "DEPOSITO EFECTIVO PRACTIC/******6172 PRAC 9918 MAR14 10:29 FOLIO:2857 DRO DBA", 2200.00, "CREDITO", None,
     "Depósito efectivo"),
    ("2026-03-14", "Depósito efectivo PRACTIC — MAR14",
     "DEPOSITO EFECTIVO PRACTIC/******6172 MAR14 10:29 PRAC 9918", 45000.00, "CREDITO", 1631254.97,
     "Depósito grande sucursal PRACTIC"),
    ("2026-03-14", "SPEI Recibido HSBC — Intercity E338",
     "SPEI RECIBIDOHSBC/0116399384 021 — 0000003 Intercity E338 338-A", 0.00, "CREDITO", None,
     "Intercity E338 dpto 338-A — monto no legible"),
    ("2026-03-14", "SPEI Recibido Bancoppel — Condesa 309-A",
     "SPEI RECIBIDOBANCOPPEL/0117832396 137 — 2597878 Condesa 309A", 0.00, "CREDITO", None,
     "Pago condesa unidad 309-A — monto no legible"),

    # ── 16 March ──────────────────────────────────────────────────────────────
    ("2026-03-16", "SPEI Recibido Nu Mexico — Transferencia",
     "SPEI RECIBIDONU MEXICO/0130869577 638 — 0160326Transferencia", 8900.00, "CREDITO", 1678654.97,
     "Transferencia Nu Mexico"),

    # ── 17 March ──────────────────────────────────────────────────────────────
    ("2026-03-17", "SPEI Recibido Inbursa — 9603171304",
     "SPEI RECIBIDOINBURSA/0132405954 036 — 9603171304ACON", 14000.00, "CREDITO", 1692654.97,
     "Depósito Inbursa"),
    ("2026-03-17", "BNET — Transferencia Intercity 497",
     "73797 2TRANSFERENCIA INTERCITY 497 BUE-D", 8500.00, "DEBITO", 1701184.97,
     "Transferencia Intercity unidad BUE-D"),

    # ── 19 March ──────────────────────────────────────────────────────────────
    ("2026-03-19", "SPEI Recibido Inbursa — Renta Marzo 2026 depto Condesa",
     "SPEI RECIBIDO 036 — rco5z6 renta Marzo 2026 depto Condesa", 19000.00, "CREDITO", None,
     "Renta Condesa marzo 2026"),

    # ── 20 March ──────────────────────────────────────────────────────────────
    ("2026-03-20", "REF CIE-0624101 — Cargo servicio",
     "REF-030041200663717260 CIE-0624101", 20148.46, "DEBITO", 1870131.64,
     "Cargo automático"),
    ("2026-03-20", "BNET FA49 Líneas hidráulicas",
     "BNET 0477813058 FA49 LINEASHIDRA", 981.36, "DEBITO", 1590697.70,
     "Líneas hidráulicas"),
    ("2026-03-20", "SPEI Recibido Bancoppel — Transf. Alberto Danilo",
     "SPEI RECIBIDOBANCOPPEL/0149750609 137 — 0850815 Transf. a Alberto Danilo Romer YR-E", 10000.00, "CREDITO", None,
     "Transferencia Bancoppel"),

    # ── 21 March ──────────────────────────────────────────────────────────────
    ("2026-03-21", "PAGO — unidad YOS-A",
     "PAGO CUENTA DE TERCERO YOS-A", 10500.00, "CREDITO", 1589319.64,
     "Depósito renta unidad Yos-A"),

    # ── 22 March ──────────────────────────────────────────────────────────────
    ("2026-03-22", "BNET OQM DROAS Condesa",
     "BNET 0465496950 OQM DROAS CONDESA", 9500.00, "DEBITO", 1598819.64,
     "Servicio OQM Condesa"),

    # ── 23 March ──────────────────────────────────────────────────────────────
    ("2026-03-23", "Depósito / Transferencia dpto 203-A",
     "BRO 203-A", 12000.00, "CREDITO", 1580776.62,
     "Renta unidad 203-A"),

    # ── 24 March ──────────────────────────────────────────────────────────────
    ("2026-03-24", "Depósito en efectivo — dpto 407-A",
     "DEPOSITO EN EFECTIVO/0005554 407-A", 13000.00, "CREDITO", 1593776.62,
     "Renta unidad 407-A"),
    ("2026-03-24", "BNET Depósito dpto 200-A",
     "BNET 2661997855 depto 200A", 14000.00, "CREDITO", 1607776.62,
     "Renta unidad 200-A"),

    # ── 25 March ──────────────────────────────────────────────────────────────
    ("2026-03-25", "Depósito en efectivo — dpto 202-A",
     "DEPOSITO EN EFECTIVO/00055560202 202-A", 14000.00, "CREDITO", 1621776.62,
     "Renta unidad 202-A"),
    ("2026-03-25", "SPEI Recibido STP — 9040086",
     "SPEI RECIBIDOSTP/0178206834 646 — 9040086", 15850.00, "CREDITO", None,
     "Transferencia STP"),

    # ── 26 March ──────────────────────────────────────────────────────────────
    ("2026-03-26", "SPEI Recibido Scotiabank — Transferencia a Riscos",
     "SPEI RECIBIDOSCOTIABANK/0186286533 044 — 0260326 Transferencia a Riscos", 0.00, "CREDITO", None,
     "Transferencia Scotiabank a Riscos — monto no legible en img"),
    ("2026-03-26", "SPEI Recibido Scotiabank — Transferencia a Riscos (2)",
     "SPEI RECIBIDOSCOTIABANK/0186292623 044 — 0260326 Transferencia a Riscos", 0.00, "CREDITO", None,
     "Segunda transferencia Scotiabank — monto no legible"),
    ("2026-03-26", "BNET Agua 440-E Intercity",
     "BNET 0125434882 AGUA 440E INTER", 879.00, "DEBITO", None,
     "Pago agua unidad 440-E"),
    ("2026-03-26", "SPEI Enviado Inbursa — Term Obra L29",
     "SPEI ENVIADO INBURSA/0095071212 036 — 1803260 Term Obra L29", 0.00, "DEBITO", None,
     "Terminación obra lote 29 — monto no legible"),

    # ── 27 March ──────────────────────────────────────────────────────────────
    ("2026-03-27", "BNET FA51 Mantenimiento dpto 43",
     "BNET 0477813058 FA 51 MTTO DPTO 43", 0.00, "DEBITO", None,
     "Mantenimiento dpto 43 — monto no legible"),
    ("2026-03-27", "BNET FA52 Puerta 307-A",
     "BNET 0477813058 FA 52 PUERTA 307A", 3758.40, "DEBITO", 1643621.62,
     "Reparación puerta dpto 307-A"),
    ("2026-03-27", "SPEI Enviado Bancoppel — Riego Condesa",
     "SPEI ENVIADO BANCOPPEL/0025245084 137 — 0270326FA 99 RIEGO CONDESA", 1992.00, "DEBITO", 1625629.00,
     "Servicio riego Condesa"),
    ("2026-03-27", "SPEI Enviado Mercado Pago — Pintura dpto 307-A",
     "SPEI ENVIADO Mercado Pago/0025211964 722 — 0270326FA 889C PINTURA 307A", 0.00, "DEBITO", None,
     "Pintura dpto 307-A — monto no legible"),
    ("2026-03-27", "SPEI Enviado Citi Mexico — Inmueble 24",
     "SPEI ENVIADO CITI MEXICO/0025208903 124 — 0270326FA 566380 INMUE 24", 0.00, "DEBITO", None,
     "Pago inmueble 24 — monto no legible"),
    ("2026-03-27", "BNET FA B4018 Ajuste chapa dpto",
     "BNET 0477813058 FA 52/51 AJUSTE", 0.00, "DEBITO", None,
     "Ajuste chapa — monto no legible"),
    ("2026-03-27", "SPEI Recibido Santander — Pago Inmobiliaria 78",
     "SPEI RECIBIDOSANTANDER/0190506781 014 — 0260327 PAGO INM. 78", 1898.55, "CREDITO", 1665170.55,
     "Pago inmobiliaria 78"),
    ("2026-03-27", "BNET FA 2612 Mantenimientos varios",
     "BNET 2712913992 FA 2612 MTTOS VARI", 8236.00, "DEBITO", None,
     "Mantenimientos varios"),
    ("2026-03-27", "BNET FA ES6BF Chapa dpto 211",
     "BNET 1512784421 FA ES6BF CHAPA 211", 1064.00, "DEBITO", None,
     "Chapa departamento 211"),

    # ── 30 March ──────────────────────────────────────────────────────────────
    ("2026-03-30", "BNET Telmex casa Lic. Al.",
     "BNET 0465496950 TELMEX CASA LIC AL", 0.00, "DEBITO", 1663908.55,
     "Pago Telmex — monto no legible"),
    ("2026-03-30", "BNET Local 102-B",
     "BNET 0477780990 local 102 B", 8480.40, "DEBITO", None,
     "Cargo local 102-B"),
    ("2026-03-30", "SPEI Recibido Banamex — Dpto 140-E",
     "SPEI RECIBIDOBANAMEX/0106530680 002 — 0300326 dpto 140e", 9500.00, "CREDITO", 1673858.95,
     "Renta unidad 140-E"),
    ("2026-03-30", "SPEI Recibido HSBC — 402-A V0",
     "SPEI RECIBIDOHSBC/0107033356 021 — 0300326 402 A V0 402-A", 14000.00, "CREDITO", 1687858.95,
     "Renta unidad 402-A"),
    ("2026-03-30", "BNET FA 4028D Jabón Manor",
     "BNET 1145096197 FA 4028D JABON MAN", 812.00, "DEBITO", 1687046.95,
     "Jabonera Manor — suministro"),
    ("2026-03-30", "SPEI Recibido Banamex — Transferencia BDI-A",
     "SPEI RECIBIDOBANAMEX/0107850688 002 — 0300326 Transferencia interbancaria DRO BDI-A", 14000.00, "CREDITO", 1701046.95,
     "Renta / transferencia BDI-A"),
]


def seed():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    # Check if already seeded
    existing = conn.execute(
        "SELECT id FROM bank_statements WHERE account_number='0481236172' AND period_month=3 AND period_year=2026"
    ).fetchone()
    if existing:
        print(f"Statement already exists (id={existing['id']}). Skipping.")
        conn.close()
        return

    # Find project (first available, or None)
    project = conn.execute("SELECT id FROM projects LIMIT 1").fetchone()
    project_id = project["id"] if project else None

    # Create statement header
    cur = conn.execute("""
        INSERT INTO bank_statements
          (project_id, bank_name, account_number, account_alias, period_month, period_year, description)
        VALUES (?,?,?,?,?,?,?)
    """, (
        project_id,
        "BBVA",
        "0481236172",
        "Cuenta Principal BBVA",
        3, 2026,
        "Estado de cuenta BBVA — Marzo 2026 — ROMERO PEREZ ALBERTO DANILO — extraído de capturas de pantalla"
    ))
    sid = cur.lastrowid
    print(f"Created bank statement id={sid}")

    # Insert lines
    for tx in TRANSACTIONS:
        (line_date, description, reference, amount, tx_type, balance, notes) = tx
        conn.execute("""
            INSERT INTO bank_statement_lines
              (statement_id, line_date, description, reference, amount, transaction_type, balance, notes)
            VALUES (?,?,?,?,?,?,?,?)
        """, (sid, line_date, description, reference, amount, tx_type, balance, notes))

    # Recalculate totals
    r = conn.execute("""
        SELECT
          COALESCE(SUM(CASE WHEN transaction_type='CREDITO' THEN amount ELSE 0 END),0) as credits,
          COALESCE(SUM(CASE WHEN transaction_type='DEBITO'  THEN amount ELSE 0 END),0) as debits
        FROM bank_statement_lines WHERE statement_id=?
    """, (sid,)).fetchone()
    conn.execute(
        "UPDATE bank_statements SET total_credits=?, total_debits=? WHERE id=?",
        (r["credits"], r["debits"], sid)
    )

    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM bank_statement_lines WHERE statement_id=?", (sid,)).fetchone()[0]
    print(f"Inserted {count} lines.")
    print(f"Total credits: ${r['credits']:,.2f}  |  Total debits: ${r['debits']:,.2f}")
    conn.close()


if __name__ == "__main__":
    seed()

