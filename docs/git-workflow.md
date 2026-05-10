# Git 版本管理与服务器更新

本项目推荐使用独立 Git 仓库管理，不再采用“本地改完后手工上传整个目录”的方式。

## 目标

- 本地负责开发、提交、推送
- Git 仓库负责保存版本历史
- 服务器负责拉取指定分支并重建容器

## 一次性初始化

在项目根目录执行：

```bash
git init -b main
git add .
git commit -m "chore: initial deploy-ready version"
git remote add origin <你的仓库地址>
git push -u origin main
```

## 日常开发

```bash
git status
git add .
git commit -m "feat: 描述本次修改"
git push
```

## 服务器更新

```bash
cd /opt/lerap-pro
bash scripts/deploy_server.sh
```

脚本会自动执行：

```bash
git fetch --all --prune
git checkout main
git pull --ff-only origin main
docker compose up -d --build
docker compose ps
```

## 生产环境文件

以下文件不要提交到 Git：

- `.env`
- `.env.production`
- `logs/`
- `output/`

真实生产密钥只保留在服务器的 `/opt/lerap-pro/.env.production`。

## 推荐提交信息

- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 重构
- `chore:` 维护性调整
