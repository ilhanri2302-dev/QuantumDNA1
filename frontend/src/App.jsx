import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'
import { scanTarget } from './services/api.js'
import { generateDnaId } from './utils/dnaId.js'
import TopBar from './components/TopBar.jsx'
import TargetPanel from './components/TargetPanel.jsx'
import GenomeVisualization from './components/GenomeVisualization.jsx'
import AssetInspector from './components/AssetInspector.jsx'

/** Group scanner findings by algorithm so one node represents one asset. */
function groupFindings(findings = []) {
  const map = new Map()

  for (const f of findings) {
    if (!map.has(f.algorithm)) {
      map.set(f.algorithm, {
        algorithm: f.algorithm,
        category: f.category,
        quantumVulnerable: f.quantum_vulnerable,
        confidence: f.confidence ?? 0,
        risk: f.risk,
        hndl: f.hndl,
        blastRadius: f.blast_radius,
        occurrences: [],
      })
    }
    const group = map.get(f.algorithm)
    group.confidence = Math.max(group.confidence, f.confidence ?? 0)
    // risk / hndl come from the first occurrence; the MVP backend
    // scores deterministically per category, so they are identical
    // across occurrences of the same algorithm.
    group.occurrences.push({
      id: f.id,
      file: f.file,
      line: f.line,
      matchedText: f.matched_text,
    })
  }

  return [...map.values()]
    .map((group) => ({
      ...group,
      dnaId: generateDnaId(group.algorithm, group.occurrences),
      files: [...new Set(group.occurrences.map((o) => o.file))],
    }))
    .sort((a, b) => (b.risk?.score ?? 0) - (a.risk?.score ?? 0))
}

/** Build the sequencing log from real findings, grouped by file. */
function buildSequenceLog(findings = []) {
  const lines = [{ type: 'boot', text: 'SEQUENCING CRYPTOGRAPHIC DNA…' }]
  const byFile = new Map()

  for (const f of findings) {
    if (!byFile.has(f.file)) byFile.set(f.file, [])
    byFile.get(f.file).push(f)
  }

  for (const [file, hits] of byFile) {
    lines.push({ type: 'file', text: `Scanning ${file}` })
    for (const hit of hits) {
      lines.push({ type: 'hit', text: `→ ${hit.algorithm} detected` })
    }
  }

  lines.push({ type: 'end', text: 'Reconstructing cryptographic genome…' })
  return lines
}

function SequencerOverlay({ lines, index }) {
  return (
    <div className="sequencer-overlay">
      <div className="sequencer-screen">
        <div className="sequencer-title">SEQUENCING CRYPTOGRAPHIC DNA…</div>
        <div className="sequencer-log">
          {lines.slice(0, index).map((line, i) => (
            <div className={`seq-line seq-${line.type}`} key={i}>
              <span className="seq-mark">
                {line.type === 'hit' ? '◈' : line.type === 'file' ? '▸' : line.type === 'end' ? '✦' : '▞'}
              </span>
              <span className="seq-text">{line.text}</span>
            </div>
          ))}
          <span className="seq-cursor" />
        </div>
      </div>
    </div>
  )
}

function ErrorPanel({ message, onRetry }) {
  return (
    <div className="genome-empty">
      <div className="genome-empty-text">
        <span className="empty-glyph">⚠</span>
        <p>SEQUENCE FAILED</p>
        <span className="muted">{message}</span>
        <button type="button" className="sequence-btn retry" onClick={onRetry}>
          RETRY SEQUENCE
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [phase, setPhase] = useState('idle')
  const [data, setData] = useState(null)
  const [groups, setGroups] = useState([])
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('overview')
  const [traceActive, setTraceActive] = useState(false)
  const [migrationAlg, setMigrationAlg] = useState(null)
  const [logLines, setLogLines] = useState([])
  const [logIndex, setLogIndex] = useState(0)
  const [error, setError] = useState(null)
  const migrationTimer = useRef(null)

  const selectedGroup = useMemo(
    () => groups.find((g) => g.algorithm === selected) || null,
    [groups, selected],
  )

  // Step through the sequencing log one line at a time.
  // The log stays empty until the scan response arrives, so the
  // sequence only starts once real findings are available.
  useEffect(() => {
    if (phase !== 'scanning') return
    if (logLines.length === 0) return
    if (logIndex >= logLines.length) {
      setPhase('reconstructed')
      return
    }
    const timer = setTimeout(() => setLogIndex((i) => i + 1), 230)
    return () => clearTimeout(timer)
  }, [phase, logIndex, logLines.length])

  useEffect(() => () => clearTimeout(migrationTimer.current), [])

  async function handleScan() {
    setPhase('scanning')
    setError(null)
    setSelected(null)
    setView('overview')
    setTraceActive(false)
    setMigrationAlg(null)
    setLogLines([])
    setLogIndex(0)

    try {
      const result = await scanTarget()
      setData(result)
      setGroups(groupFindings(result.findings))
      setLogLines(buildSequenceLog(result.findings))
      setLogIndex(0)
    } catch (err) {
      setError(err.message || 'Sequence failed — is the backend running?')
      setPhase('error')
    }
  }

  function selectAlgorithm(algorithm) {
    setSelected(algorithm)
    setView('overview')
    setTraceActive(false)
  }

  function handleMigration(algorithm) {
    setSelected(algorithm)
    setView('migration')
    setMigrationAlg(algorithm)
    clearTimeout(migrationTimer.current)
    migrationTimer.current = setTimeout(() => setMigrationAlg(null), 6000)
  }

  const demoMode = data?.dependency_graph?.mode

  return (
    <div className="app">
      <TopBar phase={phase} />

      <TargetPanel
        summary={data?.summary}
        scanning={phase === 'scanning'}
        error={phase === 'error' ? error : null}
        onScan={handleScan}
      />

      <main className="genome-area">
        {phase === 'scanning' && (
          <SequencerOverlay lines={logLines} index={logIndex} />
        )}

        {phase === 'error' && <ErrorPanel message={error} onRetry={handleScan} />}

        {phase !== 'scanning' && phase !== 'error' && (
          <GenomeVisualization
            groups={groups}
            selectedAlg={selected}
            onSelect={selectAlgorithm}
            traceActive={traceActive}
            migrationAlg={migrationAlg}
            demoMode={demoMode}
          />
        )}
      </main>

      <AssetInspector
        group={selectedGroup}
        view={view}
        setView={setView}
        traceActive={traceActive}
        setTraceActive={setTraceActive}
        onSimulateMigration={handleMigration}
      />
    </div>
  )
}
