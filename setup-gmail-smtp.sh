#!/bin/bash

# FineData Gmail SMTP Setup Script
# This script helps you configure Gmail SMTP for development

echo "🚀 FineData Gmail SMTP Setup"
echo "============================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created!"
    echo ""
fi

echo "📧 Gmail SMTP Configuration Guide"
echo "=================================="
echo ""
echo "To use Gmail SMTP, you need to:"
echo ""
echo "1. 📱 Enable 2-Step Verification on your Google Account:"
echo "   • Go to: https://myaccount.google.com/security"
echo "   • Enable 2-Step Verification"
echo ""
echo "2. 🔑 Generate an App Password:"
echo "   • Go to: https://myaccount.google.com/apppasswords"
echo "   • Select 'Mail' → 'Other (custom name)'"
echo "   • Enter: 'FineData'"
echo "   • Copy the 16-character password"
echo ""
echo "3. ✏️  Edit your .env file:"
echo "   • SMTP_USERNAME=your-gmail@gmail.com"
echo "   • SMTP_PASSWORD=your-16-character-app-password"
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

# Check if required variables are set
if [ -z "$SMTP_USERNAME" ] && [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$SMTP_USERNAME" ]; then
    echo "❌ SMTP_USERNAME not configured in .env"
    echo "Please set SMTP_USERNAME=your-gmail@gmail.com"
    exit 1
fi

if [ -z "$SMTP_PASSWORD" ]; then
    echo "❌ SMTP_PASSWORD not configured in .env"
    echo "Please set SMTP_PASSWORD=your-16-character-app-password"
    exit 1
fi

echo "✅ SMTP configuration found:"
echo "   Server: smtp.gmail.com"
echo "   Port: 587"
echo "   Username: $SMTP_USERNAME"
echo "   From: noreply@finedata.ai"
echo ""

echo "🎯 Next Steps:"
echo "=============="
echo "1. Start the services: docker-compose up -d"
echo "2. Test email sending through the API"
echo "3. Check logs for any SMTP connection issues"
echo ""

echo "📚 For more information, see:"
echo "   • SMTP Configuration: docs/smtp-setup.md"
echo "   • API Documentation: /api/docs"
echo ""
echo "🎉 Gmail SMTP setup complete!"
