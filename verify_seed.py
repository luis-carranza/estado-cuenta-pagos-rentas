import sqlite3
conn = sqlite3.connect('app.db')
conn.row_factory = sqlite3.Row

units = conn.execute("""
    SELECT u.unit_number, u.unit_type, u.floor, u.rent_price, u.is_available,
           c.tenant_name, c.start_date, c.end_date, c.monthly_rent, c.status
    FROM units u
    LEFT JOIN contracts c ON c.unit_id=u.id AND c.status='ACTIVO'
    WHERE u.project_id=1
    ORDER BY u.unit_type, u.unit_number
""").fetchall()

print(f"=== UNITS ({len(units)}) ===")
for u in units:
    tenant = u["tenant_name"] or "—"
    print(f"  {u['unit_number']:20s} | {u['unit_type']:6s} | fl={u['floor']} | ${u['rent_price']:>10,.2f} | avail={u['is_available']} | {tenant[:38]} | {u['start_date']} → {u['end_date']}")

total = conn.execute("SELECT COUNT(*) FROM units WHERE project_id=1").fetchone()[0]
rented = conn.execute("SELECT COUNT(*) FROM units WHERE project_id=1 AND is_available=0").fetchone()[0]
contracts = conn.execute("SELECT COUNT(*) FROM contracts WHERE status='ACTIVO'").fetchone()[0]
print(f"\nTotal units: {total}  |  Rented: {rented}  |  Active contracts: {contracts}")
conn.close()

