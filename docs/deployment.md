# 生产部署说明

本项目已补齐适合小型 VPS 的多容器部署文件，默认使用：

- `app`：FastAPI 后端容器
- `caddy`：同域 HTTPS 入口 + 反向代理

## 适用场景

- 2 核 2 GB 内存的小型香港 VPS
- 一个域名同时承载前端与 API
- 使用 Docker Compose 进行启动和重启

## 目录说明

- `Dockerfile`：后端镜像构建
- `docker-compose.yml`：生产编排
- `.env.production.example`：生产环境变量模板
- `deploy/Caddyfile`：Caddy 自动 HTTPS 配置

## 部署前准备

1. 复制环境变量模板：

```bash
cp .env.production.example .env.production
```

2. 编辑 `.env.production`，至少改掉：

- `SERVER_NAME`
- `DEEPSEEK_API_KEY` 或你实际使用的其他模型密钥
- `CORS_ALLOWED_ORIGINS`
- `ALLOWED_HOSTS`
- `SESSION_COOKIE_SECURE`

3. 确认域名 `A` 记录指向你的服务器公网 IP。
4. 确认服务器防火墙已放行 `80` 和 `443` 端口。

## 启动

```bash
docker compose up -d --build
```

说明：`Dockerfile` 已内置前端 Vite 构建阶段，生产部署不需要手动执行 `npm run build`。

## 推荐的版本管理与更新方式

推荐把 `L-ERAP-PRO` 作为一个独立 Git 仓库管理，然后服务器只做两件事：

1. `git pull` 拉最新代码
2. `docker compose up -d --build` 重建容器

建议流程：

```bash
# 本地第一次初始化仓库
git init -b main
git add .
git commit -m "chore: initial deploy-ready version"

# 绑定你自己的远程仓库
git remote add origin <你的仓库地址>
git push -u origin main
```

服务器首次按 Git 方式部署：

```bash
git clone --branch main <你的仓库地址> /opt/lerap-pro
cd /opt/lerap-pro
cp .env.production.example .env.production
# 填入真实生产密钥后再执行
bash scripts/deploy_server.sh
```

如果服务器里已经有仓库，只想切换成 Git 更新流程：

```bash
cd /opt/lerap-pro
bash scripts/deploy_server.sh
```

以后每次更新：

```bash
# 本地
git add .
git commit -m "feat: 你的更新说明"
git push

# 服务器
cd /opt/lerap-pro
bash scripts/deploy_server.sh
```

这样服务器不会自动改代码，只有你 `git push` 之后，服务器执行更新脚本才会切到最新版本。

## 检查

```bash
docker compose ps
docker compose logs -f app
docker compose logs -f caddy
```

浏览器访问：

- `http://你的域名`
- `https://你的域名`
- `http://你的域名/docs`
- `https://你的域名/docs`

## 当前默认安全策略

- 生产密钥不写入镜像，只从 `.env.production` 注入
- CORS 改为环境变量控制
- Host 头白名单改为环境变量控制
- Chroma、运行态 SQLite、日志、输出目录使用 Docker volume 持久化
- 登录会话使用 HttpOnly Cookie，`SESSION_COOKIE_SECURE=true` 时只允许 HTTPS 传输
- Caddy 自动申请和续期 HTTPS 证书

## 重要提醒

- 仓库中的旧 `.env` 不应用于生产。
- 如果旧密钥已经暴露或曾被提交，应该去对应模型平台后台作废并重新生成。
- 如果 Cloudflare 开启了代理，建议把 SSL/TLS 模式设为 `Full` 或 `Full (strict)`。
- `.env.production` 不要提交到 Git，只保留在服务器。
