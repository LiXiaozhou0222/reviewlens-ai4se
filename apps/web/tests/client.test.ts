import { afterEach, describe, expect, it, vi } from 'vitest'

import { ReviewRequestError, reviewDiff } from '../src/api/client'


afterEach(() => {
  vi.unstubAllGlobals()
})


describe('reviewDiff', () => {
  it('posts UTF-8 diff bytes to the stable review endpoint', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ report_id: 'report' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await reviewDiff('diff --git a/a b/a\n')

    expect(fetchMock).toHaveBeenCalledWith('/api/v1/reviews', {
      method: 'POST',
      headers: { 'content-type': 'application/octet-stream' },
      body: new TextEncoder().encode('diff --git a/a b/a\n'),
    })
  })

  it('keeps only the public error code from a failed request', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({ detail: { code: 'INVALID_DIFF_FORMAT', internal: 'secret' } }),
          { status: 400 },
        ),
      ),
    )

    await expect(reviewDiff('invalid')).rejects.toEqual(
      new ReviewRequestError('INVALID_DIFF_FORMAT'),
    )
  })
})
