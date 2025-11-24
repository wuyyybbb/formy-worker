# Formy Worker

Formy AI图像处理后台Worker服务。

## 功能

- 从Redis队列获取任务
- 调用ComfyUI Pipeline处理图像
- 支持AI换姿势、换头、换背景等功能

## 部署到 Render

### 环境变量配置

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `REDIS_URL` | Redis连接地址 | ✅ |
| `COMFYUI_URL` | ComfyUI服务地址 | ✅ |
| `SECRET_KEY` | JWT密钥 | ✅ |
| `UPLOAD_DIR` | 上传目录 | `./uploads` |
| `RESULT_DIR` | 结果目录 | `./results` |

### Render配置

```yaml
Name: formy-worker
Environment: Python 3
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python worker.py
```

### 启动日志

成功启动后应该看到：

```
[Worker] Pipeline Worker 已启动，等待任务...
[成功] Redis 连接正常
```

## 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量（.env文件）
REDIS_URL=redis://localhost:6379
COMFYUI_URL=your-comfyui-url
SECRET_KEY=your-secret-key

# 运行Worker
python worker.py
```

## 架构

```
Worker
  ├── Redis Queue (获取任务)
  ├── Pipeline Layer (处理任务)
  │   ├── PoseChangePipeline
  │   ├── HeadSwapPipeline
  │   └── BackgroundPipeline
  ├── Engine Layer (AI调用)
  │   └── ComfyUIEngine
  └── Redis (更新任务状态)
```

## 相关仓库

- Backend API: https://github.com/wuyyybbb/formy_backend
- Frontend: https://github.com/wuyyybbb/formy_frontend

