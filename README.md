# ReviewLens

## 当前规则范围与已知限制

`JS-007` 是首期固定规则集中的 Low 等级提示，只检查新增、非二进制 `.ts`/`.tsx` 行中可高置信识别的显式 `any`：变量声明、函数参数/返回类型，以及完整调用或索引表达式后的 `as any`。它不会报告 JSX 文本、注释、字符串、模板文本、正则字面量、`import`/`export` alias、语句标签或对象字面量。

为避免明显误报，首期不覆盖 `interface`/`type` object member、跨行 type assertion、裸标识符 `value as any` 和其他需要更强语法上下文的 `any` 形式；未报告不代表不存在 `any` 或代码质量风险。该规则不使用 tokenizer、AST、TypeScript Compiler 或外部解析依赖。
