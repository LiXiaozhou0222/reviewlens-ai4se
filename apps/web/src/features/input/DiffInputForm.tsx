import { FormEvent, useRef, useState } from 'react'

import { ReviewRequestError, reviewDiff } from '../../api/client'


type InputMode = 'paste' | 'upload'

const MAX_BYTES = 512_000
const MAX_LINES = 5_000

const ERROR_MESSAGES: Record<string, string> = {
  INPUT_EMPTY: '请粘贴或选择一个 Unified Diff 文件',
  INPUT_TOO_LARGE: '输入超过 500 KB 限制',
  LINE_LIMIT_EXCEEDED: '输入超过 5,000 行限制',
  INVALID_UTF8: '文件必须是 UTF-8 编码',
  INVALID_DIFF_FORMAT: '请输入有效的 Unified Diff',
  INTERNAL_ERROR: '审查请求暂时无法完成，请稍后重试',
}


export function DiffInputForm() {
  const [mode, setMode] = useState<InputMode>('paste')
  const [pasteValue, setPasteValue] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [fileInputKey, setFileInputKey] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const errorRef = useRef<HTMLParagraphElement>(null)
  const submitLockRef = useRef(false)
  const inputDescription = error === null ? 'diff-input-help' : 'diff-input-help diff-input-error'

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (isSubmitting || submitLockRef.current) {
      return
    }
    submitLockRef.current = true

    try {
      const value = await readInput(mode, pasteValue, selectedFiles)
      if (value instanceof ReviewRequestError) {
        showError(value.code)
        return
      }

      const validationCode = validateDiff(value)
      if (validationCode !== null) {
        showError(validationCode)
        return
      }

      setError(null)
      setIsSubmitting(true)
      try {
        await reviewDiff(value)
      } catch (requestError) {
        showError(
          requestError instanceof ReviewRequestError
            ? requestError.code
            : 'INTERNAL_ERROR',
        )
      } finally {
        setPasteValue('')
        setSelectedFiles([])
        setFileInputKey((key) => key + 1)
      }
    } finally {
      submitLockRef.current = false
      setIsSubmitting(false)
    }
  }

  function showError(code: string) {
    setError(ERROR_MESSAGES[code] ?? ERROR_MESSAGES.INTERNAL_ERROR)
    requestAnimationFrame(() => errorRef.current?.focus())
  }

  function changeMode(nextMode: InputMode) {
    setMode(nextMode)
    setError(null)
  }

  return (
    <section aria-labelledby="diff-input-title">
      <h2 id="diff-input-title">提交 Diff</h2>
      <p id="diff-input-help">仅支持 UTF-8 Unified Diff 或一个 .diff/.patch 文件，最多 500 KB、5,000 行。</p>

      <form onSubmit={handleSubmit}>
        <fieldset disabled={isSubmitting} aria-describedby="diff-input-help">
          <legend>输入方式</legend>
          <label>
            <input
              checked={mode === 'paste'}
              name="input-mode"
              onChange={() => changeMode('paste')}
              type="radio"
            />
            粘贴 Diff
          </label>
          <label>
            <input
              checked={mode === 'upload'}
              name="input-mode"
              onChange={() => changeMode('upload')}
              type="radio"
            />
            上传文件
          </label>

          {mode === 'paste' ? (
            <label>
              Unified Diff
              <textarea
                autoComplete="off"
                aria-describedby={inputDescription}
                name="diff"
                onChange={(event) => setPasteValue(event.target.value)}
                rows={12}
                spellCheck={false}
                value={pasteValue}
              />
            </label>
          ) : (
            <label>
              选择 Diff 文件
              <input
                accept=".diff,.patch"
                aria-describedby={inputDescription}
                key={fileInputKey}
                name="diff-file"
                onChange={(event) => setSelectedFiles(Array.from(event.target.files ?? []))}
                type="file"
              />
            </label>
          )}
        </fieldset>

        {error !== null ? (
          <p
            aria-live="assertive"
            id="diff-input-error"
            ref={errorRef}
            role="alert"
            tabIndex={-1}
          >
            {error}
          </p>
        ) : null}
        <p aria-live="polite">{isSubmitting ? '正在审查' : ''}</p>
        <button disabled={isSubmitting} type="submit">
          {isSubmitting ? '正在审查' : '开始审查'}
        </button>
      </form>
    </section>
  )
}


async function readInput(
  mode: InputMode,
  pasteValue: string,
  selectedFiles: readonly File[],
): Promise<string | ReviewRequestError> {
  if (mode === 'paste') {
    return pasteValue
  }
  if (selectedFiles.length === 0) {
    return new ReviewRequestError('INPUT_EMPTY')
  }
  if (selectedFiles.length !== 1) {
    return new ReviewRequestError('INVALID_DIFF_FORMAT')
  }
  const selectedFile = selectedFiles[0]
  if (!/\.(diff|patch)$/i.test(selectedFile.name)) {
    return new ReviewRequestError('INVALID_DIFF_FORMAT')
  }

  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(
      await selectedFile.arrayBuffer(),
    )
  } catch {
    return new ReviewRequestError('INVALID_UTF8')
  }
}


function validateDiff(value: string): string | null {
  if (value.trim().length === 0) {
    return 'INPUT_EMPTY'
  }
  if (new TextEncoder().encode(value).byteLength > MAX_BYTES) {
    return 'INPUT_TOO_LARGE'
  }
  const lines = value.split(/\r\n|\r|\n/)
  const lineCount = /(?:\r\n|\r|\n)$/.test(value) ? lines.length - 1 : lines.length
  if (lineCount > MAX_LINES) {
    return 'LINE_LIMIT_EXCEEDED'
  }
  return null
}
