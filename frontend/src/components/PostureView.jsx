import { useMemo } from 'react'

function riskLabel(group) {
  if (group.quantumVulnerable) return 'QUANTUM VULNERABLE'
  if (group.category === 'POST_QUANTUM') return 'POST-QUANTUM READY'
  return 'COMPARATIVELY RESILIENT'
}

export default function PostureView({ groups, onSelect }) {
  const { vulnerable, resilient, pqReady } = useMemo(() => {
    const v = []
    const r = []
    const p = []
    for (const g of groups) {
      if (g.quantumVulnerable) v.push(g)
      else if (g.category === 'POST_QUANTUM') p.push(g)
      else r.push(g)
    }
    return {
      vulnerable: v,
      resilient: r,
      pqReady: p,
    }
  }, [groups])

  const total = groups.length || 1
  const pct = (n) => Math.round((n / total) * 100)

  return (
    <div className="posture-view">
      <div className="panel-card">
        <div className="sub-panel-head">
          <span>POSTURE BREAKDOWN</span>
          <span className="muted">{groups.length} ASSETS</span>
        </div>

        <div className="posture-bar">
          <div
            className="posture-seg seg-vuln"
            style={{ width: `${pct(vulnerable.length)}%` }}
            title={`${vulnerable.length} quantum vulnerable`}
          />
          <div
            className="posture-seg seg-resilient"
            style={{ width: `${pct(resilient.length)}%` }}
            title={`${resilient.length} comparatively resilient`}
          />
          <div
            className="posture-seg seg-pqc"
            style={{ width: `${pct(pqReady.length)}%` }}
            title={`${pqReady.length} post-quantum ready`}
          />
        </div>

        <div className="posture-legend">
          <span className="legend-item legend-vuln">
            QUANTUM VULNERABLE · {vulnerable.length}
          </span>
          <span className="legend-item legend-resilient">
            COMPARATIVELY RESILIENT · {resilient.length}
          </span>
          <span className="legend-item legend-pqc">
            POST-QUANTUM READY · {pqReady.length}
          </span>
        </div>
      </div>

      <div className="posture-columns">
        <div className="panel-card before-card">
          <div className="sub-panel-head">
            <span>BEFORE — CURRENT FINDINGS</span>
          </div>
          {vulnerable.length ? (
            <div className="posture-list">
              {vulnerable.map((g) => (
                <button
                  type="button"
                  className="posture-item before"
                  key={g.algorithm}
                  onClick={() => onSelect(g.algorithm)}
                >
                  <span className="posture-item-alg">{g.algorithm}</span>
                  <span className="posture-item-tag">{riskLabel(g)}</span>
                </button>
              ))}
            </div>
          ) : (
            <p className="empty-note">No quantum-vulnerable findings.</p>
          )}
        </div>

        <div className="panel-card after-card">
          <div className="sub-panel-head">
            <span>AFTER — RECOMMENDED DIRECTION</span>
          </div>
          <div className="posture-list">
            {vulnerable.map((g) => (
              <div className="posture-item after" key={g.algorithm}>
                <span className="posture-item-alg">{g.algorithm}</span>
                <span className="posture-arrow">→</span>
                <span className="posture-item-target">{g.migrationTarget}</span>
                <span className="posture-item-phase">{g.migrationPhase}</span>
              </div>
            ))}
            {resilient.map((g) => (
              <div className="posture-item after keep" key={g.algorithm}>
                <span className="posture-item-alg">{g.algorithm}</span>
                <span className="posture-arrow">→</span>
                <span className="posture-item-target">{g.migrationTarget}</span>
                <span className="posture-item-phase">{g.migrationPhase}</span>
              </div>
            ))}
            {pqReady.map((g) => (
              <div className="posture-item after ready" key={g.algorithm}>
                <span className="posture-item-alg">{g.algorithm}</span>
                <span className="posture-arrow">→</span>
                <span className="posture-item-target">ALREADY POST-QUANTUM READY</span>
                <span className="posture-item-phase">READY</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <p className="model-note">
        Recommendations are derived from actual scan results and the
        QuantumDNA knowledge base. They are a UI demonstration of migration
        direction — no cryptography has been migrated and no re-scan was
        performed.
      </p>
    </div>
  )
}
