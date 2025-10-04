"""
Database setup and migration utilities for PostgreSQL prompt training app
"""

import os
import asyncio
import subprocess
import sys
from typing import Optional, List
from pathlib import Path
import logging

from database.config import DatabaseConfig, test_database_connection

logger = logging.getLogger(__name__)


class DatabaseSetup:
    """Handles database setup and initialization"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.schema_file = Path(__file__).parent / "schema.sql"
    
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
            
            # Test connection
            if not await test_database_connection():
                logger.error("✗ Database connection test failed")
                return False
            
            # Check if required tables exist
            required_tables = ['users', 'user_progress', 'user_badges']
            
            for table in required_tables:
                if await self._check_table_exists(table):
                    logger.info(f"✓ Table '{table}' exists")
                else:
                    logger.error(f"✗ Table '{table}' not found")
                    return False
            
            # Check if materialized view exists
            if await self._check_view_exists('leaderboard'):
                logger.info("✓ Materialized view 'leaderboard' exists")
            else:
                logger.error("✗ Materialized view 'leaderboard' not found")
                return False
            
            logger.info("✓ Database setup verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error verifying setup: {e}")
            return False
    
    async def _check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            from database.config import db_connection
            
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = $1
            );
            """
            
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, table_name)
                return result['exists'] if result else False
                
        except Exception as e:
            logger.error(f"Error checking table existence: {e}")
            return False
    
    async def _check_view_exists(self, view_name: str) -> bool:
        """Check if a materialized view exists in the database"""
        try:
            from database.config import db_connection
            
            query = """
            SELECT EXISTS (
                SELECT FROM pg_matviews 
                WHERE schemaname = 'public' 
                AND matviewname = $1
            );
            """
            
            async with db_connection.get_connection() as conn:
                result = await conn.fetchrow(query, view_name)
                return result['exists'] if result else False
                
        except Exception as e:
            logger.error(f"Error checking view existence: {e}")
            return False
    
    async def drop_database(self, admin_user: str=None, admin_password: str=None) -> bool:
        """Drop the database (use with caution!)"""
        try:
            db_name = self.config.database
            db_user = admin_user or self.config.user
            
            logger.warning(f"Dropping database '{db_name}'...")
            
            # Prepare environment
            env = os.environ.copy()
            env['PGPASSWORD'] = admin_password or self.config.password
            
            # Drop database command
            cmd = [
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', db_user,
                '-d', 'postgres',  # Connect to default postgres database
                '-c', f"DROP DATABASE IF EXISTS {db_name};"
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.warning(f"✓ Database '{db_name}' dropped successfully")
                return True
            else:
                logger.error(f"✗ Failed to drop database: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error dropping database: {e}")
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


class DatabaseMigration:
    """Handles database migrations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    async def run_migration(self, migration_file: str) -> bool:
        """Run a specific migration file"""
        try:
            migration_path = self.migrations_dir / migration_file
            
            if not migration_path.exists():
                logger.error(f"Migration file not found: {migration_path}")
                return False
            
            logger.info(f"Running migration: {migration_file}")
            
            db_name = self.config.database
            db_user = self.config.user
            
            # Prepare environment
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config.password
            
            # Run migration file
            cmd = [
                'psql',
                '-h', self.config.host,
                '-p', str(self.config.port),
                '-U', db_user,
                '-d', db_name,
                '-f', str(migration_path)
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Migration '{migration_file}' completed successfully")
                return True
            else:
                logger.error(f"✗ Migration failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running migration: {e}")
            return False
    
    def create_migration_template(self, migration_name: str) -> str:
        """Create a migration template file"""
        try:
            if not self.migrations_dir.exists():
                self.migrations_dir.mkdir(parents=True)
            
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{migration_name}.sql"
            filepath = self.migrations_dir / filename
            
            template = f"""-- Migration: {migration_name}
-- Created: {datetime.now().isoformat()}

-- Add your migration SQL here
-- Example:
-- ALTER TABLE users ADD COLUMN new_field VARCHAR(100);
-- CREATE INDEX idx_users_new_field ON users(new_field);

BEGIN;

-- Your migration code goes here

COMMIT;
"""
            
            with open(filepath, 'w') as f:
                f.write(template)
            
            logger.info(f"✓ Migration template created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error creating migration template: {e}")
            return ""


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
    parser.add_argument('--action', choices=['setup', 'verify', 'backup', 'drop'], 
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
    
    elif args.action == 'drop':
        success = await setup.drop_database(args.admin_user, args.admin_password)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
