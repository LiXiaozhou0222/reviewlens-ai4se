# ReviewLens

## 当前规则范围与已知限制

首期 JavaScript / TypeScript 专项确定性规则固定为 `JS-001` 至 `JS-006`。`JS-007`（显式 `any`）已在 2026-08-12 经批准的 scope revision 中移除：在不引入 tokenizer、AST、TypeScript Compiler 或外部解析依赖的架构边界内，它不能同时可靠区分 TSX 嵌套 JSX、泛型箭头函数和嵌套对象默认值。未报告 `any` 不代表不存在代码质量风险。
