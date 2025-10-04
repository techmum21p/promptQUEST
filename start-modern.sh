#!/bin/bash

# PromptQuest Modern Web Application Startup Script
# This script helps you get started with the modern Next.js + FastAPI version

echo "🎯 PromptQuest Modern Web Application"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env-modern.example .env
    echo ""
    echo "🔧 Please edit the .env file and add your Google API credentials:"
    echo "   1. Get your API key from: https://aistudio.google.com/app/apikey"
    echo "   2. Edit .env and set GOOGLE_API_KEY=your-actual-api-key"
    echo "   3. Save the file"
    echo ""
    echo "Press Enter to continue after editing .env..."
    read
fi

echo "🚀 Starting PromptQuest applications..."
echo ""
echo "Building and starting Docker containers..."
docker-compose up --build

echo ""
echo "🎉 PromptQuest is now running!"
echo ""
echo "📱 Frontend:     http://localhost:3000"
echo "🔧 API Backend:  http://localhost:8000"
echo "📖 API Docs:     http://localhost:8000/docs"
echo ""
echo "To stop the services, run: docker-compose down"
