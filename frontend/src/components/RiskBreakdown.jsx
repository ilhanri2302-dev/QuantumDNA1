const FACTORS = [
  { key: 'quantum_vulnerability', label: 'QUANTUM VULNERABILITY', max: 30, tone: 'danger' },
  { key: 'data_sensitivity', label: 'DATA SENSITIVITY', max: 20, tone: 'amber' },
  { key: 'retention_hndl', label: 'RETENTION / HNDL', max: 20, tone: 'warning' },
  { key: 'internet_exposure', label: 'INTERNET EXPOSURE', max: 15, tone: 'cyan' },
  { key: 'dependency_impact', label: 'DEPENDENCY IMPACT', max: 15, tone: 'cyan' },
]

export default function RiskBreakdown({ risk }) {
  if (!risk) return null

  const total = FACTORS.reduce((sum, f) => sum + f.max, 0)

  return (
    <div className="risk-breakdown">
      <div className="sub-panel-head">
        <span>WHY {risk.score}?</span>
        <span className="muted">QUANTUM RISK · {risk.risk_level}</span>
      </div>

      <div className="factor-list">
        {FACTORS.map(({ key, label, max, tone }) => {
          const value = risk.factors?.[key] ?? 0
          const pct = max === 0 ? 0 : Math.round((value / max) * 100)
          return (
            <div className="factor" key={key}>
              <div className="factor-top">
                <span className="factor-label">{label}</span>
                <span className="factor-value">
                  {value} <span className="muted">/ {max}</span>
                </span>
              </div>
              <div className="factor-track">
                <div
                  className={`factor-fill tone-${tone}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="factor-total">
        <span>TOTAL</span>
        <span>
          {risk.score} <span className="muted">/ {total}</span>
        </span>
      </div>

      <p className="model-note">
        QuantumDNA Internal Prioritization Model.
        <br />
        Not an official NIST formula.
      </p>
    </div>
  )
}
