export type Severity = 'Critical' | 'High' | 'Medium' | 'Low' | 'None'

export type FindingSource = 'general_rule' | 'language_rule' | 'ai'

export interface SanitizedFinding {
  rule_id: string
  rule_version: string
  source: FindingSource
  severity: Severity
  path: string
  new_line: number | null
  excerpt: string
  message: string
  suggestion: string
  redacted: boolean
  redaction_version: string
  redaction_category: string | null
}

export interface ReviewReport {
  report_id: string
  created_at: string
  updated_at: string
  diff_sha256: string
  deterministic_risk: Severity
  ai_status: string
  provider: string | null
  model: string | null
  ruleset_version: string
  app_version: string
  findings: readonly SanitizedFinding[]
}
