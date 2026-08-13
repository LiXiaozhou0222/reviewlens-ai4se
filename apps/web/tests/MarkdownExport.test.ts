import { describe, expect, it } from 'vitest'

import { buildMarkdown } from '../src/features/report/MarkdownExport'


const REPORT = {
  report_id: '00000000-0000-4000-8000-000000000001',
  created_at: '2026-08-13T00:00:00Z',
  updated_at: '2026-08-13T00:00:00Z',
  diff_sha256: 'a'.repeat(64),
  deterministic_risk: 'Low',
  ai_status: 'NOT_CONFIGURED',
  provider: null,
  model: null,
  ruleset_version: 'v1',
  app_version: 'v1',
  findings: [
    {
      rule_id: 'GEN-003',
      rule_version: 'v1',
      source: 'general_rule',
      severity: 'Low',
      path: 'src/example.ts',
      new_line: 4,
      excerpt: 'TODO',
      message: '发现 TODO。',
      suggestion: '在合并前处理。',
      redacted: false,
      redaction_version: 'v1',
      redaction_category: null,
    },
  ],
  raw_diff: 'do not export this raw Diff',
} as const


describe('buildMarkdown', () => {
  it('exports the sanitized current report without raw Diff content', () => {
    const markdown = buildMarkdown(REPORT)

    expect(markdown).toContain('确定性总体等级：Low')
    expect(markdown).toContain('GEN-003')
    expect(markdown).toContain('AI 补充建议当前不可用')
    expect(markdown).not.toContain('do not export this raw Diff')
  })
})
