反思
1. Superpowers 工作流：价值与成本
这次项目里，我认为 TDD、review、worktree、subagent 和 verification 的主要价值，是给 AI 设定明确边界，让实现过程可验证、可追踪，也减少随意扩展需求、修改无关代码或在没有证据时直接宣称完成的情况。尤其是两阶段 review 和最终 verification，让我逐渐认识到“代码能跑”和“功能真正完成”不是一回事，本地测试通过也不等于 Docker、CI、镜像发布和公网部署一定可靠。但流程并不是越细越好。前期 PLAN 一度被拆成一百多个微任务，随之产生大量 worktree、分支、测试、review、commit 和日志记录，反而让我更难掌握整体进度。我因此认为，Superpowers 的价值不在机械执行所有步骤，而在于用流程约束 AI、留下真实证据并及时暴露偏差；如果流程成本超过风险控制收益，它本身也会成为新的复杂度。
2. TDD：放大器，也有边界
TDD 对我既是帮助也是负担。对于 API、前端交互和边界条件明确的任务，RED→GREEN 很有效。例如 /ready 的测试先规定 Demo 与 private 模式返回不同的 mode，让我发现前端不应依赖 VITE_APP_MODE 自己判断，而应读取后端真实运行状态；ModeGate 的测试又明确了 Demo 下 Vault/private controls 不渲染、未知 mode 必须 fail closed，Demo 访问 private/Vault route 返回 404。这些测试把安全边界直接变成了可验证行为。
但 JS-007 让我看到另一面。一个最初只是检测显式 any 的规则，随着 TSX、泛型箭头函数、嵌套对象等测试不断增加，逐渐逼近 tokenizer 或 AST 分析。此时继续“把测试做绿”已经不等于继续创造价值。这个案例让我意识到，TDD 不只是帮助实现功能，也会提供证据，让我重新判断设计是否合理。需求稳定时它是放大器；需求本身不稳定时，机械坚持 RED→GREEN 也会扩大流程成本，必要时应该及时缩减范围。
3. Task 颗粒度与 subagent 自主性
一开始我把任务拆得很细，是为了让每一步都有清晰责任边界，方便 subagent 独立执行、测试、review 和回滚。实际推进后我发现，如果把同一个功能的 API、前端、测试、文档和配置机械拆开，会产生大量重复上下文和协调成本，也容易让 subagent 只看到局部。后来把一百多个任务收敛成更少的正式任务后，工作流明显更连续。现在我认为，一个合适的 task 应该是“一个明确目标 + 一组相关模块 + 一个可验证结果”，而不是按文件或命令机械切分。
只要目标、接口和验收标准已经确定，subagent 可以自主完成较长的 RED、GREEN、测试、review 修复和验证链路，例如 /ready、ModeGate 和 Demo 下不注册 Vault/private route。但一旦涉及 scope 扩大、架构冲突、安全边界或外部授权，就必须交回人工判断，例如是否继续 JS-007、如何定义 Provider trust boundary、是否恢复 CUT 功能，以及 GHCR 发布、创建 tag、push、合并和 Railway 部署等操作。
4. SPEC / PLAN 如何影响实现质量
Provider trust boundary 是我感受最明显的案例。最初 SPEC/PLAN 虽然要求校验 Provider 的结构化结果，但没有明确“Provider 返回的所有内容，即使已经是 Pydantic 对象，也必须视为不可信输入”。因此实现一度直接信任 SanitizedFinding 等已构造对象。后来的安全复审使用 model_construct() 构造非法对象，证明部分校验可以被绕过。后来规约被明确为：Provider 结果先递归转换为普通 Python 数据，再通过唯一的 ProviderReviewResult schema 整体重新校验；任意 Finding 不合法，整批结果映射为 INVALID_RESPONSE，不能部分进入报告。这个经历让我认识到，SPEC/PLAN 不只是功能清单，还要明确数据从哪里开始不可信、在哪一层验证、失败后如何处理。同时，规约也不是越详细越好，如果最初的假设本身错误，更多细节只会让 agent 更稳定地执行错误设计。
5. Prompt / Context Engineering
我最有效的策略，是把 prompt 写成一份“可执行的小型合同”：明确目标、相关文件、前置依赖、允许和禁止的范围、RED 测试、GREEN 验收标准、需要留下的证据，以及遇到架构冲突时必须暂停的条件。例如明确不得新增 Provider、不得恢复 CUT 功能、不得让 Demo 接入真实 OpenAI。这样可以减少 scope 漂移，也让 review 有客观标准。我也发现 context 不是越多越好，最有效的是分层提供共享原则、当前 task 直接相关的规约和接口，再明确哪些内容不属于本任务。过多历史会稀释重点，过少背景又会造成局部正确、整体错误。
6. 凭据、安全与交付
安全、Docker、CI、分发和部署让我认识到，工程交付不等于“本地能运行”。真正可交付的系统还要回答数据能否外发、哪些路由在哪种模式下存在、密钥如何保存以及失败时是否会泄露信息。ReviewLens 的 Demo 只能使用 Mock，Vault/private routes 由后端模式边界控制，前端隐藏控件不能代替安全措施。Docker 让我认识到镜像本身也是交付合同，不仅要能 build，还要确认运行时、端口、linux/amd64 架构，并在干净环境 fresh pull/run。CI 则把安装、测试和质量要求变成可重复证据；GHCR、Railway 和公网 smoke test 又说明外部发布必须经过真实验证。因此我现在会把“实现完成”和“交付完成”分开判断。
7. 如果重新做一次
如果重做 ReviewLens，我会更早同时确定范围、架构和交付目标，更早划分 P0、P1 和 CUT，不再让 PLAN 膨胀成一百多个微任务。第一阶段就建立纵向闭环：浏览器提交最小 Diff，后端确定性扫描，API 返回，前端展示，再到 Docker 启动和 smoke test。安全边界也应更早成为架构主线，Provider 不可信输入、Demo/private 隔离和 Vault 设计都应提前确定。Docker、Makefile、GitHub Actions、GitLab CI、GHCR 和 Railway 也应该更早接入，而不是最后集中处理。TDD、review 和 verification 我仍会保留，但它们应该服务于 P0 交付，而不是让流程本身成为项目的主要工作量。
8. 对 Superpowers / agentic SE 的最终判断
我最终认为，Superpowers 最大的价值不是让 AI 一次写更多代码，而是让 AI 的行为更可控、可验证、可追踪。我以后会保留 TDD、明确任务合同、规约审查、代码质量 review、verification 和真实交付证据，但不会机械照搬过细 task、过多 worktree 和重复日志。AI 更适合作为一个在明确边界内高速执行的协作者，而不是完全自主的工程师；人的价值更集中在目标定义、架构判断、安全决策、风险管理和交付取舍。
从这次项目看，Superpowers 隐含地假设任务可以被相对清晰地拆分、规约和测试能够在执行前给出稳定边界，并且额外流程成本能够换来更高可靠性。这些假设在 /ready、ModeGate 等边界清楚的任务上成立，但在 JS-007、Provider trust boundary 和后期 scope reduction 中只部分成立。软件工程不只是把功能写出来，还包括把需求变成边界，把边界变成测试，把测试变成证据，再把系统安全、稳定、可重复地交付给别人。AI 可以承担越来越长的技术执行链，但人仍然要判断什么值得做、什么应该停止，以及什么时候系统才真正算完成。

AI 辅助说明
本文观点、项目经历、案例和初始素材由本人完成；使用 ChatGPT 对本人已有素材进行了结构整理、删减和语言润色，未使用 AI 补写新的项目经历或事实。
