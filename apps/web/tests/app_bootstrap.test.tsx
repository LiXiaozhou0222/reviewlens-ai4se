import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from '../src/App'


const REPORT = {
  report_id: '00000000-0000-4000-8000-000000000001',
  created_at: '2026-08-13T00:00:00Z',
  updated_at: '2026-08-13T00:00:00Z',
  diff_sha256: 'a'.repeat(64),
  deterministic_risk: 'None',
  ai_status: 'NOT_CONFIGURED',
  provider: null,
  model: null,
  ruleset_version: 'v1',
  app_version: 'v1',
  findings: [],
}


afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('App bootstrap', () => {
  it('renders the mode shell', () => {
    render(<App />)

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'ReviewLens' })).toBeInTheDocument()
    expect(screen.getByText('Mode shell')).toBeInTheDocument()
  })

  it('announces a current report and provides a skip link after review completion', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(JSON.stringify(REPORT), { status: 200 })),
    )
    render(<App />)

    fireEvent.change(screen.getByLabelText('Unified Diff'), {
      target: { value: 'diff --git a/a b/a\n@@ -0,0 +1 @@\n+const value = 1\n' },
    })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('status')).toHaveTextContent('审查完成，已显示当前结果。')
      expect(screen.getByRole('link', { name: '跳转至当前审查结果' })).toHaveAttribute(
        'href',
        '#review-result',
      )
    })
  })
})
