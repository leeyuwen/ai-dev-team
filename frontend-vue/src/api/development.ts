import type { SSEEvent, FullResult } from '../types'

export async function generatePrd(requirement: string): Promise<{ spec: string }> {
  const res = await fetch('/prd', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ requirement }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export function approveSpec(
  sessionId: string,
  spec: string,
  onEvent: (event: SSEEvent) => void,
  onError: (error: Error) => void
): () => void {
  let controller: AbortController | null = null

  const connect = () => {
    controller = new AbortController()
    const url = '/approve'

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, spec }),
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const reader = res.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        const read = () => {
          reader.read().then(({ done, value }) => {
            if (done) return

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() ?? ''

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const dataStr = line.slice(6)
                try {
                  const data = JSON.parse(dataStr) as SSEEvent
                  onEvent(data)
                } catch {
                  // skip malformed JSON
                }
              }
            }
            if (!done) read()
          })
        }
        read()
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError(err)
        }
      })
  }

  connect()

  return () => {
    controller?.abort()
  }
}

export function createDevelopmentStream(
  requirement: string,
  onEvent: (event: SSEEvent) => void,
  onError: (error: Error) => void
): () => void {
  let controller: AbortController | null = null

  const connect = () => {
    controller = new AbortController()
    const url = '/develop/stream'

    fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requirement }),
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const reader = res.body!.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        const read = () => {
          reader.read().then(({ done, value }) => {
            if (done) return

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() ?? ''

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                // event type extracted from event: prefix — handled below
              } else if (line.startsWith('data: ')) {
                const dataStr = line.slice(6)
                try {
                  const data = JSON.parse(dataStr) as SSEEvent
                  onEvent(data)
                } catch {
                  // skip malformed JSON
                }
              }
            }
            if (!done) read()
          })
        }
        read()
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          onError(err)
        }
      })
  }

  connect()

  // Return abort function
  return () => {
    controller?.abort()
  }
}
