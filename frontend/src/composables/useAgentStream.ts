import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDiscoveryStore } from '@/stores/discovery'

export interface StreamEvent {
  type: 'phase_start' | 'llm_token' | 'phase_complete' | 'phase_result' | 'result' | 'error'
  phase?: string
  token?: string
  document?: Record<string, unknown>
  message?: string
  output?: Record<string, unknown>
}

export function useAgentStream() {
  const discoveryStore = useDiscoveryStore()
  const {
    isStreaming,
    currentPhase,
    currentToken,
    scopeDocument,
    error,
    // Research phase results
    firmHistoryResult,
    resourcesResult,
    marketResearchResult,
    // Original pipeline results
    classificationResult,
    riskAnalysisResult,
    scopeGenerationResult,
    completedPhases,
  } = storeToRefs(discoveryStore)
  const eventSource = ref<EventSource | null>(null)
  const isConnected = ref(false)

  const API_BASE_URL = import.meta.env.VITE_LARAVEL_API_URL || 'http://localhost:8000/api'

  function connect(userInput: string) {
    // Clean up any existing connection
    disconnect()

    isStreaming.value = true
    currentPhase.value = ''
    currentToken.value = ''
    scopeDocument.value = null
    error.value = null
    completedPhases.value = new Set()
    firmHistoryResult.value = null
    resourcesResult.value = null
    marketResearchResult.value = null
    classificationResult.value = null
    riskAnalysisResult.value = null
    scopeGenerationResult.value = null

    // Create EventSource connection
    const url = `${API_BASE_URL}/pipeline/run-stream`
    const formData = new FormData()
    formData.append('user_input', userInput)

    // Use fetch with streaming instead of EventSource for POST requests
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ user_input: userInput }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
          throw new Error('Response body is not readable')
        }

        isConnected.value = true

        let buffer = ''

        function readStream(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              isConnected.value = false
              isStreaming.value = false
              return
            }

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            // Keep the last (potentially incomplete) line in the buffer
            buffer = lines.pop() ?? ''

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const jsonStr = line.substring(6).trim()
                  if (jsonStr) {
                    const event: StreamEvent = JSON.parse(jsonStr)
                    handleEvent(event)
                  }
                } catch (e) {
                  console.error('Failed to parse SSE event:', e)
                }
              }
            }

            return readStream()
          })
        }

        return readStream()
      })
      .catch((err: Error) => {
        console.error('Stream error:', err)
        error.value = err.message
        isStreaming.value = false
        isConnected.value = false
      })
  }

  function handleEvent(event: StreamEvent) {
    switch (event.type) {
      case 'phase_start':
        currentPhase.value = event.phase || ''
        currentToken.value = ''
        break

      case 'llm_token':
        if (event.token) {
          currentToken.value += event.token
        }
        break

      case 'phase_result':
        if (event.output && event.phase) {
          // Research phase results
          if (event.phase === 'search_firm_history') {
            firmHistoryResult.value = event.output
          } else if (event.phase === 'check_resources') {
            resourcesResult.value = event.output
          } else if (event.phase === 'market_research') {
            marketResearchResult.value = event.output
          }
          // Original pipeline results
          else if (event.phase === 'classify') {
            classificationResult.value = event.output
          } else if (event.phase === 'analyze_risks') {
            riskAnalysisResult.value = event.output
          } else if (event.phase === 'generate_scope') {
            scopeGenerationResult.value = event.output
          }
          completedPhases.value.add(event.phase)
        }
        break

      case 'phase_complete':
        // Phase completed, wait for next phase
        break

      case 'result':
        if (event.document) {
          scopeDocument.value = event.document
        }
        isStreaming.value = false
        isConnected.value = false
        break

      case 'error':
        error.value = event.message || 'An error occurred'
        isStreaming.value = false
        isConnected.value = false
        break
    }
  }

  function disconnect() {
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }
    isConnected.value = false
    isStreaming.value = false
  }

  function reconnect(requestId: string) {
    // Clean up any existing connection
    disconnect()

    isStreaming.value = true
    currentPhase.value = ''
    currentToken.value = ''
    scopeDocument.value = null
    error.value = null

    const url = `${API_BASE_URL}/pipeline/stream/${requestId}`
    eventSource.value = new EventSource(url)

    eventSource.value.onopen = () => {
      isConnected.value = true
    }

    eventSource.value.onmessage = (event) => {
      try {
        const data: StreamEvent = JSON.parse(event.data)
        handleEvent(data)
      } catch (e) {
        console.error('Failed to parse SSE event:', e)
      }
    }

    eventSource.value.onerror = (err) => {
      console.error('EventSource error:', err)
      error.value = 'Connection error'
      isStreaming.value = false
      isConnected.value = false
      disconnect()
    }
  }

  return {
    isConnected,
    connect,
    disconnect,
    reconnect,
  }
}
