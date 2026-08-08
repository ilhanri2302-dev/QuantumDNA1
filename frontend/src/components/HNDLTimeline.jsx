/**
 * Retention years are derived from the risk explanation text because the
 * backend response does not expose them as a structured field.
 */
function retentionYears(risk) {
  const match = risk?.explanation?.match(/(\d+)\s*year/i)
  return match ? Number(match[1]) : null
}

export default function HNDLTimeline({ hndl, risk }) {
  if (!hndl) return null

  const years = retentionYears(risk)
  const stages = [
    {
      key: 'harvest',
      label: 'HARVEST',
      value: hndl.harvest_value,
      note: 'ciphertext captured today',
    },
    {
      key: 'retention',
      label: 'RETENTION WINDOW',
      value: hndl.retention_risk,
      note: years ? `${years} year(s) of confidentiality` : 'retention risk',
    },
    {
      key: 'future',
      label: 'QUANTUM FUTURE',
      value: hndl.future_decryptability,
      note: 'future decryptability',
    },
  ]

  return (
    <div className="hndl-timeline">
      <div className="sub-panel-head">
        <span>HNDL TIMELINE</span>
        <span className={`badge badge-${hndl.exposure?.toLowerCase()}`}>
          {hndl.exposure}
        </span>
      </div>

      <div className="timeline-track">
        <div className="timeline-node node-today">
          <span className="node-dot" />
          <span className="node-label">TODAY</span>
        </div>

        {stages.map((stage) => (
          <div className="timeline-node" key={stage.key}>
            <div className="node-connector">
              <div className="connector-line" />
              <span className="connector-arrow">↓</span>
            </div>
            <span className="stage-label">{stage.label}</span>
            <div className="stage-bar">
              <div
                className="stage-fill"
                style={{ width: `${stage.value}%` }}
              />
            </div>
            <span className="stage-value">{stage.value} / 100</span>
            <span className="stage-note">{stage.note}</span>
          </div>
        ))}

        <div className="timeline-node node-end">
          <div className="node-connector">
            <div className="connector-line" />
            <span className="connector-arrow">↓</span>
          </div>
          <span className="node-label">POTENTIAL DECRYPTION</span>
          <span className="node-dot-end" />
        </div>
      </div>

      <p className="timeline-thesis">
        HARVEST NOW <span className="muted">+</span> DECRYPT LATER
      </p>
    </div>
  )
}
