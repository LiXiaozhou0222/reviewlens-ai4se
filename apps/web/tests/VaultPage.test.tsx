import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { VaultPage } from '../src/features/admin/VaultPage'


afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})


describe('VaultPage', () => {
  it('shows only masked vault status', async () => {
    const rawApiKey = 'sk-private-key-must-never-render'
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            exists: true,
            unlocked: false,
            provider: 'openai',
            model: 'gpt-test',
            masked_api_key: '••••9F2A',
          }),
          { status: 200 },
        ),
      ),
    )

    render(<VaultPage />)

    await waitFor(() => {
      expect(screen.getByText('••••9F2A')).toBeInTheDocument()
    })
    expect(screen.queryByText(rawApiKey)).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: '解锁保险箱' })).toBeInTheDocument()
  })

  it('does not display an unexpected unmasked status value', async () => {
    const rawApiKey = 'sk-private-key-must-never-render'
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            exists: true,
            unlocked: false,
            provider: 'openai',
            model: 'gpt-test',
            masked_api_key: rawApiKey,
          }),
          { status: 200 },
        ),
      ),
    )

    render(<VaultPage />)

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('无法读取保险箱状态')
    })
    expect(screen.queryByText(rawApiKey)).not.toBeInTheDocument()
  })

  it('uses the local vault lock operation and refreshes its masked status', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            exists: true,
            unlocked: true,
            provider: 'openai',
            model: 'gpt-test',
            masked_api_key: '••••9F2A',
          }),
          { status: 200 },
        ),
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            exists: true,
            unlocked: false,
            provider: 'openai',
            model: 'gpt-test',
            masked_api_key: '••••9F2A',
          }),
          { status: 200 },
        ),
      )
    vi.stubGlobal('fetch', fetchMock)

    render(<VaultPage />)

    const lockButton = await screen.findByRole('button', { name: '锁定保险箱' })
    fireEvent.click(lockButton)

    await waitFor(() => {
      expect(screen.getByText('已锁定')).toBeInTheDocument()
    })
    expect(fetchMock).toHaveBeenNthCalledWith(2, '/admin/v1/vault/lock', {
      method: 'POST',
      headers: undefined,
      body: undefined,
    })
  })
})
