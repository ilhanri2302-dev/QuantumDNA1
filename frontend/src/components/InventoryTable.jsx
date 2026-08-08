import { useMemo } from 'react'

function statusTone(group) {
  if (group.quantumVulnerable) return 'danger'
  if (group.category === 'POST_QUANTUM') return 'pqc'
  return 'cyan'
}

export default function InventoryTable({ groups, selectedAlg, onSelect }) {
  const rows = useMemo(() => {
    return [...groups].sort(
      (a, b) => (b.risk?.score ?? 0) - (a.risk?.score ?? 0),
    )
  }, [groups])

  if (!rows.length) {
    return (
      <div className="panel-card">
        <div className="sub-panel-head">
          <span>CRYPTOGRAPHIC INVENTORY</span>
        </div>
        <p className="empty-note">
          No findings to list. Run a sequence to populate the inventory.
        </p>
      </div>
    )
  }

  return (
    <div className="panel-card">
      <div className="sub-panel-head">
        <span>CRYPTOGRAPHIC INVENTORY</span>
        <span className="muted">{rows.length} ASSETS</span>
      </div>

      <div className="inventory-table-wrap">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>ALGORITHM</th>
              <th>ROLE</th>
              <th>LOCATION</th>
              <th>QUANTUM STATUS</th>
              <th>RISK</th>
              <th>PRIORITY</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((group) => {
              const tone = statusTone(group)
              const isSelected = group.algorithm === selectedAlg
              return (
                <tr
                  key={group.algorithm}
                  className={isSelected ? 'is-selected' : ''}
                  onClick={() => onSelect(group.algorithm)}
                >
                  <td>
                    <span className="inv-alg">
                      <span className={`inv-dot dot-${tone}`} />
                      {group.algorithm}
                    </span>
                  </td>
                  <td className="inv-role">{group.role}</td>
                  <td className="inv-location">
                    {group.files.length === 1
                      ? group.files[0]
                      : `${group.files[0]} +${group.files.length - 1}`}
                  </td>
                  <td>
                    <span className={`inv-status status-${tone}`}>
                      {group.quantumStatus}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`mini-badge badge-${group.risk?.risk_level?.toLowerCase()}`}
                    >
                      {group.risk?.risk_level ?? '—'}
                    </span>
                  </td>
                  <td>
                    <span
                      className={`mini-badge badge-${group.risk?.migration_priority?.toLowerCase()}`}
                    >
                      {group.risk?.migration_priority ?? '—'}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
