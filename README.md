# 盲文学习互助平台

基于 Django + React + PostgreSQL 的盲文学习平台，集成 CNN 音频分类模型进行盲文识别评估。

## 功能

- **音频识别练习**：用户录制滑过盲文板的音频，后端 CNN 模型判断是否正确读出字符
- **结对练习**：学习者结对，互发盲文句子，通过 WebSocket 实时评估准确率
- **熟练度追踪**：记录学习进度，可视化准确率趋势和等级变化

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 18 + Vite + TailwindCSS + Recharts |
| 后端 | Django 4.2 + DRF + Django Channels |
| 数据库 | PostgreSQL 16 |
| 消息队列 | Redis + Celery |
| ML 模型 | PyTorch CNN (mel spectrogram) |
| 部署 | Docker Compose |

## 快速启动

### Docker 方式（推荐）

```bash
cp .env.example .env
docker-compose up --build
```

访问：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

### 本地开发

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_braille
python manage.py createsuperuser
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

**Celery Worker：**
```bash
cd backend
celery -A config worker -l info
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

**ML 模型训练：**
```bash
cd ml
pip install -r requirements.txt
# 将音频数据放入 data/raw/{a-z}/*.wav
python train.py
python export_model.py
# 将 saved_models/braille_cnn.pt 复制到 backend/ml_models/
```

## API 端点

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register/` | POST | 用户注册 |
| `/api/auth/login/` | POST | 登录获取 JWT |
| `/api/auth/refresh/` | POST | 刷新 Token |
| `/api/auth/profile/` | GET/PUT | 用户档案 |
| `/api/auth/proficiency/stats/` | GET | 熟练度统计 |
| `/api/auth/proficiency/history/` | GET | 历史数据 |
| `/api/braille/characters/` | GET | 盲文字符列表 |
| `/api/braille/sentences/` | GET/POST | 练习句子 |
| `/api/braille/sessions/` | GET/POST | 练习会话 |
| `/api/braille/sessions/{id}/end/` | POST | 结束会话 |
| `/api/audio/upload/` | POST | 上传音频 |
| `/api/audio/recordings/` | GET | 录音列表 |
| `/api/pairing/available/` | GET | 可配对伙伴 |
| `/api/pairing/sessions/` | GET/POST | 结对会话 |
| `ws/pair/{session_id}/` | WebSocket | 实时结对通信 |

## 项目结构

```
├── backend/          # Django 后端
│   ├── config/       # 项目配置（settings, urls, asgi, celery）
│   ├── accounts/     # 用户认证与档案
│   ├── braille/      # 盲文内容与练习会话
│   ├── audio/        # 音频上传与 ML 推理
│   ├── pairing/      # 结对练习 WebSocket
│   └── common/       # 共享工具
├── frontend/         # React 前端
│   └── src/
│       ├── pages/    # 页面组件
│       ├── components/ # UI 组件
│       ├── hooks/    # 自定义 Hooks
│       └── api/      # API 客户端
├── ml/               # ML 模型训练
│   ├── model.py      # CNN 架构
│   ├── train.py      # 训练脚本
│   └── export_model.py # 导出 TorchScript
└── docker-compose.yml
```
