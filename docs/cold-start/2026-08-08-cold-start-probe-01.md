# 冷启动试运行记录 01：T01.1 应用工厂合同

**日期：** 2026-08-08

**会话隔离：** 新建 `gpt-5.6-sol` session，`fork_turns=none`；没有导入主智能体的对话或 memory。

**提供的项目材料：** 仅 `SPEC.md` 与 `PLAN.md`。未提供项目背景、口头设计解释或其他项目文档。

**执行限制：** 仅分析性试运行；不读取其他项目文档，不写文件，不创建代码、测试、框架、Docker、CI、worktree 或分支，也不运行实现命令。

## 选择的 task

智能体自主选择 `T01.1`。它在开始设计 `test_create_app_boots_private_mode` 时立即暂停。

## 暂停点、问题与产出差距

原 `PLAN.md` 未规定：

- `create_app` 通过显式参数、`APP_MODE` 环境变量还是默认值得到 `private` mode；
- 首个测试的唯一最小断言是 FastAPI 类型、模式状态、路由还是其他行为；
- T01.3 之后的 settings 校验是否会改变 T01.1 的应用工厂合同。

因此，不同执行者会写出不兼容的工厂签名和测试，后续 T01.3 可能返工 T01.1，无法精确执行 RED → GREEN。

智能体还指出 `pyproject.toml` 未写出最小依赖/版本锁定范围；该点已一并纳入修订。

## 实际修订

PLAN 现固定：

1. `create_app(settings: AppSettings) -> FastAPI`；工厂自身不读取环境变量；
2. T01.1 通过 `AppSettings(mode="private")` 显式注入，并断言 FastAPI 实例与 `app.state.settings.mode == "private"`；
3. T01.3 的 `load_settings(env)` 是唯一读取/校验 `APP_MODE` 的入口，且不得改变工厂签名；
4. T01.1 明定 Python 范围、FastAPI/Pydantic v2/pytest 的有界依赖声明和实际 lockfile。

后续人工审核进一步补足了运行时入口：新增 T01.4，固定 `create_runtime_app() -> FastAPI` 仅组合 `create_app(load_settings(os.environ))`；缺失或非法 `APP_MODE` 在启动前失败，生产 ASGI/Docker 仅通过此 factory 启动。T01.1 的基础运行时依赖同时补入 Uvicorn。

## 结论

试运行成功暴露并促成修订一个真实规约缺陷；没有产生或保留任何试运行代码。课程要求为 1—2 个 task，本记录已覆盖其中 1 个；修订后的 `SPEC.md`/`PLAN.md` 仍待用户确认，正式实现仍未获授权。
