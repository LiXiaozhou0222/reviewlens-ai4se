# ReviewLens

面向个人学生开发者的 Git Diff 风险审查工具：固定确定性规则先给出可重复结论，private 模式可选附加一次 OpenAI 建议，Demo 固定使用无网络 Mock。

## 当前规则范围与已知限制

首期通用规则为 `GEN-001` 至 `GEN-005`，JavaScript / TypeScript 专项规则固定为 `JS-001` 至 `JS-006`。`JS-007`（显式 `any`）已在 2026-08-12 经批准的 scope revision 中移除：在不引入 tokenizer、AST、TypeScript Compiler 或外部解析依赖的架构边界内，它不能同时可靠区分 TSX 嵌套 JSX、泛型箭头函数和嵌套对象默认值。未报告 `any` 不代表不存在代码质量风险。

v1 只处理当前一次审查：服务端不保存 Diff、Report、Finding、摘要或历史记录；刷新后结果消失。Markdown 仅由浏览器根据当前已脱敏结果即时生成。v1 不支持 AI retry、历史 UI、筛选 UI、服务端导出缓存或 Docker Compose。

private 模式的 API key 仅以主密码加密 Vault 文件保存，默认锁定；private app 只可从本机 loopback 使用。公开 Demo 固定为 `APP_MODE=demo`、Mock、无状态，且不注册 Vault/private 路由。

## 分发与验证状态

计划交付一个 `linux/amd64` OCI image，并以单条 `docker build` 和分别的 Demo/private `docker run` 命令运行；Windows 11 x64 + Docker Desktop 是本地支持环境。Docker image、公开 Registry、CI、NJU GitLab Pipeline 和公网 Demo URL 尚未产生，后续只会在真实验证后记录。
