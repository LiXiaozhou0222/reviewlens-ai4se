import { useState } from 'react'

import { DiffInputForm } from './features/input/DiffInputForm'
import { ModeGate } from './features/admin/ModeGate'
import { ReportSummary } from './features/report/ReportSummary'
import { ReviewReport } from './features/report/types'


export default function App() {
  const [report, setReport] = useState<ReviewReport | null>(null)

  return (
    <main>
      <h1>ReviewLens</h1>
      <p>仅审查 Diff 中新增的代码行。</p>
      <ModeGate>
        <DiffInputForm onReport={setReport} />
        {report === null ? null : (
          <>
            <p aria-live="polite" role="status">审查完成，已显示当前结果。</p>
            <a href="#review-result">跳转至当前审查结果</a>
            <ReportSummary report={report} />
          </>
        )}
      </ModeGate>
    </main>
  )
}
