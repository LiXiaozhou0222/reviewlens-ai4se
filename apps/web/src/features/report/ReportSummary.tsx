import { FindingSections } from './FindingSections'
import { aiStatusMessage, downloadMarkdown } from './MarkdownExport'
import { ReviewReport } from './types'


interface ReportSummaryProps {
  report: ReviewReport
}


export function ReportSummary({ report }: ReportSummaryProps) {
  const deterministicFindings = report.findings.filter((finding) => finding.source !== 'ai')
  const aiFindings = report.findings.filter((finding) => finding.source === 'ai')
  const aiUnavailable = aiStatusMessage(report.ai_status)

  return (
    <section aria-labelledby="report-title" id="review-result">
      <h2 id="report-title">当前审查结果</h2>
      <p>{`确定性总体等级：${report.deterministic_risk}`}</p>
      <p>限制：只检查此 Diff 中新增的代码行，不代表安全认证。</p>

      <section aria-labelledby="deterministic-findings-title">
        <h3 id="deterministic-findings-title">确定性发现</h3>
        <FindingSections findings={deterministicFindings} />
      </section>

      <section aria-labelledby="ai-findings-title">
        <h3 id="ai-findings-title">AI 补充建议</h3>
        {aiUnavailable === null ? <FindingSections findings={aiFindings} /> : <p>{aiUnavailable}</p>}
      </section>

      <p>能力限制：仅对 JS/TS 文件启用语言专项规则，其他文件仅应用通用规则。</p>
      <button onClick={() => downloadMarkdown(report)} type="button">
        导出 Markdown
      </button>
    </section>
  )
}
