# ReviewLens

ReviewLens 是一个面向个人开发者的 Git unified diff 风险审查工具。它对本次提交的新增代码运行固定规则，返回可重复的风险结论，并在 private 模式下可选调用一次 OpenAI 建议。公开 Demo 固定使用无网络 Mock，不调用真实 OpenAI。

当前 v1 规则范围为 `GEN-001` 到 `GEN-005`，以及 JavaScript/TypeScript 的 `JS-001` 到 `JS-006`。每次审查只处理当前请求，服务端不保存 Diff、报告或历史记录；浏览器可将当前已脱敏结果导出为 Markdown。

## 安装

本地开发需要 Python 3.12、Node.js 22、npm、GNU Make 和 Docker Desktop（Linux containers）。

```sh
make install
```

`make install` 安装 API 的锁定依赖和 Web 的锁定依赖。也可以分别执行：

```sh
python -m pip install -r apps/api/requirements.lock
cd apps/web && npm ci
```

## 运行

### Demo 模式

Demo 使用 Mock、无状态且不注册 Vault/private 路由：

```sh
docker buildx build --platform linux/amd64 --load -t reviewlens:test .
docker run --rm -p 8080:8080 -e APP_MODE=demo reviewlens:test
```

打开 <http://localhost:8080>。就绪检查为 `GET /ready`；Demo 应返回 `{"status":"ready","mode":"demo"}`。

### Private 模式

Private 模式只绑定本机 loopback。Docker 运行时使用单一 `8080` 端口，但只向宿主机的 `127.0.0.1` 发布：

```sh
docker run --rm -p 127.0.0.1:8080:8080 \
  -v reviewlens-private:/data \
  -e APP_MODE=private \
  reviewlens:test
```

Private 模式的 Vault 管理页面通过浏览器录入、初始化、解锁、更新、锁定和清除凭据。Demo 不会挂载或请求这些 controls。

## 分发与获取

已发布并验证的公开镜像：

```sh
docker pull ghcr.io/lixiaozhou0222/reviewlens:0.1.0
docker run --rm -p 8080:8080 -e APP_MODE=demo \
  ghcr.io/lixiaozhou0222/reviewlens:0.1.0
```

`ghcr.io/lixiaozhou0222/reviewlens:0.1.0` 是已经发布并完成 `linux/amd64` fresh pull/run 验证的镜像。需要本地构建时使用上面的 `docker buildx build` 命令。

## 目录结构

```text
reviewlens-ai4se/
├── apps/
│   ├── api/                 # FastAPI 应用、领域逻辑、规则、Provider 和后端测试
│   └── web/                 # React/Vite 前端、ModeGate、Vault UI 和前端测试
├── scripts/                 # 容器、CI、文档、部署授权和公网 smoke 校验脚本
├── docs/                    # 课程要求、设计文档、冷启动和发布验证证据
├── Dockerfile               # Node 22 前端构建与 Python 3.12 runtime 的 multi-stage 镜像
├── Makefile                 # install、test、lint 和 build 的统一入口
├── .github/workflows/       # GitHub test 与 GHCR release workflows
├── .gitlab-ci.yml           # NJU GitLab 的 unit-test pipeline
├── SPEC.md                  # 已确认的产品规约与安全边界
├── PLAN.md                  # 正式任务账本和发布门禁
├── SPEC_PROCESS.md          # 规约设计、修订和冷启动过程
├── AGENT_LOG.md             # 实际实现、验证、人工决策和外部证据
└── REFLECTION.md            # 学生本人撰写的课程反思报告
```

`apps/api` 是后端唯一的模式、路由和脱敏边界；`apps/web` 负责输入、当前结果、浏览器 Markdown 导出和 private Vault 页面；`scripts` 与 `docs/verification` 保存可复核的交付检查，不承担产品运行时逻辑。

## 安全边界与 key 配置

- Demo 固定为 `APP_MODE=demo`、Mock、无状态，不调用真实 OpenAI，不注册 Vault/private routes。
- Private 模式的 Vault 文件使用主密码派生密钥和 AES-256-GCM 加密；解锁后的 API key 只保留在进程内存，锁定或重启后清除。
- private 应用只应通过 `127.0.0.1`、`::1` 或 Unix socket 暴露。公网部署只能使用 Demo 模式。
- 在目标机器上配置 key 时，先用 private 模式启动应用，再从本机私有页面录入主密码、API key、provider 和 model。应用只显示是否存在、是否解锁、provider、model 和四字符掩码尾部，不回显完整 key。
- Vault 数据目录应通过受保护的本地 Docker volume 或受限文件目录挂载到 `/data`。不要把 key、主密码、Vault 文件、`.env`、完整 Diff 或日志提交到 Git、写入镜像、命令历史或公开服务。
- 本项目不提供账户系统、团队权限、报告历史、远程仓库访问或用户代码执行能力。

## 部署架构与 CI/CD

### 应用架构

```text
Browser
   |
   v
FastAPI
   ├── 静态提供 React/Vite build
   └── Review API
```

项目交付一个 multi-stage OCI 镜像：Node 22 阶段构建 `apps/web`，Python 3.12 阶段安装 API 锁定依赖并运行 FastAPI。镜像目标为单一 `linux/amd64`，容器对外使用端口 `8080`。运行时通过同一个 `APP_MODE` 配置决定 Demo/private 路由注册，前端请求 `/ready` 并读取响应中的 `mode` 字段确认后端实际运行模式。

### Railway Demo

已验证的公网 Demo 部署在 Railway：

- URL：<https://reviewlens-demo-production.up.railway.app>
- `APP_MODE=demo`
- Mock provider、无状态
- 未配置真实 OpenAI API key、Vault、数据库或 volume
- `/ready` 返回 `mode=demo`
- `/admin/v1/vault/status` 返回 `404`

### GitHub Actions

- `.github/workflows/test.yml` 在每次 `push` 和 `pull_request` 触发。
- `unit-test` 使用 Python 3.12、Node 22 和 `APP_MODE=demo`，执行 `make install` 与 `make test`。
- `.github/workflows/release.yml` 只在推送匹配 `v*` 的 tag 时触发，使用 Buildx 发布 `linux/amd64` GHCR image。
- 已验证的发布镜像为 `ghcr.io/lixiaozhou0222/reviewlens:0.1.0`；当前 tag 的发布证据和 digest 记录在 `AGENT_LOG.md`。

### NJU GitLab CI

`.gitlab-ci.yml` 定义了课程要求的 `unit-test` job。它使用 Python 3.12、Node 22.16.0 和 `APP_MODE=demo`，执行 `make install` 与 `make test`。GitLab Pipeline 和 job 的真实链接只在实际运行后记录在 `AGENT_LOG.md`。

## 测试与验证

```sh
make test
make lint
```

`make test` 运行后端 pytest 和前端 Vitest；`make lint` 运行前端 TypeScript 检查；`make build` 先构建前端，再构建 `linux/amd64` 镜像。

## 已知限制

- v1 只处理当前一次审查，不保存 report、Finding、Diff 或历史记录。
- 不支持 report history、retry、筛选 UI、Docker Compose、SQLite、SQLAlchemy、Alembic 或 JS-007。
- AI 是单次可选 augmentation；不提供自动 retry、工具调用、Agent 自主循环或执行用户代码能力。
- Private 模式应保持 loopback 暴露；Railway 公网实例仅允许 Demo/Mock。
- 从源码开发需要 Python 3.12、Node.js 22、npm 和 GNU Make；构建 `linux/amd64` OCI image 需要 Docker 和 Buildx。直接运行已发布的 GHCR image 只需要能够运行 `linux/amd64` 镜像的 Docker/OCI runtime，不需要安装 Python、Node.js、Make 或 Buildx。
- `REFLECTION.md` 是学生本人撰写的 1,500–2,500 字课程反思，智能体不生成或代写其正文。

## 过程文档

规约、计划、设计过程、实现日志和验证证据分别见 `SPEC.md`、`PLAN.md`、`SPEC_PROCESS.md`、`AGENT_LOG.md` 和 `docs/verification/`。`REFLECTION.md` 由学生本人完成。
