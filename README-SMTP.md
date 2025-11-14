# FineData SMTP Configuration Guide

## 📧 Feishu SMTP Setup (Default for Development)

FineData has been pre-configured with your Feishu SMTP settings for the development environment.

### Current Configuration

```bash
SMTP_SERVER=smtp.feishu.cn
SMTP_PORT=587
SMTP_USERNAME=contacts@agenticeconomics.org
SMTP_PASSWORD=ZHlpHYH3GorXyywN
FROM_EMAIL=contacts@agenticeconomics.org
FROM_NAME=FineData
```

### Sending Limits

- **Rate Limit**: 200 emails per 100 seconds
- **Daily Limit**: 100 emails per day per sender
- **Port**: 587 (STARTTLS) or 465 (SSL)

## 🚀 Quick Start

1. **Copy environment template**:
   ```bash
   cp .env.template .env
   ```

2. **Start services**:
   ```bash
   docker-compose up -d
   ```

3. **Test email functionality**:
   ```bash
   # Check logs for SMTP connection
   docker-compose logs api | grep -i smtp
   ```

## 🔧 Alternative SMTP Providers

### Gmail SMTP

If you prefer to use Gmail SMTP instead:

1. Enable 2-Step Verification on your Google Account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Update your `.env` file:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-16-character-app-password
FROM_EMAIL=your-gmail@gmail.com
FROM_NAME=FineData
```

### SendGrid SMTP (Production Recommended)

For production use, SendGrid provides better deliverability:

```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=your-verified-sender@yourdomain.com
FROM_NAME=FineData
```

## 📧 Email Features

FineData will automatically send emails for:

- **Email Verification**: User registration confirmation
- **Dataset Delivery**: When processing completes
- **Payment Notifications**: Success/failure alerts
- **Order Updates**: Status change notifications

## ⚠️ Important Notes

- **Monitor Usage**: Feishu has rate limits - monitor your email sending frequency
- **Production**: Consider using SendGrid or AWS SES for production deployments
- **Security**: Never commit `.env` files with real credentials to version control

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Failed**:
   - Verify SMTP credentials are correct
   - Check if Feishu account has SMTP access

2. **Rate Limited**:
   - Wait for rate limit to reset (100 seconds for burst limit)
   - Monitor daily email count

3. **Connection Timeout**:
   - Check network connectivity
   - Verify SMTP server address and port

### Testing SMTP

Run the SMTP setup script to validate configuration:

```bash
./setup-smtp.sh
```

This will check your SMTP configuration and provide guidance for any issues.
