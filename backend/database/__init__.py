"""
Database initialization and connection management
"""
from flask import current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
import os
from contextlib import contextmanager

# Connection pool
_pool = None

def init_db(app):
    """Initialize database connection pool"""
    global _pool
    database_url = app.config.get('DATABASE_URL') or os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL not set in environment or app config")
    
    try:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=database_url
        )
        app.logger.info("Database connection pool initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize database pool: {e}")
        raise

def get_db_connection():
    """Get a database connection from the pool"""
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    return _pool.getconn()

def return_db_connection(conn):
    """Return a database connection to the pool"""
    if _pool is None:
        return
    _pool.putconn(conn)

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        return_db_connection(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    """Execute a database query"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch_one:
                result = cur.fetchone()
                conn.commit()
                return result
            elif fetch_all:
                result = cur.fetchall()
                conn.commit()
                return result
            else:
                conn.commit()
                return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        return_db_connection(conn)

def close_pool():
    """Close all database connections in the pool"""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None

