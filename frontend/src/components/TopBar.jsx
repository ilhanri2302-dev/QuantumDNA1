const STATUS = {
  idle: 'SYSTEM READY',
  scanning: 'SEQUENCING',
  reconstructed: 'GENOME RECONSTRUCTED',
  error: 'SEQUENCE FAILED',
}

/** Small inline double-helix mark for the brand. */
function DnaMark() {
  return (
    <svg className="brand-mark" viewBox="0 0 40 40" aria-hidden="true">
      <path
        className="strand strand-a"
        d="M12 6 C 20 12, 8 18, 20 24 C 28 28, 16 32, 20 36"
        fill="none"
      />
      <path
        className="strand strand-b"
        d="M28 6 C 20 12, 32 18, 20 24 C 12 28, 24 32, 20 36"
        fill="none"
      />
      <line className="rung" x1="16" y1="12" x2="24" y2="12" />
      <line className="rung" x1="15" y1="20" x2="25" y2="20" />
      <line className="rung" x1="17" y1="28" x2="23" y2="28" />
    </svg>
  )
}

export default function TopBar({ phase }) {
  const status = STATUS[phase] || STATUS.idle

  return (
    <header className="topbar">
      <div className="brand">
        <DnaMark />
        <div className="brand-text">
          <h1 className="brand-name">QUANTUMDNA</h1>
          <p className="brand-sub">CRYPTOGRAPHIC GENOME INTELLIGENCE</p>
        </div>
      </div>

      <div className={`sys-status status-${phase}`}>
        <span className="status-dot" />
        <span className="status-text">{status}</span>
      </div>
    </header>
  )
}
