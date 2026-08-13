import '@testing-library/jest-dom/vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ReportSummary } from '../src/features/report/ReportSummary'


const REPORT = {
  report_id: '00000000-0000-4000-8000-000000000001',
  created_at: '2026-08-13T00:00:00Z',
  updated_at: '2026-08-13T00:00:00Z',
  diff_sha256: 'a'.repeat(64),
  deterministic_risk: 'High',
  ai_status: 'SUCCEEDED',
  provider: 'mock',
  model: 'reviewlens-mock-v1',
  ruleset_version: 'v1',
  app_version: 'v1',
  findings: [
    {
      rule_id: 'GEN-001',
      rule_version: 'v1',
      source: 'general_rule',
      severity: 'High',
      path: 'src/settings.ts',
      new_line: 8,
      excerpt: '[REDACTED_CREDENTIAL]',
      message: '检测到硬编码凭据。',
      suggestion: '改用环境变量。',
      redacted: true,
      redaction_version: 'v1',
      redaction_category: 'credential',
    },
    {
      rule_id: 'AI-001',
      rule_version: 'v1',
      source: 'ai',
      severity: 'Medium',
      path: 'src/settings.ts',
      new_line: 8,
      excerpt: '配置读取逻辑',
      message: '补充检查配置轮换策略。',
      suggestion: '记录轮换流程。',
      redacted: false,
      redaction_version: 'v1',
      redaction_category: null,
    },
  ],
} as const


afterEach(cleanup)


describe('ReportSummary', () => {
  it('separates deterministic conclusion from AI advice', () => {
    render(<ReportSummary report={REPORT} />)

    expect(screen.getByText('确定性总体等级：High')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '确定性发现' })).toBeInTheDocument()
    expect(screen.getByText('来源：通用规则')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'AI 补充建议' })).toBeInTheDocument()
    expect(screen.getByText('来源：AI 补充建议')).toBeInTheDocument()
    expect(screen.getByText('检测到硬编码凭据。').compareDocumentPosition(
      screen.getByText('补充检查配置轮换策略。'),
    ) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('keeps deterministic findings visible when AI is unavailable', () => {
    render(<ReportSummary report={{ ...REPORT, ai_status: 'PROVIDER_UNAVAILABLE', findings: [REPORT.findings[0]] }} />)

    expect(screen.getByText('检测到硬编码凭据。')).toBeInTheDocument()
    expect(screen.getByText('AI 补充建议当前不可用：服务暂时不可用。')).toBeInTheDocument()
  })
})
