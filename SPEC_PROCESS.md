# ReviewLens 规约生成过程

## 2026-08-13 - T12.3 admin boundary evidence

T12.3 completed in isolated `codex/admin-observability-t12-3`: `9d6c0df` added the private-only Vault management router and `430e6fa` repaired a review-discovered credential-echo risk in FastAPI request-validation errors. The first review did not approve the default 422 path because malformed `master_password` or `api_key` values could appear in the response `input`. A real Python 3.12 RED reproduced 422 instead of the required sanitized public response. The minimal repair introduced stable `400 INVALID_REQUEST` without submitted input. Final evidence was 6 focused admin tests, 24 API tests, and 255 full-backend tests passed; compileall and Git checks were clean. The task ledger moved to 49/62 complete with 13 P0 tasks remaining. Loopback listener and Docker host publication remain T17 runtime evidence, while Demo route non-registration is already enforced here.

## 2026-08-13 - T12.1 health/readiness evidence

T12.1 was completed in isolated `codex/release-health` and committed as `040155b`. The implementation used Python 3.12.10 only. Real verification recorded 9 health tests passed, 66 JavaScript-rule tests passed, 249 full-backend tests passed, and clean `git diff --check`. Fresh spec-compliance and code-quality reviews approved the task without Critical findings. The task ledger was updated from 47/62 to 48/62 completed, with 14 P0 tasks remaining. No external deployment, registry, CI, OpenAI request, real credential, or private Diff was used or claimed.

## 2026-08-12：72-hour Release Scope Revision（已获用户批准）

用户批准停止进一步 triage，并授权将 109 个有效任务压缩为 62 个正式 v1 任务：30 个真实完成、32 个待执行 P0、0 个 P1。该决定不是对任何未来测试、CI、镜像、部署或 Reflection 的完成声明。

- **移除：** 报告数据库、SQLite/SQLAlchemy/Alembic、Repository、历史、AI retry、服务端导出、筛选 UI、Compose、独立 `:8081` admin listener、应用内限流和重复 fresh-start smoke；JS-007 继续保持取消。
- **保留：** 当前请求 `ReportView`、浏览器 Markdown、FindingRedactor、Vault 加密文件、单次 Mock/OpenAI、单一 OCI image、双 CI、公开无状态 Mock Demo、真实 release gate。
- **Private 边界：** private 整个 app 绑定回环；Vault routes 只在 private 注册。Demo 不注册 private/Vault routes，不持久化任何访客审查数据。
- **部署边界：** 公网部署改为 platform-neutral；HTTPS Demo、Mock、无状态和 private routes 不可达是验收，Nginx、DNS、Compose 与 HTTP 429 不再是产品合同。
- **时间表述修订：** realistic aggregate effort 约 63 小时，不能等价为串行 wall-clock 或“剩余 9 小时 buffer”；最多三条合法 lane 并行，最终锁定 8–10 小时给 Reflection、最终 CI、部署复核、secret scan、clean tree 与提交。
- **依赖修订：** T10.1 同时依赖 T05.8–T05.10 和 M06；T10.3 依赖 M06 和 M09。该规定防止任何正式 ReportView 绕过脱敏。
- **一致性要求：** scope revision 同步删除 DB-only 数据模型、迁移、持久化/历史 API、AIReviewAttempt、cascade/unique 约束、技术栈与 README 声明；Vault 文件持久化不受影响。SPEC 保留 7 个真实 INVEST 用户故事，不用已删除能力凑数。

文档修订完成后应进行一次快速一致性审查；除新的架构冲突、repair cap、已批准范围变更、不可避免的共享合同冲突或外部授权需求外，直接按新版 PLAN 三条 lane 执行。

### 移除后的真实验证

JS-007 撤除提交为 `91fd7fa`。控制器确认活跃 API 代码与测试中不再包含
`JS-007`、`scan_js_007`、元数据或专属扫描状态，并确认受影响 JS 文件与
T05.6 批准基线 `9cdd99c` 一致。Python 3.12 验证为 JS 规则 64 passed、完整
后端 133 passed。T05.10 风险聚合模块和测试尚未实现，因此不存在需要替换的
JS-007 fixture 依赖。

独立规约符合性审查和代码质量审查均批准此次撤除，均无 Critical 或 Important
finding。它们确认正式 SPEC/README 只宣称 JS-001…JS-006、PLAN 的 T05.7 是
取消状态、`3852a88` 保留为真实证据且未被表述为完成。撤除完成后按用户明确
指示暂停在 T05.8 前。

## 2026-08-12：JS-007 架构冲突后的正式移除

在从批准基线重新执行的 T05.7 中，控制器使用 Python 3.12 获得了聚焦 9 passed、JavaScript 规则 90 passed、完整后端 159 passed 的真实测试证据；这些结果不等于规约批准。独立 scoped review 随后复现了三类重要冲突：TSX 嵌套 JSX 文本可被误报为代码、泛型箭头函数可被误判为 JSX、嵌套对象默认值可被误判为支持的类型参数。真实过程与根因已记录在 `3852a88`。

用户明确拒绝 tokenizer、AST、TypeScript Compiler 和外部解析依赖，并在 JS-007 为 Low severity 的前提下选择正式移除该规则，而不是继续累积词法补丁。SPEC、PLAN、README 与正式实现随之调整：v1 JavaScript/TypeScript 规则集为 JS-001…JS-006；T05.7 标记为 `CANCELLED / REMOVED BY APPROVED SCOPE REVISION`，不记作成功完成，也不声称此前 GREEN 已满足任务。旧代码、测试和审查提交保留为真实证据，不复用为正式能力。

## 记录范围与真实性声明

- 本文件仅记录已经发生的规约工作；未发生的 brainstorming 迭代、设计签字、冷启动试运行或 SPEC/PLAN 修订均不补写或虚构。
- 当前项目定位由用户暂定为：**ReviewLens——面向学生开发者和小型团队的 Git Diff 风险审查与 AI 辅助代码评审平台**。
- 当前阶段仍受 `AGENTS.md` 约束：不得初始化框架、创建业务代码或测试、创建 Docker/CI 配置，亦不得修改 `REFLECTION.md`。

## 2026-08-05：课程要求审计（已发生）

### 已阅读的材料

1. `AGENTS.md`
2. `docs/requirements/AI4SE_Final_Project_通用要求.md`（下称“通用要求”）
3. `docs/requirements/AI4SE_Final_Project_B_应用类项目.md`（下称“B 类要求”）
4. `README.md`
5. 当时为空的 `SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md`、`AGENT_LOG.md`

### 审计结论

- 项目按 B 类“非 Harness 应用类项目”执行；完整要求为通用要求与 B 类要求的合并（通用要求开头说明、B 类要求引言）。
- B 类须构建真实且有规模的软件，至少三个职责清晰的功能模块、可一键运行的核心测试，不能是纯 demo 或玩具项目（B.1；通用要求 §3.4）。
- ReviewLens 应保持非 Agent 边界：单轮 LLM 评审功能不构成 agent；若引入自主多轮决策或工具自主调用，则该部分须满足 Harness 的实现边界和确定性测试标准（B.2）。
- 规约阶段的必经顺序是 brainstorming、用户分段确认、SPEC、writing-plans、PLAN、陌生智能体冷启动、根据反馈修订；在 SPEC、PLAN 和冷启动完成前不得写实现（通用要求 §4.1、§4.5；`AGENTS.md`）。
- 课程最终要求包括 SPEC/PLAN/SPEC_PROCESS、源代码与规范的 commit/PR 历史、分发说明、README、AGENT_LOG、`.gitlab-ci.yml` 的 `unit-test` job、最终通过的 CI/CD 记录、由学生本人撰写的 REFLECTION 和可访问的公网 WebUI（通用要求 §五）。
- 凭据不得硬编码、提交或写入日志；需安全存储、首次安全录入和管理流程，且在 SPEC 中给出威胁模型与对策（通用要求 §3.1；B.3）。分发可选容器、二进制或包管理器，README 须说明安全配置与限制（通用要求 §3.2、§4.10；B.3）。
- 实现阶段要求 worktree 与每个独立功能/大模块对应 PR、每 task 一个新鲜 subagent、先 RED 后 GREEN 再 REFACTOR，以及“spec 合规→代码质量”两阶段评审（通用要求 §4.6）。
- 已发现的待澄清歧义：通用要求 §4.8 写 GitHub Actions，而最终交付物 §五指定 `.gitlab-ci.yml` 且包含 `unit-test` job；§4.11 将云部署表述为带服务端项目“可选择”，但 §五又要求提交可访问的公网 WebUI。后续设计应先请求用户确认如何满足两者，不能自行假定。

### Superpowers brainstorming 记录

- 用户要求使用 Superpowers 的 `brainstorming` 工作流。
- 当前 Codex 会话暴露的可用 skill 清单中没有该 skill，因此无法真实调用它。为避免伪称已使用，本次采用其课程明确要求的交互形式：完成要求审计后，一次只提出一个影响范围、架构或验收的问题，给出选项、权衡与推荐，并等待用户确认。
- 这是对课程“必须使用 Superpowers”的偏离，原因是当前运行环境未提供该能力；已同步记录到 `AGENT_LOG.md`。后续若该 skill 可用，应改为真实调用并补充记录。

### 设计迭代与签字状态

- 已完成关键迭代：12 / 至少 3。前十二轮用户范围决策已确认；这不是最终 SPEC 的签字。
- 尚未生成最终 `SPEC.md` 或 `PLAN.md`。
- 尚未进行陌生智能体冷启动；因此没有冷启动缺陷、试运行代码、修订前后差异或验证结论。

## 2026-08-05：Brainstorming 迭代 1 — 目标用户与协作边界（已确认）

### 智能体问题与建议

- 问题：首期主要用户是谁？该决定影响身份模型、协作能力、Diff 输入、数据保留策略和验收场景。
- 选项：A. 个人学生开发者；B. 小型团队成员（多用户与项目空间）；C. 个人优先、导出报告供团队共享。
- 推荐：C，以保留小团队使用价值，同时避免首期的认证、授权与多租户复杂度。

### 用户决定与理由

- 用户选择 **C**，并明确首期主要用户是个人学生开发者，也服务于小型团队中的单个成员在提交前自查。
- 项目描述调整为“面向个人学生开发者，并支持将审查报告导出后供小型团队共享”。
- 系统为单用户、自托管工具；不做注册登录、多用户账号、团队空间、在线协作、共享链接、成员权限或多租户。
- 用户通过粘贴或上传 Git Diff 发起审查；报告保存于本机或当前部署实例，支持导出 Markdown；用户使用课程群、邮件、GitHub PR 等外部渠道分享，首期不提供平台内分享功能。
- 数据边界：不需要账号/身份系统；默认保存审查报告和必要的 Diff 摘要；用户能查看历史并主动删除报告；是否保存完整 Diff 留待安全设计确认，候选方向为“默认保存且可删除”或“配置为不保存原始 Diff”。

### 设计影响

- 移除身份认证、角色权限、团队协作、共享链接和协作评论模块，避免不必要的多租户数据隔离要求。
- 后续规约须提供本地/实例级报告历史、删除与 Markdown 导出，并明确原始 Diff 的保存策略及删除语义。

## 2026-08-05：Brainstorming 迭代 2 — Diff 输入、校验与拒绝边界（已确认）

### 智能体问题与建议

- 问题：首期支持怎样输入 Git Diff，以及单次限制为何；该决定影响上传安全、部署成本、LLM 上下文控制、性能与验收。
- 选项：A. 仅粘贴；B. 粘贴或上传 `.diff`/`.patch`；C. 增加 GitHub/GitLab URL 或仓库连接。
- 推荐：调整后的 B，允许本地 UTF-8 unified diff 的粘贴或单文件上传，并禁止远程仓库连接；限制为 500 KB 和 5,000 行，任一超出即拒绝。

### 用户决定与理由

- 用户选择调整后的 **B**：网页文本框粘贴 UTF-8 unified diff，或上传一个 UTF-8 编码的 `.diff` / `.patch` 文件。
- 每次输入同时受 500 KB 与 5,000 行限制；任一限制超出均拒绝，绝不静默截断，并提示用户拆分 Diff 后重新审查。
- 首期明确不支持 GitHub PR URL、GitLab MR URL、OAuth/仓库授权、远程仓库克隆或拉取、ZIP/二进制/压缩格式、一次多个文件和非 UTF-8 文件。
- 上传校验不得只看扩展名：还须校验实际大小、UTF-8 解码结果和 unified diff 基本结构。所有输入都是不可信文本，系统不得执行其中的代码或命令。
- 可解码但不符合 unified diff 基本结构的内容须返回“Diff 格式无效”，且不创建审查报告。

### 已确认的未来 SPEC 验收标准

1. 粘贴合法 Diff 能进入审查。
2. 上传合法 `.diff` 或 `.patch` 文件能进入审查。
3. 空输入、非 UTF-8、错误格式、超过 500 KB、超过 5,000 行均被拒绝。
4. 错误信息能区分格式错误、编码错误和大小超限。
5. 系统不访问远程仓库，且不执行 Diff 中任何内容。

### 设计影响

- 输入模块须有粘贴与单文件上传两个入口，并以“实际内容 + 字节数 + 行数 + 解码 + diff 结构”作为准入条件。
- 失败输入不得创建任何审查报告或历史记录；上述约束同时属于安全边界与客观验收标准。

## 2026-08-05：Brainstorming 迭代 3 — 支持语言、规则分层与降级行为（已确认）

### 智能体问题与建议

- 问题：首期对哪些语言提供语言感知风险规则；该决定影响规则库、Diff 解析、LLM 上下文、误判风险与验收范围。
- 选项：A. 仅 TypeScript/JavaScript；B. TypeScript/JavaScript 加 Python；C. 仅语言无关启发式。
- 推荐：A，优先在十天内把单一生态的规则深度与工程闭环做完整。

### 用户决定与理由

- 用户选择调整后的 **A**：语言专项规则仅支持 `.ts`、`.tsx`、`.js`、`.jsx`；原因是在十天内优先保证确定性规则深度、测试质量和工程闭环，而非维护多套不稳定规则。
- 规则分两层：
  1. **语言无关通用规则**：对所有文本文件运行，覆盖疑似凭据、TODO/FIXME/HACK、危险 Shell/数据库破坏性命令、单文件修改规模过大、可疑硬编码地址、Diff 基本结构和文件统计。
  2. **TypeScript/JavaScript 专项规则**：仅对支持扩展名运行，首期包括 `console.log`/`console.debug`、空 `catch` 或吞异常、`eval()`、`innerHTML`/`dangerouslySetInnerHTML`、明显未等待的异步调用、过度新增 `any`（低等级提示）、生产代码 `debugger`。
- Python、Java、Go、C/C++ 等不受语言专项支持的文件不导致整个 Diff 被拒绝：继续执行通用规则并可参与一次 LLM 补充评审；报告必须写明“该文件未启用语言专项确定性规则”，不得将未扫描表示为未发现风险，也不得套用 JavaScript 规则。
- 识别依据为 Diff 中的文件扩展名；无法识别时，仅运行通用规则并标记为 `unknown`。
- 首期明确不做 Python/Java 专项规则、完整 AST 或编译器级静态分析、ESLint/TypeScript Compiler 等外部工具执行、安装/执行用户依赖、运行用户代码。

### 已确认的能力矩阵与未来 SPEC 验收标准

| 文件类型 | 通用规则 | JS/TS 专项规则 | 单轮 AI 补充评审 | 必须显示的能力提示 |
| --- | --- | --- | --- | --- |
| `.ts`、`.tsx`、`.js`、`.jsx` | 是 | 是 | 是 | 已启用 JS/TS 专项规则 |
| 其他可识别文本扩展名 | 是 | 否 | 是 | 未启用语言专项确定性规则 |
| 扩展名无法识别 | 是 | 否 | 是 | `unknown`；未启用语言专项确定性规则 |

1. `.ts`、`.tsx`、`.js`、`.jsx` 能触发相应的语言专项规则。
2. JavaScript 专项规则不会应用到 `.py` 或 `.java`。
3. 不支持的语言仍可完成通用扫描并生成报告。
4. 报告区分“通用规则”“语言专项规则”“AI 评审”三种来源。
5. 不支持语言的界面提示清楚，且不得表示为完整语言审查。
6. 未来每条首期规则均须设计命中、不命中和边界条件测试；当前阶段未创建测试。

### 设计影响

- 后续 `SPEC.md` 须写入上述支持矩阵、扩展名识别、降级行为和“不支持不等于安全”的明确提示。
- 核心定位固定为：**JS/TS = 通用规则 + 语言专项规则 + AI 补充评审；其他语言 = 通用规则 + AI 补充评审 + 能力受限提示。**

## 2026-08-05：Brainstorming 迭代 4 — 确定性风险等级、去重与 AI 隔离（已确认）

### 智能体问题与建议

- 问题：风险评分方式；该决定影响规则等级、报告排序、确定性与 AI 结果的边界，以及可重复的验收标准。
- 选项：A. 透明等级汇总；B. 0–100 加权数值；C. 不给出总风险等级。
- 推荐：A，将每条确定性规则映射到固定等级，使用确定性聚合逻辑；AI 建议单独显示且不影响总等级。

### 用户决定与理由

- 用户选择 **A**，明确拒绝首期 0–100 数值分数，理由是权重缺乏依据时会造成“看起来精确但不可信”的结果。
- 固定规则严重性语义为：Critical = 凭据泄露、严重数据破坏或明显高危安全问题；High = 高风险安全接口、危险操作或可能造成严重故障；Medium = 异常处理、可靠性和明显可维护性风险；Low = 调试代码、TODO、一般代码质量提醒。
- 总等级只由去重后的确定性 Finding 计算：有任一 Critical → Critical；否则有任一 High → High；否则 Medium ≥ 3 → High；否则有任一 Medium → Medium；否则 Low ≥ 5 → Medium；否则有任一 Low → Low；否则 None。
- 多个 High 不得升级为 Critical；Critical 仅可由本身定义为 Critical 的确定性规则触发。None 必须显示“未发现确定性规则风险”，不得表示“代码安全”或“审查通过”。
- 重复 Finding 至少按规则编号、文件路径、新文件行号、命中内容或标准化命中位置判断；去重完成后再计数和聚合。
- AI Finding 可建议 Critical/High/Medium/Low，但仅影响 AI 分区内排序；不得改变确定性总等级、不得计入等级阈值、不得被表达为经确定性验证的事实。AI 调用失败不影响确定性结论生成。
- 报告固定分为确定性 Finding 与 AI Finding 两区；每区内按 Critical → High → Medium → Low，再按文件路径、行号、规则编号稳定排序。相同输入必须产生相同的确定性等级与排序。

### 已确认的未来 SPEC 验收标准

1. 无 Finding 为 None；仅有 Low 为 Low；5 个去重 Low 升级为 Medium。
2. 仅有 Medium 为 Medium；3 个去重 Medium 升级为 High；任一 High 为 High；任一 Critical 为 Critical。
3. 重复 Finding 不重复计数，多个 High 不升级为 Critical。
4. AI Finding 的数量或建议等级不改变确定性总等级。
5. 相同输入重复分析得到相同的确定性等级与排序。
6. 当前阶段未创建上述验收测试；它们仅是未来 SPEC/PLAN 的真实待实现要求。

### 设计影响

- 后续 `SPEC.md` 须把等级定义、去重标识、聚合顺序、稳定排序和 AI 隔离写成可执行前的精确规约。
- UI/导出报告不得使用“安全”“通过”等超出确定性规则结论的措辞。

## 2026-08-05：Brainstorming 迭代 5 — 单一 LLM Provider 与 AI 失败降级（已确认）

### 智能体问题与建议

- 问题：首期 LLM Provider 范围与调用失败降级；该决定影响凭据治理、部署边界、数据外发和报告生命周期。
- 选项：A. 仅 OpenAI 官方 API；B. 可配置 OpenAI-compatible endpoint；C. 多个原生 Provider 并自动切换。
- 推荐：A，确定性扫描先完成并持久化；AI 失败只影响 AI 分区，不阻断报告，不自动重试或切换 Provider。

### 用户决定与理由

- 用户选择 **A**：真实 LLM Provider 仅为 `OpenAIReviewProvider`，后端通过 OpenAI 官方 SDK 调用官方 API，前端不得直接调用 OpenAI。
- `MockReviewProvider` 保留给自动化测试、CI、离线开发与明确标记的演示模式；它不构成面向用户的第二真实 Provider，也不得冒充真实 OpenAI 调用。
- 首期拒绝自定义 Base URL、OpenAI-compatible 第三方接口、Anthropic、Gemini、其他 Provider、自动 Provider 切换、本地模型、用户输入任意远程 endpoint；范围收窄理由是避免多套认证、协议、错误处理和成本治理。
- 用户配置自己的 OpenAI API key 与一个可更新的模型标识；模型不可写死为唯一型号，Base URL 不可修改。后端应把无效或无权限模型映射为公开、明确错误。
- Key 仅在后端使用，不返回前端、不写日志、不进入 Git/fixture/截图；状态展示只能是已配置/未配置与脱敏尾号。用户要求使用加密保险箱保存，但具体保险箱技术方案尚未在此前迭代确定，保留为下一项待决设计问题。

### 报告与 AI 状态机

固定顺序：校验/解析 Diff → 执行确定性规则 → 计算确定性总等级 → 持久化确定性报告 → 仅尝试一次 AI 补充评审 → 成功则追加 AI Finding，失败则保留确定性报告并写入 AI 状态。

| AI 状态 | 含义 |
| --- | --- |
| `NOT_CONFIGURED` | 未配置 API key |
| `PENDING` | 正在请求 |
| `SUCCEEDED` | 评审成功 |
| `AUTH_FAILED` | key 无效或无权限 |
| `MODEL_UNAVAILABLE` | 模型不存在或当前账户不可用 |
| `RATE_LIMITED` | 速率或额度限制 |
| `TIMEOUT` | 请求超时 |
| `INPUT_TOO_LARGE` | AI 输入超限 |
| `INVALID_RESPONSE` | 返回值不符合结构化 schema |
| `PROVIDER_UNAVAILABLE` | 上游服务或网络不可用 |

- 前端仅显示分类、脱敏后的公开原因；不得展示原始上游响应、完整请求、堆栈、可能含敏感内容的错误正文或 key。
- 任一 AI 失败（未配置、认证、模型、超时、限流、网络、非法 JSON、AI 输入过大）均不得使整个审查失败、丢弃确定性报告、静默截断 Diff、自动切换 Provider 或无限重试。
- 报告详情页允许用户手动“重新发起 AI 评审”；只重跑 AI 部分，更新同一报告的 AI 分区，不重复创建报告或执行确定性扫描；同一时刻仅允许一个 AI 重试任务。

### 数据外发与 Prompt Injection 边界

- 发送给 OpenAI 的内容限于评审所需的 Diff 或受控摘要、文件路径、确定性规则摘要和结构化输出要求；禁止发送其他本机文件、完整仓库、Git 历史、环境变量、API key、本地绝对路径或其他报告。
- 若选择 Responses API，用户要求显式设置 `store=false`、不使用后台模式，并在隐私说明中告知用户代码变更内容会发送给 OpenAI。
- Diff 内的注释、字符串和文本均为不可信待审查数据，不能被作为系统指令；模型只能返回指定 schema，不得调用工具或要求执行命令。
- 输出必须经过 Pydantic/JSON Schema 校验；校验失败为 `INVALID_RESPONSE`，不得直接展示未经验证的原始输出。

### 已确认的未来 SPEC 验收标准

1. 未配置 key、认证失败、超时、限流、网络失败、AI 输入过大或非法 JSON 时，仍生成完整确定性报告。
2. OpenAI 成功时仅向 AI 分区追加结构化 Finding；AI Finding 不改变确定性总等级。
3. 手动重试只更新同一报告的 AI 分区；重复点击不产生并发重复调用。
4. 前端与日志不出现完整 key；CI 只用 Mock Provider，不发真实网络请求；Mock 模式醒目标记。
5. 相同 Mock 输入得到可重复结果；当前阶段未创建上述测试或 CI 配置。

### 设计影响

- 后续 `SPEC.md` 的架构、安全、错误处理、隐私和验收章节须包含本轮 Provider 边界、状态机、最小数据外发与降级语义。
- 具体的安全凭据保险箱、录入/更新/清除流程和部署密钥注入方式仍是未决问题，不能因本轮决定而视为已设计完成。

## 2026-08-05：Brainstorming 迭代 6 — 凭据保险箱与受限管理入口（已确认）

### 智能体问题与建议

- 问题：单用户自托管环境的 API key 安全存储和管理方式；这决定课程 §3.1 所需的安全存储、录入、更新、清除与公网 WebUI 的攻击面。
- 选项：A. 跨平台加密保险箱文件与管理员主密码；B. 操作系统钥匙串；C. 云 KMS/Secret Manager。
- 推荐：A，跨 Windows、容器、无桌面 Linux 和云服务器一致；公网 WebUI 不提供凭据管理，服务器操作者仅从本机受限入口管理。

### 用户决定与理由

- 用户选择 **A**，理由是它属于课程认可的带主密码加密文件，并避免操作系统钥匙串的容器/无桌面兼容性问题和云 KMS 的平台绑定。
- 最关键的安全边界：**公开 WebUI 只负责审查；真实 API key 只能由服务器操作者通过本机受限入口管理。**

### 加密保险箱规约

- 保险箱位置示例为 `data/credentials/vault.json`，位于部署实例私有数据目录。它只能保存格式版本、KDF 参数、随机 salt、随机 nonce、密文、认证标签和非敏感状态信息；禁止保存明文 key、管理员主密码、可还原主密码的信息、解密后 key、完整 key 的日志或缓存。
- 使用成熟密码学库，不自行设计算法：主密码以 scrypt 或 Argon2id 派生密钥，API key 以 AES-256-GCM 等带认证加密算法加密；每次创建或更新必须生成新的随机 salt 和 nonce。
- 首次启动无保险箱时，应用可执行确定性扫描且 AI 状态为 `NOT_CONFIGURED`。操作者从回环管理入口设置并确认主密码、以隐藏输入录入 API key、可选录入模型标识；成功后仅显示已配置状态与脱敏尾号。
- 保存采用临时文件后原子替换，初始化失败不得留下部分写入或损坏的保险箱。

### 管理入口、解锁与生命周期

- API key 管理接口只能通过 `127.0.0.1`、`::1` 或 Unix socket 等本机访问方式访问；不得绑定 `0.0.0.0`、经公网反向代理开放、依赖隐藏 URL，或通过公开 API 上传/读取 key。云服务器管理经临时 SSH 端口转发到服务器 localhost。
- 服务启动默认锁定。锁定时确定性审查仍工作，AI 分区显示“凭据保险箱未解锁”；正确主密码解锁后，解密 key 只存在进程内存，绝不落盘、入库、入日志或缓存。服务重启后必须重新解锁；操作者可主动锁定以立即清除内存 key；首期没有“记住我”或主密码自动保存。
- 管理功能包括查看状态、解锁、更新 API key、更新模型标识、清除凭据、主动锁定。状态只能返回保险箱是否存在、是否解锁、Provider、模型标识和脱敏尾号；更新/清除前必须再次验证主密码。
- 清除必须删除保险箱、清除内存 key 并将 AI 状态恢复为 `NOT_CONFIGURED`，但不得删除已存在的确定性报告。

### 凭据威胁模型与对策

| 威胁 | 已确认对策 |
| --- | --- |
| 仓库、镜像、fixture 或日志泄露 key | 保险箱位于 Git 忽略的私有数据目录；不得进入镜像、fixture、截图、日志或响应；CI 仅用 Mock/测试密文 |
| 公开 WebUI 被访问者滥用以读取或设置 key | 凭据管理仅绑定回环/Unix socket；不得经公网暴露；远程操作经 SSH 端口转发 |
| 磁盘或 Volume 被读取 | 使用主密码派生密钥与认证加密；禁止明文或可还原主密码 |
| 内存凭据在不需要时暴露 | 默认锁定；仅在进程内存保存；可主动锁定并在重启时清除 |
| 暴力猜测、密文损坏或认证标签错误泄露信息 | KDF 增强猜测成本；统一“解锁失败”响应；递增短延迟；不输出底层密码学异常 |
| 保险箱损坏导致不安全回退 | 不读取明文或不安全模式；AI 保持不可用，确定性扫描继续；提示操作者清除并重建 |
| 容器持久化与文件权限不当 | 保险箱经 Docker Volume 持久化、不进入镜像；Linux 尽可能仅服务用户读写；README 说明 Windows/Linux 权限差异 |

### 公网演示与未来 SPEC 验收标准

- 公网演示模式默认使用醒目标识的 `MockReviewProvider`，不存储真实 OpenAI key、不开放凭据管理，也不得把 Mock 结果冒充真实 AI。
- 仓库仅提供 `.env.example`；不提供真实 `.env`，`.env` 也不是长期凭据存储首选。
- 未来验收至少覆盖首次隐藏输入创建、保险箱不含明文 key/主密码、正确/错误主密码、脱敏状态、更新使旧 key 不可用、清除、重启再锁定、锁定时确定性扫描、全链路无完整 key、外网不可访问管理入口、Volume 删除后的凭据消失，以及 CI 不用真实 key。当前阶段未创建测试、Docker 或 CI。

### 设计影响

- 后续 `SPEC.md` 的安全、凭据管理、部署、README 与验收章节须采用此方案，并明确拒绝操作系统钥匙串与云 KMS 的原因。
- 数据保留范围尚未完成决定：尤其是完整 Diff 是否默认保存、保存期限与报告删除的级联语义，保留为下一项问题。

## 2026-08-05：Brainstorming 迭代 7 — 数据最小化、摘要重试与硬删除（已确认）

### 智能体问题与建议

- 问题：原始 Diff、报告和 AI 重试数据的保留与删除策略。它直接影响“同一报告只重试 AI”的实现方式与代码变更数据的长期暴露风险。
- 选项：A. 不持久化原始 Diff，重试时重交并比对摘要；B. 加密持久化完整 Diff；C. 每报告选择是否持久化完整 Diff。
- 推荐：A。报告保存至手动删除，完整 Diff 仅本次内存使用；AI 重试要求重交相同摘要的 Diff，从而不重新执行确定性扫描。

### 用户决定与理由

- 用户选择 **A**，最终数据边界为：完整 Diff 仅单次请求内存短暂使用；报告与 Finding 保存至用户删除；Diff 摘要随报告保存以校验重试；重试只更新同一报告的 AI 分区；删除报告时硬删除全部关联数据。
- B 被拒绝，因为随报告长期保存完整代码变更扩大敏感数据范围并要求额外加密/解锁设计；C 被拒绝，因为逐报告存储开关增加交互、状态和验收复杂度。
- 原始 Diff 仅可在输入校验、解析、确定性扫描、首次 AI 补充评审和生成结构化报告期间存在于进程内存；请求完成后及时释放引用。不得写入数据库、普通文件、日志、缓存、错误响应、测试输出、埋点、镜像或备份。
- 运行环境不能保证可靠内存清零；规约应如实表述为避免持久化、避免复制、禁止日志并尽快释放引用，不能声称实现内存安全擦除。

### Diff 摘要规范与 AI 重试

- 摘要不是“加密哈希”，不可恢复原始内容，仅用于确认重试输入相同。
- 固定计算方法：确认 UTF-8 → 去除可选 UTF-8 BOM → 将 CRLF 与 CR 统一为 LF → 不删除行内空格或任意裁剪内容 → 对规范化后的 UTF-8 字节计算 SHA-256 → 保存十六进制摘要。相同内容在 Windows/Linux 换行差异下必须得出相同摘要。
- 用户点击 AI 重试后须重新粘贴或上传原始 Diff；后端以相同方法计算摘要。相等时仅重跑 AI、更新原报告 AI 分区，不新建报告、不重跑确定性规则；不等时拒绝并显示“提交内容与原报告不一致”。不得以文件名、文件数或行数近似判断相同。
- 同一报告最多一个 `PENDING` AI 尝试；重复点击须拒绝或复用当前任务，不可产生并发重复计费。

### 持久化、导出与删除规则

- 报告可保存 ID、创建/更新时间、Diff 摘要、文件路径/类型/增删行数/文件数、确定性 Finding/总等级、Schema 校验后的 AI Finding 与状态、Provider/模型标识、AI 尝试的时间/次数/公开错误分类、prompt 和 schema 版本。不得保存完整 Diff、完整 prompt、原始 OpenAI 响应、未经校验输出、API key、上游错误正文或堆栈。
- 每次 AI 调用只保存最小化 `AIReviewAttempt` 元数据：尝试编号、报告 ID、状态、Provider、模型标识、开始/完成时间、公开错误码、prompt 模板版本、输出 schema 版本。报告仅展示最新有效结构化 AI Finding；历史失败只保留最小元数据。
- 报告保留至用户主动删除；首期不做自动过期任务。删除为硬删除，级联移除报告、文件统计、确定性/AI Finding、AI 尝试、Diff 摘要和关联导出缓存；提供“清空全部报告”且须二次确认。
- 删除不影响用户已下载或外部分享的 Markdown，也无法删除 LLM Provider 侧可能存在的数据；README 与隐私说明须明确。
- Markdown 默认只含统计、确定性结论/规则 Finding、AI Finding、支持范围/能力限制，不含完整 Diff。首轮页面可显示当前请求必要代码片段，但不得将完整 Diff 暗中保存为导出缓存。

### 已确认的未来 SPEC 验收标准

1. 数据库、数据目录、日志与错误响应均无完整原始 Diff；首次审查仍能完成。
2. 同一 Diff 重交可仅重试 AI；CRLF 与 LF 版本摘要相同；有效内容变化导致摘要不一致，且不得更新原报告。
3. AI 重试不重跑确定性规则、不创建第二份报告，且同报告不并发执行两次 AI。
4. 删除报告后关联 Finding、摘要、尝试记录和导出缓存均不存在；清空全部报告须二次确认。
5. 导出不包含系统未持久化的完整 Diff；测试只能使用虚构 Diff。当前阶段未创建测试。

### 设计影响

- 后续 `SPEC.md` 的数据模型、安全、生命周期、错误处理、隐私说明与验收章节须采用此摘要规范、重试流程和硬删除规则。
- 公网演示在无账号模型下如何隔离输入与报告仍未决定，是下一项待澄清问题。

## 2026-08-05：Brainstorming 迭代 8 — 公网无状态 Mock 演示与私有实例隔离（已确认）

### 智能体问题与建议

- 问题：满足课程公网 WebUI 要求时，公开演示在无账号体系下如何避免访客互见数据、真实 key 暴露和 API 成本滥用。
- 选项：A. 无状态 Mock 演示；B. 匿名标识的短期持久化公开实例；C. 对公网开放真实 OpenAI。
- 推荐：A，公开 URL 与私有实例独立部署，演示使用 Mock、无历史、无凭据入口、无服务端持久化且限流。

### 用户决定与理由

- 用户选择 **A**：公网 WebUI 展示完整交互、确定性扫描和结构化 AI 分区，但不连接真实 OpenAI、不保存访客数据。
- B 被拒绝，因为匿名访客隔离、cookie、自动过期与隐私处理会扩大范围，并与首期不做自动过期任务冲突；C 被拒绝，因为会引入真实 key、成本滥用与访客代码外发风险。
- 公网与本地/私有真实实例必须独立部署，不共用数据库、数据目录、Docker Volume、保险箱、OpenAI 配置、报告历史或日志文件。技术名称可调整，但演示模式必须语义等价于 `APP_MODE=demo`、`REVIEW_PROVIDER=mock`、`PERSISTENCE_ENABLED=false`、`CREDENTIAL_MANAGEMENT_ENABLED=false`。

### 公网模式行为与禁用边界

- 公网用户可粘贴或上传合规 UTF-8 `.diff`/`.patch`，运行确定性扫描，查看统计、总等级、Finding 和 Mock AI 建议，筛选当前结果并导出当前 Markdown；继续执行 500 KB / 5,000 行限制、禁止远程仓库和禁止执行 Diff 内容。
- 公网模式禁止 OpenAI key 配置、保险箱所有操作、真实 OpenAI、自定义 Provider/Base URL、报告历史/永久链接、AI 手动重试、匿名用户标识、cookie 身份、跨页面恢复、服务端导出缓存与访客数据共享。
- 禁用管理 API 不能只隐藏前端按钮：必须不注册路由或返回明确禁用状态。
- 单次请求内存完成校验、解析、扫描和 Mock；只把完整结果返回当前浏览器，结束后不保存报告、摘要、Finding 或 AI 尝试。刷新/关闭/离开页面后丢失。不得写入数据库、文件系统、缓存、日志正文、分析埋点或临时导出目录。Markdown 由浏览器当前结果直接生成，或服务端即时返回但不落盘。

### Mock、限流与最小可观测性

- Mock 必须醒目标识：“当前为公开演示模式。AI 补充建议由确定性 Mock Provider 生成，不代表真实模型评审结果。”它使用与真实 Provider 相同的结构化 schema，不发网络请求、不需真实 key、对相同输入稳定可重复，并可展示预设错误降级；可以基于摘要、文件类型与确定性 Finding 生成固定模板，但绝不声称来自 OpenAI。
- 首期公网限流建议并获用户确认作为初始目标：每来源 IP 10 分钟最多 10 次审查、短时突发最多 3 次、实例限制并发审查数量；超限返回 HTTP 429 和可理解等待提示。具体数值允许在压测后调整，但必须写入配置与 README。
- 若经过 Nginx 等反向代理，仅信任已配置代理的转发头；不无条件信任客户端 `X-Forwarded-For`；限制请求体、超时和并发连接。首期不做验证码、账号封禁或复杂反滥用。
- 公网日志仅可记录请求时间、结果状态、输入大小区间、文件数、耗时、错误分类和限流次数；不得记录完整 Diff/代码片段、完整 IP 长期历史、key、原始请求或原始模型输出，也不得向用户返回未处理堆栈。README 须说明日志保留策略。

### 双运行模式矩阵与未来验收标准

| 能力 | 公网演示实例 | 私有自托管实例 |
| --- | --- | --- |
| 确定性扫描 | 支持 | 支持 |
| Mock AI | 支持 | 可用于测试/演示 |
| 真实 OpenAI | 禁止 | 保险箱解锁后支持 |
| 报告历史 | 不保存 | 保存至用户删除 |
| AI 重试 | 不支持 | 重交同摘要 Diff 后支持 |
| 凭据管理 | 禁止 | 仅本机受限入口 |

- 未来验收至少验证公网粘贴/上传、确定性扫描、合规 Mock、醒目演示标记、无 OpenAI 网络调用、无 key 管理/可用管理 API、请求后无持久化、刷新丢失结果、访客不可互见、日志无代码/完整 Diff、输入/限流拒绝、无导出缓存和独立配置/数据目录。当前阶段未实施或测试这些要求。

### 设计影响

- 后续 `SPEC.md` 的部署架构、数据生命周期、安全边界、限流、可观测性、README 和验收章节必须明确区分公网/私有运行模式。
- 首期“用户能否配置、忽略或抑制规则 Finding”等产品范围尚未决定，是下一项待澄清问题。

## 2026-08-05：Brainstorming 迭代 9 — 固定规则集、筛选边界与版本追溯（已确认）

### 智能体问题与建议

- 问题：首期是否允许规则配置、关闭、忽略/豁免 Finding；它影响规则集可复现性、配置持久化、报告语义和测试矩阵。
- 选项：A. 固定内置规则；B. 部署操作者可开关/改等级；C. 自定义正则、忽略和豁免。
- 推荐：A。仅提供显示筛选和导出，规则、等级、聚合保持固定，以缩小范围并确保可重复结论。

### 用户决定与理由

- 用户选择 **A**：所有确定性规则内置并固定规则编号、名称、适用文件类型、检测逻辑、严重等级、问题说明、修复建议和通用/语言专项分类。
- 用户与部署操作者均不能通过 WebUI、配置、环境变量或 API 关闭规则、改等级、加规则、改正则、忽略/豁免 Finding 或改聚合算法。
- B 被拒绝，因为会引入配置存储/版本、报告可追溯与同一 Diff 得到不同结论的问题；C 被拒绝，因为自定义规则、豁免审计、正则性能/安全和复杂 UI 超出首期。

### 允许操作与误报边界

- 仅允许按严重等级、文件路径、来源（通用规则/语言专项规则/AI 建议）筛选当前显示，展开/收起 Finding，以及导出完整报告。
- 筛选只影响页面显示，不影响已保存 Finding、确定性总等级、数量统计或 Markdown 导出；导出必须包括全部 Finding，不得因页面隐藏而遗漏。
- 首期无忽略按钮。用户认为误报时，页面说明固定规则是机械判断，用户自行结合上下文；README 记录已知限制，开发阶段以真实误报改进，规则只能随新应用版本发布。AI 可补充上下文但不得否定、删除或覆盖确定性 Finding。

### 版本与双模式一致性

- 每份报告保存 `ruleset_version`、应用版本、每条 Finding 的规则编号和规则版本。首期可用统一 `ruleset_version = "1.0.0"`；规则逻辑、等级或聚合有实质变化时必须更新 ruleset 版本。
- 历史报告保留生成时原始结果，升级后不得自动重算。
- 公网 Mock 与私有自托管实例必须使用相同规则集、等级、去重和聚合算法；两者仅可在持久化、真实 OpenAI、凭据管理和 AI 重试方面不同。
- 确定性等级说明固定为“基于 ReviewLens 固定规则集计算；筛选不会改变报告结论”。

### 已确认的未来 SPEC 验收标准

1. 相同 ruleset 和 Diff 的确定性结果相同；网页/API 不能关规则或改等级。
2. 筛选不改变等级、数据库 Finding 或导出；AI 不可删除/覆盖确定性 Finding。
3. 公网和私有实例对相同 Diff 的确定性结果一致；报告保存对应 ruleset 版本，应用升级不改变历史结果。
4. 每条规则均需设计命中、不命中和边界条件测试；当前阶段未创建测试。

### 设计影响

- 后续 `SPEC.md` 的规则引擎、报告模型、版本管理、README 已知限制和验收章节须纳入固定规则集原则。
- 系统的编程语言、前后端、持久化和部署技术选型尚未决定，是下一项待澄清问题。

## 2026-08-05：Brainstorming 迭代 10 — 技术选型、双模式架构与持久化边界（已确认）

### 智能体问题与建议

- 问题：首期前后端与本地持久化技术栈；它决定 Pydantic schema 校验、保险箱、SQLite 数据、双运行模式、TDD task 拆分和 Open Design 记录。
- 选项：A. Python FastAPI/Pydantic/SQLite + React/TypeScript；B. TypeScript 全栈；C. Next.js 全栈。
- 推荐：A，因为它与用户已指定的 Pydantic、单用户 SQLite 和独立管理入口最一致，前后端可信边界清楚。

### 用户决定与理由

- 用户选择 **A**：Python 3.12、FastAPI、Pydantic v2、SQLAlchemy 2、Alembic、SQLite、pytest、pytest-cov、cryptography、OpenAI 官方 Python SDK，以及仅确有需要时的 httpx；前端为 React、TypeScript、Vite、MUI、React Router、Axios 或原生 fetch（二者最终只选一项）、Vitest、React Testing Library；UI 由 Open Design 辅助设计并在 SPEC 记录。
- B 被拒绝，因为它要以 Zod/JSON Schema 替代已明确的 Pydantic 方向；C 被拒绝，因为全栈耦合会模糊公开演示、私有管理入口与回环监听的安全边界。
- 不采用 Django、Flask、PostgreSQL/MySQL、Redis、Celery、消息队列、LangChain/AutoGen/CrewAI 等 Agent 框架、后台自主 Agent、用户代码执行环境、Next.js/SSR、Redux（除非有明确局部状态无法解决的问题）、复杂图表库、WebSocket、微前端或多套 UI 框架。

### 前后端职责与运行模式

- 前端仅处理 Diff/文件选择、即时 UX 提示、后端调用、当前报告展示与筛选、Markdown 下载、私有历史页面和本机受限管理界面；前端校验不能替代后端校验，也不得直接访问 OpenAI。
- 后端负责权威输入校验、UTF-8 解码、Diff 解析、规则扫描、去重/等级、OpenAI 调用、Pydantic schema、持久化、保险箱、限流、日志脱敏和模式安全边界。
- 私有实例以 SQLite 保存报告、文件统计、确定性/AI Finding、最小 AI 尝试元数据、Diff SHA-256、ruleset 与应用版本及时间戳；完整 Diff 不入 SQLite。数据访问必须通过明确 Repository 接口，服务层不得散落 SQL。
- 公网演示不写 SQLite；按模式采用如 `SqliteReportRepository` 与 `NoopReportRepository`/请求级内存实现。后端而非仅前端必须禁用持久化、凭据路由和真实 Provider。
- 普通审查与本机管理 API 结构分离；不必拆为两个后端应用，但必须有独立 Router、配置开关、端口或监听策略。凭据管理仅回环地址，云端经 SSH 隧道，不能复用公开审查 API 的暴露方式。

### 仅供未来 SPEC/PLAN 的目录、测试与分发设计

- 可在 SPEC/PLAN 规划但当前不能创建的目录为 `apps/api/app/{api,config,diff_parser,rules,reviews,providers,credentials,persistence,observability}`、`apps/api/tests`、`apps/web/src/{api,components,pages,features,types}`、`apps/web/tests`。
- 后端未来测试重点是 Diff/规则/去重/聚合/AI schema 与降级/保险箱/摘要重试/双模式/脱敏/级联删除；前端未来测试重点是输入、提示、分区、筛选、Mock 标记、AI 状态、私有历史和演示模式禁用。CI 只能使用临时 SQLite 与 Mock，不使用真实 key 或 OpenAI 网络。
- 根目录未来统一命令为 `make install`、`make test`、`make lint`、`make build`、`make up`、`make down`；未来 Docker Compose 要区分私有自托管与公网演示，且不拆微服务或独立数据库容器。当前均只是计划，未创建 Makefile、Docker 或 CI。
- SPEC 只记录主要技术栈与版本策略；确切依赖版本在实现 task 中按当时稳定版本锁定。Python 使用锁文件，Node 提交 lockfile，基础镜像指定明确标签，CI/本地统一主要运行时版本；禁止无版本约束或“永远最新”的承诺。

### 已确认的未来 SPEC 验收标准

1. 后端请求/响应通过 Pydantic；非法 AI 输出不能进入正式报告；前端不直连 OpenAI。
2. 私有 SQLite 持久化报告但不含完整 Diff；演示模式不持久化且无凭据路由；两模式共用相同确定性规则。
3. 私有重启后历史仍在而保险箱重新锁定；演示刷新/重启后访客报告不可恢复。
4. 根目录一键测试命令、双模式 Docker 启动与各层测试是未来实现验收，不是当前阶段的完成声明。

### 设计影响

- 后续 `SPEC.md` 的技术选型、架构、数据模型、测试、分发和 Open Design 章节须采用本轮选择。
- 性能、可用性和可观测性的客观指标尚未决定，是下一项待澄清问题。

## 2026-08-05：Brainstorming 迭代 11 — 可验证的性能、可用性与可观测性目标（已确认）

### 智能体问题与建议

- 问题：首期应承诺怎样可重复验证的性能、可用性和可观测性指标；它决定同步处理、AI 超时、健康检查、日志和部署资源预算。
- 选项：A. 平衡的单机目标；B. 激进低延迟与高并发；C. 只验功能不设指标。
- 推荐：A，在明确单机基线上验收确定性/Mock 5 秒和 AI 30 秒降级，不承诺高并发或互联网级可用率。

### 用户决定与理由

- 用户选择 **A**：它适配单用户自托管、500 KB/5,000 行限制、公开无状态 Mock 和十天周期；所有目标须能测试或部署检查验证，不能对未测环境虚称达标。
- B 被拒绝，因为会引入额外优化、压测和调优；C 被拒绝，因为不能提供 SPEC 所需性能、可用性和可观测性的客观验收。

### 性能、并发与恢复性指标

- 基线：2 vCPU、4 GB RAM、Python 3.12、本地 SQLite、单实例；测试输入不超过上限，真实 OpenAI 网络等待不计入确定性指标。开发机/CI 不同必须记录实际环境。
- 对合法 Diff，校验、规范化、解析/统计、通用与 JS/TS 规则、去重、等级计算和私有报告持久化合计 5 秒内完成。以小型、多文件中型、近上限、多规则命中虚构 Diff 验收；预热后连续 10 次至少 9 次不超过 5 秒，不可用偶发冷启动代替稳定测量。
- 真实 AI 单次请求 30 秒超时；超时为 `TIMEOUT`，保留确定性报告，显示 AI 不可用且不自动无限重试。系统不承诺 OpenAI 固定返回时间。
- 公网 Mock 从合法提交到完整确定性+Mock 结果 5 秒内返回；无外网、不模拟人为延迟、相同输入稳定；限流/超限请求尽早拒绝。
- 首期只承诺私有实例稳定处理一个活动审查请求，公网设置明确并发上限，繁忙/超限返回明确响应，不无限积压；失败请求不使进程退出，超限输入不导致明显内存失控。不承诺 QPS、互联网级吞吐或大型团队并发。
- 私有模式 AI 失败不影响报告、重启后报告存在而保险箱锁定；SQLite 写失败给出明确错误且不留下半完整报告，报告与关联 Finding 具事务边界；保险箱更新仍采用临时文件/原子替换。演示模式刷新后无恢复。

### 健康检查、日志与错误边界

- 提供未来 `/health`（仅进程存活，不依赖 OpenAI）和 `/ready`（配置、私有数据库、规则集等本地必要依赖就绪）端点。未配置 OpenAI、保险箱锁定或 Provider 暂不可用不得让确定性服务整体不健康；Provider 状态单列。响应不含 key、数据库路径、完整配置、完整堆栈。
- 使用脱敏结构化日志：时间戳、请求关联 ID、模式、接口、HTTP 状态、输入大小区间、文件数、确定性/AI 耗时、AI 状态、公开错误分类、限流标记、ruleset 与应用版本。禁止完整 Diff/代码片段、key、主密码、完整 prompt/原始响应、未脱敏上游错误和浏览器可见堆栈。
- 稳定错误代码至少包括 `INPUT_EMPTY`、`INPUT_TOO_LARGE`、`LINE_LIMIT_EXCEEDED`、`INVALID_UTF8`、`INVALID_DIFF_FORMAT`、`RATE_LIMITED`、`AI_NOT_CONFIGURED`、`AI_TIMEOUT`、`AI_AUTH_FAILED`、`AI_INVALID_RESPONSE`、`INTERNAL_ERROR`；前端显示可操作中文提示，并可用关联 ID 对照日志。

### UI 可用性与首期非承诺

- 核心输入、提交、筛选、导出可键盘完成；交互元素有焦点，控件有标签，等级不只依赖颜色；不同输入/格式/限流错误有不同提示；加载禁重复提交，AI 失败不遮挡确定性报告，Mock 标识和不支持语言能力限制持续可见，删除/清空二次确认，常见桌面尺寸无关键遮挡。
- 桌面 Web 优先，窄窗口不应完全不可用，但不承诺完整移动体验。
- 首期不承诺 99.9% 可用率、多区域容灾、自动扩缩容、大并发、分布式追踪平台、Prometheus/Grafana、最大 Diff 1 秒、真实 OpenAI 固定时间或完整移动端。

### 已确认的未来 SPEC 验收标准

1. 近上限 Diff 达到确定性时间目标；Mock 达到 5 秒；真实 AI 到 30 秒正确降级且不影响确定性报告。
2. `/health`/`/ready` 正确区分存活与就绪，OpenAI 未配置时确定性服务仍可用。
3. 日志含关联 ID、耗时、分类但无 Diff、key、主密码或完整 prompt；预期错误有稳定代码与可读提示。
4. 关键键盘流程可操作、等级文字可见、重复提交受阻、SQLite 写失败不留半完整报告、私有/演示恢复行为符合约定。
5. 当前阶段未创建性能测试、健康端点、日志或部署检查；这些是未来验收而非完成声明。

### 设计影响

- 后续 `SPEC.md` 的非功能、可观测性、错误处理、可用性与验收章节须采用本轮指标。
- 首期规则目录中哪些候选规则实际进入固定 `ruleset_version=1.0.0` 尚未确认，是下一项待澄清问题。

## 2026-08-05：Brainstorming 迭代 12 — 新增行归因、上下文与新文件行号（已确认）

### 智能体问题与建议

- 问题：确定性规则扫描 Diff 的哪些行；它决定 Finding 是否代表“本次变更引入的风险”、行号语义、去重和报告措辞。
- 选项：A. 仅新增行，结构/规模规则用完整元数据；B. 新增+上下文；C. 所有可见内容包括删除行。
- 推荐：A，代码 Finding 必须归因于新增代码；规则可读取受限上下文帮助解释，但不能因旧代码独立告警。

### 用户决定与理由

- 用户选择 **A**：统一 Diff 中以 `+` 开头且不是 `+++` 文件头的新增代码行，才可触发通用/JS/TS 代码风险规则。这符合“审查本次变更引入的风险”的定位。
- B 被拒绝，因为会把既有问题归入本次提交；C 被拒绝，因为会把被删除的问题误报为风险。
- 新增文件、已有文件修改 hunk、重命名后的目标文件新增代码均扫描；删除行、未改上下文、Diff 头、被删除的问题、二进制内容和不可解析文本均不得产生代码 Finding。

### 上下文、完整元数据与行号语义

- 规则可读取当前 hunk 有限上下文与相邻新增行，以理解多行 `catch`、异步等待、`dangerouslySetInnerHTML` 属性或注释/字符串语境；上下文只解释新增代码，不计入命中数量。若不能可靠归因到新增行，首期放弃 Finding。
- Diff 合法性、文件数、增删行数、单文件规模、新建/删除/重命名、类型识别、输入大小/行数、二进制提示使用完整 Diff 元数据。规模类 Finding 为 `file-level`，行号为 `null`，不得伪造代码行号。
- 代码 Finding 使用目标文件新行号：hunk 中的新增行按新文件行号计算，不使用 Diff 物理行或旧文件行；新文件从目标第 1 行计，重命名用目标路径。
- 每条 Finding 至少含规则编号、目标路径、新文件行号或 `null`、等级、命中新增片段、说明、修复建议、规则来源和 ruleset 版本。

### 去重、删除与报告/AI 边界

- 代码 Finding 去重键至少为规则编号、目标路径、新文件行号、标准化命中内容或范围；文件级为规则编号、目标路径、Finding 类型。同一新增语句不能因读取多条上下文重复报告。
- 删除行只用于删除统计、hunk 行号、结构理解、文件删除判断与摘要；即使含 key、`eval()`、调试、危险命令或 TODO 也不得告警。
- 确定性报告必须说明“主要检查本次 Diff 新增代码，不代表完整仓库或既有代码的全面安全审计”。None 显示“未在本次新增代码中发现确定性规则风险”，禁止“代码完全安全”“仓库没有风险”“审查通过”等措辞。
- AI 可接收必要新增、删除和上下文理解变更意图，Finding 优先归因新增代码；AI 上下文发现不改变确定性总等级，也不得称已删除问题仍存在。

### 已确认的未来 SPEC 验收标准

1. 新增敏感内容触发；同内容仅在上下文/删除行时不触发；`+++` 文件头不被误判。
2. 新文件扫描，删除文件不产代码风险；文件规模规则用完整增删统计且行号 `null`。
3. 多行规则可读上下文但锚定新增新文件行；纯旧上下文不产生 Finding；同一新增语句不会重复。
4. 报告有明确的新增代码范围声明。当前阶段未创建相关测试。

### 设计影响

- 后续 `SPEC.md` 的 Diff 解析、规则引擎、行号、去重、AI 边界与验收章节须采用此归因模型。
- 接下来不再拆分微问题；待把固定 ruleset 目录、显式不做项和客观验收汇总为一次设计总确认后，才可生成最终 SPEC。

## 2026-08-05：设计基线修订 — 双仓库、容器分发与开发过程（待最终签字）

### 用户确认的课程基础设施策略

- 不再把 GitHub Actions 视为“仅有 GitHub 镜像时的可选补充”。为同时覆盖课程文件的 GitHub 与 NJU GitLab 要求，项目采用**双仓库策略**：GitHub 是公开主开发/展示仓库，保留完整分支、commit、Pull Request 与评审历史；NJU GitLab 保存相同代码与 commit 历史，作为课程最终提交仓库。
- 未来 GitHub Actions 在每次 push 或 PR 自动运行测试；未来 `.gitlab-ci.yml` 必含名为 `unit-test` 的 job。最终提交前，GitHub Actions 与 NJU GitLab Pipeline 均须为 Pass。
- README 后续须注明两个仓库的用途与真实链接。当前尚无仓库 URL、Pipeline、Actions 或执行记录，绝不创建占位链接、伪造状态或宣称通过。
- 同步具体机制、远程地址和是否由同一 bare history 推送，属于实施计划细节；不改变“双仓库、相同 commit 历史”的确认目标。

### 用户确认的分发设计

- 首期选择 Docker/OCI 容器分发。未来提供后端和前端 Dockerfile，或经实现计划确认的统一生产镜像；提供 Docker Compose，并区分私有自托管与公网无状态 Demo 模式。
- SQLite 与凭据保险箱经私有 Volume 持久化，绝不进入镜像；版本化镜像推送到公开 Registry，优先 GitHub Container Registry。
- README 后续必须说明镜像获取、构建/运行、Volume、端口、私有模式 key 安全配置、Demo 模式、目标平台与已知限制；未来必须在全新目录或全新环境验证从零启动。
- 上述 Docker、Compose、镜像、Registry 推送和全新环境验证均未创建或执行，当前只是明确的未来交付/验收目标。

### 用户确认的开发过程基线

- 实现阶段依次遵循 `using-git-worktrees`、`subagent-driven-development`、严格 RED–GREEN–REFACTOR TDD、每 task 的 spec compliance review 后 code quality review、`finishing-a-development-branch`。
- 每主要模块对应独立分支、worktree 和 PR/MR；Critical 问题修复前不能继续。每个 task 完成后在 `PLAN.md` 回填真实 commit hash；`AGENT_LOG.md` 记录 skill、prompt/context、RED/GREEN 证据、评审、人工干预和 commit。
- 禁止伪造测试、CI、PR/MR、部署或冷启动证据。当前阶段不创建 worktree、subagent 实现任务、测试、评审、CI 或部署。

### 待最终签字设计基线（合并版）

1. **产品和范围**：ReviewLens 面向个人学生开发者的单用户自托管 Git Diff 风险审查工具；Markdown 由用户外部共享；无账号、多用户、在线分享、远程仓库/OAuth 或自主 Agent。
2. **输入与解析**：粘贴或单个 UTF-8 `.diff`/`.patch`，500 KB/5,000 行上限，格式/编码/上限错误拒绝；不执行或拉取用户内容。确定性代码规则只对新增行告警，可读有限上下文但 Finding 必锚定新文件行；结构/规模规则用完整 Diff 元数据。
3. **固定规则与报告**：固定、版本化 ruleset；通用规则及 JS/TS 专项规则，其他语言仅通用规则+AI+能力受限提示。用户只能筛选/导出，不能改规则、等级、聚合或豁免。确定性风险与 AI 建议严格分区。
4. **风险和 AI**：确定性 Critical/High/Medium/Low/None 等级、去重、固定聚合和稳定排序；AI 不改变总等级。真实 Provider 仅 OpenAI，失败保留确定性报告；手动 AI 重试重交同摘要 Diff，仅更新同一报告的 AI 分区。
5. **数据与安全**：不保存完整 Diff；规范化 SHA-256 摘要用于重试；报告与最小 AI 元数据保存至硬删除。API key 使用主密码加密保险箱，回环/SSH 本机管理，默认锁定；公开 WebUI 永不管理真实 key。
6. **双运行模式**：私有模式为 SQLite 历史 + 可选真实 OpenAI；独立公网 Demo 为无状态、Mock、限流、无凭据、无报告恢复。两模式确定性规则结果相同。
7. **技术与质量**：Python/FastAPI/Pydantic/SQLAlchemy/Alembic/SQLite 后端，React/TypeScript/Vite/MUI/Open Design 前端；2 vCPU/4 GB 基线，确定性/Mock 5 秒，AI 30 秒超时降级，脱敏日志、health/ready、桌面关键可访问性。
8. **交付和过程**：双仓库双 CI、Docker/OCI/Compose/公开 Registry、全新环境启动验证；每主要模块 worktree+PR/MR+新鲜 subagent，严格 TDD、两阶段评审、真实过程/commit/CI/冷启动记录。

该基线仍须用户明确最终确认，确认后才能生成 `SPEC.md`；它不等同于解锁实现阶段。

## 2026-08-05：最终设计签字与 SPEC 生成（已发生）

- 用户在阅读修订后的最终设计摘要后明确回复“确认最终设计摘要”。这授权生成完整 `SPEC.md`，不授权实现阶段。
- 本次 SPEC 将已确认的产品范围、规则、数据/凭据安全、双模式、技术、容器分发、双仓库双 CI、TDD/worktree/评审与验收要求沉淀为规约。
- 当前会话未暴露 OpenAI 官方文档 MCP。为保持当前“只写规约”的范围，没有安装或修改 MCP 配置；SPEC 将 OpenAI API 的具体 SDK/参数列为实现前必须用官方文档复核的约束，而未把它们伪装成已完成验证。
- 未创建或修改业务代码、框架、测试、Docker、CI、数据库迁移、部署、REFLECTION、worktree、PR/MR 或冷启动证据。

## 2026-08-08：人工审核后的 SPEC 安全与可实现性修订（待用户最终确认）

### 人工审核要求与处理决定

用户要求在生成 PLAN 或进入实现前修订 SPEC，内容为：状态与真实更新时间、Demo 数据流、Finding 敏感信息脱敏、Open Design 的明确选择、容器目标平台、数据实体关系、API Surface，以及一次 placeholder/内部矛盾/范围/歧义自检。

- **状态与时间：** `SPEC.md` 已从“设计已由用户确认”改为“待用户最终确认”，更新时间改为实际 `2026-08-08 20:29:29 +08:00`。
- **Demo 数据流：** Mermaid 改为私有确定性结果先脱敏并事务持久化，Demo 仅脱敏请求级结果；Mock/失败分支经脱敏后回到 Demo 响应，不再流向 SQLite。
- **Finding 脱敏：** 新增 `FindingRedactor`。它位于去重后、Pydantic 持久化模型/API 响应/导出/日志/错误处理之前；`GEN-001` 和任一 AI Finding 不保存、显示或导出真实凭据、尾号、可逆片段或可离线猜测的派生值。发送 OpenAI 前也遮盖高置信凭据。
- **Open Design：** 此处早期文本曾在未完成 capability 核验时写入 `Linear`/`live-dashboard`，该表述不是已验证的实际选型，已由 2026-08-08 的设计阶段 compatibility closure 更正。MUI 始终仅是实现层组件库，不能替代 Open Design。
- **平台：** Docker/OCI 主要交付目标定为 Linux `linux/amd64`；Windows 11 x64 + Docker Desktop（Linux containers）是本地支持环境；未承诺 Windows container、`linux/arm64` 或其他平台。
- **数据与 API：** 增加 Report/FileStat/Finding/AIReviewAttempt 的一对多关系、外键级联删除、唯一性、状态和脱敏约束；增加完整 API Surface 表，明示私有/Demo 可用性，Demo 禁用端点不注册路由，管理 API 仅本机监听。

### 修订前后关键差异

| 主题 | 修订前 | 修订后 |
| --- | --- | --- |
| Demo 架构 | Mock schema 校验后 Mermaid 无条件流向 SQLite | Demo 仅请求内存响应，任何 Demo 分支均不流向 SQLite |
| Finding 数据安全 | 仅规定完整 Diff 不落盘 | Finding/AI 文本也统一脱敏后才能持久化、响应、导出或日志 |
| UI 设计 | 仅说未来说明 Open Design | 早期草案错误地提前写入未经核验的 system/skill；已由后续真实 compatibility closure 更正为明确的上游选择及通过门禁 |
| 分发平台 | 未限定 CPU/平台 | Linux `linux/amd64` 主要交付；Windows 11 Docker Desktop 本地支持 |
| 数据/API 可实现性 | 实体字段概述、无模式 API 表 | 关系/级联/约束与模式化 API Surface 明确 |

### 自检范围与结果

- 已检查 placeholder：SPEC 不含 `TBD`、`TODO`、`FIXME`、`<...>` 或伪造 URL/commit/CI 状态；两个仓库 URL 仍须在其真实创建后写入 README，未填占位值。
- 已检查内部矛盾：Demo 的持久化和管理 API 禁用语义现在同时在 Mermaid、模式表、API 表、数据模型和验收标准一致；私有模式的持久化、AI 重试和级联删除一致。
- 已检查范围：仅修改 `SPEC.md`、`SPEC_PROCESS.md` 和 `AGENT_LOG.md`，未生成 PLAN、业务代码、测试、Docker、CI、迁移或部署配置。
- 已检查剩余歧义：OpenAI SDK/API 的易变参数仍标记为实现前用官方文档复核；Dockerfile 是后续实现任务，尚未决定统一镜像还是前后端镜像，符合既有“经计划确认”的边界。

本次修订仍须用户最终确认。未经该确认，不得调用 `writing-plans` 或开始冷启动/实现。

## 2026-08-08：第二轮 PLAN 人工审核修订（待用户最终确认）

### 审核发现与验证

用户按课程要求、SPEC 一致性、PLAN 内部一致性、TDD 可执行性和最终交付闭环进行人工审核，要求继续停在设计阶段。

- **Ruleset 编号：** 审核指出 PLAN 曾将 `GEN-002`/`GEN-003` 以及 JS-002、JS-005、JS-006、JS-007 的语义错位。重新对照 SPEC §4.4 后确认：SPEC 的固定编号是 `GEN-001` 凭据、`GEN-002` 危险 Shell/数据库、`GEN-003` TODO/FIXME/HACK、`GEN-004` 非回环 HTTP、`GEN-005` 文件级规模；JS-001 console、JS-002 debugger、JS-003 eval、JS-004 innerHTML、JS-005 empty/swallowed catch、JS-006 unhandled fetch、JS-007 explicit any。PLAN 已按该编号修复，未修改 SPEC 来迁就错误计划。
- **AI retry HTTP 缺口：** 审核确认 `ReviewService.retry_ai_review` 与前端重试已有计划，但 M11 没有 HTTP route。SPEC 的旧 API 表路径与本轮用户明确指定路径不同。统一决定采用私有 `POST /api/v1/reviews/{report_id}/ai-retry`；Demo 不注册。SPEC 和 PLAN 均已同步，计划覆盖摘要一致、摘要不一致、PENDING 拒绝与 Demo route 缺失。
- **关系模型措辞：** 审核确认 PLAN 中“`Report.id` 外键”错误。SPEC §5.1.1 已正确描述 Report 为聚合根；PLAN 已改为 `Report.id` 主键，三个子实体各自 `report_id` 外键引用 Report 并级联删除，FileStat 路径唯一。
- **Open Design 课程歧义：** 重新阅读课程通用和 B 类文件：它们将 Open Design 说为“强烈推荐”，同时在 SPEC 内容要求中写前端“须说明所选 Open Design 设计系统与 skill”。当时会话仅暴露 `visualize`，没有可调用的 Open Design capability，因此移除了“Material Design fallback 已充分满足课程”的断言，并先设 M13 compatibility gate。该阶段性方案已由后文真实 closure 替代：选择已固定为 `linear-app`/`web-design-guidelines`，当前没有任何已批准 fallback；`visualize` 不被描述为 Open Design skill。
- **Vault 算法歧义：** 用户要求消除 scrypt/Argon2id 的实现分支。SPEC 与 PLAN 固定为 scrypt 派生 32 字节密钥 + AES-256-GCM；不允许首期实现自行改选 Argon2id。
- **交付顺序：** 因 M19 和 M20 都改 README、AGENT_LOG 与验证证据，取消并行：M20 依赖 M17/M18，M19 依赖 M17/M18/M20，H01 依赖 M19/M20，最终链为 M18 → M20 → M19 → H01 → R01。
- **CI 验证：** 将仅检查 `unit-test:`/触发器文本的弱验证改为 `verify-ci-contract.ps1`。该未来检查必须确认 GitHub Actions 与 GitLab `unit-test` 实际执行后端 pytest 和前端 Vitest，使用 Mock/临时 SQLite 且不要求真实 OpenAI key；最终真实性仍由 R01 对最后 commit 的双端 Pipeline Pass 证明。

### 修订前后关键差异

| 主题 | 修订前 | 修订后 |
| --- | --- | --- |
| 通用/JS 规则 | PLAN 的编号与 SPEC 错位 | PLAN 的编号、测试节点和规则语义逐一以 SPEC 为准 |
| AI retry API | 只有服务和 UI，HTTP 断链 | 私有 retry route、摘要/PENDING/Demo 测试任务完整连通 |
| SQLite 描述 | 误把 `Report.id` 称为外键 | 明确 Report 主键和三个子表外键/级联 |
| Open Design | 直接将非 Open Design fallback 视为足够 | 可审计 compatibility gate 与课程方确认门槛 |
| 任务时间表述 | 把整个 task 称为 2–5 分钟 | task 由一个 fresh subagent 完成；其内部执行 step 目标为 2–5 分钟 |
| 最终顺序 | M19 与 M20 并行 | 先部署 M20，再最终文档 M19，再 H01 与 R01 |

本轮仅更新 `SPEC.md`、`PLAN.md` 与 `SPEC_PROCESS.md`。早期文本关于 `AGENTS.md` 不允许 `AGENT_LOG.md` 的判断不正确；实际允许清单已含该过程文件，后续已据此如实补记日志，无需修改 `AGENTS.md`。未创建或运行业务代码、测试、容器、CI、迁移、冷启动或部署。

## 2026-08-08：最终确认前跨文档工程一致性修订（待用户快速核验）

### 审核发现、课程核验与决定

用户再次交叉审核 SPEC/PLAN，要求在冷启动前解决容器分发、Docker 管理端口、HTTP 客户端和 Reflection AI 润色的矛盾，并允许记录真实 `AGENT_LOG.md`。

- **统一 OCI image：** 对照课程通用要求的“单条 `docker build` + 单条 `docker run` 可启动”后，确认原 PLAN 的 API/Web 双镜像与 M18 单一 `IMAGE_REF` 矛盾。决定首期只发布一个根目录 multi-stage production image：Node 阶段构建 React，Python 阶段运行 FastAPI 并服务前端静态文件/history fallback。Compose 仅编排同一 image 的私有/Demo 运行模式；M18 的 GHCR、pull、inspect、clean-environment 验证均对应此单一 image。
- **Docker admin 边界：** 确认“容器内部 bind 127.0.0.1”会使 Windows Docker Desktop 宿主机无法经端口映射访问 admin UI。决定直接宿主机运行仍仅 loopback/Unix socket；Docker 私有模式可在容器内部使用独立 admin listener，但固定只发布 `127.0.0.1:8081:8081`，审查端口为 `127.0.0.1:8080:8080`。公网 Nginx 只能代理审查端口，永不代理 admin；Demo 不启动 listener 且不注册路由。
- **前端 HTTP 客户端：** SPEC 原来保留“Axios 或原生 fetch”，而 PLAN 已固定 native `fetch`。为避免陌生智能体自行选择，SPEC 现固定原生 `fetch`，不引入 Axios。
- **Reflection：** 对照课程原文“学生本人撰写，禁止 AI 代写（可用 AI 辅助润色，但需标注）”，修复 H01 的自相矛盾措辞：观点、案例、结构和完整初稿由学生完成；AI 不得代写或补全实质内容，但可在完整初稿后作已披露的语言润色和形式检查。
- **AGENT_LOG 权限：** 重新读取实际 `AGENTS.md` 后发现它已经允许更新 `AGENT_LOG.md`；用户要求的权限扩展已存在，因此未制造重复或无意义的 AGENTS 修改。本轮真实日志已补记至 `AGENT_LOG.md`。

### 修订前后关键差异

| 主题 | 修订前 | 修订后 |
| --- | --- | --- |
| OCI 分发 | 双 Dockerfile 与单一 `IMAGE_REF` 并存 | 一个根目录 multi-stage production image，单条 build/run、Compose、Registry 与验证均指向同一 image |
| Docker admin | 要求容器内绝对 loopback，宿主机无法安全访问 | Docker 内独立 listener，宿主机仅 `127.0.0.1:8081:8081` 发布；Nginx/公网不可达 |
| HTTP 客户端 | SPEC 保留 Axios/fetch 二选一 | SPEC/PLAN 均固定 native `fetch` |
| Reflection AI | “不得润色”与“可润色但标注”冲突 | 禁止代写/实质补全；允许学生完整初稿后的已披露语言润色 |

未创建或运行任何业务代码、测试、Dockerfile、Compose、CI、迁移、镜像、部署或冷启动。当前仍等待用户最终快速核验，不能自行进入冷启动或实现。

## 2026-08-08：SPEC 确认后的 PLAN 生成（待用户确认）

- 用户明确确认修订后的 `SPEC.md`。这授权在当前设计阶段使用 `writing-plans` 生成 `PLAN.md`，但不授权冷启动、worktree、实现、测试、Docker、CI 或部署。
- 实际使用 `superpowers:writing-plans` 生成单一 `PLAN.md`（用户/仓库要求覆盖该 skill 的默认 `docs/superpowers/plans/` 存放位置）。计划包含 19 个唯一 task、精确未来路径、共享接口、分支/worktree、依赖/并行关系、未来 RED–GREEN–REFACTOR、双评审、真实 commit 记录和冷启动门槛。
- 因 `AGENTS.md` 当前明确禁止生成可执行测试和业务实现，本 PLAN 仅记录非可执行的失败测试规格、验证命令与预期 RED 条件；没有写入测试代码、实现代码、Docker、CI、迁移或脚手架。这是对 `writing-plans` 通常要求代码示例的受限偏离，理由已如实记录。
- 已执行计划自检：19 个 task 编号唯一；SPEC 覆盖、共享接口一致性和红旗占位符扫描通过。`TODO` 一词仅出现在已确认的 `GEN-003` 规则名称，非未完成占位符；`git diff --check` 无空白错误。
- PLAN 现在等待用户确认。确认后仍必须进行不同类型陌生智能体的冷启动试运行、记录歧义并实际修订 SPEC/PLAN；只有用户最终明确解除限制，才可执行 T01。

## 2026-08-08：Open Design 设计阶段兼容性 closure（未通过，暂停）

### 用户要求、真实检查与选择

用户要求在最终确认和陌生智能体冷启动前关闭“前端 SPEC 须说明所选 Open Design design system 与 skill”的规约缺口；只允许设计阶段检查或经批准的安装，不允许创建前端/后端、测试、Docker、CI、数据库或部署资产。

- **上游选择：** 依据 Open Design 上游仓库的实际目录，固定选择 `linear-app` 设计系统（`design-systems/linear-app/DESIGN.md`）和 `web-design-guidelines` skill（`skills/web-design-guidelines/SKILL.md`）。前者适合开发工具的密集信息层级；后者用于审阅布局、排版、颜色、动效和可访问性准则。此选择取代早期未核验的 `Linear`/`live-dashboard` 表述。
- **本地可用性检查：** 当前环境未发现 `od` 命令，也没有安装 `web-design-guidelines` skill。该结论是本地 capability 检查结果，不是对上游项目不存在的推测。
- **真实安装与连通性证据：** 经用户授权，按现有 `skill-installer` 的 GitHub 安装脚本尝试安装 `nexu-io/open-design` 的 `skills/web-design-guidelines` 路径；该命令在无成功安装输出的情况下超时。随后直接检查 `https://github.com/nexu-io/open-design.git` 的 Git 连通性，得到“Recv failure: Connection was reset”。没有伪称安装成功、skill 已调用或已有 UI 产出。
- **fallback 状态：** 未取得课程方对 Material/MUI、`visualize` 或其他 fallback 的书面确认。MUI 仍可作为未来 React 组件库，但不构成 Open Design design system/skill 的替代证据。

### 设计与计划修订

1. `SPEC.md` 现在明确写入准确的上游系统与 skill、选型理由和使用边界，并将状态标为“Open Design 兼容性门禁未通过”。
2. `PLAN.md` 将 system/skill 决策从 M13 的未来分支移至已发生的设计阶段事实；M13 以后只基于该固定选择产出 UI 方向、可访问性合同和状态矩阵，不再检查、安装、替换或决定是否采用 Open Design。
3. 陌生智能体冷启动和用户对 SPEC/PLAN 的最终流程确认均被该门禁阻止。关闭路径只有：成功安装并真实调用上述已选资产、记录 context/产出；或获得课程方对明确 fallback 的书面确认。

### 当前暂停点

本 closure **未通过**。下一步不是实现或冷启动，而是等待可恢复的 Open Design 安装/调用条件，或用户提供课程方书面 fallback 批准。仅在真实证据补齐后才可将门禁改为通过并请用户最终确认 SPEC/PLAN。

### 本轮文档自检

- **旧名称与 fallback：** 检查 `SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md`、`AGENT_LOG.md` 后，现行规约只把 `linear-app`/`web-design-guidelines` 作为选择；`Linear`/`live-dashboard` 仅保留在带有“早期未核验、已更正”说明的历史记录中。未发现把 MUI、`visualize` 或搜索结果表述为已满足 Open Design 的现行结论。
- **门禁与范围：** SPEC 状态、PLAN 执行前置条件、M13 说明、冷启动门禁和过程记录均显示当前“未通过”；没有把选择误写为安装/调用成功，也未创建任何受禁的业务代码、测试、Docker、CI、数据库或部署资产。
- **计划一致性：** PLAN 仍有 106 个正式 `Txx.yy` task、无重复编号，M13 仍有 6 个 task，且 T13.1–T13.3 已不再作 Open Design 可用性/产品选型分支。`git diff --check` 未报告空白错误。

## 2026-08-08：用户确认与 Open Design 门禁关闭（已发生）

### 确认、真实资源使用与审阅

用户明确回复“确认”，确认 `SPEC.md` 与 `PLAN.md`。该确认不解除 `AGENTS.md` 实现限制；根据计划，下一步先关闭已选 Open Design 门禁。

- **本机 skill：** 重新检查后，`web-design-guidelines` 已存在于本机 Codex skill 目录。实际阅读其 `SKILL.md` 与 pinned `references/guidelines.md`，未把它仅当作可用列表中的名称。
- **实际 skill 使用：** 按该 skill 的审阅方法，将 `SPEC.md` 中的 UI 要求作为当前阶段唯一可审阅的界面规约工件。审阅发现原 §6.3 已覆盖键盘、标签、文字等级、错误和删除确认，但缺少具体的语义控件/标题结构、`:focus-visible`、`aria-live`、首个错误焦点、禁止阻止粘贴与 `prefers-reduced-motion` 约束；这些项已真实补入 SPEC §6.3。没有伪造 UI 代码审阅、截图或测试输出。
- **实际 system 使用：** 网络恢复后，直接读取 Open Design 上游 `design-systems/linear-app/DESIGN.md`。该公开资源规定深色优先的分层表面、克制靛紫强调、细边框、8px 间距、普通/技术文本的排版角色和响应式桌面信息密度。已将不涉及品牌复制的原则写入 SPEC §6.3.1；明确不使用 Linear 品牌、徽标或营销素材。
- **门禁决定：** `linear-app` 是可读取的 `DESIGN.md` design-system 资源而非业务可执行组件；直接读取并将其原则用于规约，结合已安装并实际运行于规约审阅的 `web-design-guidelines` skill，构成已选 system/skill 的真实 source、context 与产出。因此 Open Design 门禁从“未通过”改为“已关闭”。此前 `od` CLI 缺失和安装超时的事实仍保留，但不再是当前门禁阻塞条件。

### 修订与下一阶段

1. `SPEC.md` 状态改为“已获用户确认；门禁已通过；进入陌生智能体冷启动验证阶段”，并新增 §6.3.1 与可访问性补充。
2. `PLAN.md` 状态、执行前置条件、M13 前提、自检和执行交接均改为门禁已关闭；下一步只允许 §7 冷启动，仍不允许 T01 或实现资产。
3. 本次只更新 `SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md` 与 `AGENT_LOG.md`；没有创建或运行业务代码、测试、Docker、CI、迁移、数据库或部署资产。

## 2026-08-08：陌生智能体冷启动试运行 1 — 应用工厂合同（已暂停并修订）

### 验证设置与真实产出

- **陌生性与输入边界：** 使用新建的 `gpt-5.6-sol` cold-start session，`fork_turns=none`，不导入主智能体对话或 memory；任务提示只给出 `SPEC.md` 和 `PLAN.md` 的绝对路径，并要求它不得读取其他项目文档、写入文件、创建代码或运行实现命令。
- **选择的微任务：** 智能体自主选择 `T01.1`，并在第一项 RED 测试设计处停止；满足“选择 1—2 个 task、遇不确定立即暂停”的要求。
- **暂停点与问题：** 原计划要求 `test_create_app_boots_private_mode`，但未定义 `create_app` 从参数、`APP_MODE` 还是默认值获得 mode，也未定义最小可观察断言。原 T01.3 才引入 settings 配置校验，使不同执行者可能建立不兼容的工厂签名并在随后重写 T01.1。
- **产出差距：** 无法精确写出唯一的 RED 测试、最小 GREEN 或后续兼容实现；次级风险是原 T01.1 未说明 `pyproject.toml` 的最小依赖与锁定范围。智能体未猜测、未写文件、未运行任何命令或测试。

### 根据冷启动的实际修订

| 项目 | 修订前 | 修订后 |
| --- | --- | --- |
| 应用工厂 | 仅写“定义 `create_app`”，mode 来源和断言不明 | 固定 `create_app(settings: AppSettings) -> FastAPI`；必须暴露 `app.state.settings.mode` |
| 初始 mode | `private` 测试未说明如何注入 | T01.1 明定 `AppSettings(mode="private")` 显式注入；唯一启动合同为 FastAPI 实例与可观察 private mode |
| 环境变量 | 可能由 T01.1 或 T01.3 任意读取 | T01.3 唯一负责 `load_settings(env)` 读取/校验 `APP_MODE`，不得改变工厂签名 |
| 依赖基础 | `pyproject.toml` 无最小范围/锁定约束 | T01.1 固定 Python 范围、FastAPI/Pydantic v2/pytest 的有界声明和同 task 实际 lockfile |

PLAN §3 与 T01.1/T01.3 已按上表修改。冷启动暴露的歧义已记录并实际修订；课程门槛为 1—2 个微任务，本次已完成其中 1 个的真实分析性试运行。当前仍不具备实现解锁资格，原因是修订后的 SPEC/PLAN 尚待用户确认，且只有用户可明确解除 `AGENTS.md` 限制。

## 2026-08-08：解除实现限制前人工审核修订 — 冷启动状态与运行时 bootstrap

用户审核 Probe 01 修订后，要求在解除限制前继续保持禁止 T01，并修正过时冷启动状态及补齐 ASGI runtime 合同。

- **状态链修订：** 原 PLAN 顶部、§7、§9、§10 仍有“冷启动下一步待执行”的历史表述，SPEC §11 也仍以未来时描述已发生的 Probe 01。现统一改为：Open Design 门禁已关闭；Probe 01 已完成并因 T01.1 歧义暂停；暂停反馈修订已完成；当前唯一剩余条件是用户最终确认并明确解除 `AGENTS.md` 限制。
- **Probe 01 门禁结论：** 课程要求为 1—2 个 task；Probe 01 实际选择 1 个 T01.1、遇不确定即暂停、记录并触发实际修订，已满足本轮冷启动门禁。由于该 probe 严格只读、没有试运行代码，未创建 branch/worktree；§7 保留了任何未来会产生试运行代码时必须使用可丢弃 branch/worktree 的规则，并如实说明本次无清理对象。
- **运行时合同修订：** 保留纯 `create_app(settings: AppSettings)` 与唯一配置入口 `load_settings(env)`；新增 `create_runtime_app() -> FastAPI`，唯一职责为 `create_app(load_settings(os.environ))`。`APP_MODE` 缺失或非法均导致启动配置失败，不允许默认模式。生产 ASGI 和 Docker runtime 均只能通过该 factory 启动。
- **计划修订：** 新增独立 T01.4，精确 RED/GREEN 节点为 `test_create_runtime_app_uses_env_and_rejects_missing_or_invalid_mode`；T01.1 的最小依赖增加 Uvicorn，以支持 ASGI runtime；M01 评审范围更新为 T01.1–T01.4。正式 task 总数从 106 变为 107，PLAN §9 自检已同步。

### 修订前后差异

| 项目 | 修订前 | 修订后 |
| --- | --- | --- |
| 当前阶段 | 部分位置仍称“下一步冷启动” | 所有现行状态改为仅待用户最终确认与明确解除限制 |
| ASGI 入口 | 只有显式注入的 `create_app(settings)`，生产模式来源未定义 | `create_runtime_app()` 固定组合环境加载与纯工厂 |
| 缺失/非法 `APP_MODE` | 仅规定未知值拒绝，未明确缺失和 Docker/ASGI 行为 | 缺失及非法均为启动配置失败；Docker/ASGI 只经 runtime factory |
| 计划任务 | T01.1–T01.3，106 个 task | 新增 T01.4，107 个 task；有精确 RED/GREEN 测试 |

本轮未创建或运行 `apps/`、测试、Docker、CI、迁移、数据库或部署资产。当前暂停等待用户最终决定。

## 2026-08-08：冷启动修订的用户最终确认（尚未解除限制）

用户回复“行，最终确认了”，据此确认经 Probe 01 修订后的 `SPEC.md` 与 `PLAN.md`。该确认已反映到两份文档状态和执行前置条件。

用户尚未明确说出解除 `AGENTS.md` 阶段限制或授权开始 T01；因此本次确认不构成实现授权。当前唯一阻塞是该明确解除，所有业务代码、测试、Docker、CI、迁移、数据库和部署资产继续禁止。

## 2026-08-08：用户明确解除阶段限制并授权 T01 实现

用户明确指示：“解除 AGENTS.md 阶段限制，授权开始 T01 实现。”因此此前的设计阶段门禁已正式关闭：Open Design 已完成、Probe 01 已完成并推动规约修订、修订后的 SPEC/PLAN 已获用户最终确认。

本仓库据此将 `AGENTS.md` 切换为实现阶段约束：从 T01 开始在独立 worktree 中按既定依赖顺序执行，使用 fresh subagent、RED→GREEN→REFACTOR、规约符合性评审、代码质量评审和真实过程留痕。该授权不预先确认任何实现、测试、CI、容器、发布或部署结果，也不解除 `REFLECTION.md` 禁止修改、禁止伪造证据和凭据/敏感数据保护等红线。

## 2026-08-12：JS-007 真实误报后的人工范围收窄

在 `codex/js-rules-risk` 的 T05.7 尝试中，Python 3.12 真实回归分别复现了 JSX 文本、对象字面量、`import`/`export` alias、语句标签和正则字面量中的 `as any`/`: any` 误报。多轮 scoped review 表明，在首期不使用 tokenizer、AST、TypeScript Compiler 或外部解析依赖的约束下，继续扩大 interface/type member 与复杂 TSX 语境识别会造成不可靠的规则膨胀。

用户明确选择 B：保留 JS-007 的 Low 等级，但收窄为变量声明、函数参数/返回类型和完整调用/索引表达式 type assertion 等高置信形式；首期不再要求 interface/type object member、跨行 assertion 或裸标识符 assertion 覆盖。用户同时明确要求 JSX 文本、字符串、模板文本、正则字面量、import/export alias 不得产生 Finding，并确认“保守漏报优于明显误报”。

据此，`SPEC.md`、`PLAN.md` 和 README 已同步精确支持/不支持边界；T05.7 将从批准基线 `98916c8` 在新 `codex/js-any-narrow` worktree 由 fresh subagent 重新执行，至少保留三项已复现误报的 regression tests 与代表性 positive tests。旧分支保留为真实过程证据，不删除、不改写，也不复用其实现 session 或未批准代码；新 worktree 本轮尚未开始新的 T05.7 实现。
