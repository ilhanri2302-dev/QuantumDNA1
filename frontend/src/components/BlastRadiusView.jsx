export default function BlastRadiusView({
  blast,
  traceActive,
  onToggleTrace,
}) {
  if (!blast) {
    return (
      <div className="blast-view">
        <div className="sub-panel-head">
          <span>BLAST RADIUS</span>
        </div>
        <p className="empty-note">
          This asset is not modeled in the dependency graph.
          <br />
          Blast radius is unavailable.
        </p>
      </div>
    )
  }

  const direct = blast.direct_dependencies || []
  const downstream = (blast.affected_assets || []).filter(
    (asset) => !direct.includes(asset),
  )

  return (
    <div className="blast-view">
      <div className="sub-panel-head">
        <span>BLAST RADIUS</span>
        <span className={`badge badge-${blast.blast_radius_level?.toLowerCase()}`}>
          {blast.blast_radius_level}
        </span>
      </div>

      <div className="blast-score">
        <span className="blast-score-num">{blast.blast_radius_score}</span>
        <span className="muted">/ 100</span>
      </div>

      <div className="blast-metrics">
        <div className="blast-metric">
          <span className="metric-num">{blast.affected_asset_count}</span>
          <span className="metric-label">AFFECTED ASSETS</span>
        </div>
        <div className="blast-metric">
          <span className="metric-num">{blast.dependency_depth}</span>
          <span className="metric-label">DEPTH</span>
        </div>
      </div>

      <button
        type="button"
        className={`trace-btn ${traceActive ? 'active' : ''}`}
        onClick={onToggleTrace}
      >
        {traceActive ? '■ STOP TRACE' : '▶ TRACE BLAST RADIUS'}
      </button>

      <div className="blast-assets">
        {direct.length > 0 && (
          <div className="asset-group">
            <span className="asset-group-label">DIRECT DEPENDENCIES</span>
            <div className="asset-chips">
              {direct.map((asset) => (
                <span className="chip chip-direct" key={asset}>
                  {asset}
                </span>
              ))}
            </div>
          </div>
        )}

        {downstream.length > 0 && (
          <div className="asset-group">
            <span className="asset-group-label">DOWNSTREAM</span>
            <div className="asset-chips">
              {downstream.map((asset) => (
                <span className="chip chip-downstream" key={asset}>
                  {asset}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <p className="demo-note">MVP DEMONSTRATION GRAPH</p>
    </div>
  )
}
