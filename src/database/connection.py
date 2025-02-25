"""
Database connection management module.
"""
import os
from typing import Any

import mysql.connector
from mysql.connector import pooling

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "sharad"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "database": os.getenv("DB_NAME", "customer-support-db"),
    "pool_name": "mypool",
    "pool_size": 5
}

# Create connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**DB_CONFIG)

def get_db_connection():
    """
    Get a connection from the pool.
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object
    """
    return connection_pool.get_connection()

def execute_query(query: str, params: tuple = None) -> list[dict[str, Any]]:
    """
    Execute a SQL query and fetch results.
    
    Args:
        query (str): SQL query string.
        params (tuple, optional): Parameters for the SQL query. Defaults to None.
    
    Returns:
        list[dict[str, Any]]: List of dictionaries representing query results.
    """
    conn = None  # Initialize conn outside the try block
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        print(f"Executing SQL Query: {query} with params: {params}")  # Log the query
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        print(f"Query was: {query} with params: {params}") # Print query on error as well
        return []
    finally:
        if conn:
            conn.close()

def execute_update(query: str, params: tuple = None) -> None:
    """
    Execute a SQL UPDATE, INSERT, or DELETE query.
    
    Args:
        query (str): SQL query string.
        params (tuple, optional): Parameters for the SQL query. Defaults to None.
    """
    conn = None  # Initialize conn outside the try block
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"Executing SQL Update: {query} with params: {params}") # Log the update query
        cursor.execute(query, params)
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error executing update: {err}")
        print(f"Query was: {query} with params: {params}") # Print query on error as well
    finally:
        if conn:
            conn.close() 