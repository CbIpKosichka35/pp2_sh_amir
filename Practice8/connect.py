import psycopg2
from config import DB_CONFIG
 
def get_connection():
    """Создает и возвращает подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
 
def get_cursor(conn):
    """Возвращает курсор для выполнения запросов"""
    if conn:
        return conn.cursor()
    return None