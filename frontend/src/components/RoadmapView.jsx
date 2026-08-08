const STEPS = [
  {
    key: 'identify',
    title: 'IDENTIFY',
    description:
      'Scan the target to discover every cryptographic algorithm and its location.',
  },
  {
    key: 'prioritize',
    title: 'PRIORITIZE',
    description:
      'Rank assets by quantum risk, HNDL exposure and blast radius.',
  },
  {
    key: 'migrate',
    title: 'MIGRATE',
    description:
      'Move key establishment toward ML-KEM and signatures toward ML-DSA.',
  },
  {
    key: 'rescan',
    title: 'RE-SCAN',
    description:
      'Run the scanner again to verify the improved post-quantum posture.',
  },
  {
    key: 'monitor',
    title: 'MONITOR',
    description:
      'Track new dependencies and re-evaluate risk as standards evolve.',
  },
]

export default function RoadmapView() {
  return (
    <div className="panel-card">
      <div className="sub-panel-head">
        <span>MIGRATION ROADMAP</span>
        <span className="muted">DISCOVER → ASSESS → TRACE → MIGRATE</span>
      </div>

      <div className="roadmap-flow">
        {STEPS.map((step, i) => (
          <div className="roadmap-step" key={step.key} style={{ '--i': i }}>
            <div className="roadmap-node">
              <span className="roadmap-index">0{i + 1}</span>
              <span className="roadmap-title">{step.title}</span>
            </div>
            <p className="roadmap-desc">{step.description}</p>
          </div>
        ))}
      </div>

      <p className="model-note">
        Conceptual workflow for the POC. Migration itself is performed by
        the engineering team — QuantumDNA provides the direction, not the
        automated migration.
      </p>
    </div>
  )
}
