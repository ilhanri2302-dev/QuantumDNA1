// QuantumDNA backend client.
// Override the target with VITE_API_URL if needed (e.g. deployment).

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const TIMEOUT_MS = 15000

/**
 * Sequence a target directory through the QuantumDNA backend.
 * Returns the full scan payload: { summary, findings, dependency_graph }.
 */
export async function scanTarget(path = '../sample-target') {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), TIMEOUT_MS)

  let response
  try {
    response = await fetch(`${API_BASE}/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path }),
      signal: controller.signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error(`Backend did not respond within ${TIMEOUT_MS / 1000} seconds`)
    }
    throw new Error('Could not reach the QuantumDNA backend')
  } finally {
    clearTimeout(timeout)
  }

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) {
        detail = typeof body.detail === 'string'
          ? body.detail
          : JSON.stringify(body.detail)
      }
    } catch {
      // response body was not JSON; keep the default message
    }
    throw new Error(detail)
  }

  return response.json()
}
