export class ReviewRequestError extends Error {
  constructor(readonly code: string) {
    super(code)
  }
}


export async function reviewDiff(diff: string): Promise<unknown> {
  const response = await fetch('/api/v1/reviews', {
    method: 'POST',
    headers: { 'content-type': 'application/octet-stream' },
    body: new TextEncoder().encode(diff),
  })
  const payload: unknown = await response.json()

  if (!response.ok) {
    throw new ReviewRequestError(publicErrorCode(payload))
  }
  return payload
}


function publicErrorCode(payload: unknown): string {
  if (
    typeof payload === 'object'
    && payload !== null
    && 'detail' in payload
    && typeof payload.detail === 'object'
    && payload.detail !== null
    && 'code' in payload.detail
    && typeof payload.detail.code === 'string'
  ) {
    return payload.detail.code
  }
  return 'INTERNAL_ERROR'
}
