#!/bin/bash

# FineData SMTP Setup Script
# This script helps you configure SMTP for development

echo "🚀 FineData SMTP Setup"
echo "======================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created!"
    echo ""
fi

echo "📧 SMTP Configuration Options"
echo "============================="
echo ""
echo "FineData supports multiple SMTP providers:"
echo ""
echo "1. 🏢 Feishu (飞书) SMTP - Default for development:"
echo "   • Server: smtp.feishu.cn"
echo "   • Port: 587 (STARTTLS)"
echo "   • Username: contacts@agenticeconomics.org"
echo "   • Limits: 200 emails/100s, 100 emails/day"
echo ""
echo "2. 📧 Gmail SMTP (alternative):"
echo "   • Enable 2-Step Verification"
echo "   • Generate App Password at https://myaccount.google.com/apppasswords"
echo "   • Use 16-character password (not login password)"
echo ""
echo "3. 🏭 SendGrid SMTP (production recommended):"
echo "   • Server: smtp.sendgrid.net"
echo "   • Port: 587"
echo "   • Username: apikey"
echo "   • Password: your-sendgrid-api-key"
echo ""
echo "4. 🏢 Enterprise SMTP (custom):"
echo "   • Configure your organization's SMTP settings"
echo ""

echo "📝 Current SMTP Configuration:"
echo "=============================="

# Load current configuration
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null)
fi

echo "   Server: ${SMTP_SERVER:-smtp.feishu.cn}"
echo "   Port: ${SMTP_PORT:-587}"
echo "   Username: ${SMTP_USERNAME:-contacts@agenticeconomics.org}"
echo "   From: ${FROM_EMAIL:-contacts@agenticeconomics.org}"
echo ""

read -p "Do you want to edit the .env file now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "Please edit .env file manually with your preferred editor"
    fi
fi

echo ""
echo "🔍 Testing SMTP Configuration..."
echo "================================"

# Reload configuration after potential edits
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs 2>/dev/null)
fi

if [ -z "$SMTP_USERNAME" ]; then
    echo "❌ SMTP_USERNAME not configured in .env"
    echo "Please set SMTP_USERNAME in your .env file"
    exit 1
fi

if [ -z "$SMTP_PASSWORD" ]; then
    echo "❌ SMTP_PASSWORD not configured in .env"
    echo "Please set SMTP_PASSWORD in your .env file"
    exit 1
fi

echo "✅ SMTP configuration validated:"
echo "   Server: $SMTP_SERVER"
echo "   Port: $SMTP_PORT"
echo "   Username: $SMTP_USERNAME"
echo "   From: ${FROM_EMAIL:-noreply@finedata.ai}"
echo ""

echo "🎯 Next Steps:"
echo "=============="
echo "1. Start the services: docker-compose up -d"
echo "2. Test email sending through the API"
echo "3. Check logs for any SMTP connection issues"
echo ""

echo "📧 Feishu SMTP Limits Reminder:"
echo "==============================="
echo "• 200 emails per 100 seconds"
echo "• 100 emails per day per sender"
echo "• Monitor usage to avoid hitting limits"
echo ""

echo "📚 For more information, see:"
echo "   • SMTP Configuration: docs/smtp-setup.md"
echo "   • API Documentation: /api/docs"
echo ""
echo "🎉 SMTP setup complete!"
