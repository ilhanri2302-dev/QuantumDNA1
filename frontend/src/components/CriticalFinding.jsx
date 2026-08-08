import { useMemo } from 'react'

const FACTOR_LABELS = {
  quantum_vulnerability: 'QUANTUM VULNERABILITY',
  data_sensitivity: 'DATA SENSITIVITY',
  retention_hndl: 'RETENTION / HNDL',
  internet_exposure: 'INTERNET EXPOSURE',
  dependency_impact: 'DEPENDENCY IMPACT',
}

export default function CriticalFinding({ groups, onSelect }) {
  const top = useMemo(() => {
    if (!groups.length) return null
    return [...groups].sort(
      (a, b) => (b.risk?.score ?? 0) - (a.risk?.score ?? 0),
    )[0]
  }, [groups])

  if (!top) return null

  const level = top.risk?.risk_level ?? 'LOW'
  const factors = top.risk?.factors ?? {}

  return (
    <div className={`panel-card critical-card crit-${level.toLowerCase()}`}>
      <div className="sub-panel-head">
        <span>TOP PRIORITY FINDING</span>
        <span className={`mini-badge badge-${level.toLowerCase()}`}>
          {level} PRIORITY
        </span>
      </div>

      <div className="crit-head">
        <div className="crit-alg">{top.algorithm}</div>
        <div className="crit-score">
          {top.risk?.score ?? '—'}
          <span className="muted">/100</span>
        </div>
      </div>

      <div className="crit-why">
        <span className="crit-why-label">WHY IT IS HIGH PRIORITY</span>
        <p className="crit-why-text">
          {top.risk?.explanation || top.explanation}
        </p>
      </div>

      <div className="crit-factors">
        {Object.entries(factors).map(([key, value]) => (
          <div className="crit-factor" key={key}>
            <span className="crit-factor-label">
              {FACTOR_LABELS[key] ?? key}
            </span>
            <span className="crit-factor-value">{value}</span>
          </div>
        ))}
      </div>

      <button
        type="button"
        className="action-btn trace"
        onClick={() => onSelect(top.algorithm)}
      >
        OPEN ASSET INSPECTOR
      </button>
    </div>
  )
}
