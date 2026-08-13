import { FindingSource, ReviewReport } from './types'


const SOURCE_LABELS: Record<FindingSource, string> = {
  general_rule: '通用规则',
  language_rule: '语言规则',
  ai: 'AI 补充建议',
}

const AI_UNAVAILABLE_MESSAGES: Record<string, string> = {
  NOT_CONFIGURED: 'AI 补充建议当前不可用：尚未配置。',
  AUTH_FAILED: 'AI 补充建议当前不可用：认证失败。',
  MODEL_UNAVAILABLE: 'AI 补充建议当前不可用：模型不可用。',
  RATE_LIMITED: 'AI 补充建议当前不可用：请求受限。',
  TIMEOUT: 'AI 补充建议当前不可用：请求超时。',
  INPUT_TOO_LARGE: 'AI 补充建议当前不可用：输入过大。',
  INVALID_RESPONSE: 'AI 补充建议当前不可用：响应无效。',
  PROVIDER_UNAVAILABLE: 'AI 补充建议当前不可用：服务暂时不可用。',
}


export function aiStatusMessage(status: string): string | null {
  if (status === 'SUCCEEDED') {
    return null
  }
  return AI_UNAVAILABLE_MESSAGES[status] ?? 'AI 补充建议当前不可用。'
}


export function buildMarkdown(report: ReviewReport): string {
  const deterministicFindings = report.findings.filter((finding) => finding.source !== 'ai')
  const aiFindings = report.findings.filter((finding) => finding.source === 'ai')
  const lines = [
    '# ReviewLens 审查报告',
    '',
    `确定性总体等级：${report.deterministic_risk}`,
    '限制：只检查此 Diff 中新增的代码行，不代表安全认证。',
    '',
    '## 确定性发现',
    ...findingMarkdown(deterministicFindings),
    '',
    '## AI 补充建议',
  ]

  const aiStatus = aiStatusMessage(report.ai_status)
  if (aiStatus !== null) {
    lines.push(aiStatus)
  } else {
    lines.push(...findingMarkdown(aiFindings))
  }

  lines.push('', '能力限制：仅对 JS/TS 文件启用语言专项规则，其他文件仅应用通用规则。')
  return lines.join('\n')
}


export function downloadMarkdown(report: ReviewReport) {
  const blob = new Blob([buildMarkdown(report)], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = 'reviewlens-report.md'
  anchor.click()
  URL.revokeObjectURL(url)
}


function findingMarkdown(findings: readonly ReviewReport['findings'][number][]): string[] {
  if (findings.length === 0) {
    return ['没有发现。']
  }
  return findings.flatMap((finding) => [
    `- ${finding.severity} - ${finding.rule_id}（来源：${SOURCE_LABELS[finding.source]}）`,
    `  - 位置：${finding.new_line === null ? finding.path : `${finding.path}:${finding.new_line}`}`,
    `  - 问题：${finding.message}`,
    `  - 建议：${finding.suggestion}`,
    `  - 片段：${finding.excerpt}`,
  ])
}
