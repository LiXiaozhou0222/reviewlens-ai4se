import { ReactNode, useEffect, useState } from 'react'

import { VaultPage } from './VaultPage'


type RuntimeMode = 'demo' | 'private'
type ModeState = RuntimeMode | 'loading' | 'unavailable'


function isRuntimeMode(value: unknown): value is RuntimeMode {
  return value === 'demo' || value === 'private'
}


export function ModeGate({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ModeState>('loading')

  useEffect(() => {
    let active = true

    void fetch('/ready')
      .then(async (response) => {
        if (!response.ok) {
          return null
        }
        const payload: unknown = await response.json()
        if (
          typeof payload !== 'object'
          || payload === null
          || !('status' in payload)
          || payload.status !== 'ready'
          || !('mode' in payload)
          || !isRuntimeMode(payload.mode)
        ) {
          return null
        }
        return payload.mode
      })
      .then((loadedMode) => {
        if (active) {
          setMode(loadedMode ?? 'unavailable')
        }
      })
      .catch(() => {
        if (active) {
          setMode('unavailable')
        }
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <>
      <section aria-label="运行模式">
        {mode === 'loading' ? <p role="status">正在确认运行模式。</p> : null}
        {mode === 'demo' ? (
          <p>Demo 模式：使用 Mock 建议，不会调用真实 OpenAI；刷新后结果会消失。</p>
        ) : null}
        {mode === 'private' ? (
          <p>私有模式：本机保险箱中的凭据不会显示在审查页面。</p>
        ) : null}
        {mode === 'unavailable' ? (
          <p role="alert">无法确认运行模式，已隐藏本机私有控制。</p>
        ) : null}
      </section>
      {mode === 'private' ? <VaultPage /> : null}
      {children}
    </>
  )
}
