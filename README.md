# 一步 Career Companion · AI 求职成长陪伴产品

> 从"招聘"到"成长陪伴"——早连接、早认知、早准备、早陪伴

## 项目概述

一步是一款面向全体在校大学生的 AI 求职成长陪伴小程序。通过三维用户画像（专业、学历、阶段），为每位学生提供个性化、阶段感知的 AI 陪伴和成长方案。

### 核心功能

| 模块 | 功能 |
|---|---|
| **引导问卷** | 1分钟完成三维画像定位，自动识别当前阶段 |
| **AI 陪伴对话** | 阶段感知的 AI 对话，提供个性化建议 |
| **成长方案** | 根据阶段推荐内容（行业认知、简历模板、面试准备等） |
| **用户画像** | 可视化三维画像，随时切换阶段 |

## 项目结构

```
career-companion/
├── backend/                    # 后端服务 (FastAPI)
│   ├── main.py                # 应用入口
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── models.py              # 数据模型
│   ├── data_definitions.py    # 三维画像数据定义
│   ├── routers/
│   │   ├── user.py            # 用户 & 引导问卷 API
│   │   ├── chat.py            # AI 对话 API
│   │   └── content.py         # 内容推荐 API
│   ├── services/
│   │   ├── stage_engine.py    # 阶段识别引擎
│   │   └── ai_service.py     # AI 对话服务
│   └── requirements.txt       # Python 依赖
│
└── miniprogram/               # 微信小程序前端
    ├── app.js                 # 应用入口
    ├── app.json               # 应用配置
    ├── app.wxss               # 全局样式
    ├── utils/
    │   └── api.js             # API 接口封装
    └── pages/
        ├── index/             # 首页
        ├── onboarding/        # 引导问卷
        ├── chat/              # AI 对话
        ├── content/           # 成长方案
        └── profile/           # 我的画像
```

## 快速开始

### 1. 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 AI_API_KEY 等信息

# 启动服务
python main.py
```

服务默认运行在 `http://localhost:8000`

### 2. 小程序配置

1. 使用微信开发者工具打开 `miniprogram/` 目录
2. 修改 `project.config.json` 中的 `appid` 为你的小程序 AppID
3. 修改 `app.js` 中的 `apiBase` 为你的后端地址
4. 添加 tab bar 图标文件到 `miniprogram/images/` 目录：
   - `tab-home.png` / `tab-home-active.png`
   - `tab-chat.png` / `tab-chat-active.png`
   - `tab-content.png` / `tab-content-active.png`
   - `tab-profile.png` / `tab-profile-active.png`

### 3. 环境变量说明

| 变量 | 说明 | 默认值 |
|---|---|---|
| `DATABASE_URL` | 数据库连接 URL | `sqlite+aiosqlite:///./career_companion.db` |
| `AI_API_KEY` | AI 服务 API Key | - |
| `AI_API_BASE` | AI 服务 API 地址 | `https://api.openai.com/v1` |
| `AI_MODEL` | AI 模型名称 | `gpt-4o-mini` |

## API 文档

启动后端后访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

### 主要接口

| Method | Path | 说明 |
|---|---|---|
| POST | `/api/user/login` | 用户登录/注册 |
| GET | `/api/user/onboarding/questions` | 获取引导问卷 |
| POST | `/api/user/onboarding/submit` | 提交引导问卷 |
| GET | `/api/user/profile/{id}` | 获取用户画像 |
| POST | `/api/user/stage` | 更新阶段 |
| GET | `/api/user/stages` | 阶段列表 |
| POST | `/api/chat/send` | 发送消息 |
| POST | `/api/chat/stream` | 流式发送消息 |
| GET | `/api/chat/history/{id}` | 对话历史 |
| GET | `/api/content/stage/{id}` | 阶段内容推荐 |

## 阶段定义 (S1-S7)

| 阶段 | 名称 | 核心需求 |
|---|---|---|
| S1 | 刚入学 / 迷茫探索期 | 行业认知扫盲、专业出路地图 |
| S2 | 专业积累期 | 技能差距分析、学习路径推荐 |
| S3 | 实习准备期 | 简历优化、模拟面试、JD拆解 |
| S4 | 实习验证期 | 经验沉淀、转正策略、软技能 |
| S5 | 正式求职期 | 投递管理、面试复盘、Offer比较 |
| S6 | 已上岸衔接期 | 入职准备、技能预修、身份转换 |
| S7 | 深造准备期 | 选校定位、推荐信、备选方案 |

## 设计理念

本产品基于「三维用户画像」模型：

1. **第一维：专业类型** — 7大类覆盖全专业
2. **第二维：学历与院校** — 国内/海外、本科/硕士/博士全覆盖
3. **第三维：当前阶段** — 7个动态阶段，自动识别 + 手动切换

阶段识别引擎会根据用户的学历类型和年级自动推荐阶段，同时支持手动切换，确保精准匹配每一位用户的实际状态。
