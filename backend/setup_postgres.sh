#!/bin/bash

# PostgreSQL Setup Script for PromptQUEST
# This script helps set up PostgreSQL for the PromptQUEST application

echo "Setting up PostgreSQL for PromptQUEST..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install PostgreSQL first."
    echo "On macOS: brew install postgresql"
    echo "On Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "On CentOS/RHEL: sudo yum install postgresql postgresql-server"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL first."
    echo "On macOS: brew services start postgresql"
    echo "On Ubuntu: sudo systemctl start postgresql"
    echo "On CentOS/RHEL: sudo systemctl start postgresql"
    exit 1
fi

# Create database and user
echo "Creating database and user..."

# Create database
createdb promptquest 2>/dev/null || echo "Database 'promptquest' already exists or creation failed"

# Create user (optional - you can use existing postgres user)
# createuser -s promptquest_user 2>/dev/null || echo "User 'promptquest_user' already exists or creation failed"

echo "PostgreSQL setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the correct DATABASE_URL"
echo "2. Run the migration script: python migrate_to_postgres.py ../user_progress.json"
echo "3. Start the FastAPI backend: python main.py"
echo ""
echo "Example DATABASE_URL: postgresql://postgres:password@localhost:5432/promptquest"
