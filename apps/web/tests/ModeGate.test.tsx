import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App'


afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})


describe('ModeGate', () => {
  it('does not render private controls in demo mode', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ready', mode: 'demo' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    await waitFor(() => {
      expect(screen.getByText(/Demo 模式/)).toBeInTheDocument()
    })
    expect(screen.queryByRole('heading', { name: '本机保险箱' })).not.toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('renders the allowed vault workspace in private mode', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn()
        .mockResolvedValueOnce(
          new Response(JSON.stringify({ status: 'ready', mode: 'private' }), { status: 200 }),
        )
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              exists: false,
              unlocked: false,
              provider: null,
              model: null,
              masked_api_key: null,
            }),
            { status: 200 },
          ),
        ),
    )

    render(<App />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: '初始化保险箱' })).toBeInTheDocument()
    })
  })

  it('fails closed when ready is unavailable or returns an unknown mode', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ status: 'ready', mode: 'staging' }), { status: 200 }),
      ),
    )

    render(<App />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('无法确认运行模式')
    })
    expect(screen.queryByRole('heading', { name: '本机保险箱' })).not.toBeInTheDocument()
  })

  it('fails closed when the ready request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network unavailable')))

    render(<App />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('无法确认运行模式')
    })
    expect(screen.queryByRole('heading', { name: '本机保险箱' })).not.toBeInTheDocument()
  })
})
