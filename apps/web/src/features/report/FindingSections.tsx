import { SanitizedFinding } from './types'


const SOURCE_LABELS: Record<SanitizedFinding['source'], string> = {
  general_rule: '通用规则',
  language_rule: '语言规则',
  ai: 'AI 补充建议',
}


interface FindingSectionsProps {
  findings: readonly SanitizedFinding[]
}


export function FindingSections({ findings }: FindingSectionsProps) {
  if (findings.length === 0) {
    return <p>没有发现。</p>
  }

  return (
    <ul>
      {findings.map((finding) => (
        <li key={`${finding.source}-${finding.rule_id}-${finding.path}-${finding.new_line ?? 'file'}`}>
          <p>{`${finding.severity} - ${finding.rule_id}`}</p>
          <p>{`来源：${SOURCE_LABELS[finding.source]}`}</p>
          <p>{finding.new_line === null ? finding.path : `${finding.path}:${finding.new_line}`}</p>
          <p>{finding.message}</p>
          <p>{finding.suggestion}</p>
          <p>{finding.excerpt}</p>
        </li>
      ))}
    </ul>
  )
}
