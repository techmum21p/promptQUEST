"""
Standalone database setup script for PostgreSQL prompt training app
Run this from the project root directory
"""

import os
import asyncio
import subprocess
import sys
from typing import Optional, List
from pathlib import Path
import logging

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, skip loading
    pass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DatabaseConfig:
    """Simple database configuration"""
    
    def __init__(self):
        # PostgreSQL connection settings
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = os.getenv('POSTGRES_DB', 'prompt_training_db')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', '')
        
        # SSL settings
        self.ssl_mode = os.getenv('POSTGRES_SSL_MODE', 'prefer')
        
        # Connection timeout
        self.command_timeout = float(os.getenv('POSTGRES_COMMAND_TIMEOUT', '30.0'))


class DatabaseSetup:
    """Handles database setup and initialization"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.schema_file = Path(__file__).parent / "database" / "schema.sql"
    
    async def check_postgresql_available(self) -> bool:
        """Check if PostgreSQL is available in the system"""
        try:
            # Check if psql command is available
            result = subprocess.run(
                ['psql', '--version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"PostgreSQL found: {result.stdout.strip()}")
                return True
            else:
                logger.warning("PostgreSQL not found in PATH")
                return False
        except FileNotFoundError:
            logger.warning("PostgreSQL (psql) command not found")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("PostgreSQL check timed out")
            return False
    
    async def create_database(self, admin_user: str = None, admin_password: str = None) -> bool:
        """Create the database if it doesn't exist"""
        try:
            # Use admin credentials if provided, otherwise use default superuser
            db_name = self.config.database
            db_user = admin_user or self.config.user
            password_env = f"PGPASSWORD={admin_password or self.config.password}"
            
            logger.info(f"Creating database '{db_name}'...")
            
            # Create database command
            cmd = [
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', db_user,
                '-d', 'postgres',  # Connect to default postgres database
                '-c', f"CREATE DATABASE {db_name};"
            ]
            
            # Run command with password
            env = os.environ.copy()
            env['PGPASSWORD'] = admin_password or self.config.password
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Database '{db_name}' created successfully")
                return True
            else:
                # Check if database already exists
                if "already exists" in result.stderr.lower():
                    logger.info(f"✓ Database '{db_name}' already exists")
                    return True
                else:
                    logger.error(f"✗ Failed to create database: {result.stderr}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    async def setup_schema(self, admin_user: str = None, admin_password: str = None) -> bool:
        """Setup database schema from SQL file"""
        try:
            if not self.schema_file.exists():
                logger.error(f"Schema file not found: {self.schema_file}")
                return False
            
            logger.info(f"Setting up database schema from {self.schema_file}...")
            
            # SQL command to run schema file
            db_name = self.config.database
            db_user = admin_user or self.config.user
            
            # Prepare environment
            env = os.environ.copy()
            env['PGPASSWORD'] = admin_password or self.config.password
            
            # Run schema file
            cmd = [
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', db_user,
                '-d', db_name,
                '-f', str(self.schema_file)
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✓ Database schema setup completed successfully")
                return True
            else:
                logger.error(f"✗ Schema setup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up schema: {e}")
            return False
    
    async def verify_setup(self) -> bool:
        """Verify database setup is correct"""
        try:
            logger.info("Verifying database setup...")
            
            # Check if schema file exists
            if not self.schema_file.exists():
                logger.error(f"Schema file not found: {self.schema_file}")
                return False
            
            # Test connection by checking if we can connect to the database
            result = subprocess.run([
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', self.config.user,
                '-d', self.config.database,
                '-c', 'SELECT 1;'
            ], env={**os.environ, 'PGPASSWORD': self.config.password}, 
               capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("✓ Database connection test passed")
            else:
                logger.error(f"✗ Database connection test failed: {result.stderr}")
                return False
            
            # Check if required tables exist
            required_tables = ['users', 'user_progress', 'user_badges']
            
            for table in required_tables:
                check_cmd = [
                    'psql',
                    '-h', self.config.host,
                    '-p', str(self.config.port),
                    '-U', self.config.user,
                    '-d', self.config.database,
                    '-c', f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table}');"
                ]
                
                result = subprocess.run(
                    check_cmd,
                    env={**os.environ, 'PGPASSWORD': self.config.password},
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0 and 't' in result.stdout.lower():
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' not found")
                    return False
            
            # Check if materialized view exists
            view_check_cmd = [
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', self.config.user,
                '-d', self.config.database,
                '-c', "SELECT EXISTS (SELECT FROM pg_matviews WHERE schemaname = 'public' AND matviewname = 'leaderboard');"
            ]
            
            result = subprocess.run(
                view_check_cmd,
                env={**os.environ, 'PGPASSWORD': self.config.password},
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 't' in result.stdout.lower():
                logger.info("✓ Materialized view 'leaderboard' exists")
            else:
                logger.error("✗ Materialized view 'leaderboard' not found")
                return False
            
            logger.info("✓ Database setup verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying setup: {e}")
            return False
    
    async def backup_database(self, backup_file: str = None) -> Optional[str]:
        """Backup the database to a SQL file"""
        try:
            if not backup_file:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"prompt_training_backup_{timestamp}.sql"
            
            logger.info(f"Creating database backup: {backup_file}")
            
            db_name = self.config.database
            db_user = self.config.user
            
            # Prepare environment
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.password
            
            # pg_dump command
            cmd = [
                'pg_dump',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', db_user,
                '-f', backup_file,
                db_name
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Database backup created: {backup_file}")
                return backup_file
            else:
                logger.error(f"✗ Backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None


async def setup_database(admin_user: str = None, admin_password: str = None) -> bool:
    """Complete database setup process"""
    try:
        logger.info("Starting database setup process...")
        
        setup = DatabaseSetup()
        
        # Step 1: Check PostgreSQL availability
        if not await setup.check_postgresql_available():
            logger.error("PostgreSQL is not available. Please install PostgreSQL first.")
            return False
        
        # Step 2: Create database
        if not await setup.create_database(admin_user, admin_password):
            logger.error("Failed to create database")
            return False
        
        # Step 3: Setup schema
        if not await setup.setup_schema(admin_user, admin_password):
            logger.error("Failed to setup schema")
            return False
        
        # Step 4: Verify setup
        if not await setup.verify_setup():
            logger.error("Database setup verification failed")
            return False
        
        logger.info("✓ Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False


async def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database setup utility for Prompt Training App")
    parser.add_argument('--action', choices=['setup', 'verify', 'backup'], 
                       default='setup', help='Action to perform')
    parser.add_argument('--admin-user', help='PostgreSQL admin username')
    parser.add_argument('--admin-password', help='PostgreSQL admin password')
    parser.add_argument('--backup-file', help='Backup file path')
    
    args = parser.parse_args()
    
    setup = DatabaseSetup()
    
    if args.action == 'setup':
        success = await setup_database(args.admin_user, args.admin_password)
        sys.exit(0 if success else 1)
    
    elif args.action == 'verify':
        success = await setup.verify_setup()
        sys.exit(0 if success else 1)
    
    elif args.action == 'backup':
        backup_file = await setup.backup_database(args.backup_file)
        sys.exit(0 if backup_file else 1)


if __name__ == "__main__":
    logger.info("🚀 PostgreSQL Setup for Prompt Training App")
    logger.info("=" * 50)
    asyncio.run(main())
