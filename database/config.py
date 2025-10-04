"""
Database configuration and connection utilities for PostgreSQL
"""

import os
import asyncio
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        # PostgreSQL connection settings
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = os.getenv('POSTGRES_DB', 'prompt_training_db')
        self.user = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', '')
        
        # Connection pool settings
        self.min_connections = int(os.getenv('POSTGRES_MIN_CONNECTIONS', '5'))
        self.max_connections = int(os.getenv('POSTGRES_MAX_CONNECTIONS', '20'))
        
        # SSL settings
        self.ssl_mode = os.getenv('POSTGRES_SSL_MODE', 'prefer')
        
        # Connection timeout
        self.command_timeout = float(os.getenv('POSTGRES_COMMAND_TIMEOUT', '30.0'))
        
    @property
    def dsn(self) -> str:
        """Return database DSN string"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def get_pool_config(self) -> dict:
        """Return connection pool configuration"""
        config = {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'min_size': self.min_connections,
            'max_size': self.max_connections,
            'command_timeout': self.command_timeout,
        }
        
        # Only add SSL mode if it's not 'disable'
        if self.ssl_mode and self.ssl_mode.lower() not in ['disable', 'none']:
            config['ssl'] = self.ssl_mode
            
        return config


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.pool = None
        self._connection_count = 0
    
    async def initialize_pool(self) -> bool:
        """Initialize the connection pool"""
        try:
            # Check if pool already exists and is healthy
            if self.pool and not self.pool._closed:
                logger.info("Pool already exists and is healthy")
                return True
            
            # Close existing pool if it exists but is closed
            if self.pool:
                try:
                    await self.close_pool()
                except Exception as e:
                    logger.warning(f"Error closing old pool: {e}")
                
            pool_config = self.config.get_pool_config()
            
            # Additional asyncpg-specific configurations
            # Note: asyncpg.create_pool() doesn't accept pool_size, max_queries, etc.
            # These are controlled by min_size and max_size parameters which are already set
            
            self.pool = await asyncpg.create_pool(**pool_config)
            logger.info(f"Database pool initialized with {self.config.min_connections}-{self.config.max_connections} connections")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            return False
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool with improved error handling"""
        # Check if we're in a valid event loop context
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                logger.error("Event loop is closed, cannot create connection")
                raise Exception("Event loop is closed")
        except RuntimeError:
            logger.warning("No event loop running")
        
        if not self.pool:
            initialized = await self.initialize_pool()
            if not initialized:
                raise Exception("Failed to initialize database pool")
        
        conn = None
        try:
            conn = await self.pool.acquire()
            self._connection_count += 1
            logger.debug(f"Acquired connection #{self._connection_count}")
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            # Handle common asyncpg errors gracefully
            if "Event loop is closed" in str(e) or "connection was closed" in str(e):
                logger.warning("Database connection closed, this is likely due to Streamlit rerun")
                raise Exception("Database temporarily unavailable due to Streamlit lifecycle")
            raise
        finally:
            if conn and self.pool and not self.pool._closed:
                try:
                    await self.pool.release(conn)
                    logger.debug(f"Released connection #{self._connection_count}")
                except Exception as e:
                    logger.error(f"Error releasing connection: {e}")
            elif conn:
                logger.warning("Pool is closed or unavailable, cannot release connection")
    
    async def execute_query(self, query: str, *args):
        """Execute a query and return results"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_single(self, query: str, *args):
        """Execute a query and return single result"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_non_query(self, query: str, *args):
        """Execute a query without returning results"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def check_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchrow("SELECT 1 as test")
                return result['test'] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database connection instance
db_connection = DatabaseConnection()


class DatabaseHealthCheck:
    """Database health check utilities"""
    
    def __init__(self, db_conn: DatabaseConnection):
        self.db = db_conn
    
    async def get_database_info(self) -> dict:
        """Get database information and statistics"""
        try:
            async with self.db.get_connection() as conn:
                # Database size
                size_query = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;
                """
                size_result = await conn.fetchrow(size_query)
                
                # Connection count
                conn_count_query = """
                SELECT count(*) as connection_count 
                FROM pg_stat_activity 
                WHERE datname = current_database();
                """
                conn_result = await conn.fetchrow(conn_count_query)
                
                # Table row counts
                table_stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as total_inserts,
                    n_tup_upd as total_updates,
                    n_tup_del as total_deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples
                FROM pg_stat_user_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename;
                """
                table_stats = await conn.fetch(table_stats_query)
                
                return {
                    'database_size': size_result['database_size'],
                    'connection_count': conn_result['connection_count'],
                    'table_stats': [dict(row) for row in table_stats],
                    'status': 'healthy'
                }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def get_pool_info(self) -> dict:
        """Get connection pool information"""
        if not self.db.pool:
            return {'status': 'pool_not_initialized'}
        
        return {
            'status': 'healthy',
            'min_connections': self.config.min_connections,
            'max_connections': self.config.max_connections,
            'current_pool_size': len(self.db.pool._queue)
        }


# Database utility functions
async def init_database():
    """Initialize database connection pool"""
    return await db_connection.initialize_pool()


async def close_database():
    """Close database connection pool"""
    await db_connection.close_pool()


async def test_database_connection() -> bool:
    """Test database connection"""
    return await db_connection.check_connection()


if __name__ == "__main__":
    """Test database configuration"""
    async def test_db():
        logger.info("Testing database configuration...")
        
        # Test configuration
        config = DatabaseConfig()
        logger.info(f"Database: {config.database}")
        logger.info(f"Host: {config.host}:{config.port}")
        logger.info(f"User: {config.user}")
        logger.info(f"DSN: {config.dsn}")
        
        # Test connection
        if await test_database_connection():
            logger.info("✓ Database connection successful")
        else:
            logger.error("✗ Database connection failed")
            
        # Test health check
        health = DatabaseHealthCheck(db_connection)
        info = await health.get_database_info()
        logger.info(f"Database health: {info}")
        
        await close_database()
    
    asyncio.run(test_db())
