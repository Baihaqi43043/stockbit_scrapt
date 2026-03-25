import mysql.connector
from mysql.connector import pooling
import config

_pool = None


def get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="stockbit_pool",
            pool_size=3,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            charset="utf8mb4",
        )
    return _pool


def get_connection():
    return get_pool().get_connection()
