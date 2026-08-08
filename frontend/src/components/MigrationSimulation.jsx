/** Deterministic demo migration path per algorithm family. */
function migrationPath(algorithm) {
  const upper = String(algorithm || '').toUpperCase()

  if (upper.includes('RSA')) {
    return {
      hybrid: 'HYBRID RSA + ML-KEM',
      target: 'ML-KEM',
      step: 'Wrap RSA key establishment in a hybrid RSA + ML-KEM construction.',
    }
  }

  if (upper.includes('ECDSA')) {
    return {
      hybrid: 'HYBRID TRANSITION',
      target: 'ML-DSA',
      step: 'Transition ECDSA signatures toward the ML-DSA standard.',
    }
  }

  return {
    hybrid: 'HYBRID TRANSITION',
    target: 'ML-DSA',
    step: 'Plan migration toward post-quantum signatures and key exchange.',
  }
}

export default function MigrationSimulation({ group }) {
  if (!group) return null

  const path = migrationPath(group.algorithm)
  const steps = [
    { label: 'CURRENT', value: group.algorithm, tone: 'danger' },
    { label: 'HYBRID', value: path.hybrid, tone: 'amber' },
    { label: 'PQC TARGET', value: path.target, tone: 'pqc' },
  ]

  return (
    <div className="migration-sim">
      <div className="sub-panel-head">
        <span>MIGRATION SIMULATION</span>
      </div>

      <div className="migration-stages">
        {steps.map((step, i) => (
          <div className="migration-stage" key={step.label} style={{ '--i': i }}>
            <div className={`migration-card tone-${step.tone}`}>
              <span className="migration-card-label">{step.label}</span>
              <span className="migration-card-value">{step.value}</span>
            </div>
            {i < steps.length - 1 && <span className="migration-arrow">↓</span>}
          </div>
        ))}
      </div>

      <div className="migration-caption">
        CURRENT → HYBRID → PQC TARGET
      </div>

      <p className="migration-step-note">{path.step}</p>

      <p className="model-note">
        UI simulation only — no cryptography has been migrated.
      </p>
    </div>
  )
}
