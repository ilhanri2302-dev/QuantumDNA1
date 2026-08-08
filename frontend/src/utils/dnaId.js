// Deterministic QuantumDNA internal asset identifiers.
//
// Format:  QDNA·<ALGORITHM>·P<occurrences>·<hash4>
// Example: QDNA·RSA2048·P03·7F2A
//
// This is an internal QuantumDNA identifier, NOT an industry-standard one.
// It is derived only from the finding data so it stays stable between scans.

/** FNV-1a 32-bit hash — small, fast, deterministic. */
function fnv1a(input) {
  let hash = 0x811c9dc5
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i)
    hash = Math.imul(hash, 0x01000193)
  }
  return hash >>> 0
}

/** Strip punctuation so the algorithm becomes ID-safe: RSA-2048 -> RSA2048. */
export function sanitizeAlgorithm(algorithm) {
  return String(algorithm).replace(/[^A-Za-z0-9]/g, '')
}

/**
 * Generate a stable internal ID for a grouped algorithm.
 *
 * @param {string} algorithm  e.g. "RSA-2048"
 * @param {Array<{file: string, line: number}>} occurrences
 * @returns {string} e.g. "QDNA·RSA2048·P03·7F2A"
 */
export function generateDnaId(algorithm, occurrences) {
  const seed = [
    algorithm,
    occurrences
      .map((o) => `${o.file}:${o.line}`)
      .sort()
      .join(','),
  ].join('|')

  const hash = fnv1a(seed).toString(16).toUpperCase().padStart(8, '0').slice(0, 4)
  const slug = sanitizeAlgorithm(algorithm)
  const count = String(occurrences.length).padStart(2, '0')

  return `QDNA·${slug}·P${count}·${hash}`
}
