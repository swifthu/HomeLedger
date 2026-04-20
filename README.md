# HomeLedger - 家庭记账本

一款基于 AI 的智能家庭收支管理应用，支持文字描述和图片识别自动记账。

## 功能特性

### 智能记账
- **文字记账**：输入"早餐包子5元"，AI 自动识别分类和金额
- **图片记账**：上传小票/发票图片，AI 自动识别商品明细和总价
- **规则引擎**：常用消费模式（如"瑞幸"、"外卖"）毫秒级匹配
- **AI 兜底**：未知消费调用 MiniMax 大模型进行分类

### 分类体系
| 分类 | 图标 | 说明 |
|------|------|------|
| 餐饮 | 🍜 | 早午晚餐、饮料、零食 |
| 交通 | 🚗 | 打车、公交、地铁、油费 |
| 购物 | 🛒 | 网购、超市、便利店 |
| 居住 | 🏠 | 房租、水电、物业 |
| 医疗 | 💊 | 买药、看病、体检 |
| 娱乐 | 🎮 | 电影、游戏、旅游 |
| 教育 | 📚 | 培训、买书、课程 |
| 其他 | 📌 | 其他支出 |

### 数据管理
- 记录列表：分页浏览所有记账记录
- 记录详情：修改分类、金额、描述
- 待审核：AI 置信度不足的记录需人工确认
- 月度统计：自动计算 AI/规则/手动分类占比和准确率

### 导入导出
- **Excel 导出**：按日期范围导出消费记录
- **本地备份**：一键生成数据库备份文件
- **恢复数据**：上传备份文件还原历史数据

## 技术架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (React)                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Dashboard │ │ Records │ │ Review  │           │
│  └─────────┘ └─────────┘ └─────────┘           │
│                     │                            │
│              API: /api/records                   │
└─────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────┐
│               后端 (FastAPI + SQLite)            │
│  ┌──────────────┐    ┌──────────────────┐       │
│  │  规则引擎    │    │   AI 分类器      │       │
│  │  rules.yaml  │    │ MiniMax M2.7     │       │
│  └──────────────┘    └──────────────────┘       │
│                     │                            │
│              SQLite Database                      │
└─────────────────────────────────────────────────┘
```

### 前端技术栈
- React 18 + TypeScript
- Vite 构建工具
- React Router 客户端路由
- TanStack Query 数据请求
- 纯 CSS 样式（无框架依赖）

### 后端技术栈
- FastAPI Web 框架
- SQLAlchemy ORM
- SQLite 本地数据库
- MiniMax API（文字分类 + 图片识别）

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- MiniMax API Key（用于 AI 分类和图片识别）

### 1. 克隆项目
```bash
git clone https://github.com/swifthu/HomeLedger.git
cd HomeLedger
```

### 2. 配置后端
```bash
cd backend
echo "MINIMAX_API_KEY=你的API密钥" > .env
echo "MINIMAX_API_HOST=https://api.minimax.chat" >> .env
echo "MINIMAX_VLM_HOST=https://api.minimaxi.com" >> .env

# 安装依赖（使用项目专用虚拟环境）
/Users/jimmyhu/Documents/CC/.venv/bin/pip install fastapi uvicorn sqlalchemy pydantic openpyxl pyyaml httpx python-multipart

# 启动服务
/Users/jimmyhu/Documents/CC/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8022
```

### 3. 启动前端（如需独立开发）
```bash
cd frontend
npm install
npm run dev
```

> 生产环境：后端已内置前端静态文件，单端口 8022 即可访问全部功能。

### 4. 访问应用
打开浏览器访问：http://127.0.0.1:8022

## API 文档

### 记账相关

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/records` | 获取记录列表（支持分页、筛选） |
| POST | `/api/records` | 创建新记录 |
| PUT | `/api/records/{id}` | 更新记录 |
| DELETE | `/api/records/{id}` | 删除记录 |

### AI 相关

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/classify` | 文字分类（返回分类、金额、置信度） |
| POST | `/api/ai/image` | 图片识别（上传小票图片） |

### 统计导出

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/monthly` | 获取月度统计 |
| GET | `/api/export/excel` | 导出 Excel |
| GET | `/api/backup` | 创建备份 |
| POST | `/api/backup/restore` | 恢复备份 |

## 项目结构

```
HomeLedger/
├── backend/
│   ├── main.py          # FastAPI 主应用
│   ├── models.py        # 数据库模型
│   ├── ai/
│   │   ├── classifier.py  # 两级分类器
│   │   ├── rules.yaml     # 规则引擎配置
│   │   ├── client.py      # MiniMax API 客户端
│   │   └── image_client.py # 图片理解客户端
│   ├── db/
│   │   └── database.py  # 数据库初始化
│   └── tests/           # 单元测试
├── frontend/
│   ├── src/
│   │   ├── api/client.ts    # API 请求封装
│   │   ├── components/      # UI 组件
│   │   │   ├── ChatInput.tsx   # 记账输入框
│   │   │   ├── RecordCard.tsx  # 记录卡片
│   │   │   └── RecordList.tsx  # 记录列表
│   │   ├── pages/          # 页面组件
│   │   │   ├── Dashboard.tsx   # 首页
│   │   │   ├── Records.tsx      # 记录列表
│   │   │   ├── RecordDetail.tsx # 记录详情
│   │   │   └── Review.tsx       # 待审核
│   │   └── App.tsx         # 路由配置
│   └── dist/              # 编译后的静态文件
└── data/                  # SQLite 数据库文件
```

## 设计原则

### 两级分类系统
1. **规则优先**：命中的规则直接确认（置信度 1.0）
2. **AI 兜底**：规则未命中时调用 MiniMax M2.7 模型
3. **置信度决策**：置信度 ≥ 85% 自动确认，否则进入待审核

### 准确率目标
- AI 分类准确率目标：90%
- 通过用户纠正持续优化模型
- 每月统计准确率作为优化依据

## License

MIT