# ReviewLens

面向个人学生开发者的 Git Diff 风险审查工具：固定确定性规则先给出可重复结论，private 模式可选附加一次 OpenAI 建议，Demo 固定使用无网络 Mock。

## 当前规则范围与已知限制

首期通用规则为 `GEN-001` 至 `GEN-005`，JavaScript / TypeScript 专项规则固定为 `JS-001` 至 `JS-006`。`JS-007`（显式 `any`）已在 2026-08-12 经批准的 scope revision 中移除：在不引入 tokenizer、AST、TypeScript Compiler 或外部解析依赖的架构边界内，它不能同时可靠区分 TSX 嵌套 JSX、泛型箭头函数和嵌套对象默认值。未报告 `any` 不代表不存在代码质量风险。

v1 只处理当前一次审查：服务端不保存 Diff、Report、Finding、摘要或历史记录；刷新后结果消失。Markdown 仅由浏览器根据当前已脱敏结果即时生成。v1 不支持 AI retry、历史 UI、筛选 UI、服务端导出缓存或 Docker Compose。

private 模式的 API key 仅以主密码加密 Vault 文件保存，默认锁定；private app 只可从本机 loopback 使用。公开 Demo 固定为 `APP_MODE=demo`、Mock、无状态，且不注册 Vault/private 路由。

## 分发与验证状态

计划交付一个 `linux/amd64` OCI image，并以单条 `docker build` 和分别的 Demo/private `docker run` 命令运行；Windows 11 x64 + Docker Desktop 是本地支持环境。Docker image、公开 Registry、CI、NJU GitLab Pipeline 和公网 Demo URL 尚未产生，后续只会在真实验证后记录。

## 安装

需要 Python 3.12、Node.js 22、npm、GNU Make 和 Docker Desktop。Linux/macOS 或 CI 中可运行：

```sh
make install
```

Windows 当前开发环境可分别运行 API lockfile 和 Web lockfile 安装；不要将 `.env`、Vault、真实 API key 或私有 Diff 提交到仓库。

## 运行

构建统一镜像后，Demo 使用 Mock 且不注册 Vault 路由：

```sh
docker buildx build --platform linux/amd64 --load -t reviewlens:test .
docker run --rm -p 8080:8080 -e APP_MODE=demo reviewlens:test
```

私有模式只应发布到本机回环地址：

```sh
docker run --rm -p 127.0.0.1:8080:8080 -v reviewlens-private:/data -e APP_MODE=private reviewlens:test
```

私有 Vault 的主密码和 API key 只能通过本机私有页面提交；不要在公开 Demo、命令历史、日志或仓库文件中填写真实凭据。

## 安全边界

- Demo 是无状态 Mock，不保存审查结果，不调用真实 OpenAI，不注册 Vault/private 路由。
- private Vault 仅设计为 loopback 服务边界；浏览器隐藏不是安全措施。
- `.dockerignore` 排除环境文件、Vault、密钥、运行数据和测试，以免进入镜像构建上下文。

## 已知限制

- 本机已验证 API、前端测试、Vite 生产构建、TypeScript 检查和 Docker 上下文排除检查。
- 当前机器找不到 `docker` 和 `make` 命令，因此尚未运行真实 `docker buildx`、容器 smoke 或 `make` 命令；公开 GHCR 镜像、远程 CI Pass 和 HTTPS Demo URL 均尚未产生。
- `REFLECTION.md` 必须由学生本人完成；相关过程边界见 `docs/reflection-evidence.md`。
