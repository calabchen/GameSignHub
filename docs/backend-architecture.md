# GameSignHub 后端架构规划

> 版本: v1.0
> 许可证: GPL-3.0
> Python: 3.11+
> 包管理器: uv

---

## 一、项目定位

本地运行的多游戏社区签到可视化管理工具。

- 插件式架构，每个游戏平台（米游社、库洛等）是一个独立插件
- 单密码解锁 + AES-256-GCM 加密存储用户凭据
- FastAPI 后端 + Vue 3 前端，仅本地访问
- Docker 和本地两种部署方式

---

## 二、目录结构

```
GameSignHub/
├── pyproject.toml                  # 项目元数据 + 依赖管理 (uv)
├── Dockerfile                      # 多阶段构建
├── docker-compose.yml              # 本地一键部署
├── .env.example                    # 环境变量模板
├── .gitignore
├── LICENSE                         # GPL-3.0
├── README.md
│
├── app/                            # FastAPI 后端
│   ├── __init__.py
│   ├── main.py                     # FastAPI 入口，lifespan 管理
│   ├── config.py                   # Pydantic Settings
│   ├── database.py                 # SQLAlchemy async engine + session
│   │
│   ├── models/                     # SQLAlchemy ORM 模型
│   │   ├── __init__.py
│   │   ├── credential.py           # 加密凭据表
│   │   └── sign_log.py             # 签到日志表
│   │
│   ├── schemas/                    # Pydantic 请求/响应
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── plugin.py
│   │   ├── credential.py
│   │   ├── sign.py
│   │   └── log.py
│   │
│   ├── core/                       # 核心业务
│   │   ├── __init__.py
│   │   ├── auth.py                 # 密码验证 + 密钥派生
│   │   ├── vault.py                # Credential Vault (加密/解密)
│   │   ├── plugin_base.py          # BaseGamePlugin 抽象基类
│   │   ├── plugin_loader.py        # 插件发现 + 加载
│   │   ├── orchestrator.py         # 签到编排器
│   │   ├── push.py                 # 推送通知模块
│   │   └── scheduler.py            # APScheduler 定时任务
│   │
│   ├── routers/                    # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py                 # POST /api/unlock, /api/lock
│   │   ├── plugins.py              # GET /api/plugins
│   │   ├── credentials.py          # CRUD /api/credentials
│   │   ├── sign.py                 # POST /api/sign/*
│   │   ├── logs.py                 # GET /api/logs
│   │   ├── schedule.py             # GET/PUT /api/schedule
│   │   └── push_config.py          # GET/PUT /api/push-config
│   │
│   └── utils/
│       ├── __init__.py
│       ├── encryption.py           # AES-256-GCM 加解密工具
│       └── ws_logger.py            # WebSocket 日志广播
│
├── plugins/                        # 内置官方插件
│   ├── mhy_plugin/
│   │   ├── __init__.py
│   │   ├── plugin.py               # MhyPlugin(BaseGamePlugin)
│   │   ├── client.py               # MhyHttpClient (DS 签名)
│   │   ├── bbs.py                  # 论坛签到/任务
│   │   ├── captcha.py              # 验证码处理
│   │   ├── models.py               # 插件内部数据类
│   │   ├── pyproject.toml          # 独立依赖声明
│   │   └── games/                  # 每个游戏一个文件
│   │       ├── __init__.py
│   │       ├── base.py             # BaseGame 基类
│   │       ├── genshin.py          # 原神
│   │       ├── honkai_sr.py        # 崩坏星穹铁道
│   │       ├── zzz.py              # 绝区零
│   │       ├── honkai3rd.py        # 崩坏3
│   │       └── honkai2.py          # 崩坏2
│   │
│   └── kuro_plugin/
│       ├── __init__.py
│       ├── plugin.py               # KuroPlugin(BaseGamePlugin)
│       ├── client.py               # KuroHttpClient
│       ├── forum.py                # 论坛任务
│       ├── models.py
│       └── games/
│           ├── __init__.py
│           ├── base.py
│           ├── wuwa.py             # 鸣潮
│           └── pgr.py              # 战双
│
├── user_plugins/                   # 用户自行安装的第三方插件（.gitignore）
│
├── frontend/                       # Vue 3 前端
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/index.ts
│       ├── stores/                 # Pinia
│       ├── api/                    # axios 封装
│       ├── views/
│       │   ├── Unlock.vue          # 密码解锁页
│       │   ├── Dashboard.vue       # 仪表盘（插件卡片）
│       │   ├── Credentials.vue     # 凭据管理
│       │   ├── Logs.vue            # 签到日志
│       │   └── Settings.vue        # 定时 + 推送设置
│       └── components/
│
├── logs/                           # 运行日志输出目录
└── data/                           # SQLite + 密钥持久化目录
```

---

## 三、核心技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 语言 | Python | >=3.11 | 后端运行时 |
| Web 框架 | FastAPI | latest | REST API |
| ASGI 服务器 | Uvicorn | latest | 生产级运行 |
| ORM | SQLAlchemy 2.0 | latest | 数据库操作 |
| 数据库 | SQLite + aiosqlite | - | 本地数据存储 |
| 密码哈希 | bcrypt | latest | 密码存储 |
| 密钥派生 | argon2-cffi | latest | Argon2id 密钥派生 |
| 对称加密 | cryptography | latest | AES-256-GCM 凭据加密 |
| 包管理 | uv | latest | 依赖/虚拟环境管理 |
| 任务调度 | APScheduler | latest | 定时签到 |
| 认证 | python-jose | latest | JWT 会话令牌 |
| HTTP | httpx | latest | 异步请求游戏 API |
| 推送 | (自实现) | - | 17+ 推送渠道 |

---

## 四、核心架构设计

### 4.1 整体架构图

```
┌────────────────────────────────────────────────────────────┐
│                    Vue 3 Frontend                           │
│        (密码解锁 → 仪表盘 → 插件卡片 → 管理页)              │
└──────────────────────┬─────────────────────────────────────┘
                       │ REST API + WebSocket (日志)
┌──────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐       │
│  │  Auth     │  │ PluginLoader │  │ APScheduler      │       │
│  │ (密钥派生) │  │ (插件发现)   │  │ (定时任务)       │       │
│  └──────────┘  └──────┬───────┘  └──────────────────┘       │
│                        │                                      │
│  ┌─────────────────────▼──────────────────────────────────┐  │
│  │               Plugin Registry                           │  │
│  │   mhy_plugin  │  kuro_plugin  │  user_plugins/*       │  │
│  └────────────────────────────────────────────────────────┘  │
│                        │                                      │
│  ┌─────────────────────▼──────────────────────────────────┐  │
│  │  Orchestrator (签到编排器)                               │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────────────┐   │  │
│  │  │ sign_one()  │ │ sign_user() │ │ sign_all()     │   │  │
│  │  └─────────────┘ └─────────────┘ └────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                        │                                      │
│  ┌─────────────────────▼──────────────────────────────────┐  │
│  │  Vault (凭据保险库)                                     │  │
│  │  ┌────────────┐ ┌────────────┐ ┌──────────────────┐   │  │
│  │  │ unlock()   │ │ lock()     │ │ AES-256-GCM      │   │  │
│  │  │ (内存缓存)  │ │ (销毁密钥)  │ │ (磁盘加密)       │   │  │
│  │  └────────────┘ └────────────┘ └──────────────────┘   │  │
│  └──────────┬─────────────────────────────────────────────┘  │
│             │                                                │
│  ┌──────────▼─────────────────────────────────────────────┐  │
│  │  SQLite                                                │  │
│  │  credentials (加密存储) │ sign_logs │ configs          │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 模块职责

| 模块 | 职责 |
|------|------|
| **Auth** | 密码验证 (bcrypt)、Argon2id 密钥派生、JWT 签发/验证 |
| **Vault** | 凭据的加密存储 (AES-256-GCM)、内存缓存、锁定/销毁 |
| **PluginLoader** | 扫描 plugins/ 和 user_plugins/ 目录，动态加载 BaseGamePlugin 实现 |
| **PluginRegistry** | 已加载插件的注册中心，提供按 id 查询和列表功能 |
| **Orchestrator** | 签到编排：遍历插件/用户/游戏，调用签到、写日志、触发推送 |
| **Scheduler** | APScheduler 封装：cron 表达式管理、持久化、手动触发 |
| **Push** | 消息推送：支持多种渠道 (Telegram、ServerChan、PushPlus 等) |

### 4.3 插件系统设计

#### BaseGamePlugin 接口

```python
class PluginInfo(TypedDict):
    id: str                        # "mhy"
    name: str                      # "米游社"
    version: str                   # "1.0.0"
    description: str               # "米游社游戏签到工具"
    homepage: str | None
    supported_games: list[GameInfo]

class GameInfo(TypedDict):
    id: str                        # "genshin"
    name: str                      # "原神"
    has_forum: bool                # 是否有论坛任务

class BaseGamePlugin(ABC):
    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo: ...

    @abstractmethod
    async def validate_credentials(self, credentials: dict) -> bool:
        """验证 Cookie/Token 是否有效"""

    @abstractmethod
    async def sign_in(
        self, credentials: dict, game_id: str
    ) -> list[SignInResult]:
        """单个游戏签到，返回所有角色的结果"""

    @abstractmethod
    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        """该用户在该插件下的所有游戏签到"""

    @abstractmethod
    async def get_user_info(self, credentials: dict) -> dict:
        """获取用户信息（展示用）"""

    async def forum_tasks(self, credentials: dict) -> list[SignInResult]:
        """论坛任务（可选实现）"""
        return []
```

#### 插件隔离机制

```
                游戏隔离 (BaseGame 子类)
         genshin    hsr    zzz    bbs/forum
用户 A   [client_A ──────────────────────]
用户 B   [client_B ──────────────────────]
                 ↑
         同一用户的多个游戏
         共享同一个 client 实例
```

- **纵轴（用户）**：每个用户独立的 `MhyHttpClient` 实例，携带自己的 Cookie
- **横轴（游戏）**：`BaseGame` 不同子类，各自定义 endpoint/act_id/域名
- **用户之间完全隔离**，用户内的游戏共享认证凭据（符合同一套账号体系）

---

## 五、数据库设计

### 5.1 credentials（加密凭据表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| plugin_id | TEXT | 归属插件，如 "mhy" |
| display_name | TEXT | 用户备注名，如"大号" |
| encrypted_data | BLOB | AES-256-GCM 加密后的凭据 JSON |
| enabled_games | TEXT | 启用的游戏列表，JSON 数组 |
| is_enabled | BOOLEAN | 总开关 |
| sort_order | INTEGER | 排序值 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 5.2 sign_logs（签到日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 主键 |
| credential_id | INTEGER FK | 关联凭据 |
| credential_name | TEXT | 冗余，凭据被删后仍可识别 |
| plugin_id | TEXT | 插件 id |
| game_id | TEXT | 游戏 id |
| status | TEXT | success/already/failed/captcha |
| reward | TEXT | 签到奖励名称 |
| message | TEXT | 详细消息 |
| raw_response | TEXT | 原始 API 响应（可选） |
| signed_at | DATETIME | 签到日期（按游戏时区） |
| created_at | DATETIME | 记录创建时间 |

### 5.3 configs（配置表，key-value）

| 字段 | 类型 | 说明 |
|------|------|------|
| key | TEXT PK | 配置键名 |
| value | TEXT | 配置值，JSON 格式 |

内置配置键：

| key | 默认值 | 说明 |
|-----|--------|------|
| schedule_cron | "0 7 * * *" | 定时签到 cron 表达式 |
| schedule_enabled | true | 定时签到开关 |
| push_enabled | false | 推送总开关 |
| push_config | {} | 各渠道推送配置 |
| password_hash | "" | bcrypt 密码 hash（首次设置生成） |

---

## 六、API 路由设计

### 6.1 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/unlock | 输入密码解锁，返回 JWT |
| POST | /api/lock | 锁定（销毁内存密钥） |
| GET | /api/status | 当前锁定状态 |

### 6.2 插件

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/plugins | 已加载的插件列表 |
| GET | /api/plugins/{id} | 单个插件详情 |

### 6.3 凭据管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/credentials | 凭据列表（脱敏） |
| POST | /api/credentials | 新增凭据 |
| PUT | /api/credentials/{id} | 更新凭据 |
| DELETE | /api/credentials/{id} | 删除凭据 |
| POST | /api/credentials/{id}/validate | 验证凭据是否有效 |
| PATCH | /api/credentials/{id}/reorder | 排序 |

### 6.4 签到

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/sign/all | 全部签到 |
| POST | /api/sign/plugin/{plugin_id} | 某插件全部用户 |
| POST | /api/sign/{plugin_id}/{game_id} | 某插件某游戏（所有用户） |
| POST | /api/sign/credential/{cred_id} | 指定用户全部 |
| GET | /api/sign/status | 当前签到任务进度 |

### 6.5 日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/logs | 日志查询（分页+筛选） |
| GET | /api/logs/today | 今日签到汇总 |

### 6.6 配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/schedule | 定时配置 |
| PUT | /api/schedule | 更新定时配置 |
| POST | /api/schedule/trigger | 手动触发定时 |
| GET | /api/push-config | 推送配置 |
| PUT | /api/push-config | 更新推送配置 |

---

## 七、安全设计

### 7.1 密码认证 + 密钥派生

```
用户设置密码
    │
    ▼
bcrypt(password)         → hash 存储 (用于验证)
Argon2id(password+salt)  → 256-bit 密钥 (用于加密)
    │
    ▼
密钥保留在内存 (app.state._decrypt_key)
原始密码立即丢弃
```

- 密码使用 **bcrypt** 哈希，用于后续解锁验证
- 使用 **Argon2id** (time_cost=3, mem_cost=64MB, parallelism=4) 派生加密密钥
- 派生密钥仅存于内存，退出/锁定时销毁

### 7.2 凭据加密存储

```
明文凭据 JSON
    │
    ▼
AES-256-GCM 加密
├─ 密钥: Argon2id 派生 (256-bit)
├─ nonce: 随机 12 字节
├─ 附加数据 (AAD): credential_id 的 bytes
    │
    ▼
存入 SQLite (encrypted_data BLOB 列)
```

- 使用 **AES-256-GCM**（认证加密模式，防篡改）
- 每次加密生成随机 nonce，相同凭据每次密文不同
- 附加数据 (AAD) 绑定 credential_id，防止密文被替换

### 7.3 会话安全

- JWT 存活时间 = 浏览器会话周期（关闭即失效），或设置较短超时（如 1 小时无操作）
- 解密密钥不放入 JWT payload，而是存储在 `app.state.decrypt_key`（服务器端内存）
- JWT 仅携带 session_id，用于关联服务器端缓存的密钥

### 7.4 攻击面分析

| 攻击场景 | 防护措施 |
|----------|---------|
| SQLite 文件泄露 | 凭据全部 AES-256-GCM 加密，无密钥无法解密 |
| 内存 dump | 可选的敏感内存加锁（`mlock`），退出/锁定主动擦除 |
| CSRF | FastAPI 同源策略 + CORS 限制 localhost |
| XSS | Vue 3 默认转义，前端不渲染原始 HTML |

---

## 八、启动流程

```
FastAPI lifespan 启动
│
├─ 1. config.py         ← 加载环境变量
├─ 2. database.py       ← 初始化 SQLite 连接 + 建表
├─ 3. utils/            ← 加密工具初始化
├─ 4. auth.py           ← bcrypt + Argon2id 准备
├─ 5. vault.py          ← Vault 实例创建，初始为锁定状态
├─ 6. plugin_base.py    ← 加载插件抽象基类
├─ 7. plugin_loader.py  ← 扫描 plugins/ 和 user_plugins/ 加载插件
├─ 8. orchestrator.py   ← 签到编排器实例化
├─ 9. scheduler.py      ← 从 DB 加载 cron 配置，启动 APScheduler
│
├─ 10. routers/*         ← 注册所有 API 路由
│
└─ 等待请求...
    │
    ├─ POST /api/unlock  → Vault.unlock(password) → 解密凭据到内存
    ├─ POST /api/sign/*  → Orchestrator 使用内存中的明文凭据执行签到
    ├─ POST /api/lock    → Vault.lock() → 销毁密钥和缓存
    └─ 定时触发          → Scheduler 触发 → Orchestrator.sign_all()
```

---

## 九、依赖拓扑与实现顺序

### 9.1 模块依赖关系

```
                    ┌─────────────┐
                    │  config.py  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ database.py │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐ ┌────▼─────┐
       │ encryption │ │ models │ │ auth.py  │
       │ (utils)    │ │ (ORM)  │ │ (密钥派生)│
       └──────┬─────┘ └───┬────┘ └────┬─────┘
              │            │           │
              └────────────┼───────────┘
                           │
                    ┌──────▼──────┐
                    │   vault.py  │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼─────┐ ┌───▼────┐  ┌────▼─────┐
       │plugin_base │ │ push   │  │ scheduler│
       └──────┬─────┘ └────────┘  └────┬─────┘
              │                        │
       ┌──────▼─────┐                  │
       │plugin_loader│                 │
       └──────┬─────┘                  │
              │                        │
       ┌──────▼───────────────────────▼──┐
       │        orchestrator.py          │
       └──────────────┬──────────────────┘
                      │
              ┌───────┴────────┐
              │                │
       ┌──────▼─────┐   ┌─────▼──────┐
       │  schemas   │   │  routers   │
       └────────────┘   └─────┬──────┘
                              │
                       ┌──────▼──────┐
                       │   main.py   │
                       └─────────────┘
```

### 9.2 推荐实现顺序

```
Phase 1 (骨架)
  config.py → database.py → plugin_base.py → plugin_loader.py
  → main.py (FastAPI 启动 + 空路由)
  验证: /api/plugins 返回已加载的插件列表

Phase 2 (安全层)
  encryption.py → auth.py → vault.py + schemas/auth.py
  → routers/auth.py
  验证: POST /api/unlock 成功拿到 JWT

Phase 3 (签到能力)
  mhy_plugin 内容实现 + schemas/credential.py + schemas/sign.py
  → orchestrator.py → routers/credentials.py + routers/sign.py
  → models/sign_log.py + schemas/log.py + routers/logs.py
  验证: 添加 Cookie → 签到 → 返回结果 → 写入日志

Phase 4 (完整功能)
  kuro_plugin 内容实现
  → push.py + routers/push_config.py
  → scheduler.py + routers/schedule.py
  验证: 定时任务执行、推送通知

Phase 5 (优化)
  WebSocket 日志广播
  Dockerfile + docker-compose.yml
  Vue 3 前端对接
```

---

## 十、推送模块

### 10.1 支持的推送渠道

| 渠道 | 配置方式 | 用途 |
|------|----------|------|
| Telegram | Bot Token + Chat ID | 国际用户常用 |
| ServerChan (ftqq) | SendKey | 微信推送 |
| PushPlus | Token | 微信推送 |
| PushMe | URL + Keys | 自定义推送 |
| CQHTTP | API URL | QQ 机器人推送 |
| SMTP Email | SMTP 配置 | 邮件推送 |
| 企业微信 (WeCom) | Webhook URL | 企业微信推送 |
| PushDeer | Key | iOS 推送 |
| 钉钉机器人 | Webhook URL | 钉钉推送 |
| 飞书机器人 | Webhook URL | 飞书推送 |
| Bark | URL + Key | iOS 推送 |
| Gotify | Server URL + Token | 自托管推送 |
| IFTTT | Webhook Key | IFTTT 联动 |
| WebHook | 自定义 URL | 通用 |
| Qmsg | QQ 号 | QQ 推送 |
| Discord | Webhook URL | Discord 频道推送 |
| WxPusher | App Token + UID | 微信推送 |

### 10.2 推送等级

| 等级 | 行为 |
|------|------|
| 1 | 仅推送汇总：今日签到成功 X / 失败 Y / 跳过 Z |
| 2 | 逐用户推送：每个用户一条消息，包含该用户所有游戏结果 |
| 3 | 逐条推送：每个游戏的每个结果单独发送 |

---

## 十一、部署方案

### 11.1 本地部署

```bash
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
# 浏览器访问 http://127.0.0.1:8000
```

### 11.2 Docker 部署

```yaml
# docker-compose.yml
services:
  game-sign-hub:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./plugins:/app/plugins
      - ./user_plugins:/app/user_plugins
    restart: unless-stopped
```

---

## 十二、扩展性设计

### 12.1 新增游戏

对于已有的插件（如 mhy_plugin），只需在 `games/` 下新增一个文件：

```python
# plugins/mhy_plugin/games/themis.py
class ThemisGame(BaseGame):
    game_id = "tears_of_themis"
    display_name = "未定事件簿"
    act_id = "e202202251749321"

    async def sign_in(self, role: GameRole) -> SignInResult:
        return await self.client.post(
            "...",
            data={"act_id": self.act_id, "region": role.region, "uid": role.uid},
        )
```

然后在 `plugin.py` 的 `supported_games` 中加上即可。

### 12.2 新增插件平台

创建一个新目录 `plugins/ark_plugin/`，实现 `BaseGamePlugin`。放到 `plugins/` 或 `user_plugins/` 后重启即生效，前端自动出现对应的插件卡片。

---

## 十三、技术债务与风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 米游社 DS salt 变更 | 签到失败 | 在 WebUI 提供"更新 Salt"入口；或从公开源自动抓取 |
| 验证码 (retcode 1034) | 签到中断 | captcha 检测后标记"需人工处理"，WebUI 弹验证通道 |
| Cookie 过期 | 签到失败 | Stoken 自动刷新机制；过期后 WebUI 提示用户更新 |
| 插件接口破坏性变更 | 第三方插件不兼容 | 遵守语义化版本；变更时写升级指南 |
| 内存密钥安全性 | 进程 dump 泄露 | 可选项：`ctypes.memset` 主动擦除；Python 层无法完全防护 |
