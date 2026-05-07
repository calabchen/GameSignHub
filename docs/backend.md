# 后端文档

## 目录结构

```
├── app/
│   ├── main.py                  # FastAPI 入口，lifespan，路由注册
│   ├── schemas.py               # Pydantic 请求/响应模型
│   │
│   ├── core/
│   │   ├── config.py            # 配置管理，基于 __file__ 解析项目根路径
│   │   ├── security.py          # bcrypt 密码哈希 + JWT 签发/验证
│   │   ├── db.py                # SQLAlchemy 异步引擎与会话工厂
│   │   ├── crud_log.py          # 签到日志表 DDL + 分页查询
│   │   ├── crud_yaml.py         # YAML 账号凭证存储（增删改查）
│   │   ├── orchestrator.py      # 签到编排器（遍历插件/账号/游戏）
│   │   ├── plugin_base.py       # 插件抽象基类（BaseGamePlugin）
│   │   ├── plugin_loader.py     # 插件发现与动态加载
│   │   └── scheduler.py         # APScheduler 定时调度封装
│   │
│   ├── routers/
│   │   ├── auth.py              # POST /api/unlock, /api/lock, /api/status
│   │   ├── accounts.py          # CRUD /api/accounts，定时设置
│   │   ├── plugins.py           # GET /api/plugins 插件信息
│   │   ├── sign.py              # POST /api/signs/* 签到触发
│   │   ├── logs.py              # GET /api/logs，今日汇总，清空
│   │   ├── schedule.py          # GET/PUT /api/schedules 全局定时
│   │   └── deps.py              # 认证依赖（require_auth, require_unlocked）
│   │
│   └── config/                  # 运行时配置（不提交到 git）
│       └── kuro/
│           └── 1.yaml           # 库街区账号凭证
│
├── plugins/
│   ├── kuro_plugin/             # 库街区插件（已实现：鸣潮 + 战双）
│   │   ├── plugin.py
│   │   ├── client.py            # Kuro API HTTP 客户端
│   │   ├── models.py            # 数据模型
│   │   └── games/
│   │       └── base.py          # 签到逻辑（WuwaGame, PGRGame）
│   └── mhy_plugin/              # 米游社插件（骨架，待实现）
│       └── plugin.py
│
└── config/                      # 旧配置目录（已废弃）
```

## API 路由

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/status | 系统状态（已解锁/已设密码/插件数） |
| POST | /api/unlock | 解锁 / 首次设置密码 |
| POST | /api/lock | 锁定 |
| PUT | /api/unlock/password | 修改密码 |
| GET | /api/accounts | 账号列表 |
| POST | /api/accounts | 创建账号 |
| GET | /api/accounts/{id} | 账号概要 |
| GET | /api/accounts/{id}/detail | 账号完整信息（含 token） |
| PATCH | /api/accounts/{id} | 更新账号 |
| DELETE | /api/accounts/{id} | 删除账号 |
| POST | /api/accounts/{id}/validate | 校验凭证有效性 |
| GET | /api/accounts/{id}/schedule/{game_id} | 获取定时配置 |
| PUT | /api/accounts/{id}/schedule/{game_id} | 更新定时配置 |
| GET | /api/plugins | 插件列表 |
| GET | /api/plugins/{id} | 插件详情 |
| POST | /api/signs/plugins/{id}/credentials/{cid}/games/{gid} | 单次签到 |
| POST | /api/signs/plugins/{id} | 插件全部签到 |
| POST | /api/schedules/triggers | 触发全局签到 |
| GET | /api/schedules | 全局定时配置 |
| PUT | /api/schedules | 更新全局定时 |
| GET | /api/logs | 日志列表（分页+筛选） |
| GET | /api/logs/today | 今日签到汇总 |
| DELETE | /api/logs | 清空日志 |
| GET | /version | 版本信息 |

## YAML 账号凭证明细

`app/config/kuro/1.yaml`：

```yaml
enable: true
user_id: '12345678'
token: eyJhbGciOiJIUzI1NiJ9.xxx
devcode: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
distinct_id: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
wuwa:
  role_id: '123456789'
  enabled: true
  schedule_cron: '0 7 * * *'
  schedule_enabled: true
pgr:
  role_id: '987654321'
  enabled: false
  schedule_cron: ''
  schedule_enabled: false
```

| 字段 | 说明 |
|---|---|
| enable | 账号启用状态 |
| user_id | 库街区用户 ID |
| token | 库街区登录 Token |
| devcode | 设备码 |
| distinct_id | 设备指纹 |
| wuwa.role_id | 鸣潮游戏角色 ID |
| pgr.role_id | 战双帕弥什游戏角色 ID |
| {game}.enabled | 该游戏签到开关 |
| {game}.schedule_cron | 定时签到 cron 表达式 |
| {game}.schedule_enabled | 定时签到开关 |

## 获取 Token

库街区 Token 获取方式参考：[Kuro_login](https://github.com/mxyooR/Kuro_login)
