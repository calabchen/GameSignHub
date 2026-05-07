# 前端文档

## 目录结构

```
├── src/
│   ├── main.ts                    # Vue 3 入口，挂载 Pinia + Router + Element Plus
│   ├── App.vue                    # 根组件，检查状态，控制路由跳转
│   │
│   ├── api/
│   │   └── index.ts               # Axios 实例 + 全部 API 函数
│   │
│   ├── stores/
│   │   └── app.ts                 # Pinia 全局状态（解锁状态、插件列表、选中游戏）
│   │
│   ├── router/
│   │   └── index.ts               # 路由：/ 解锁页，/app 主页
│   │
│   ├── views/
│   │   ├── Unlock.vue             # 解锁/首次设置密码页
│   │   └── AppView.vue            # 主布局：侧边栏（游戏树）+ 内容区
│   │
│   ├── components/
│   │   ├── AccountTable.vue       # 账号表格（增删改、定时设置、立即签到）
│   │   ├── LogTerminal.vue        # 签到日志终端（暗色主题，筛选器）
│   │   ├── WelcomePage.vue        # 欢迎页（未选择游戏时显示）
│   │   └── ChangePasswordForm.vue # 修改密码表单
│   │
│   └── utils/
│       ├── color.ts               # 按 gameId 生成主题色和渐变
│       └── pinyin.ts              # 中文拼音排序、A-Z 索引分组
│
├── public/
│   └── icons/                     # 游戏图标（wuwa.png, genshin.png 等）
│
└── vite.config.ts                 # Vite 配置，开发代理 /api → 8000
```

## 技术栈

| 工具 | 用途 |
|---|---|
| Vue 3 | 前端框架 |
| Pinia | 状态管理 |
| Vue Router | 路由 |
| Element Plus | UI 组件库 |
| Axios | HTTP 请求 |
| pinyin-pro | 中文拼音排序 |
| Vite | 构建工具 |

## 开发

```bash
cd frontend
npm install
npm run dev        # http://localhost:8001（API 代理到 8000）
npm run build      # 输出到 dist/
```

## 构建产物

`npm run build` 后生成 `frontend/dist/`，由后端 FastAPI 的 `StaticFiles` 挂载到 `/`，访问 `http://localhost:8000` 即可使用完整功能。
