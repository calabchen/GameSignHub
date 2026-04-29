# GameSignHub 鍚庣鏋舵瀯瑙勫垝

> 鐗堟湰: v1.0
> 璁稿彲璇? GPL-3.0
> Python: 3.11+
> 鍖呯鐞嗗櫒: uv

---

## 涓€銆侀」鐩畾浣?
鏈湴杩愯鐨勫娓告垙绀惧尯绛惧埌鍙鍖栫鐞嗗伐鍏枫€?
- 鎻掍欢寮忔灦鏋勶紝姣忎釜娓告垙骞冲彴锛堢背娓哥ぞ銆佸簱娲涚瓑锛夋槸涓€涓嫭绔嬫彃浠?- 鍗曞瘑鐮佽В閿?+ AES-256-GCM 鍔犲瘑瀛樺偍鐢ㄦ埛鍑嵁
- FastAPI 鍚庣 + Vue 3 鍓嶇锛屼粎鏈湴璁块棶
- Docker 鍜屾湰鍦颁袱绉嶉儴缃叉柟寮?
---

## 浜屻€佸綋鍓嶅疄鐜扮姸鎬?
> **鏂颁汉璇蜂紭鍏堥槄璇绘湰绔?*锛岄伩鍏嶅皢瑙勫垝褰撲綔宸插畬鎴愬姛鑳姐€?
### 2.1 瀹炵幇杩涘害鎬昏

| 妯″潡 | 鐘舵€?| 璇存槑 |
|------|------|------|
| 鏍稿績楠ㄦ灦 (FastAPI + SQLAlchemy) | 鉁?瀹屾垚 | main.py / config.py / database.py |
| 璁よ瘉绯荤粺 (bcrypt + Argon2id + JWT) | 鉁?瀹屾垚 | POST /api/unlock, /lock, /status, /password |
| 鍑嵁淇濋櫓搴?(AES-256-GCM) | 鉁?瀹屾垚 | Vault 澧炲垹鏀规煡 + 鍐呭瓨瀵嗛挜绠＄悊 |
| 鎻掍欢绯荤粺 (BaseGamePlugin + Loader) | 鉁?瀹屾垚 | 鎻掍欢鍙戠幇/鍔犺浇/娉ㄥ唽 |
| 绛惧埌缂栨帓鍣?(Orchestrator) | 鉁?瀹屾垚 | 鍗曠敤鎴?鍏ㄦ彃浠?鍏ㄩ儴绛惧埌 |
| 瀹氭椂璋冨害鍣?(APScheduler) | 鉁?瀹屾垚 | cron 鎸佷箙鍖?+ GET/PUT /api/schedules |
| 绛惧埌鏃ュ織 | 鉁?瀹屾垚 | 鍒嗛〉鏌ヨ + 浠婃棩姹囨€?+ 娓呯┖ |
| 鍑嵁绠＄悊 (CRUD) | 鉁?瀹屾垚 | 鏂板/缂栬緫/鍒犻櫎/楠岃瘉 |
| **搴撹鍖烘彃浠?(kuro_plugin)** | 鉁?瀹屾垚 | 楦ｆ疆 + 鎴樺弻甯曞讥浠€ 绛惧埌鍙敤 |
| **绫虫父绀炬彃浠?(mhy_plugin)** | 鉂?绌哄３ | 浠呮敞鍐?6 涓父鎴忓厓淇℃伅锛屾墍鏈夌鍒版柟娉?`raise NotImplementedError` |
| 鎺ㄩ€佹ā鍧?(Push) | 鉂?鏈紑濮?| 17+ 娓犻亾鍏ㄩ儴鏈疄鐜帮紝鏃?`push.py` |
| WebSocket 鏃ュ織骞挎挱 | 鉂?鏈紑濮?| 鏃?`ws_logger.py` |
| Docker 閮ㄧ讲 | 鉂?鏈紑濮?| 鏃?Dockerfile / docker-compose.yml |
| README.md | 鉂?涓嶅瓨鍦?| 鏃犻」鐩鏄庢枃妗?|
| 鍓嶇 Settings 椤甸潰 | 鉂?鏈紑濮?| 鏃?`Settings.vue` |
| 鍑嵁鎺掑簭 (reorder) | 鉂?鏈紑濮?| 鏃?`PATCH /api/credentials/{id}/reorder` |

### 2.2 鎻掍欢瀹屾垚搴?
| 鎻掍欢 | 鐗堟湰 | 鐘舵€?| 绛惧埌 | 璁哄潧浠诲姟 | 鏀寔娓告垙 |
|------|------|------|------|----------|----------|
| kuro_plugin (搴撹鍖? | 0.1.0 | **鍙敤** | 楦ｆ疆銆佹垬鍙屽笗寮ヤ粈 | 鉂?鏈疄鐜?| 2 |
| mhy_plugin (绫虫父绀? | 0.1.0 | **绌哄３** | 鍏ㄩ儴 NotImplementedError | 鉂?鏈疄鐜?| 6锛堝叏閮ㄤ笉鍙敤锛?|
| user_plugins | 鈥?| 绌虹洰褰?| 鈥?| 鈥?| 0 |

### 2.3 API 瀹炵幇瀵圭収

宸插疄鐜?vs 鏂囨。涓鍒掔殑宸紓锛?
| 鏂囨。瑙勫垝 | 瀹為檯瀹炵幇 | 宸紓璇存槑 |
|----------|----------|----------|
| `POST /api/signs/{plugin_id}/{game_id}` | 涓嶅瓨鍦?| 鏈疄鐜版寜娓告垙缁村害鐨勭鍒?|
| `POST /api/signs/credential/{cred_id}` | 宸插疄鐜?| 瀹為檯鏈夋绔偣锛屾枃妗ｆ湭鍒楀嚭 |
| `PATCH /api/credentials/{id}/reorder` | 涓嶅瓨鍦?| 鎺掑簭鍔熻兘鏈疄鐜?|
| `GET /api/push-config` | 涓嶅瓨鍦?| 鎺ㄩ€佹ā鍧楁湭寮€濮?|
| `PUT /api/push-config` | 涓嶅瓨鍦?| 鎺ㄩ€佹ā鍧楁湭寮€濮?|
| `PUT /api/unlock/password` | 宸插疄鐜?| 淇敼瀵嗙爜鍔熻兘锛屾枃妗ｆ湭鍒楀嚭 |
| `DELETE /api/logs` | 宸插疄鐜?| 娓呯┖鏃ュ織锛屾枃妗ｆ湭鍒楀嚭 |

### 2.4 鏂囨。鐩綍 vs 瀹為檯鏂囦欢

浠ヤ笅鍦ㄦ灦鏋勬枃妗ｇ洰褰曟爲涓垪鍑轰絾瀹為檯涓嶅瓨鍦ㄧ殑鏂囦欢/鐩綍锛?
| 鏂囨。鍒楀嚭 | 瀹為檯鎯呭喌 |
|----------|----------|
| `Dockerfile`銆乣docker-compose.yml` | 涓嶅瓨鍦?|
| `README.md` | 涓嶅瓨鍦?|
| `app/core/push.py` | 鎺ㄩ€佹ā鍧楁湭寮€濮?|
| `app/routers/push_config.py` | 鎺ㄩ€佹ā鍧楁湭寮€濮?|
| `app/utils/ws_logger.py` | WebSocket 鏈疄鐜?|
| `app/schemas/plugin.py` | 涓嶅瓨鍦紙鏈娇鐢ㄧ嫭绔?Schema锛?|
| `plugins/kuro_plugin/forum.py` | 璁哄潧浠诲姟鏈疄鐜?|
| `plugins/kuro_plugin/games/wuwa.py` | WuwaGame 瀹為檯鍦?`base.py` 涓?|
| `plugins/kuro_plugin/games/pgr.py` | PGRGame 瀹為檯鍦?`base.py` 涓?|
| `plugins/mhy_plugin/client.py` | mhy_plugin 涓虹┖澹?|
| `plugins/mhy_plugin/bbs.py` | 涓嶅瓨鍦?|
| `plugins/mhy_plugin/captcha.py` | 涓嶅瓨鍦?|
| `plugins/mhy_plugin/models.py` | 涓嶅瓨鍦?|
| `plugins/mhy_plugin/pyproject.toml` | 涓嶅瓨鍦?|
| `plugins/mhy_plugin/games/genshin.py` 绛?| 浠?`games/__init__.py` 绌烘枃浠?|
| `frontend/src/views/Settings.vue` | 涓嶅瓨鍦?|
| `frontend/src/components/` | 鐩綍涓嶅瓨鍦?|
| `logs/` | 鐩綍涓嶅瓨鍦?|

### 2.5 鎺ㄨ崘鍚庣画寮€鍙戦『搴?
鍩轰簬褰撳墠瀹屾垚搴︼細

1. **楂樹紭鍏?* 鈥?mhy_plugin 绛惧埌瀹炵幇锛? 娆剧背鍝堟父娓告垙锛岀敤鎴烽噺鏈€澶э級
2. **楂樹紭鍏?* 鈥?鍓嶇 Settings.vue锛圓PI 宸插氨缁紝浠呯己鍓嶇椤甸潰锛?3. **涓紭鍏?* 鈥?Docker 閮ㄧ讲锛圖ockerfile + docker-compose.yml锛?4. **涓紭鍏?* 鈥?鎺ㄩ€佹ā鍧?(push.py锛?7+ 娓犻亾)
5. **浣庝紭鍏?* 鈥?WebSocket 鏃ュ織骞挎挱
6. **浣庝紭鍏?* 鈥?鍑嵁鎺掑簭銆佽鍧涗换鍔?
---

## 涓夈€佺洰褰曠粨鏋?
```
GameSignHub/
鈹溾攢鈹€ pyproject.toml                  # 椤圭洰鍏冩暟鎹?+ 渚濊禆绠＄悊 (uv)
鈹溾攢鈹€ Dockerfile                      # 澶氶樁娈垫瀯寤?鈹溾攢鈹€ docker-compose.yml              # 鏈湴涓€閿儴缃?鈹溾攢鈹€ .env.example                    # 鐜鍙橀噺妯℃澘
鈹溾攢鈹€ .gitignore
鈹溾攢鈹€ LICENSE                         # GPL-3.0
鈹溾攢鈹€ README.md
鈹?鈹溾攢鈹€ app/                            # FastAPI 鍚庣
鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹溾攢鈹€ main.py                     # FastAPI 鍏ュ彛锛宭ifespan 绠＄悊
鈹?  鈹溾攢鈹€ config.py                   # Pydantic Settings
鈹?  鈹溾攢鈹€ database.py                 # SQLAlchemy async engine + session
鈹?  鈹?鈹?  鈹溾攢鈹€ models/                     # SQLAlchemy ORM 妯″瀷
鈹?  鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹?  鈹溾攢鈹€ credential.py           # 鍔犲瘑鍑嵁琛?鈹?  鈹?  鈹斺攢鈹€ sign_log.py             # 绛惧埌鏃ュ織琛?鈹?  鈹?鈹?  鈹溾攢鈹€ schemas/                    # Pydantic 璇锋眰/鍝嶅簲
鈹?  鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹?  鈹溾攢鈹€ auth.py
鈹?  鈹?  鈹溾攢鈹€ plugin.py
鈹?  鈹?  鈹溾攢鈹€ credential.py
鈹?  鈹?  鈹溾攢鈹€ sign.py
鈹?  鈹?  鈹斺攢鈹€ log.py
鈹?  鈹?鈹?  鈹溾攢鈹€ core/                       # 鏍稿績涓氬姟
鈹?  鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹?  鈹溾攢鈹€ auth.py                 # 瀵嗙爜楠岃瘉 + 瀵嗛挜娲剧敓
鈹?  鈹?  鈹溾攢鈹€ vault.py                # Credential Vault (鍔犲瘑/瑙ｅ瘑)
鈹?  鈹?  鈹溾攢鈹€ plugin_base.py          # BaseGamePlugin 鎶借薄鍩虹被
鈹?  鈹?  鈹溾攢鈹€ plugin_loader.py        # 鎻掍欢鍙戠幇 + 鍔犺浇
鈹?  鈹?  鈹溾攢鈹€ orchestrator.py         # 绛惧埌缂栨帓鍣?鈹?  鈹?  鈹溾攢鈹€ push.py                 # 鎺ㄩ€侀€氱煡妯″潡
鈹?  鈹?  鈹斺攢鈹€ scheduler.py            # APScheduler 瀹氭椂浠诲姟
鈹?  鈹?鈹?  鈹溾攢鈹€ routers/                    # API 璺敱
鈹?  鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹?  鈹溾攢鈹€ auth.py                 # POST /api/unlock, /api/lock
鈹?  鈹?  鈹溾攢鈹€ plugins.py              # GET /api/plugins
鈹?  鈹?  鈹溾攢鈹€ credentials.py          # CRUD /api/credentials
鈹?  鈹?  鈹溾攢鈹€ sign.py                 # POST /api/signs/*
鈹?  鈹?  鈹溾攢鈹€ logs.py                 # GET /api/logs
鈹?  鈹?  鈹溾攢鈹€ schedule.py             # GET/PUT /api/schedules
鈹?  鈹?  鈹斺攢鈹€ push_config.py          # GET/PUT /api/push-config
鈹?  鈹?鈹?  鈹斺攢鈹€ utils/
鈹?      鈹溾攢鈹€ __init__.py
鈹?      鈹溾攢鈹€ encryption.py           # AES-256-GCM 鍔犺В瀵嗗伐鍏?鈹?      鈹斺攢鈹€ ws_logger.py            # WebSocket 鏃ュ織骞挎挱
鈹?鈹溾攢鈹€ plugins/                        # 鍐呯疆瀹樻柟鎻掍欢
鈹?  鈹溾攢鈹€ mhy_plugin/
鈹?  鈹?  鈹溾攢鈹€ __init__.py
鈹?  鈹?  鈹溾攢鈹€ plugin.py               # MhyPlugin(BaseGamePlugin)
鈹?  鈹?  鈹溾攢鈹€ client.py               # MhyHttpClient (DS 绛惧悕)
鈹?  鈹?  鈹溾攢鈹€ bbs.py                  # 璁哄潧绛惧埌/浠诲姟
鈹?  鈹?  鈹溾攢鈹€ captcha.py              # 楠岃瘉鐮佸鐞?鈹?  鈹?  鈹溾攢鈹€ models.py               # 鎻掍欢鍐呴儴鏁版嵁绫?鈹?  鈹?  鈹溾攢鈹€ pyproject.toml          # 鐙珛渚濊禆澹版槑
鈹?  鈹?  鈹斺攢鈹€ games/                  # 姣忎釜娓告垙涓€涓枃浠?鈹?  鈹?      鈹溾攢鈹€ __init__.py
鈹?  鈹?      鈹溾攢鈹€ base.py             # BaseGame 鍩虹被
鈹?  鈹?      鈹溾攢鈹€ genshin.py          # 鍘熺
鈹?  鈹?      鈹溾攢鈹€ honkai_sr.py        # 宕╁潖鏄熺┕閾侀亾
鈹?  鈹?      鈹溾攢鈹€ zzz.py              # 缁濆尯闆?鈹?  鈹?      鈹溾攢鈹€ honkai3rd.py        # 宕╁潖3
鈹?  鈹?      鈹斺攢鈹€ honkai2.py          # 宕╁潖2
鈹?  鈹?鈹?  鈹斺攢鈹€ kuro_plugin/
鈹?      鈹溾攢鈹€ __init__.py
鈹?      鈹溾攢鈹€ plugin.py               # KuroPlugin(BaseGamePlugin)
鈹?      鈹溾攢鈹€ client.py               # KuroHttpClient
鈹?      鈹溾攢鈹€ forum.py                # 璁哄潧浠诲姟
鈹?      鈹溾攢鈹€ models.py
鈹?      鈹斺攢鈹€ games/
鈹?          鈹溾攢鈹€ __init__.py
鈹?          鈹溾攢鈹€ base.py
鈹?          鈹溾攢鈹€ wuwa.py             # 楦ｆ疆
鈹?          鈹斺攢鈹€ pgr.py              # 鎴樺弻
鈹?鈹溾攢鈹€ user_plugins/                   # 鐢ㄦ埛鑷瀹夎鐨勭涓夋柟鎻掍欢锛?gitignore锛?鈹?鈹溾攢鈹€ frontend/                       # Vue 3 鍓嶇
鈹?  鈹溾攢鈹€ index.html
鈹?  鈹溾攢鈹€ package.json
鈹?  鈹溾攢鈹€ vite.config.ts
鈹?  鈹溾攢鈹€ tsconfig.json
鈹?  鈹斺攢鈹€ src/
鈹?      鈹溾攢鈹€ main.ts
鈹?      鈹溾攢鈹€ App.vue
鈹?      鈹溾攢鈹€ router/index.ts
鈹?      鈹溾攢鈹€ stores/                 # Pinia
鈹?      鈹溾攢鈹€ api/                    # axios 灏佽
鈹?      鈹溾攢鈹€ views/
鈹?      鈹?  鈹溾攢鈹€ Unlock.vue          # 瀵嗙爜瑙ｉ攣椤?鈹?      鈹?  鈹溾攢鈹€ Dashboard.vue       # 浠〃鐩橈紙鎻掍欢鍗＄墖锛?鈹?      鈹?  鈹溾攢鈹€ Credentials.vue     # 鍑嵁绠＄悊
鈹?      鈹?  鈹溾攢鈹€ Logs.vue            # 绛惧埌鏃ュ織
鈹?      鈹?  鈹斺攢鈹€ Settings.vue        # 瀹氭椂 + 鎺ㄩ€佽缃?鈹?      鈹斺攢鈹€ components/
鈹?鈹溾攢鈹€ logs/                           # 杩愯鏃ュ織杈撳嚭鐩綍
鈹斺攢鈹€ data/                           # SQLite + 瀵嗛挜鎸佷箙鍖栫洰褰?```

---

## 鍥涖€佹牳蹇冩妧鏈爤

| 灞傜骇 | 鎶€鏈?| 鐗堟湰 | 鐢ㄩ€?|
|------|------|------|------|
| 璇█ | Python | >=3.11 | 鍚庣杩愯鏃?|
| Web 妗嗘灦 | FastAPI | latest | REST API |
| ASGI 鏈嶅姟鍣?| Uvicorn | latest | 鐢熶骇绾ц繍琛?|
| ORM | SQLAlchemy 2.0 | latest | 鏁版嵁搴撴搷浣?|
| 鏁版嵁搴?| SQLite + aiosqlite | - | 鏈湴鏁版嵁瀛樺偍 |
| 瀵嗙爜鍝堝笇 | bcrypt | latest | 瀵嗙爜瀛樺偍 |
| 瀵嗛挜娲剧敓 | argon2-cffi | latest | Argon2id 瀵嗛挜娲剧敓 |
| 瀵圭О鍔犲瘑 | cryptography | latest | AES-256-GCM 鍑嵁鍔犲瘑 |
| 鍖呯鐞?| uv | latest | 渚濊禆/铏氭嫙鐜绠＄悊 |
| 浠诲姟璋冨害 | APScheduler | latest | 瀹氭椂绛惧埌 |
| 璁よ瘉 | python-jose | latest | JWT 浼氳瘽浠ょ墝 |
| HTTP | httpx | latest | 寮傛璇锋眰娓告垙 API |
| 鎺ㄩ€?| (鑷疄鐜? | - | 17+ 鎺ㄩ€佹笭閬?|

---

## 浜斻€佹牳蹇冩灦鏋勮璁?
### 5.1 鏁翠綋鏋舵瀯鍥?
```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                   Vue 3 Frontend                           鈹?鈹?       (瀵嗙爜瑙ｉ攣 鈫?浠〃鐩?鈫?鎻掍欢鍗＄墖 鈫?绠＄悊椤?              鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                       鈹?REST API + WebSocket (鏃ュ織)
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?                   FastAPI Backend                           鈹?鈹?                                                             鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?      鈹?鈹? 鈹? Auth     鈹? 鈹?PluginLoader 鈹? 鈹?APScheduler      鈹?      鈹?鈹? 鈹?(瀵嗛挜娲剧敓) 鈹? 鈹?(鎻掍欢鍙戠幇)   鈹? 鈹?(瀹氭椂浠诲姟)       鈹?      鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?      鈹?鈹?                       鈹?                                     鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹? 鈹?              Plugin Registry                           鈹? 鈹?鈹? 鈹?  mhy_plugin  鈹? kuro_plugin  鈹? user_plugins/*       鈹? 鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹?                       鈹?                                     鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹? 鈹? Orchestrator (绛惧埌缂栨帓鍣?                               鈹? 鈹?鈹? 鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹? 鈹?鈹? 鈹? 鈹?sign_one()  鈹?鈹?sign_user() 鈹?鈹?sign_all()     鈹?  鈹? 鈹?鈹? 鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹? 鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹?                       鈹?                                     鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹? 鈹? Vault (鍑嵁淇濋櫓搴?                                     鈹? 鈹?鈹? 鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹? 鈹?鈹? 鈹? 鈹?unlock()   鈹?鈹?lock()     鈹?鈹?AES-256-GCM      鈹?  鈹? 鈹?鈹? 鈹? 鈹?(鍐呭瓨缂撳瓨)  鈹?鈹?(閿€姣佸瘑閽?  鈹?鈹?(纾佺洏鍔犲瘑)       鈹?  鈹? 鈹?鈹? 鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹? 鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹?            鈹?                                               鈹?鈹? 鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹? 鈹? SQLite                                                鈹? 鈹?鈹? 鈹? credentials (鍔犲瘑瀛樺偍) 鈹?sign_logs 鈹?configs          鈹? 鈹?鈹? 鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### 5.2 妯″潡鑱岃矗

| 妯″潡 | 鑱岃矗 |
|------|------|
| **Auth** | 瀵嗙爜楠岃瘉 (bcrypt)銆丄rgon2id 瀵嗛挜娲剧敓銆丣WT 绛惧彂/楠岃瘉 |
| **Vault** | 鍑嵁鐨勫姞瀵嗗瓨鍌?(AES-256-GCM)銆佸唴瀛樼紦瀛樸€侀攣瀹?閿€姣?|
| **PluginLoader** | 鎵弿 plugins/ 鍜?user_plugins/ 鐩綍锛屽姩鎬佸姞杞?BaseGamePlugin 瀹炵幇 |
| **PluginRegistry** | 宸插姞杞芥彃浠剁殑娉ㄥ唽涓績锛屾彁渚涙寜 id 鏌ヨ鍜屽垪琛ㄥ姛鑳?|
| **Orchestrator** | 绛惧埌缂栨帓锛氶亶鍘嗘彃浠?鐢ㄦ埛/娓告垙锛岃皟鐢ㄧ鍒般€佸啓鏃ュ織銆佽Е鍙戞帹閫?|
| **Scheduler** | APScheduler 灏佽锛歝ron 琛ㄨ揪寮忕鐞嗐€佹寔涔呭寲銆佹墜鍔ㄨЕ鍙?|
| **Push** | 娑堟伅鎺ㄩ€侊細鏀寔澶氱娓犻亾 (Telegram銆丼erverChan銆丳ushPlus 绛? |

### 5.3 鎻掍欢绯荤粺璁捐

#### BaseGamePlugin 鎺ュ彛

```python
class PluginInfo(TypedDict):
    id: str                        # "mhy"
    name: str                      # "绫虫父绀?
    version: str                   # "1.0.0"
    description: str               # "绫虫父绀炬父鎴忕鍒板伐鍏?
    homepage: str | None
    supported_games: list[GameInfo]

class GameInfo(TypedDict):
    id: str                        # "genshin"
    name: str                      # "鍘熺"
    has_forum: bool                # 鏄惁鏈夎鍧涗换鍔?
class BaseGamePlugin(ABC):
    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo: ...

    @abstractmethod
    async def validate_credentials(self, credentials: dict) -> bool:
        """楠岃瘉 Cookie/Token 鏄惁鏈夋晥"""

    @abstractmethod
    async def sign_in(
        self, credentials: dict, game_id: str
    ) -> list[SignInResult]:
        """鍗曚釜娓告垙绛惧埌锛岃繑鍥炴墍鏈夎鑹茬殑缁撴灉"""

    @abstractmethod
    async def sign_in_all(self, credentials: dict) -> dict[str, list[SignInResult]]:
        """璇ョ敤鎴峰湪璇ユ彃浠朵笅鐨勬墍鏈夋父鎴忕鍒?""

    @abstractmethod
    async def get_user_info(self, credentials: dict) -> dict:
        """鑾峰彇鐢ㄦ埛淇℃伅锛堝睍绀虹敤锛?""

    async def forum_tasks(self, credentials: dict) -> list[SignInResult]:
        """璁哄潧浠诲姟锛堝彲閫夊疄鐜帮級"""
        return []
```

#### 鎻掍欢闅旂鏈哄埗

```
                娓告垙闅旂 (BaseGame 瀛愮被)
         genshin    hsr    zzz    bbs/forum
鐢ㄦ埛 A   [client_A 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€]
鐢ㄦ埛 B   [client_B 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€]
                 鈫?         鍚屼竴鐢ㄦ埛鐨勫涓父鎴?         鍏变韩鍚屼竴涓?client 瀹炰緥
```

- **绾佃酱锛堢敤鎴凤級**锛氭瘡涓敤鎴风嫭绔嬬殑 `MhyHttpClient` 瀹炰緥锛屾惡甯﹁嚜宸辩殑 Cookie
- **妯酱锛堟父鎴忥級**锛歚BaseGame` 涓嶅悓瀛愮被锛屽悇鑷畾涔?endpoint/act_id/鍩熷悕
- **鐢ㄦ埛涔嬮棿瀹屽叏闅旂**锛岀敤鎴峰唴鐨勬父鎴忓叡浜璇佸嚟鎹紙绗﹀悎鍚屼竴濂楄处鍙蜂綋绯伙級

---

## 鍏€佹暟鎹簱璁捐

### 6.1 credentials锛堝姞瀵嗗嚟鎹〃锛?
| 瀛楁 | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | INTEGER PK | 涓婚敭 |
| plugin_id | TEXT | 褰掑睘鎻掍欢锛屽 "mhy" |
| display_name | TEXT | 鐢ㄦ埛澶囨敞鍚嶏紝濡?澶у彿" |
| encrypted_data | BLOB | AES-256-GCM 鍔犲瘑鍚庣殑鍑嵁 JSON |
| enabled_games | TEXT | 鍚敤鐨勬父鎴忓垪琛紝JSON 鏁扮粍 |
| is_enabled | BOOLEAN | 鎬诲紑鍏?|
| sort_order | INTEGER | 鎺掑簭鍊?|
| created_at | DATETIME | 鍒涘缓鏃堕棿 |
| updated_at | DATETIME | 鏇存柊鏃堕棿 |

### 6.2 sign_logs锛堢鍒版棩蹇楄〃锛?
| 瀛楁 | 绫诲瀷 | 璇存槑 |
|------|------|------|
| id | INTEGER PK | 涓婚敭 |
| credential_id | INTEGER FK | 鍏宠仈鍑嵁 |
| credential_name | TEXT | 鍐椾綑锛屽嚟鎹鍒犲悗浠嶅彲璇嗗埆 |
| plugin_id | TEXT | 鎻掍欢 id |
| game_id | TEXT | 娓告垙 id |
| status | TEXT | success/already/failed/captcha |
| reward | TEXT | 绛惧埌濂栧姳鍚嶇О |
| message | TEXT | 璇︾粏娑堟伅 |
| raw_response | TEXT | 鍘熷 API 鍝嶅簲锛堝彲閫夛級 |
| signed_at | DATETIME | 绛惧埌鏃ユ湡锛堟寜娓告垙鏃跺尯锛?|
| created_at | DATETIME | 璁板綍鍒涘缓鏃堕棿 |

### 6.3 configs锛堥厤缃〃锛宬ey-value锛?
| 瀛楁 | 绫诲瀷 | 璇存槑 |
|------|------|------|
| key | TEXT PK | 閰嶇疆閿悕 |
| value | TEXT | 閰嶇疆鍊硷紝JSON 鏍煎紡 |

鍐呯疆閰嶇疆閿細

| key | 榛樿鍊?| 璇存槑 |
|-----|--------|------|
| schedule_cron | "0 7 * * *" | 瀹氭椂绛惧埌 cron 琛ㄨ揪寮?|
| schedule_enabled | true | 瀹氭椂绛惧埌寮€鍏?|
| push_enabled | false | 鎺ㄩ€佹€诲紑鍏?|
| push_config | {} | 鍚勬笭閬撴帹閫侀厤缃?|
| password_hash | "" | bcrypt 瀵嗙爜 hash锛堥娆¤缃敓鎴愶級 |

---

## 涓冦€丄PI 璺敱璁捐

### 7.1 璁よ瘉

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| POST | /api/unlock | 杈撳叆瀵嗙爜瑙ｉ攣锛岃繑鍥?JWT |
| POST | /api/lock | 閿佸畾锛堥攢姣佸唴瀛樺瘑閽ワ級 |
| GET | /api/status | 褰撳墠閿佸畾鐘舵€?|

### 7.2 鎻掍欢

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| GET | /api/plugins | 宸插姞杞界殑鎻掍欢鍒楄〃 |
| GET | /api/plugins/{id} | 鍗曚釜鎻掍欢璇︽儏 |

### 7.3 鍑嵁绠＄悊

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| GET | /api/credentials | 鍑嵁鍒楄〃锛堣劚鏁忥級 |
| POST | /api/credentials | 鏂板鍑嵁 |
| PUT | /api/credentials/{id} | 鏇存柊鍑嵁 |
| DELETE | /api/credentials/{id} | 鍒犻櫎鍑嵁 |
| POST | /api/credentials/{id}/validate | 楠岃瘉鍑嵁鏄惁鏈夋晥 |
| PATCH | /api/credentials/{id}/reorder | 鎺掑簭 |

### 7.4 绛惧埌

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| POST | /api/signs/all | 鍏ㄩ儴绛惧埌 |
| POST | /api/signs/plugin/{plugin_id} | 鏌愭彃浠跺叏閮ㄧ敤鎴?|
| POST | /api/signs/{plugin_id}/{game_id} | 鏌愭彃浠舵煇娓告垙锛堟墍鏈夌敤鎴凤級 |
| POST | /api/signs/credential/{cred_id} | 鎸囧畾鐢ㄦ埛鍏ㄩ儴 |
| GET | /api/signs/status | 褰撳墠绛惧埌浠诲姟杩涘害 |

### 7.5 鏃ュ織

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| GET | /api/logs | 鏃ュ織鏌ヨ锛堝垎椤?绛涢€夛級 |
| GET | /api/logs/today | 浠婃棩绛惧埌姹囨€?|

### 7.6 閰嶇疆

| 鏂规硶 | 璺緞 | 璇存槑 |
|------|------|------|
| GET | /api/schedules | 瀹氭椂閰嶇疆 |
| PUT | /api/schedules | 鏇存柊瀹氭椂閰嶇疆 |
| POST | /api/schedules/triggers | 鎵嬪姩瑙﹀彂瀹氭椂 |
| GET | /api/push-config | 鎺ㄩ€侀厤缃?|
| PUT | /api/push-config | 鏇存柊鎺ㄩ€侀厤缃?|

---

## 鍏€佸畨鍏ㄨ璁?
### 8.1 瀵嗙爜璁よ瘉 + 瀵嗛挜娲剧敓

```
鐢ㄦ埛璁剧疆瀵嗙爜
    鈹?    鈻?bcrypt(password)         鈫?hash 瀛樺偍 (鐢ㄤ簬楠岃瘉)
Argon2id(password+salt)  鈫?256-bit 瀵嗛挜 (鐢ㄤ簬鍔犲瘑)
    鈹?    鈻?瀵嗛挜淇濈暀鍦ㄥ唴瀛?(app.state._decrypt_key)
鍘熷瀵嗙爜绔嬪嵆涓㈠純
```

- 瀵嗙爜浣跨敤 **bcrypt** 鍝堝笇锛岀敤浜庡悗缁В閿侀獙璇?- 浣跨敤 **Argon2id** (time_cost=3, mem_cost=64MB, parallelism=4) 娲剧敓鍔犲瘑瀵嗛挜
- 娲剧敓瀵嗛挜浠呭瓨浜庡唴瀛橈紝閫€鍑?閿佸畾鏃堕攢姣?
### 8.2 鍑嵁鍔犲瘑瀛樺偍

```
鏄庢枃鍑嵁 JSON
    鈹?    鈻?AES-256-GCM 鍔犲瘑
鈹溾攢 瀵嗛挜: Argon2id 娲剧敓 (256-bit)
鈹溾攢 nonce: 闅忔満 12 瀛楄妭
鈹溾攢 闄勫姞鏁版嵁 (AAD): credential_id 鐨?bytes
    鈹?    鈻?瀛樺叆 SQLite (encrypted_data BLOB 鍒?
```

- 浣跨敤 **AES-256-GCM**锛堣璇佸姞瀵嗘ā寮忥紝闃茬鏀癸級
- 姣忔鍔犲瘑鐢熸垚闅忔満 nonce锛岀浉鍚屽嚟鎹瘡娆″瘑鏂囦笉鍚?- 闄勫姞鏁版嵁 (AAD) 缁戝畾 credential_id锛岄槻姝㈠瘑鏂囪鏇挎崲

### 8.3 浼氳瘽瀹夊叏

- JWT 瀛樻椿鏃堕棿 = 娴忚鍣ㄤ細璇濆懆鏈燂紙鍏抽棴鍗冲け鏁堬級锛屾垨璁剧疆杈冪煭瓒呮椂锛堝 1 灏忔椂鏃犳搷浣滐級
- 瑙ｅ瘑瀵嗛挜涓嶆斁鍏?JWT payload锛岃€屾槸瀛樺偍鍦?`app.state.decrypt_key`锛堟湇鍔″櫒绔唴瀛橈級
- JWT 浠呮惡甯?session_id锛岀敤浜庡叧鑱旀湇鍔″櫒绔紦瀛樼殑瀵嗛挜

### 8.4 鏀诲嚮闈㈠垎鏋?
| 鏀诲嚮鍦烘櫙 | 闃叉姢鎺柦 |
|----------|---------|
| SQLite 鏂囦欢娉勯湶 | 鍑嵁鍏ㄩ儴 AES-256-GCM 鍔犲瘑锛屾棤瀵嗛挜鏃犳硶瑙ｅ瘑 |
| 鍐呭瓨 dump | 鍙€夌殑鏁忔劅鍐呭瓨鍔犻攣锛坄mlock`锛夛紝閫€鍑?閿佸畾涓诲姩鎿﹂櫎 |
| CSRF | FastAPI 鍚屾簮绛栫暐 + CORS 闄愬埗 localhost |
| XSS | Vue 3 榛樿杞箟锛屽墠绔笉娓叉煋鍘熷 HTML |

---

## 涔濄€佸惎鍔ㄦ祦绋?
```
FastAPI lifespan 鍚姩
鈹?鈹溾攢 1. config.py         鈫?鍔犺浇鐜鍙橀噺
鈹溾攢 2. database.py       鈫?鍒濆鍖?SQLite 杩炴帴 + 寤鸿〃
鈹溾攢 3. utils/            鈫?鍔犲瘑宸ュ叿鍒濆鍖?鈹溾攢 4. auth.py           鈫?bcrypt + Argon2id 鍑嗗
鈹溾攢 5. vault.py          鈫?Vault 瀹炰緥鍒涘缓锛屽垵濮嬩负閿佸畾鐘舵€?鈹溾攢 6. plugin_base.py    鈫?鍔犺浇鎻掍欢鎶借薄鍩虹被
鈹溾攢 7. plugin_loader.py  鈫?鎵弿 plugins/ 鍜?user_plugins/ 鍔犺浇鎻掍欢
鈹溾攢 8. orchestrator.py   鈫?绛惧埌缂栨帓鍣ㄥ疄渚嬪寲
鈹溾攢 9. scheduler.py      鈫?浠?DB 鍔犺浇 cron 閰嶇疆锛屽惎鍔?APScheduler
鈹?鈹溾攢 10. routers/*         鈫?娉ㄥ唽鎵€鏈?API 璺敱
鈹?鈹斺攢 绛夊緟璇锋眰...
    鈹?    鈹溾攢 POST /api/unlock  鈫?Vault.unlock(password) 鈫?瑙ｅ瘑鍑嵁鍒板唴瀛?    鈹溾攢 POST /api/signs/*  鈫?Orchestrator 浣跨敤鍐呭瓨涓殑鏄庢枃鍑嵁鎵ц绛惧埌
    鈹溾攢 POST /api/lock    鈫?Vault.lock() 鈫?閿€姣佸瘑閽ュ拰缂撳瓨
    鈹斺攢 瀹氭椂瑙﹀彂          鈫?Scheduler 瑙﹀彂 鈫?Orchestrator.sign_all()
```

---

## 鍗併€佷緷璧栨嫇鎵戜笌瀹炵幇椤哄簭

### 10.1 妯″潡渚濊禆鍏崇郴

```
                    鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                    鈹? config.py  鈹?                    鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹?                           鈹?                    鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹?                    鈹?database.py 鈹?                    鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹?                           鈹?              鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?              鈹?           鈹?           鈹?       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?       鈹?encryption 鈹?鈹?models 鈹?鈹?auth.py  鈹?       鈹?(utils)    鈹?鈹?(ORM)  鈹?鈹?(瀵嗛挜娲剧敓)鈹?       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹攢鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹?              鈹?           鈹?          鈹?              鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                           鈹?                    鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹?                    鈹?  vault.py  鈹?                    鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹?                           鈹?              鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?              鈹?           鈹?           鈹?       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?鈹屸攢鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹? 鈹屸攢鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?       鈹俻lugin_base 鈹?鈹?push   鈹? 鈹?scheduler鈹?       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹? 鈹斺攢鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹?              鈹?                       鈹?       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?                 鈹?       鈹俻lugin_loader鈹?                鈹?       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹?                 鈹?              鈹?                       鈹?       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹?       鈹?       orchestrator.py          鈹?       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?                      鈹?              鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?              鈹?               鈹?       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹?  鈹屸攢鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹?       鈹? schemas   鈹?  鈹? routers   鈹?       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?  鈹斺攢鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹?                              鈹?                       鈹屸攢鈹€鈹€鈹€鈹€鈹€鈻尖攢鈹€鈹€鈹€鈹€鈹€鈹?                       鈹?  main.py   鈹?                       鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

### 10.2 鎺ㄨ崘瀹炵幇椤哄簭

```
Phase 1 (楠ㄦ灦)
  config.py 鈫?database.py 鈫?plugin_base.py 鈫?plugin_loader.py
  鈫?main.py (FastAPI 鍚姩 + 绌鸿矾鐢?
  楠岃瘉: /api/plugins 杩斿洖宸插姞杞界殑鎻掍欢鍒楄〃

Phase 2 (瀹夊叏灞?
  encryption.py 鈫?auth.py 鈫?vault.py + schemas/auth.py
  鈫?routers/auth.py
  楠岃瘉: POST /api/unlock 鎴愬姛鎷垮埌 JWT

Phase 3 (绛惧埌鑳藉姏)
  kuro_plugin 鍐呭瀹炵幇 + schemas/credential.py + schemas/sign.py
  鈫?orchestrator.py 鈫?routers/credentials.py + routers/sign.py
  鈫?models/sign_log.py + schemas/log.py + routers/logs.py
  楠岃瘉: 娣诲姞 Token 鈫?绛惧埌楦ｆ疆/鎴樺弻 鈫?杩斿洖缁撴灉 鈫?鍐欏叆鏃ュ織

Phase 4 (瀹氭椂浠诲姟)
  scheduler.py 鈫?routers/schedule.py
  鈫?鎸佷箙鍖?cron 閰嶇疆 鈫?APScheduler 鑷姩绛惧埌
  楠岃瘉: 璁剧疆 cron 琛ㄨ揪寮?鈫?瀹氭椂瑙﹀彂绛惧埌

Phase 5 (浼樺寲)
  WebSocket 鏃ュ織骞挎挱
  Dockerfile + docker-compose.yml
  Vue 3 鍓嶇瀵规帴

Phase 6 (绫虫父绀?
  mhy_plugin 鍐呭瀹炵幇
  鈫?push.py + routers/push_config.py
  楠岃瘉: 娣诲姞 Cookie 鈫?绛惧埌鍘熺绛?娓告垙 鈫?鎺ㄩ€侀€氱煡
  Vue 3 鍓嶇瀵规帴
```

---

## 鍗佷竴銆佹帹閫佹ā鍧?
### 11.1 鏀寔鐨勬帹閫佹笭閬?
| 娓犻亾 | 閰嶇疆鏂瑰紡 | 鐢ㄩ€?|
|------|----------|------|
| Telegram | Bot Token + Chat ID | 鍥介檯鐢ㄦ埛甯哥敤 |
| ServerChan (ftqq) | SendKey | 寰俊鎺ㄩ€?|
| PushPlus | Token | 寰俊鎺ㄩ€?|
| PushMe | URL + Keys | 鑷畾涔夋帹閫?|
| CQHTTP | API URL | QQ 鏈哄櫒浜烘帹閫?|
| SMTP Email | SMTP 閰嶇疆 | 閭欢鎺ㄩ€?|
| 浼佷笟寰俊 (WeCom) | Webhook URL | 浼佷笟寰俊鎺ㄩ€?|
| PushDeer | Key | iOS 鎺ㄩ€?|
| 閽夐拤鏈哄櫒浜?| Webhook URL | 閽夐拤鎺ㄩ€?|
| 椋炰功鏈哄櫒浜?| Webhook URL | 椋炰功鎺ㄩ€?|
| Bark | URL + Key | iOS 鎺ㄩ€?|
| Gotify | Server URL + Token | 鑷墭绠℃帹閫?|
| IFTTT | Webhook Key | IFTTT 鑱斿姩 |
| WebHook | 鑷畾涔?URL | 閫氱敤 |
| Qmsg | QQ 鍙?| QQ 鎺ㄩ€?|
| Discord | Webhook URL | Discord 棰戦亾鎺ㄩ€?|
| WxPusher | App Token + UID | 寰俊鎺ㄩ€?|

### 11.2 鎺ㄩ€佺瓑绾?
| 绛夌骇 | 琛屼负 |
|------|------|
| 1 | 浠呮帹閫佹眹鎬伙細浠婃棩绛惧埌鎴愬姛 X / 澶辫触 Y / 璺宠繃 Z |
| 2 | 閫愮敤鎴锋帹閫侊細姣忎釜鐢ㄦ埛涓€鏉℃秷鎭紝鍖呭惈璇ョ敤鎴锋墍鏈夋父鎴忕粨鏋?|
| 3 | 閫愭潯鎺ㄩ€侊細姣忎釜娓告垙鐨勬瘡涓粨鏋滃崟鐙彂閫?|

---

## 鍗佷簩銆侀儴缃叉柟妗?
### 12.1 鏈湴閮ㄧ讲

```bash
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
# 娴忚鍣ㄨ闂?http://127.0.0.1:8000
```

### 12.2 Docker 閮ㄧ讲

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

## 鍗佷笁銆佹墿灞曟€ц璁?
### 13.1 鏂板娓告垙

瀵逛簬宸叉湁鐨勬彃浠讹紙濡?mhy_plugin锛夛紝鍙渶鍦?`games/` 涓嬫柊澧炰竴涓枃浠讹細

```python
# plugins/mhy_plugin/games/themis.py
class ThemisGame(BaseGame):
    game_id = "tears_of_themis"
    display_name = "鏈畾浜嬩欢绨?
    act_id = "e202202251749321"

    async def sign_in(self, role: GameRole) -> SignInResult:
        return await self.client.post(
            "...",
            data={"act_id": self.act_id, "region": role.region, "uid": role.uid},
        )
```

鐒跺悗鍦?`plugin.py` 鐨?`supported_games` 涓姞涓婂嵆鍙€?
### 13.2 鏂板鎻掍欢骞冲彴

鍒涘缓涓€涓柊鐩綍 `plugins/ark_plugin/`锛屽疄鐜?`BaseGamePlugin`銆傛斁鍒?`plugins/` 鎴?`user_plugins/` 鍚庨噸鍚嵆鐢熸晥锛屽墠绔嚜鍔ㄥ嚭鐜板搴旂殑鎻掍欢鍗＄墖銆?
---

## 鍗佸洓銆佹妧鏈€哄姟涓庨闄?
| 椋庨櫓 | 褰卞搷 | 缂撹В鎺柦 |
|------|------|---------|
| 绫虫父绀?DS salt 鍙樻洿 | 绛惧埌澶辫触 | 鍦?WebUI 鎻愪緵"鏇存柊 Salt"鍏ュ彛锛涙垨浠庡叕寮€婧愯嚜鍔ㄦ姄鍙?|
| 楠岃瘉鐮?(retcode 1034) | 绛惧埌涓柇 | captcha 妫€娴嬪悗鏍囪"闇€浜哄伐澶勭悊"锛學ebUI 寮归獙璇侀€氶亾 |
| Cookie 杩囨湡 | 绛惧埌澶辫触 | Stoken 鑷姩鍒锋柊鏈哄埗锛涜繃鏈熷悗 WebUI 鎻愮ず鐢ㄦ埛鏇存柊 |
| 鎻掍欢鎺ュ彛鐮村潖鎬у彉鏇?| 绗笁鏂规彃浠朵笉鍏煎 | 閬靛畧璇箟鍖栫増鏈紱鍙樻洿鏃跺啓鍗囩骇鎸囧崡 |
| 鍐呭瓨瀵嗛挜瀹夊叏鎬?| 杩涚▼ dump 娉勯湶 | 鍙€夐」锛歚ctypes.memset` 涓诲姩鎿﹂櫎锛汸ython 灞傛棤娉曞畬鍏ㄩ槻鎶?|


