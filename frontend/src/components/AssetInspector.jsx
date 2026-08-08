import BlastRadiusView from './BlastRadiusView.jsx'
import HNDLTimeline from './HNDLTimeline.jsx'
import MigrationSimulation from './MigrationSimulation.jsx'
import RiskBreakdown from './RiskBreakdown.jsx'

function statusInfo(group) {
  if (group.quantumVulnerable) {
    return { text: 'QUANTUM VULNERABLE', tone: 'danger' }
  }
  if (group.category === 'POST_QUANTUM') {
    return { text: 'POST-QUANTUM READY', tone: 'pqc' }
  }
  return { text: 'RESILIENT CLASSICAL', tone: 'cyan' }
}

export default function AssetInspector({
  group,
  view,
  setView,
  traceActive,
  setTraceActive,
  onSimulateMigration,
}) {
  if (!group) {
    return (
      <aside className="inspector">
        <div className="inspector-empty">
          <span className="empty-glyph">🧬</span>
          <p>SELECT A CRYPTOGRAPHIC NODE</p>
          <span className="muted">Click any genome node to inspect it</span>
        </div>
      </aside>
    )
  }

  const status = statusInfo(group)
  const risk = group.risk
  const hndl = group.hndl
  const blast = group.blastRadius

  const hasBlast = Boolean(blast)
  const canMigrate = group.quantumVulnerable

  return (
    <aside className="inspector">
      <div className="inspector-head">
        <h2 className="asset-name">{group.algorithm}</h2>
        <div className="asset-id" title="Internal QuantumDNA asset identifier">
          {group.dnaId}
        </div>

        <div className="asset-meta">
          <div className="meta-row">
            <span className="meta-key">FILES / OCCURRENCES</span>
            <span className="meta-value">{group.occurrences.length}</span>
          </div>
          <div className="meta-row">
            <span className="meta-key">CATEGORY</span>
            <span className="meta-value">{group.category}</span>
          </div>
          <div className="meta-row">
            <span className="meta-key">QUANTUM STATUS</span>
            <span className={`meta-value status-${status.tone}`}>
              {status.text}
            </span>
          </div>
          <div className="meta-row">
            <span className="meta-key">CONFIDENCE</span>
            <span className="meta-value">
              {Math.round((group.confidence || 0) * 100)}%
            </span>
          </div>
        </div>

        <div className="metric-grid">
          <button
            type="button"
            className={`metric-card ${view === 'risk' ? 'active' : ''}`}
            onClick={() => setView('risk')}
          >
            <span className="metric-name">QUANTUM RISK</span>
            <span className="metric-score">
              {risk?.score ?? '—'}
              <span className="muted">/100</span>
            </span>
            <span className={`mini-badge badge-${risk?.risk_level?.toLowerCase()}`}>
              {risk?.risk_level}
            </span>
          </button>

          <button
            type="button"
            className={`metric-card ${view === 'hndl' ? 'active' : ''}`}
            onClick={() => setView('hndl')}
          >
            <span className="metric-name">HNDL EXPOSURE</span>
            <span className="metric-score">
              {hndl?.score ?? '—'}
              <span className="muted">/100</span>
            </span>
            <span className={`mini-badge badge-${hndl?.exposure?.toLowerCase()}`}>
              {hndl?.exposure}
            </span>
          </button>

          <button
            type="button"
            className={`metric-card ${view === 'blast' ? 'active' : ''}`}
            onClick={() => {
              if (hasBlast) setView('blast')
            }}
            disabled={!hasBlast}
          >
            <span className="metric-name">BLAST RADIUS</span>
            <span className="metric-score">
              {hasBlast ? blast.blast_radius_score : '—'}
              <span className="muted">/100</span>
            </span>
            <span className="mini-badge">
              {hasBlast ? blast.blast_radius_level : 'NO GRAPH'}
            </span>
          </button>
        </div>

        <div className="inspector-actions">
          <button
            type="button"
            className={`action-btn trace ${traceActive ? 'active' : ''}`}
            onClick={() => {
              if (!hasBlast) return
              setTraceActive(!traceActive)
              setView('blast')
            }}
            disabled={!hasBlast}
          >
            {traceActive ? '■ END TRACE' : '▶ TRACE BLAST RADIUS'}
          </button>
          <button
            type="button"
            className="action-btn"
            onClick={() => onSimulateMigration(group.algorithm)}
            disabled={!canMigrate}
          >
            SIMULATE MIGRATION
          </button>
        </div>
      </div>

      <div className="inspector-body">
        {view === 'risk' && <RiskBreakdown risk={risk} />}
        {view === 'hndl' && <HNDLTimeline hndl={hndl} risk={risk} />}
        {view === 'blast' && (
          <BlastRadiusView
            blast={blast}
            traceActive={traceActive}
            onToggleTrace={() => setTraceActive(!traceActive)}
          />
        )}
        {view === 'migration' && <MigrationSimulation group={group} />}

        {view === 'overview' && (
          <div className="occurrences">
            <div className="sub-panel-head">
              <span>DETECTED OCCURRENCES</span>
            </div>
            {group.occurrences.map((occ) => (
              <div className="occurrence" key={occ.id}>
                <span className="occ-file">{occ.file}</span>
                <span className="occ-line">L{occ.line}</span>
                <code className="occ-text">{occ.matchedText}</code>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}
