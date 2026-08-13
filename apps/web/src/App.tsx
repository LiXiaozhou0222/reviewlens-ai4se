import { DiffInputForm } from './features/input/DiffInputForm'


export default function App() {
  return (
    <main>
      <h1>ReviewLens</h1>
      <p>仅审查 Diff 中新增的代码行。</p>
      <p>Mode shell</p>
      <DiffInputForm />
    </main>
  )
}
