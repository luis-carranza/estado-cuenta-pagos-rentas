from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
import os

app = FastAPI(title="Estado de Cuenta - Pagos Rentas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edo cuenta pagos rentas Final.xlsx")


# ── Pydantic Models ──────────────────────────────────────────────────────────

class PagoBase(BaseModel):
    fecha: Optional[str] = None
    ubicacion: Optional[str] = None
    desarrollo: Optional[str] = None
    mes_correspondiente: Optional[str] = None
    cliente: Optional[str] = None
    concepto: Optional[str] = None
    monto: float = 0.0
    forma_de_pago: Optional[str] = None
    semana_fiscal: Optional[int] = None


class PagoCreate(PagoBase):
    pass


class Pago(PagoBase):
    consecutivo: int

    class Config:
        from_attributes = True


# ── Helpers ──────────────────────────────────────────────────────────────────

def _str(val) -> Optional[str]:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    return str(val).strip()


def _float(val) -> float:
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def load_excel() -> dict:
    df = pd.read_excel(EXCEL_FILE, header=None)

    def _date(val):
        if isinstance(val, datetime):
            return val.strftime("%Y-%m-%d")
        return _str(val)

    periodo       = _date(df.iloc[1, 2])
    desarrollo    = _str(df.iloc[2, 2])
    fecha_reporte = _date(df.iloc[3, 2])

    total_efectivo       = _float(df.iloc[6, 2])
    total_transferencias = _float(df.iloc[7, 2])
    gran_total           = _float(df.iloc[8, 2])
    pago_servicios       = _float(df.iloc[6, 5])
    pago_renta           = _float(df.iloc[7, 5])

    pagos = []
    for _, row in df.iloc[11:].iterrows():
        raw_id = row[0]
        if raw_id is None or (isinstance(raw_id, float) and pd.isna(raw_id)):
            continue
        try:
            consecutivo = int(raw_id)
        except (ValueError, TypeError):
            continue

        pagos.append({
            "consecutivo": consecutivo,
            "fecha": _date(row[1]),
            "ubicacion": _str(row[2]),
            "desarrollo": _str(row[3]),
            "mes_correspondiente": _str(row[4]),
            "cliente": _str(row[5]),
            "concepto": _str(row[6]),
            "monto": _float(row[7]),
            "forma_de_pago": _str(row[8]),
            "semana_fiscal": int(row[9]) if pd.notna(row[9]) else None,
        })

    return {
        "header": {
            "periodo": periodo,
            "desarrollo": desarrollo,
            "fecha_reporte": fecha_reporte,
        },
        "resumen": {
            "total_efectivo": total_efectivo,
            "total_transferencias": total_transferencias,
            "gran_total": gran_total,
            "pago_servicios": pago_servicios,
            "pago_renta": pago_renta,
        },
        "pagos": pagos,
    }


store = load_excel()


def _recalc_resumen():
    efectivo = sum(
        p["monto"] for p in store["pagos"]
        if p.get("forma_de_pago") and p["forma_de_pago"].upper() == "EFECTIVO"
    )
    transferencias = sum(
        p["monto"] for p in store["pagos"]
        if p.get("forma_de_pago") and p["forma_de_pago"].upper() != "EFECTIVO"
    )
    gran_total = efectivo + transferencias
    pago_servicios = sum(
        p["monto"] for p in store["pagos"]
        if p.get("concepto") and any(
            kw in p["concepto"].upper() for kw in ("AGUA", "SERVICIO", "LUZ", "GAS")
        )
    )
    pago_renta = gran_total - pago_servicios
    store["resumen"].update({
        "total_efectivo": efectivo,
        "total_transferencias": transferencias,
        "gran_total": gran_total,
        "pago_servicios": pago_servicios,
        "pago_renta": pago_renta,
    })


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Estado de Cuenta API — running"}


@app.get("/api/estado-cuenta")
async def get_estado_cuenta():
    return {"header": store["header"], "resumen": store["resumen"]}


@app.get("/api/pagos", response_model=list[Pago])
async def get_pagos(
    forma_pago: Optional[str] = None,
    semana_fiscal: Optional[int] = None,
    search: Optional[str] = None,
):
    pagos = store["pagos"]
    if forma_pago:
        pagos = [p for p in pagos if p.get("forma_de_pago") and forma_pago.lower() in p["forma_de_pago"].lower()]
    if semana_fiscal is not None:
        pagos = [p for p in pagos if p.get("semana_fiscal") == semana_fiscal]
    if search:
        s = search.lower()
        pagos = [p for p in pagos if any(
            p.get(f) and s in str(p[f]).lower()
            for f in ("cliente", "concepto", "ubicacion", "forma_de_pago")
        )]
    return pagos


@app.get("/api/pagos/{consecutivo}", response_model=Pago)
async def get_pago(consecutivo: int):
    for p in store["pagos"]:
        if p["consecutivo"] == consecutivo:
            return p
    raise HTTPException(status_code=404, detail="Pago no encontrado")


@app.post("/api/pagos", response_model=Pago, status_code=201)
async def create_pago(pago: PagoCreate):
    new_id = (max(p["consecutivo"] for p in store["pagos"]) + 1) if store["pagos"] else 1
    new_pago = {"consecutivo": new_id, **pago.model_dump()}
    store["pagos"].append(new_pago)
    _recalc_resumen()
    return new_pago


@app.put("/api/pagos/{consecutivo}", response_model=Pago)
async def update_pago(consecutivo: int, pago: PagoCreate):
    for i, p in enumerate(store["pagos"]):
        if p["consecutivo"] == consecutivo:
            updated = {"consecutivo": consecutivo, **pago.model_dump()}
            store["pagos"][i] = updated
            _recalc_resumen()
            return updated
    raise HTTPException(status_code=404, detail="Pago no encontrado")


@app.delete("/api/pagos/{consecutivo}")
async def delete_pago(consecutivo: int):
    for i, p in enumerate(store["pagos"]):
        if p["consecutivo"] == consecutivo:
            store["pagos"].pop(i)
            _recalc_resumen()
            return {"message": "Pago eliminado", "consecutivo": consecutivo}
    raise HTTPException(status_code=404, detail="Pago no encontrado")
