// SVG cryptographic genome — the visual centerpiece.
// Algorithms become helix nodes; dependencies become connections.
// Layout is deterministic so the genome looks the same on every scan.

const W = 1080
const H = 680
const CY = 336
const PAD_X = 140
const AMP = 148
const FREQ = 0.52
const SERVICE_R = 122
const DEEP_R = 196

function nodeTone(group) {
  if (group.quantumVulnerable) return 'vuln'
  if (group.category === 'POST_QUANTUM') return 'pqc'
  return 'resilient'
}

function buildLayout(groups) {
  const algNodes = []
  const n = groups.length

  groups.forEach((group, i) => {
    const strand = i % 2
    const t = n <= 1 ? 0.5 : i / (n - 1)
    const x = PAD_X + t * (W - 2 * PAD_X)
    const y = CY + AMP * Math.sin(t * Math.PI * 2 * FREQ + (strand ? Math.PI : 0))
    algNodes.push({ group, x, y, strand })
  })

  // Place services in a deterministic fan around their first owner.
  const placeServices = (radius, depthKey) => {
    const placed = new Map()
    algNodes.forEach(({ group, x, y }) => {
      const br = group.blastRadius
      if (!br) return
      const names = depthKey === 'direct'
        ? br.direct_dependencies || []
        : (br.affected_assets || []).filter(
            (a) => !(br.direct_dependencies || []).includes(a),
          )
      const m = names.length
      names.forEach((name, j) => {
        if (placed.has(name)) return
        const angle = m <= 1
          ? Math.PI / 2
          : Math.PI * (0.14 + (0.72 * j) / (m - 1))
        placed.set(name, {
          name,
          x: x + Math.cos(angle) * radius,
          y: y + Math.sin(angle) * radius,
          deep: depthKey !== 'direct',
        })
      })
    })
    return placed
  }

  const direct = placeServices(SERVICE_R, 'direct')
  const deep = placeServices(DEEP_R, 'deep')
  // Direct placement wins over the outer ring for shared services.
  const services = new Map([...deep, ...direct])

  // Edges: algorithm -> every service it can reach.
  const edges = []
  algNodes.forEach(({ group, x, y }) => {
    const br = group.blastRadius
    if (!br) return
    const directNames = br.direct_dependencies || []
    directNames.forEach((name) => {
      const svc = services.get(name)
      if (svc) edges.push({ x1: x, y1: y, x2: svc.x, y2: svc.y, depth: 1, owner: group.algorithm, name })
    })
    ;(br.affected_assets || [])
      .filter((a) => !directNames.includes(a))
      .forEach((name) => {
        const svc = services.get(name)
        if (svc) edges.push({ x1: x, y1: y, x2: svc.x, y2: svc.y, depth: 2, owner: group.algorithm, name })
      })
  })

  return { algNodes, services, edges }
}

function guidePath(strand) {
  const points = []
  for (let t = 0; t <= 1.001; t += 0.02) {
    const x = PAD_X + t * (W - 2 * PAD_X)
    const y = CY + AMP * Math.sin(t * Math.PI * 2 * FREQ + (strand ? Math.PI : 0))
    points.push(`${t === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`)
  }
  return points.join(' ')
}

function traceState(group, traceActive) {
  if (!group || !traceActive || !group.blastRadius) return null
  const direct = new Set(group.blastRadius.direct_dependencies || [])
  const deep = new Set(
    (group.blastRadius.affected_assets || []).filter((a) => !direct.has(a)),
  )
  return { direct, deep }
}

export default function GenomeVisualization({
  groups,
  selectedAlg,
  onSelect,
  traceActive,
  migrationAlg,
  demoMode,
}) {
  if (!groups.length) {
    return (
      <div className="genome-empty">
        <svg className="helix-ghost" viewBox={`0 0 ${W} ${H}`}>
          <path className="ghost-guide" d={guidePath(false)} />
          <path className="ghost-guide" d={guidePath(true)} />
        </svg>
        <div className="genome-empty-text">
          <span className="empty-glyph">🧬</span>
          <p>AWAITING GENOME SAMPLE</p>
          <span className="muted">
            Press SEQUENCE SYSTEM to reconstruct the target genome
          </span>
        </div>
      </div>
    )
  }

  const { algNodes, services, edges } = buildLayout(groups)
  const selected = groups.find((g) => g.algorithm === selectedAlg) || null
  const trace = traceState(selected, traceActive)

  // Migration morph: source -> target PQC node.
  let migration = null
  if (migrationAlg) {
    const source = algNodes.find((n) => n.group.algorithm === migrationAlg)
    const targetName = /RSA/i.test(migrationAlg) ? 'ML-KEM' : 'ML-DSA'
    const target = algNodes.find((n) => n.group.algorithm === targetName)
    if (source && target) {
      const midX = (source.x + target.x) / 2
      const midY = Math.min(source.y, target.y) - 90
      migration = {
        source,
        target,
        path: `M ${source.x} ${source.y} Q ${midX} ${midY} ${target.x} ${target.y}`,
      }
    }
  }

  // Decorative particles.
  const particles = Array.from({ length: 16 }, (_, i) => ({
    cx: (i * 173) % W,
    cy: (i * 257) % H,
    r: (i % 3) + 1,
    delay: (i % 6) * 0.9,
  }))

  return (
    <div className="genome">
      <svg
        className="genome-svg"
        viewBox={`0 0 ${W} ${H}`}
        role="img"
        aria-label="Cryptographic genome"
      >
        <defs>
          <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* guide helix */}
        <path className="guide-helix" d={guidePath(false)} />
        <path className="guide-helix" d={guidePath(true)} />

        {/* base-pair rungs */}
        {algNodes.slice(0, -1).map((node, i) => {
          const next = algNodes[i + 1]
          return (
            <line
              key={`rung-${i}`}
              className="base-rung"
              x1={node.x}
              y1={node.y}
              x2={next.x}
              y2={next.y}
            />
          )
        })}

        {/* particles */}
        {particles.map((p, i) => (
          <circle
            key={`p-${i}`}
            className="particle"
            cx={p.cx}
            cy={p.cy}
            r={p.r}
            style={{ animationDelay: `${p.delay}s` }}
          />
        ))}

        {/* dependency edges */}
        {edges.map((edge, i) => {
          const lit = trace && edge.owner === selectedAlg
          const litCls = lit
            ? edge.depth === 1 ? 'lit-1' : 'lit-2'
            : ''
          const delay = lit && edge.depth === 2 ? '0.55s' : '0s'
          return (
            <line
              key={`e-${i}`}
              className={`edge edge-depth-${edge.depth} ${litCls}`}
              x1={edge.x1}
              y1={edge.y1}
              x2={edge.x2}
              y2={edge.y2}
              style={lit ? { animationDelay: delay } : undefined}
            />
          )
        })}

        {/* migration path + particle */}
        {migration && (
          <g className="migration-layer">
            <path className="migration-path" d={migration.path} />
            <circle className="migration-particle" r="4" filter="url(#glow)">
              <animateMotion dur="2.6s" repeatCount="indefinite" path={migration.path} />
            </circle>
          </g>
        )}

        {/* shockwave from trace source */}
        {trace && (
          <circle
            className="shockwave"
            cx={algNodes.find((n) => n.group.algorithm === selectedAlg)?.x}
            cy={algNodes.find((n) => n.group.algorithm === selectedAlg)?.y}
            r="26"
          />
        )}

        {/* service nodes */}
        {[...services.values()].map((svc) => {
          const cls = trace
            ? trace.direct.has(svc.name)
              ? 'trace-1'
              : trace.deep.has(svc.name)
                ? 'trace-2'
                : ''
            : ''
          return (
            <g
              key={`svc-${svc.name}`}
              className={`service-node ${svc.deep ? 'is-deep' : ''} ${cls}`}
              transform={`translate(${svc.x} ${svc.y})`}
            >
              <circle className="service-core" r={svc.deep ? 7 : 9} />
              <text className="service-name" textAnchor="middle" y="21">
                {svc.name}
              </text>
            </g>
          )
        })}

        {/* algorithm nodes */}
        {algNodes.map((node) => {
          const { group } = node
          const tone = nodeTone(group)
          const isSelected = group.algorithm === selectedAlg
          const traceCls = trace && isSelected ? 'trace-source' : ''
          const isMigrating = migrationAlg === group.algorithm
          const isMigrateTarget = migration && group.algorithm === migration.target?.group?.algorithm
          return (
            <g
              key={group.algorithm}
              className={[
                'genome-node',
                `tone-${tone}`,
                isSelected ? 'is-selected' : '',
                traceCls,
                isMigrating ? 'is-migrating' : '',
                isMigrateTarget ? 'is-migrate-target' : '',
              ].join(' ')}
              transform={`translate(${node.x} ${node.y})`}
              onClick={() => onSelect(group.algorithm)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') onSelect(group.algorithm)
              }}
            >
              <circle className="node-halo" r="32" />
              <circle className="node-ring" r="24" />
              <circle className="node-core" r="18" />
              <text className="node-count" textAnchor="middle" y="-46">
                ×{group.occurrences.length}
              </text>
              <text className="node-name" textAnchor="middle" y="-33">
                {group.algorithm}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="genome-footer">
        <div className="legend">
          <span className="legend-item legend-vuln">QUANTUM VULNERABLE</span>
          <span className="legend-item legend-pqc">POST-QUANTUM</span>
          <span className="legend-item legend-resilient">RESILIENT</span>
          <span className="legend-item legend-service">SERVICE</span>
        </div>
        {demoMode === 'DEMO' && (
          <span className="demo-chip">MVP DEMONSTRATION GRAPH</span>
        )}
      </div>
    </div>
  )
}
