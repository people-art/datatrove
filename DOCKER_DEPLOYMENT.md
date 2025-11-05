# 🐳 FineData Docker Deployment Guide

本指南介绍如何使用Docker Compose部署完整的FineData服务栈。

## 📋 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存
- 至少10GB可用磁盘空间

## 🚀 快速启动

### 1. 克隆项目并进入目录

```bash
git clone <repository-url>
cd finedata
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑配置文件（必需）
nano .env
```

**必需配置项：**
- `STRIPE_SECRET_KEY`: Stripe测试密钥
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook密钥
- `STRIPE_PUBLISHABLE_KEY`: Stripe发布密钥

**可选配置项：**
- AWS S3配置（用于数据集存储）
- Hugging Face配置（用于数据集发布）
- SendGrid配置（用于邮件通知）

### 3. 启动服务

**启动命令配置说明：**

- **前端服务**: 使用 `npm run dev` 启动 Next.js 开发服务器
- **后端服务**: 使用 `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` 启动 FastAPI 服务器

```bash
# 开发模式（推荐用于测试）
./docker-start.sh

# 或直接使用docker-compose
docker-compose up --build -d

# 生产模式（带nginx反向代理）
./docker-start.sh prod
```

### 4. 测试配置

运行配置测试脚本验证所有组件：

```bash
# 测试Docker配置
./docker-test.sh
```

### 5. 访问应用

- **前端**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🏗️ 服务架构

```
┌─────────────────┐    ┌─────────────────┐
│   Nginx (443)   │    │   Frontend      │
│                 │    │   (Next.js)     │
│  Reverse Proxy  │────│   Port: 3000   │
└─────────────────┘    └─────────────────┘
          │                       │
          │                       │
          └───────────────────────┼──────────────────────┐
                                  │                      │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Backend API   │    │   PostgreSQL    │
                    │   (FastAPI)     │    │   Database      │
                    │   Port: 8000    │    │   Port: 5432    │
                    └─────────────────┘    └─────────────────┘
                              │
                              │
                    ┌─────────────────┐
                    │     Redis       │
                    │     Cache       │
                    │   Port: 6379    │
                    └─────────────────┘
```

## 📁 项目结构

```
finedata/
├── docker-compose.yml          # 主编排文件
├── docker-compose.override.yml # 开发环境覆盖
├── api/                        # 后端应用
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
├── web/                        # 前端应用
│   ├── Dockerfile
│   ├── next.config.ts
│   └── src/
├── nginx/                      # Nginx配置
│   └── nginx.conf
├── init-db.sql                 # 数据库初始化
├── env.example                 # 环境变量模板
└── docker-start.sh            # 启动脚本
```

## ⚙️ 环境配置

### 开发环境

开发环境使用`docker-compose.override.yml`自动覆盖配置：

- **热重载**: 代码变更自动重载
- **调试模式**: 启用详细日志
- **直接端口暴露**: 无需nginx反向代理

### 生产环境

生产环境启用nginx反向代理：

```bash
docker-compose --profile production up -d
```

**生产环境特性：**
- HTTPS支持（需要SSL证书）
- 请求压缩
- 静态文件缓存
- 安全头配置

## 🔧 服务管理

### 查看服务状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看服务日志
docker-compose logs [service-name]

# 实时查看日志
docker-compose logs -f [service-name]
```

### 重启服务

```bash
# 重启特定服务
docker-compose restart api

# 重启所有服务
docker-compose restart
```

### 停止和清理

```bash
# 停止服务
docker-compose down

# 停止服务并删除卷
docker-compose down -v

# 清理所有镜像和卷
docker-compose down --rmi all -v
```

## 🔍 故障排除

### 常见问题

#### 1. 服务启动命令

确保服务使用正确的启动命令：

**前端服务 (Next.js)**:
```yaml
command: ["npm", "run", "dev"]
```

**后端服务 (FastAPI)**:
```yaml
command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### 2. 端口占用

```bash
# 检查端口占用
lsof -i :3000
lsof -i :8000

# 修改docker-compose.yml中的端口映射
ports:
  - "3001:3000"  # 改为3001
```

#### 3. 数据库连接失败

```bash
# 检查PostgreSQL日志
docker-compose logs postgres

# 重置数据库
docker-compose down -v
docker-compose up postgres -d
```

#### 3. 构建失败

```bash
# 清理构建缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

#### 4. 内存不足

```bash
# 检查Docker内存设置
docker system info | grep "Total Memory"

# 增加Docker内存分配（Docker Desktop）
# Preferences -> Resources -> Memory
```

### 健康检查

```bash
# 检查所有服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost:8000/health
curl http://localhost:3000
```

## 🔒 安全配置

### SSL证书（生产环境）

1. 获取SSL证书（Let's Encrypt或其他）
2. 放置证书文件：
   ```
   nginx/ssl/
   ├── finedata.crt
   └── finedata.key
   ```
3. 更新nginx.conf中的证书路径

### 环境变量安全

- 绝不要将`.env`文件提交到版本控制
- 使用强密码和随机密钥
- 定期轮换API密钥

## 📊 监控和日志

### 日志收集

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定时间范围的日志
docker-compose logs --since "1h" api

# 导出日志
docker-compose logs api > api.log
```

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df
```

## 🚀 部署到生产

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 部署应用

```bash
# 克隆代码
git clone <repository-url>
cd finedata

# 配置生产环境
cp env.example .env
nano .env  # 配置生产环境变量

# 启动生产栈
./docker-start.sh prod
```

### 3. 配置反向代理（可选）

如果需要额外的反向代理（如Caddy或Traefik），可以参考nginx.conf配置。

## 📈 扩展和优化

### 水平扩展

```yaml
# 在docker-compose.yml中添加副本
services:
  api:
    deploy:
      replicas: 3
    # 添加负载均衡配置
```

### 性能优化

1. **数据库优化**:
   - 配置连接池
   - 添加索引
   - 启用查询缓存

2. **缓存策略**:
   - Redis集群
   - 应用级缓存
   - CDN集成

3. **监控告警**:
   - Prometheus + Grafana
   - ELK Stack
   - Sentry错误跟踪

## 🆘 支持

如果遇到问题，请：

1. 查看[故障排除](#故障排除)部分
2. 检查GitHub Issues
3. 查看详细日志：`docker-compose logs -f`
4. 联系技术支持

---

**注意**: 生产部署前，请确保所有安全配置都已正确设置，并进行充分的测试。
