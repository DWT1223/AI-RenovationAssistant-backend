# 装修AI小程序后端

基于 FastAPI + MySQL 的装修AI助手后端服务

## 环境要求

- Python 3.11+
- MySQL 8.0+

## 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥
```

## 启动服务

```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## API文档

启动服务后访问: http://localhost:8000/docs

## 初始化数据库

```bash
# 创建数据库
mysql -u root -p < init.sql

# 或使用 Alembic 迁移
alembic upgrade head
```
