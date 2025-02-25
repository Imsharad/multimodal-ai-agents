"""
Database package initialization.
This module provides database connectivity and operations for the customer support system.
"""

from .connection import get_db_connection, execute_query, execute_update
from .schema import init_schema

__all__ = [
    'get_db_connection',
    'execute_query',
    'execute_update',
    'init_schema'
] 