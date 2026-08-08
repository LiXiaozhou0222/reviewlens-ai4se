# AGENT_LOG

## 2026-08-05 21:37:46 +08:00 — 阶段：需求澄清 / 课程要求审计

- **Task / 当前工作**：在不进入实现阶段的前提下，完整阅读 `AGENTS.md`、两份课程要求、`README.md` 与当前规约/计划/过程/日志文件；审计 B 类项目要求。
- **使用的 Superpowers skill**：用户要求 `brainstorming`。当前会话的已暴露 skill 清单未提供该 skill，因此未实际调用；改为遵循课程 §4.1 所描述的分段澄清与逐项确认形式。
- **关键 prompt / context**：用户确定项目为 B 类“非 Harness 应用类项目”，暂定为 ReviewLens（面向学生开发者和小型团队的 Git Diff 风险审查与 AI 辅助代码评审平台）；明确禁止初始化框架、业务代码、测试、Docker、CI 和 `REFLECTION.md` 修改。
- **智能体建议 / 关键发现**：ReviewLens 应明确保持单轮 LLM、无自主循环与工具自主调用的非 Agent 边界（B.2）；课程文本存在 CI 平台与公网部署要求的歧义，需在设计中向用户确认后写入 SPEC。
- **用户确认、否决与人工修改**：用户要求先完成课程要求审计，然后才开始一次一问的 brainstorming；尚未对任何设计选项作出确认、否决或签字。
- **课程流程偏离及理由**：无法在当前环境实际调用 `brainstorming` skill，已如实记录；不宣称该 skill 已被使用。后续采用与课程 §4.1 相符的单问题、等待确认流程，若能力可用则改用正式 skill。
- **学到的教训**：B 类不是免除工程流程；它仅排除 Harness 特有的领域与机制设计、Harness 内核、mock-LLM 测试和机制演示。任何 LLM 功能仍须先界定是否产生自主 agent 行为。

## 2026-08-05 21:46:23 +08:00 — 阶段：Brainstorming / 迭代 1

- **Task / 当前工作**：澄清首期目标用户、单用户边界与团队共享方式。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见上一条记录。
- **关键 prompt / context**：首期目标用户决定身份模型、协作能力、Diff 输入、数据保存和验收场景。建议选“个人优先、导出报告供团队共享”。
- **智能体建议**：不在十天内引入认证、授权、多租户、项目空间或平台内共享；以 Markdown 导出满足小团队外部共享路径。
- **用户确认、否决与人工修改**：用户选择 C，明确系统单用户、自托管；不做注册登录、团队空间、共享链接、协作评论、成员权限或多租户。报告可导出 Markdown，平台内无分享；完整 Diff 是否保存尚待安全设计决定。
- **课程流程偏离及理由**：无新增偏离。
- **学到的教训**：将“团队可用”限定为报告导出后的外部分享，可以保留实际使用场景，同时显著缩小首期身份和数据治理范围。

## 2026-08-05 22:09:01 +08:00 — 阶段：Brainstorming / 迭代 2

- **Task / 当前工作**：澄清 Git Diff 输入通道、大小与行数上限、上传校验、拒绝语义及远程访问边界。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：输入方式和限制会决定上传安全、LLM 上下文控制、性能、数据模型和验收。推荐粘贴/单文件上传的调整后 B，且不连接远程仓库。
- **智能体建议**：支持 UTF-8 unified diff 的粘贴或单个 `.diff`/`.patch` 上传；对 500 KB、5,000 行任一超限直接拒绝，并以内容校验替代仅扩展名校验。
- **用户确认、否决与人工修改**：用户采纳调整后 B，并具体确认所有限制、错误区分和“不得执行 Diff 内容”；明确拒绝 PR/MR URL、OAuth、仓库授权、远程拉取、多文件、压缩/二进制和非 UTF-8。要求在未来 SPEC 的输入规约、安全边界和验收标准中保留这些决定。
- **课程流程偏离及理由**：无新增偏离。
- **学到的教训**：把超限处理设为显式拒绝而非截断，能避免风险报告针对不完整代码变更产生误导性结论；不可信 Diff 必须始终被当作数据而非可执行内容。

## 2026-08-05 22:17:42 +08:00 — 阶段：Brainstorming / 迭代 3

- **Task / 当前工作**：澄清首期语言支持、通用与语言专项规则的分层，以及不支持语言的降级语义。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：语言范围决定确定性规则库的深度、误判风险、LLM 上下文和验收范围。建议只深度支持 JS/TS，非支持语言不拒绝但须告知能力限制。
- **智能体建议**：将语言无关规则与 JS/TS 专项规则分离；非支持语言保留通用规则和单轮 AI 评审，避免跨语言规则误判。
- **用户确认、否决与人工修改**：用户确认 `.ts`、`.tsx`、`.js`、`.jsx` 为唯一语言专项范围，明确通用规则、专项规则候选清单、扩展名识别、`unknown` 行为和“不支持不等于安全”。用户明确排除其他语言专项规则、AST/编译器分析、外部静态工具、依赖安装和用户代码执行。
- **课程流程偏离及理由**：无新增偏离。
- **学到的教训**：语言覆盖面不能替代规则可信度；报告必须把“没有执行某层检查”与“检查后未发现风险”明确区分。

## 2026-08-05 22:35:52 +08:00 — 阶段：Brainstorming / 迭代 4

- **Task / 当前工作**：澄清确定性风险等级、总等级聚合、重复 Finding 处理、稳定排序以及 AI 建议的隔离。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：风险结论必须可解释、可重复，且不能让 AI 推测改变确定性风险结论。建议固定等级汇总，不使用难以证明的 0–100 权重。
- **智能体建议**：采用 Critical/High/Medium/Low/None 与透明阈值；确定性与 AI Finding 分区，AI 结果不参与计数或总等级。
- **用户确认、否决与人工修改**：用户采纳等级汇总，拒绝数值评分；明确全部聚合阈值、Critical 不可由多个 High 升级、重复判定字段、稳定排序和 AI 失败降级。要求未来 SPEC 记录全部算法与验收标准。
- **课程流程偏离及理由**：无新增偏离。
- **学到的教训**：评分系统的可信度来自等级语义、聚合规则和可复现性，而不是未校准数值的表面精度。

## 2026-08-05 22:51:29 +08:00 — 阶段：Brainstorming / 迭代 5

- **Task / 当前工作**：澄清 OpenAI Provider 范围、确定性先行的报告流程、AI 状态机、手动重试、数据外发和 Prompt Injection 输出边界。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：AI 评审不得阻断确定性扫描或改变确定性总等级；单一 Provider 能缩小认证、错误处理、成本与安全范围。
- **智能体建议**：仅支持 OpenAI 官方 API；先持久化确定性报告；AI 失败仅降级 AI 分区，不自动重试或切换 Provider，用户可手动重试同一报告。
- **用户确认、否决与人工修改**：用户采纳单一官方 OpenAI Provider，保留仅供测试/CI/离线开发/演示的 Mock；确认状态集、失败降级、单任务手动重试、最小数据外发、`store=false` 条件、Diff 不可信处理和 Pydantic/JSON Schema 校验。用户拒绝多 Provider、自定义 endpoint、自动切换、本地模型与无限重试。
- **课程流程偏离及理由**：无新增偏离。当前会话尚未验证用户提及的 OpenAI API 细节，后续技术选型落入 SPEC 前须以官方文档复核。
- **学到的教训**：把确定性结果先持久化，并把 AI 作为可恢复的附加层，能同时避免外部 API 不稳定导致核心审查失败，以及把模型推测误作确定性证据。

## 2026-08-05 23:00:27 +08:00 — 阶段：Brainstorming / 迭代 6

- **Task / 当前工作**：澄清跨平台 API key 加密保险箱、回环受限管理入口、解锁生命周期、清除语义、公网演示模式和凭据威胁模型。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：课程要求安全存储、首次安全录入、查看/更新/清除；公开 WebUI 与 key 管理必须隔离。推荐主密码保护的跨平台加密保险箱。
- **智能体建议**：使用成熟 KDF 和认证加密、只经 loopback/Unix socket 管理、默认锁定、进程内存短暂持有 key、重启重新解锁。
- **用户确认、否决与人工修改**：用户采纳加密保险箱，明确文件内容、scrypt/Argon2id、AES-GCM、随机 salt/nonce、原子保存、本机管理、SSH 转发、全部管理动作、统一失败提示、递增延迟、Volume/文件权限、公网 Mock 演示与验收标准；拒绝操作系统钥匙串和云 KMS。
- **课程流程偏离及理由**：无新增偏离。本文仅记录未来安全设计，未创建密码学、Docker、CI 或测试实现。
- **学到的教训**：把凭据管理限定为服务器操作者的本机职责，能让无账号体系的公开审查 UI 仍具有清晰的 key 安全边界。

## 2026-08-05 23:09:14 +08:00 — 阶段：Brainstorming / 迭代 7

- **Task / 当前工作**：澄清完整 Diff 的内存边界、规范化摘要、同报告 AI 重试、报告持久化、Markdown 导出与级联硬删除。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：不持久化原始 Diff 会与报告详情的 AI 重试产生冲突；建议以规范化 SHA-256 摘要要求用户重新提交相同 Diff，从而只重跑 AI。
- **智能体建议**：选择默认不持久化原始 Diff；报告保留最小化元数据至手动删除，硬删除关联数据，重试以摘要严格匹配。
- **用户确认、否决与人工修改**：用户采纳 A，精确定义 UTF-8/BOM/换行规范化、SHA-256、最小报告字段、AI 尝试元数据、导出内容、硬删除与二次确认；拒绝长期保存或逐报告选择保存完整 Diff。
- **课程流程偏离及理由**：无新增偏离。本文记录了未来数据/验收要求，未创建数据库、测试、Docker 或实现代码。
- **学到的教训**：用内容摘要支持重试能保留报告一致性，却不把原始代码变更长期沉淀为系统数据资产；同一设计也必须如实说明内存擦除的语言运行时限制。

## 2026-08-05 23:15:01 +08:00 — 阶段：Brainstorming / 迭代 8

- **Task / 当前工作**：澄清课程所需公网 WebUI 的运行模式、与私有实例的隔离、无状态数据生命周期、Mock 行为、限流和最小化日志。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：无账号的公开站不能与私有报告/凭据共享；真实 Provider 会带来 key、成本和代码外发风险。推荐独立、无状态、限流的 Mock 演示。
- **智能体建议**：公开实例不保存报告/摘要/尝试记录、不暴露管理路由、Mock 输出确定可复现，并对 IP、突发和并发限流。
- **用户确认、否决与人工修改**：用户采纳 A，确认全部隔离对象、可用/禁用功能、无状态导出、Mock 标识与行为、初始限流阈值、反向代理信任边界、日志允许字段和双模式矩阵；拒绝匿名持久化和公网真实 OpenAI。
- **课程流程偏离及理由**：无新增偏离。本文只记录未来部署和验收约束，未创建 Docker、反向代理、限流、日志或测试实现。
- **学到的教训**：在无账号公网演示中，“无状态 Mock + 显式能力标签”比临时匿名持久化更容易给出可验证的数据隔离和费用安全边界。

## 2026-08-05 23:19:29 +08:00 — 阶段：Brainstorming / 迭代 9

- **Task / 当前工作**：澄清确定性规则配置、结果筛选、误报处理、规则版本与公网/私有规则一致性。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：允许规则开关、等级调整或自定义规则会破坏固定结论的可复现性并显著扩大配置/审计范围。建议固定内置 ruleset。
- **智能体建议**：用户只能筛选查看和导出，不能改变规则或结论；报告绑定 ruleset 版本，升级不自动重算历史结果。
- **用户确认、否决与人工修改**：用户采纳固定规则集，确认规则属性、筛选不改结论、全量导出、误报处理、AI 不覆盖、版本字段和双模式规则一致性；拒绝规则开关、等级调整、自定义规则、忽略/豁免/已解决和团队策略。
- **课程流程偏离及理由**：无新增偏离。本文仅记录规约，未创建规则实现、配置、API 或测试。
- **学到的教训**：首期把规则治理收敛为版本化发布，而不是运行时自由配置，能让风险等级和报告历史始终有清晰、可追溯的含义。

## 2026-08-05 23:23:59 +08:00 — 阶段：Brainstorming / 迭代 10

- **Task / 当前工作**：澄清前后端、schema、持久化、双运行模式、管理入口、未来目录/测试/分发与版本锁定策略。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：Pydantic、加密保险箱、单用户持久化、无状态演示与回环管理入口需要职责清晰的后端；UI 项目应在 SPEC 记录 Open Design。
- **智能体建议**：选择 Python FastAPI/Pydantic/SQLite 与 React/TypeScript，按 Repository 隔离持久化，以运行模式在后端禁用演示持久化和凭据管理。
- **用户确认、否决与人工修改**：用户采纳 A，明确所有主要组件、职责边界、SQLite 内容、Noop 演示持久化、管理 Router、未来目录、测试范围、统一命令、Compose 模式、依赖版本锁定；拒绝完整列出的框架、服务、Agent、用户代码执行与复杂前端能力。
- **课程流程偏离及理由**：无新增偏离。严格遵守当前限制：用户给出的目录、测试、Docker、CI 和命令仅记录到文档，未初始化、未安装、未创建。
- **学到的教训**：将“同一业务内核”与“不同持久化/Provider/管理边界”分开，既能减少双模式实现分叉，也能使公开演示的安全断言具备后端可验证性。

## 2026-08-05 23:29:07 +08:00 — 阶段：Brainstorming / 迭代 11

- **Task / 当前工作**：澄清单机性能测量、AI 超时、Mock 性能、并发边界、健康检查、结构化日志、错误码、关键可访问性和可恢复性。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：SPEC 需客观非功能验收，但十天项目不应虚构高并发、可用率或复杂监控能力。建议有基线的 5 秒确定性/Mock 和 30 秒 AI 降级。
- **智能体建议**：在 2 vCPU/4GB 基线上用预热 10 次测量；Provider 不可用不影响确定性服务；脱敏结构化日志和桌面关键可访问性作为首期下限。
- **用户确认、否决与人工修改**：用户采纳 A，并精确定义性能样例与 9/10 次规则、AI 超时、Mock、并发、health/ready、日志字段与禁记字段、错误码、可用性、恢复性和全部不承诺项；拒绝高并发/高可用/复杂监控承诺。
- **课程流程偏离及理由**：无新增偏离。性能测试、健康端点、日志和部署检查均未创建，文档中的指标仅用于未来验收。
- **学到的教训**：性能承诺只有同时固定输入上限、运行环境、测量方法和不包含的外部等待时才可被诚实验证；对单用户工具，失败降级比不可证明的高可用宣称更有价值。

## 2026-08-05 23:32:26 +08:00 — 阶段：Brainstorming / 迭代 12

- **Task / 当前工作**：澄清代码风险扫描范围、上下文读取例外、文件级规则、目标文件行号、去重、删除行、报告措辞和 AI 归因。
- **使用的 Superpowers skill**：按 `brainstorming` 的一次一问、选项比较与等待确认形式执行；未实际调用该 skill，原因见首条记录。
- **关键 prompt / context**：提交前审查应说明本次变更引入的风险；允许上下文直接告警会误归因既有问题，扫描删除行会误报正在被移除的问题。
- **智能体建议**：仅新增行触发代码 Finding，完整 Diff 元数据服务于结构/规模规则；上下文仅用于理解、Finding 必须锚定新增新文件行。
- **用户确认、否决与人工修改**：用户采纳 A，并完整定义扫描/排除范围、有限上下文规则、文件级 Finding、行号、字段、去重、删除行、报告措辞、AI 边界和验收；拒绝将旧上下文或删除代码作为风险来源。
- **课程流程偏离及理由**：无新增偏离。本文只记录未来解析/规则/测试要求，未创建实现、测试或业务目录。
- **学到的教训**：把“可读取上下文”与“可产生告警”严格分离，能同时提升多行规则理解能力和本次变更风险归因的可信度。

## 2026-08-05 23:37:16 +08:00 — 阶段：设计基线修订 / 待最终签字

- **Task / 当前工作**：根据用户对已汇总设计基线的确认，补足课程基础设施、容器分发和实施过程约束，并重新提交最终设计摘要。
- **使用的 Superpowers skill**：无新增 skill 调用；本轮是用户对 brainstorming 结果的基线修订与签字前整理。
- **关键 prompt / context**：课程文本同时出现 GitHub Actions 与 `.gitlab-ci.yml`；用户要求以双仓库策略覆盖两者，且要求 Docker/OCI 分发及完整 Superpowers 实施纪律。
- **用户确认、否决与人工修改**：用户确认其余产品设计不变；明确 GitHub 为公开主开发仓库、NJU GitLab 为最终提交仓库，双 CI 最终均须 Pass；确认 Docker/OCI/Compose、私有 Volume、公开 Registry、全新环境启动验证，以及 worktree/subagent/TDD/两阶段评审/真实证据基线。否决了“GitHub Actions 仅有镜像才补充”的旧表述。
- **课程流程偏离及理由**：无新增偏离。没有创建仓库远程、CI、Docker、镜像、worktree、测试、PR/MR、部署或验证记录；所有项目均作为未来 SPEC/PLAN 约束记录。
- **学到的教训**：面对课程基础设施要求的文本冲突，双仓库与双 CI 能形成可审计的覆盖策略；但在真实远程地址与流水线运行前，绝不能把策略写成已经完成的证据。

## 2026-08-05 23:41:34 +08:00 — 阶段：规约生成 / 用户已签字

- **Task / 当前工作**：在用户明确确认最终设计摘要后，创建完整 `SPEC.md`；仍不进入实现阶段。
- **使用的 Superpowers skill**：本会话可用清单仍无 `brainstorming`；此前已按其分段确认形式完成 12 轮真实设计迭代。为核验 OpenAI 技术细节而读取 `openai-docs` skill；当前会话未暴露其官方文档 MCP，因此未安装/修改 MCP，而将 API 参数复核列为实现前约束。
- **关键 prompt / context**：用户确认单用户自托管、固定 ruleset、新增行归因、确定性与 AI 隔离、无原始 Diff 持久化、保险箱、双运行模式、双仓库双 CI、Docker/OCI 分发与严格实施过程。
- **人工确认与修改**：用户明确授权生成 SPEC，未授权创建业务代码、测试、框架、Docker、CI、迁移、部署或 REFLECTION。
- **课程流程偏离及理由**：`brainstorming` skill 未暴露，已如实记录并采用课程 §4.1 的一次一问、分段确认；官方文档 MCP 未暴露，未在规约阶段扩大权限安装配置。没有伪造任何实现或外部验证证据。
- **学到的教训**：可实现规约应把用户已决定的边界写成可观察的输入、状态、数据生命周期和验收条件，同时把尚需外部核验的 API 细节明确保留为风险，而不是以推测填补。

## 2026-08-08 20:29:29 +08:00 — 阶段：人工审核后 SPEC 修订 / 待最终确认

- **Task / 当前工作**：根据人工审核修订 SPEC，不生成 PLAN，不进入实现。
- **使用的 Superpowers skill**：实际使用 `superpowers:receiving-code-review` 逐项理解、核对并处理人工审核意见；本轮不调用 `writing-plans`。
- **关键 prompt / context**：必须修复状态时间、Demo Mock → SQLite 架构矛盾、敏感 Finding 持久化风险、Open Design 选择、容器平台、实体关系/级联和 API Surface，并在最后做文档自检。
- **处理结果**：SPEC 现为“待用户最终确认”；新增 `FindingRedactor`，明确 `GEN-001`/AI Finding 的不可逆脱敏与 OpenAI 载荷遮盖；Demo 全程无状态；明确 `linux/amd64` + Windows 11 Docker Desktop、实体关系/约束与模式 API。该条当时写入的 `Linear` + `live-dashboard` 属于未完成真实 capability 核验的早期草案，已由 2026-08-08 的 Open Design compatibility closure 更正，不能作为实际 skill 证据。
- **人工确认、否决与修改**：人工审核要求在修订后暂停等待最终确认；未授权生成 PLAN、写代码、创建测试/Docker/CI 或进入实现。
- **课程流程偏离及理由**：无新增偏离。使用真实审核处理 skill；Open Design 的选定 skill 尚未在前端工作中调用，因此未伪称已使用。
- **学到的教训**：Diff 不落盘不足以保护凭据；Finding、AI 文字、导出和日志必须共享同一脱敏边界。运行模式隔离也必须同时体现在数据流、路由注册、持久化和验收条件中。

## 2026-08-08 20:38:17 +08:00 — 阶段：PLAN 生成 / 待用户确认

- **Task / 当前工作**：用户确认修订后的 SPEC 后，生成完整 `PLAN.md`；不执行计划。
- **使用的 Superpowers skill**：实际使用 `superpowers:writing-plans`，并按其要求提供任务分解、接口、依赖、worktree/分支、RED–GREEN–REFACTOR、两阶段评审和执行交接。
- **关键 prompt / context**：PLAN 必须满足 `AGENTS.md`：每 task 可由新鲜 subagent 独立完成，含精确路径、失败测试、验证、worktree/分支、依赖/并行；当前阶段仍禁止创建实现、测试、Docker、CI 或迁移。
- **智能体建议与处理**：将计划拆为 19 个 task，覆盖后端核心、规则/脱敏、持久化/保险箱、Provider/模式 API、Open Design UI、前端、容器、双 CI 和文档；每 task 需先由 fresh subagent 在隔离 worktree 执行并经历 spec 合规、代码质量两轮评审。
- **人工确认、否决与修改**：用户确认修订 SPEC，授权生成 PLAN；未授权执行 T01、创建 worktree、启动冷启动或进入实现。
- **课程流程偏离及理由**：`writing-plans` 通常包含可执行测试/实现示例；为遵守当前阶段禁令，PLAN 改为非可执行测试规格、未来命令和预期 RED 条件，未生成代码。该偏离仅限格式，不减少计划中的 TDD/验证要求。
- **自检与教训**：已验证 19 个唯一 task、SPEC 覆盖、共享接口一致性、无未完成红旗占位符（唯一 TODO 为规则名）及无 diff 空白错误。详细实施计划必须在表达足够精确和不提前生成受禁代码之间保持边界。

## 2026-08-08 21:43:14 +08:00 — 阶段：最终确认前跨文档工程一致性修订 / 待用户快速核验

- **Task / 当前工作**：根据用户对 SPEC/PLAN 的最终确认前复审，处理统一容器分发、Docker admin 网络边界、前端 HTTP 客户端和 Reflection AI 润色的矛盾；不启动冷启动或实现。
- **使用的 Superpowers skill**：实际按 `superpowers:receiving-code-review` 的“先核验、再处理”流程审阅人工反馈；未调用实现、TDD、worktree 或部署 skill。
- **关键 prompt / context**：用户指出 M17 双镜像与 M18 单 `IMAGE_REF` 矛盾、容器 localhost 与 Docker Desktop 端口映射矛盾、Axios/fetch 二义性及 Reflection 对 AI 润色前后冲突；要求只进行文档与真实过程日志修订。
- **核验与智能体建议**：重新读取课程文件，确认容器应支持单条 `docker build` + 单条 `docker run`，并确认 Reflection 必须学生本人撰写但可使用已标注的 AI 润色。建议将正式分发固定为一个 root multi-stage OCI image，并将 Docker 私有 admin 防护定位为“宿主机 loopback-only publish”，而非“容器内绝对 loopback”。
- **用户确认、否决与人工修改**：用户要求锁定统一 production image、修复 Docker admin 边界、固定 native `fetch`、修复 Reflection 规则；同意 Open Design compatibility gate 保持为未决风险门禁，要求 M13 在前端视觉实现前解决。用户还指出应允许记录 `AGENT_LOG.md`；实际 `AGENTS.md` 已包含该允许项，故未作重复改动。
- **课程流程偏离及理由**：无新增偏离。当前阶段仍禁止 Dockerfile、Compose、CI、测试、代码、镜像和部署资产；文档中的 build/run 命令均为未来验收契约，未执行或伪造成证据。
- **学到的教训**：容器安全边界必须从宿主机公开面而非容器自身 localhost 判断；同时，分发镜像的数量、Compose 结构、Registry 标签和验收命令必须先统一，否则陌生智能体会按照互相冲突的正确片段做出错误系统。

## 2026-08-08 22:02:36 +08:00 — 阶段：Open Design 设计阶段兼容性 closure / 未通过

- **Task / 当前工作**：在最终确认和冷启动前，真实核验并固定前端项目的 Open Design system 与 skill；不创建业务资产。
- **使用的 Superpowers skill**：实际阅读并遵循 `skill-installer` 的安装流程说明；未调用任何未安装的 Open Design skill。
- **关键 prompt / context**：用户要求现在而非 M13 之后解决“SPEC 须说明所选 Open Design design system 与 skill”的课程规约缺口；若不可用，必须保留真实证据且不得声称已满足。
- **实际检查与智能体建议**：上游目录核对后选定 Open Design `linear-app` 设计系统（`design-systems/linear-app/DESIGN.md`）和 `web-design-guidelines` skill（`skills/web-design-guidelines/SKILL.md`）。本地检查未发现 `od` 命令或已安装 skill；经授权的直接安装命令超时；随后 Git 连通性检查返回“Recv failure: Connection was reset”。建议把这视为未通过门禁，而非擅自以 MUI/`visualize` fallback 取代。
- **用户确认、否决与人工修改**：用户要求将具体选择和真实状态同步至 SPEC、PLAN、SPEC_PROCESS，并把 M13 改为只基于既定选择产出 UI 设计；没有授予实现、冷启动、框架、测试、容器、CI、数据库或部署权限。
- **课程流程偏离及理由**：无。当前 `AGENTS.md` 已允许更新 `SPEC_PROCESS.md` 与 `AGENT_LOG.md`，故如实记录；没有安装成功、没有调用 Open Design，也没有伪造课程方 fallback 批准。
- **学到的教训**：上游项目中存在设计系统或 skill 只能完成“选择”，不能完成“可调用/已使用”的过程证据；课程门禁需要区分精确选型、真实安装/调用与外部 fallback 批准三种状态。
- **文档自检**：实际检查确认现行 SPEC/PLAN 均显示“未通过”；M13 只保留基于既定选择的 UI/可访问性工作，正式 task 计数为 106、无重复编号，`git diff --check` 无空白错误。历史中的 `Linear`/`live-dashboard` 仅以已更正的早期草案形式保留。

## 2026-08-08 22:46:47 +08:00 — 阶段：用户确认 / Open Design 门禁关闭

- **Task / 当前工作**：记录用户对 SPEC/PLAN 的明确确认，重新核验并真实使用已选 Open Design system/skill，关闭冷启动前门禁；不进入实现。
- **使用的 skill**：实际使用本机 `web-design-guidelines`：读取 `SKILL.md` 与 pinned `references/guidelines.md`，审阅 `SPEC.md` 的 UI 要求；不调用任何业务实现、测试或容器 skill。
- **关键 prompt / context**：用户确认后，流程要求先关闭 Open Design 门禁，系统固定为 `linear-app`、skill 为 `web-design-guidelines`。当前阶段没有 UI 代码，故审阅对象是已有 UI 规约而非虚构的前端文件。
- **真实产出与人工修改**：从 Open Design 上游实际读取 `design-systems/linear-app/DESIGN.md`；将其不涉及品牌复制的桌面深色分层、克制强调、技术文本与密度原则写入 SPEC §6.3.1。skill 审阅指出语义控件/标题、`:focus-visible`、`aria-live`、首错焦点、粘贴和减弱动效的规约缺口，已补入 SPEC §6.3。用户没有授权任何 UI 代码、截图或测试。
- **门禁状态**：`linear-app` 作为 `DESIGN.md` 资源已被实际读取并用于规约，`web-design-guidelines` 已安装且被实际用于该规约审阅；source/context/产出已留痕，故门禁关闭。此前无 `od` CLI、安装超时和 Git 重置的历史证据未被删除或伪造为从未发生。
- **下一步与限制**：下一步为不同类型陌生智能体的冷启动试运行；冷启动不是实现授权，仍不得创建业务代码、测试、Docker、CI、迁移、数据库或部署资产。

## 2026-08-08 22:55:00 +08:00 — 阶段：陌生智能体冷启动试运行 1 / T01.1 暂停

- **Task / 当前工作**：按已确认 SPEC/PLAN 执行首个只读冷启动验证；要求陌生智能体从计划中选择 1—2 个微任务、遇不确定立即停止。
- **智能体与上下文边界**：使用新的 `gpt-5.6-sol` session（`fork_turns=none`）；只提供 `SPEC.md` 与 `PLAN.md` 路径，不传入主对话/memory 或项目解释。智能体未读取其他项目文档、未写文件、未运行命令。
- **选择与暂停**：智能体选 `T01.1`，在 `test_create_app_boots_private_mode` 的 RED 设计处暂停：`create_app` 的 mode 来源、调用签名与唯一最小断言未定义，而 settings 校验被排在 T01.3。
- **人工/智能体修订**：采纳暂停结果，将共享合同和 T01.1/T01.3 固定为显式 `AppSettings` 注入、`create_app(settings)`、`app.state.settings.mode` 可观察性与唯一 `load_settings(env)`/`APP_MODE` 入口；补足基础依赖/lockfile范围。修订前后差异已写入 `SPEC_PROCESS.md` 及 `docs/cold-start/2026-08-08-cold-start-probe-01.md`。
- **限制与教训**：该试运行没有产生代码，因此没有正式实现成果。课程要求为 1—2 个 task，本次已完成其中 1 个；现在需由用户审核冷启动修订并自行决定是否解除限制。教训是应用工厂、配置来源与首个可观察测试合同必须在同一最小任务中定死，不能推迟给后续设置任务。

## 2026-08-08 23:09:06 +08:00 — 阶段：解除限制前人工审核修订 / 仍禁止 T01

- **Task / 当前工作**：根据人工审核清除过时冷启动状态，并补齐纯应用工厂与生产 ASGI/Docker bootstrap 的合同；不开始 T01。
- **使用的 Superpowers skill**：实际使用 `receiving-code-review`，先核验 PLAN 顶部、§7、§9、§10、SPEC §11 和既有工厂合同后再修订。
- **审核采纳与修订**：将现行状态统一为 Open Design 已关闭、Probe 01 已完成/暂停/修订、只待用户最终确认与明确解除限制。新增 `create_runtime_app() -> FastAPI = create_app(load_settings(os.environ))`；缺失或非法 `APP_MODE` 均启动失败；生产 ASGI/Docker 均只用此 factory。新增 T01.4 的精确 RED/GREEN 节点，T01.1 增加 Uvicorn，正式 task 总数更新为 107。
- **真实过程边界**：Probe 01 是只读分析，无试运行代码，因此没有 branch/worktree 清理对象；PLAN 保留未来若生成试运行代码时的 worktree 规则。未创建或运行 apps、测试、Docker、CI、迁移、数据库或部署资产。
- **下一步与限制**：仅等待用户最终确认修订后的 SPEC/PLAN，并明确解除 `AGENTS.md` 阶段限制；未收到该授权前不得执行 T01。

## 2026-08-08 23:14:05 +08:00 — 阶段：冷启动修订用户最终确认 / 仍待解除限制

- **用户确认**：用户明确回复“行，最终确认了”，确认经 Probe 01 反馈修订后的 SPEC/PLAN。
- **权限判断**：`AGENTS.md` 要求用户明确解除阶段限制才可开始实现；本次回复没有包含解除限制或授权开始 T01 的表述，因此不能推断为实现授权。
- **当前状态**：已同步 SPEC/PLAN 状态为“用户最终确认完成，仅待明确解除 `AGENTS.md` 限制”；未创建或执行任何实现资产。

## 2026-08-08 23:21:31 +08:00 — 阶段：实现授权 / T01 启动准备

- **用户授权**：用户明确指示“解除 AGENTS.md 阶段限制，授权开始 T01 实现”。这是此前唯一未满足的解锁条件，不能以较早的“最终确认”替代。
- **使用的 Superpowers skill**：实际读取并采用 `using-superpowers`、`executing-plans`、`using-git-worktrees`、`subagent-driven-development`、`test-driven-development` 和 `verification-before-completion` 的执行约束；实现将使用 fresh subagent、TDD、隔离 worktree 与每任务双阶段评审。
- **实际修订**：将 `AGENTS.md` 切换为实现阶段约束；同步 `SPEC.md`、`PLAN.md` 当前状态与执行交接，记录阶段限制已经由用户解除而非智能体自行宣布。
- **范围与红线**：当前仅启动 T01，后续任务和外部交付均未发生、未预先声明完成；`REFLECTION.md`、伪造证据、凭据/私有 Diff 泄露和未经授权的外部推送/发布仍继续禁止。

## 2026-08-09 00:00:53 +08:00 — 阶段：T01.1 环境预检 / 阻塞

- **Task / 当前工作**：在 `codex/foundation` 隔离 worktree 中开始 T01.1 前，核验 PLAN 所固定的 Python 3.12 运行时；尚未创建 `apps/`、实现代码、测试或依赖文件。
- **使用的 Superpowers skill**：实际采用 `using-git-worktrees`、`subagent-driven-development`、`test-driven-development` 与 `verification-before-completion` 的前置要求。创建了 Git 忽略的 SDD 账本和唯一 T01.1 简报；原 SDD shell helper 因 Windows 环境拒绝运行 `bash.exe`，故按其目录/账本约定手工建立等价过程文件，并保留该偏离事实。
- **真实证据**：`py -3.12 --version` 返回 “No suitable Python runtime found”；`py -0p` 仅列出 Python 3.13。曾在用户授权下调用 `winget install --id Python.Python.3.12 --exact --source winget --accept-package-agreements --accept-source-agreements`，命令窗口在 120 秒后超时；随后解释器仍不可用，未把 3.13 作为 `>=3.12,<3.13` 目标环境替代。
- **subagent 过程**：已派发一个 fresh T01.1 实现 subagent，要求先做只读 `py -3.12` 预检；其未能在合理时间内完成阻塞报告，已中断，未采纳其任何未验证实现结论，也未允许其创建项目文件。
- **阻塞与下一步**：T01.1 的 RED/GREEN 必须在 Python 3.12 运行，当前不能诚实执行。等待目标解释器可用后，再由新的 fresh implementation subagent 从 T01.1 的失败测试开始；不回填 PLAN commit hash、不开始 T01.2–T01.4。
