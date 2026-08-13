# 实现阶段工作约束（已解锁）

本仓库选择 AI4SE 期末项目 B 类“非 Harness 应用类项目”。用户已于 2026-08-08 明确解除原先的规约/计划阶段限制，并授权从 `PLAN.md` 的 T01 开始实现。该授权不等于预先确认任何后续任务、测试、CI、镜像、部署、PR/MR 或课程交付物已经完成。

本文件适用于所有主智能体、实现子智能体、评审智能体和后续验证智能体。所有工作必须以已确认的 `SPEC.md`、`PLAN.md` 为唯一实现基线；遇到二者冲突、缺失或需要改变范围时，必须暂停并请求用户确认。

## 一、当前阶段目标

当前进入实现阶段，按 `PLAN.md` 的依赖顺序执行已授权任务；当前起点为 T01。每个微任务均必须：

1. 在对应 `codex/...` 分支与隔离 worktree 中实施；
2. 由一个全新的实现 subagent 完成；
3. 严格执行 RED → GREEN → REFACTOR，并保留真实命令与结果；
4. 先完成规约符合性评审，再完成代码质量评审；
5. 修复所有 Critical 问题并复审后，才可进入下一任务；
6. 在真实提交后，向 `PLAN.md` 回填真实 commit hash，并在 `AGENT_LOG.md` 留存真实过程证据。

课程原始要求文件始终只读，不得修改、删减、重命名或覆盖。

## 二、允许的工作

- 阅读课程要求、现有文档、源代码和 Git 历史。
- 严格按照 `SPEC.md` 与 `PLAN.md` 创建或修改实现代码、测试、依赖配置、数据库迁移、Docker/OCI、Compose、CI 和部署文档。
- 使用 `using-git-worktrees`、`subagent-driven-development`、`test-driven-development`、评审和验证 skills；其真实输入、输出、评审结论和人工决策必须记录。
- 创建或更新 `AGENTS.md`、`SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md`、`AGENT_LOG.md`、`README.md`、`docs/cold-start/` 及计划明确列出的实现资产。
- 检查 Git 状态、差异、测试、构建、镜像、CI 与部署结果；只在真实发生后创建合理的提交、PR/MR 或验证记录。

## 三、仍然禁止的工作

- 脱离已确认 `SPEC.md`、`PLAN.md` 的范围自行增加功能、依赖、Provider、外部服务、Agent 自主循环或自动执行用户代码能力。
- 跳过隔离 worktree、TDD、任务级双阶段评审、Critical 问题修复或真实验证。
- 生成或伪造测试输出、覆盖率、CI、部署、镜像、commit hash、PR/MR、评审或冷启动证据。
- 创建、修改、代写或补全 `REFLECTION.md`；其学生本人撰写与可披露语言润色边界仍按课程要求和 `PLAN.md` H01 执行。
- 将真实 API Key、主密码、私有 Diff、原始 Prompt/响应、未脱敏凭据或用户敏感内容写入 Git、测试 fixture、日志、镜像、文档或截图。
- 在用户尚未授权相应外部动作时推送远程仓库、创建 PR/MR、发布 Registry 镜像、部署公网实例或访问真实 OpenAI API。
- 声称尚未由真实运行、审查和外部系统证明的功能、测试、CI、分发或部署已经完成。

## 四、执行与留痕规则

- `SPEC.md` 与 `PLAN.md` 是执行合同；`SPEC_PROCESS.md` 记录真实的设计、冷启动与实质规约修订过程；`AGENT_LOG.md` 按时间记录 task、skill、prompt/context、subagent 输出、RED/GREEN 证据、评审、人工干预、偏离与教训。
- 每个 task 完成后，先做规约符合性评审，再做代码质量评审。发现 Critical 问题必须修复并复审；任何未解决且会影响后续任务的缺陷必须暂停并报告用户。
- 计划中的完成状态、commit hash、PR/MR、CI、镜像或部署 URL 只能在实际产生后写入。历史冷启动记录不得被伪造、抹除或重新表述为未发生。
- 如用户请求与本文件、`SPEC.md` 或 `PLAN.md` 冲突，必须指出冲突并请求明确更新；未经授权，不得扩大范围。

## 五、阶段边界

此前的设计阶段解锁条件已满足并有真实记录：`SPEC.md`、`PLAN.md` 已获用户确认；Open Design 门禁已关闭；Probe 01 陌生智能体冷启动已完成并据其暂停反馈修订文档。当前授权仅开启正式实现，最终交付仍须逐项满足 `PLAN.md` 的 R01 门禁及课程要求，且不得由智能体自行宣布完成。
