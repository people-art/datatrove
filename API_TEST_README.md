# FineData API Endpoint Test Script

这个bash脚本用于测试FineData项目的全部API endpoint，确保各个服务正常工作。

## 使用方法

### 前置条件

1. 确保Docker Compose服务正在运行：
   ```bash
   docker-compose up -d
   ```

2. 确保API服务可访问（端口18000）：
   ```bash
   curl http://localhost:18000/health
   ```

### 运行测试

```bash
./test_api_endpoints.sh
```

## 测试覆盖的Endpoint

### 基础健康检查
- `GET /health` - 服务健康状态检查

### 邮件验证 (Email Validation)
- `POST /api/v1/email/validate` - 邮件地址格式验证
- `POST /api/v1/email/verify/send` - 发送邮件验证码

### 基准测试 (Benchmark)
- `POST /api/v1/benchmark/quote` - 生成数据集报价
- `POST /api/v1/benchmark/jobs` - 创建基准测试任务
- `GET /api/v1/benchmark/jobs/{job_id}` - 获取任务状态

### 订单管理 (Orders)
- `POST /api/v1/orders` - 创建数据集生成订单
- `GET /api/v1/orders/{order_id}` - 获取订单状态
- `GET /api/v1/orders/{order_id}/production` - 获取生产任务状态

### 支付处理 (Payments)
- `POST /api/v1/checkout/session` - 创建Stripe支付会话

## 测试结果说明

脚本会输出彩色结果：
- 🟢 **绿色**: 测试通过
- 🔴 **红色**: 测试失败
- 🟡 **黄色**: 警告（某些功能在开发环境不可用）

### 开发环境中的已知问题

在开发环境中，以下测试可能失败（这是正常的）：

1. **订单创建**: 可能因数据库配置或Stripe集成问题失败
2. **支付会话**: 需要有效的Stripe测试密钥
3. **邮件发送**: 需要SendGrid API密钥

## 脚本特性

- 自动检查Docker服务状态
- 彩色输出便于阅读
- 详细的测试报告
- 优雅处理已知问题
- 不因单个测试失败而停止整个测试套件

## 故障排除

### 服务未运行
```
ERROR: finedata-api service is not running
```
**解决**: 运行 `docker-compose up -d`

### API不可访问
```
ERROR: Connection refused
```
**解决**: 检查端口18000是否被占用，或等待服务完全启动

### 数据库连接问题
某些测试可能因数据库初始化问题失败，这在首次运行时是正常的。
