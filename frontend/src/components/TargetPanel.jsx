export default function TargetPanel({ summary, scanning, error, onScan }) {
  const stats = [
    { label: 'FILES SCANNED', value: summary?.files_scanned },
    { label: 'CRYPTO ASSETS', value: summary?.crypto_findings },
    { label: 'QUANTUM VULNERABLE', value: summary?.quantum_vulnerable },
    { label: 'CRITICAL ASSETS', value: summary?.critical_risk_assets },
  ]

  return (
    <aside className="target-panel">
      <div className="panel-title">TARGET SYSTEM</div>

      <div className="target-path" title={summary?.path}>
        {summary?.path || 'sample-target'}
      </div>

      <button
        type="button"
        className="sequence-btn"
        onClick={onScan}
        disabled={scanning}
      >
        {scanning ? 'SEQUENCING…' : 'SEQUENCE SYSTEM'}
      </button>

      <dl className="stat-list">
        {stats.map(({ label, value }) => (
          <div className="stat" key={label}>
            <dt>{label}</dt>
            <dd className={value == null ? 'stat-empty' : ''}>
              {value ?? '—'}
            </dd>
          </div>
        ))}
      </dl>

      {error && <p className="panel-error">{error}</p>}
    </aside>
  )
}
