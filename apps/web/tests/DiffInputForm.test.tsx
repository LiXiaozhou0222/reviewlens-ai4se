import '@testing-library/jest-dom/vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DiffInputForm } from '../src/features/input/DiffInputForm'


const VALID_DIFF = [
  'diff --git a/src/example.ts b/src/example.ts',
  'index 1111111..2222222 100644',
  '--- a/src/example.ts',
  '+++ b/src/example.ts',
  '@@ -0,0 +1 @@',
  '+console.log("review me")',
].join('\n')


afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})


describe('DiffInputForm', () => {
  it('prevents duplicate submit while loading', async () => {
    let resolveRequest: ((value: Response) => void) | undefined
    const fetchMock = vi.fn(
      () => new Promise<Response>((resolve) => {
        resolveRequest = resolve
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    render(<DiffInputForm />)

    fireEvent.change(screen.getByLabelText('Unified Diff'), {
      target: { value: VALID_DIFF },
    })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('button', { name: '正在审查' })).toBeDisabled()
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)

    resolveRequest?.(new Response(JSON.stringify({}), { status: 200 }))
    await waitFor(() => expect(screen.getByRole('button', { name: '开始审查' })).toBeEnabled())
  })

  it('switches between paste and one-file upload inputs', () => {
    render(<DiffInputForm />)

    expect(screen.getByLabelText('Unified Diff')).toBeInTheDocument()
    expect(screen.queryByLabelText('选择 Diff 文件')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('radio', { name: '上传文件' }))

    expect(screen.queryByLabelText('Unified Diff')).not.toBeInTheDocument()
    expect(screen.getByLabelText('选择 Diff 文件')).toBeInTheDocument()
  })

  it('blocks an oversize paste before requesting a review', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    render(<DiffInputForm />)

    fireEvent.change(screen.getByLabelText('Unified Diff'), {
      target: { value: 'x'.repeat(512_001) },
    })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      const alert = screen.getByRole('alert')
      expect(alert).toHaveTextContent('输入超过 500 KB 限制')
      expect(document.activeElement).toBe(alert)
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('accepts an exact 5,000-line paste ending in a newline', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({}), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)
    render(<DiffInputForm />)

    fireEvent.change(screen.getByLabelText('Unified Diff'), {
      target: { value: `${Array(5_000).fill('x').join('\n')}\n` },
    })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(screen.queryByRole('alert')).toBeNull()
  })

  it('associates input constraints and blocking errors with the active input', async () => {
    render(<DiffInputForm />)

    const pasteInput = screen.getByLabelText('Unified Diff')
    expect(pasteInput).toHaveAttribute('aria-describedby', 'diff-input-help')
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveAttribute('id', 'diff-input-error')
      expect(pasteInput).toHaveAttribute(
        'aria-describedby',
        'diff-input-help diff-input-error',
      )
    })

    fireEvent.click(screen.getByRole('radio', { name: '上传文件' }))
    expect(screen.getByLabelText('选择 Diff 文件')).toHaveAttribute(
      'aria-describedby',
      'diff-input-help',
    )
  })

  it('treats whitespace-only paste as empty input', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    render(<DiffInputForm />)

    fireEvent.change(screen.getByLabelText('Unified Diff'), {
      target: { value: '  \n\t' },
    })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(
        '请粘贴或选择一个 Unified Diff 文件',
      )
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('rejects multiple uploaded files before requesting a review', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    render(<DiffInputForm />)

    fireEvent.click(screen.getByRole('radio', { name: '上传文件' }))
    const input = screen.getByLabelText('选择 Diff 文件')
    const firstFile = new File([], 'first.diff')
    const secondFile = new File([], 'second.diff')
    fireEvent.change(input, { target: { files: [firstFile, secondFile] } })

    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('请输入有效的 Unified Diff')
    })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('clears pasted Diff after a failed request', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: { code: 'INVALID_DIFF_FORMAT' } }), {
          status: 400,
        }),
      ),
    )
    render(<DiffInputForm />)

    const input = screen.getByLabelText('Unified Diff')
    fireEvent.change(input, { target: { value: VALID_DIFF } })
    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent('请输入有效的 Unified Diff')
    })
    expect(input).toHaveValue('')
  })

  it('clears the selected file after a successful review', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(new Response(JSON.stringify({}), { status: 200 })),
    )
    render(<DiffInputForm />)

    fireEvent.click(screen.getByRole('radio', { name: '上传文件' }))
    const input = screen.getByLabelText('选择 Diff 文件')
    const file = Object.assign(new File([], 'change.diff'), {
      arrayBuffer: () => Promise.resolve(new TextEncoder().encode(VALID_DIFF).buffer),
    })
    fireEvent.change(input, { target: { files: [file] } })
    expect((input as HTMLInputElement).files).toHaveLength(1)

    fireEvent.click(screen.getByRole('button', { name: '开始审查' }))

    await waitFor(() => {
      const clearedInput = screen.getByLabelText('选择 Diff 文件')
      expect(clearedInput).not.toBe(input)
      expect((clearedInput as HTMLInputElement).files).toHaveLength(0)
    })
  })
})
