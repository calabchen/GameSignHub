# GameSignHub

多游戏社区签到可视化管理工具

## 功能特性

- 支持鸣潮、战双帕弥什签到（库街区），米游社（骨架）
- 定时签到（cron 表达式）
- 签到日志查询与筛选
- 多账号管理
- 一键锁定/解锁，密码保护

## 环境要求

| 工具 | 版本 |
|---|---|
| Python | >= 3.11 |
| Node.js | >= 20 |

## 快速开始（本地开发）

### 1. 后端

```bash
uv venv
uv sync
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev     # 开发模式（端口 8001，代理 API 到 8000）
npm run build   # 生产构建
```

### 3. 访问

- 开发模式：`http://localhost:8001`
- 生产模式：`npm run build` 后访问 `http://localhost:8000`

## Docker 部署

### GitHub Actions 自动构建

推送 `main` 分支后自动构建并推送到 ghcr.io：

```bash
git push
```

### 服务器运行

```bash
# 登录
echo $GITHUB_TOKEN | docker login ghcr.io -u <用户名> --password-stdin

# 首次运行
docker run -d -p 8000:8000 \
  -v gamesignhub-data:/app/app/config \
  --name gamesignhub \
  ghcr.io/calabchen/gamesignhub:latest

# 更新
docker stop gamesignhub && docker rm gamesignhub
docker pull ghcr.io/calabchen/gamesignhub:latest
docker run -d -p 8000:8000 \
  -v gamesignhub-data:/app/app/config \
  --name gamesignhub \
  ghcr.io/calabchen/gamesignhub:latest
```

### 本地构建

```bash
docker build -t gamesignhub .
docker run -d -p 8000:8000 -v gamesignhub-data:/app/app/config --name gamesignhub gamesignhub
```

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11, FastAPI, SQLAlchemy, APScheduler |
| 前端 | Vue 3, Pinia, Element Plus, Vite |
| 存储 | SQLite (签到日志), YAML (账号凭证) |
| 部署 | Docker, GitHub Actions, ghcr.io |
