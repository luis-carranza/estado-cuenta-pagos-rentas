const fmt = (n) =>
  new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(n ?? 0);

export default function ResumenPagos({ resumen }) {
  return (
    <div className="card mb-6">
      <div className="section-header">
        <span className="section-title">RESUMEN DE PAGOS</span>
      </div>
      <div className="resumen-grid">
        <div className="resumen-left">
          <div className="resumen-row">
            <span className="resumen-label">Total Efectivo:</span>
            <span className="resumen-value efectivo">{fmt(resumen?.total_efectivo)}</span>
          </div>
          <div className="resumen-row">
            <span className="resumen-label">Total Transferencias:</span>
            <span className="resumen-value transferencia">{fmt(resumen?.total_transferencias)}</span>
          </div>
          <div className="resumen-row total-row">
            <span className="resumen-label">Gran Total:</span>
            <span className="resumen-value total">{fmt(resumen?.gran_total)}</span>
          </div>
        </div>
        <div className="resumen-right">
          <div className="resumen-row">
            <span className="resumen-label">Pago Servicios:</span>
            <span className="resumen-value servicios">{fmt(resumen?.pago_servicios)}</span>
          </div>
          <div className="resumen-row">
            <span className="resumen-label">Pago Renta:</span>
            <span className="resumen-value renta">{fmt(resumen?.pago_renta)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
