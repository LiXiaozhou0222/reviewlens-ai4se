import { FormEvent, useEffect, useState } from 'react'


interface VaultStatus {
  exists: boolean
  unlocked: boolean
  provider: string | null
  model: string | null
  masked_api_key: string | null
}

function isVaultStatus(value: unknown): value is VaultStatus {
  return (
    typeof value === 'object'
    && value !== null
    && 'exists' in value
    && typeof value.exists === 'boolean'
    && 'unlocked' in value
    && typeof value.unlocked === 'boolean'
    && 'provider' in value
    && (typeof value.provider === 'string' || value.provider === null)
    && 'model' in value
    && (typeof value.model === 'string' || value.model === null)
    && 'masked_api_key' in value
    && (value.masked_api_key === null || isMaskedApiKey(value.masked_api_key))
  )
}


function isMaskedApiKey(value: unknown): value is string {
  return typeof value === 'string' && /^••••.{4}$/u.test(value)
}


export function VaultPage() {
  const [status, setStatus] = useState<VaultStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const [masterPassword, setMasterPassword] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('')
  const [confirmClear, setConfirmClear] = useState(false)

  const refreshStatus = async () => {
    const response = await fetch('/admin/v1/vault/status')
    const payload: unknown = await response.json()
    if (!response.ok || !isVaultStatus(payload)) {
      throw new Error('vault-status-unavailable')
    }
    setStatus(payload)
  }

  useEffect(() => {
    void refreshStatus().catch(() => {
      setError('无法读取保险箱状态，请检查本机私有服务。')
    })
  }, [])

  const runOperation = async (path: string, body?: object) => {
    setPending(true)
    setError(null)
    try {
      const response = await fetch(path, {
        method: 'POST',
        headers: body === undefined ? undefined : { 'content-type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
      })
      if (!response.ok) {
        throw new Error('vault-operation-failed')
      }
      setMasterPassword('')
      setApiKey('')
      setModel('')
      setConfirmClear(false)
      await refreshStatus()
    } catch {
      setError('保险箱操作未完成，请检查本机状态后重试。')
    } finally {
      setPending(false)
    }
  }

  const submitInitializeOrUpdate = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void runOperation(
      status?.exists ? '/admin/v1/vault/update' : '/admin/v1/vault/initialize',
      { master_password: masterPassword, api_key: apiKey, model },
    )
  }

  const submitUnlock = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void runOperation('/admin/v1/vault/unlock', { master_password: masterPassword })
  }

  const submitClear = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void runOperation('/admin/v1/vault/clear', { master_password: masterPassword })
  }

  const vaultExists = status?.exists ?? false
  const vaultUnlocked = status?.unlocked ?? false

  return (
    <section aria-labelledby="vault-title">
      <h2 id="vault-title">本机保险箱</h2>
      {status === null ? <p role="status">正在读取保险箱状态。</p> : null}
      {status !== null ? (
        <dl>
          <dt>状态</dt>
          <dd>{vaultExists ? (vaultUnlocked ? '已解锁' : '已锁定') : '尚未初始化'}</dd>
          <dt>Provider</dt>
          <dd>{status.provider ?? '未配置'}</dd>
          <dt>模型</dt>
          <dd>{status.model ?? '未配置'}</dd>
          <dt>API Key</dt>
          <dd>{status.masked_api_key ?? '未配置'}</dd>
        </dl>
      ) : null}
      {error === null ? null : <p role="alert">{error}</p>}

      {status !== null && (!vaultExists || vaultUnlocked) ? (
        <form onSubmit={submitInitializeOrUpdate}>
          <h3>{vaultExists ? '更新保险箱' : '初始化保险箱'}</h3>
          <label>
            主密码
            <input
              autoComplete="current-password"
              disabled={pending}
              onChange={(event) => setMasterPassword(event.target.value)}
              required
              type="password"
              value={masterPassword}
            />
          </label>
          <label>
            OpenAI API Key
            <input
              autoComplete="off"
              disabled={pending}
              onChange={(event) => setApiKey(event.target.value)}
              required
              type="password"
              value={apiKey}
            />
          </label>
          <label>
            模型
            <input
              disabled={pending}
              onChange={(event) => setModel(event.target.value)}
              required
              value={model}
            />
          </label>
          <button disabled={pending} type="submit">
            {vaultExists ? '更新保险箱' : '初始化保险箱'}
          </button>
        </form>
      ) : status !== null ? (
        <form onSubmit={submitUnlock}>
          <label>
            主密码
            <input
              autoComplete="current-password"
              disabled={pending}
              onChange={(event) => setMasterPassword(event.target.value)}
              required
              type="password"
              value={masterPassword}
            />
          </label>
          <button disabled={pending} type="submit">解锁保险箱</button>
        </form>
      ) : null}

      {status !== null && vaultExists && vaultUnlocked ? (
        <>
          <button disabled={pending} onClick={() => void runOperation('/admin/v1/vault/lock')} type="button">
            锁定保险箱
          </button>
          <button disabled={pending} onClick={() => setConfirmClear(true)} type="button">
            清除保险箱
          </button>
        </>
      ) : null}

      {confirmClear ? (
        <div aria-labelledby="clear-vault-title" role="dialog">
          <h3 id="clear-vault-title">确认清除保险箱</h3>
          <p>清除后需要重新初始化保险箱。</p>
          <form onSubmit={submitClear}>
            <label>
              主密码
              <input
                autoComplete="current-password"
                disabled={pending}
                onChange={(event) => setMasterPassword(event.target.value)}
                required
                type="password"
                value={masterPassword}
              />
            </label>
            <button disabled={pending} type="submit">确认清除</button>
            <button disabled={pending} onClick={() => setConfirmClear(false)} type="button">取消</button>
          </form>
        </div>
      ) : null}
    </section>
  )
}
