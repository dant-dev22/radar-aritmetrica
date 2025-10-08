import logging
from config import get_db_connection
import pymysql
import os
from pymysql.err import IntegrityError

# Configuración básica del logger
logger = logging.getLogger("crud")
logger.setLevel(logging.DEBUG)  # Cambiar a INFO en producción
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def create_user_in_db(email: str, password: str):
    logger.debug(f"create_user_in_db called with email={email}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
        cursor.execute(sql, (email, password))
        conn.commit()
        user_id = cursor.lastrowid
        logger.debug(f"User created with id={user_id}")
        return user_id
    except IntegrityError:
        logger.error("Email already exists")
        raise ValueError("Email already exists")
    except Exception as e:
        logger.error(f"create_user_in_db exception: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("create_user_in_db connection closed")

def get_all_users():
    logger.debug("get_all_users called")
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        logger.debug(f"get_all_users fetched {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"get_all_users exception: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("get_all_users connection closed")

def get_user_by_id(user_id: int):
    logger.debug(f"get_user_by_id called with user_id={user_id}")
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        logger.debug(f"get_user_by_id result: {user}")
        return user
    except Exception as e:
        logger.error(f"get_user_by_id exception: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("get_user_by_id connection closed")

def update_user_in_db(user_id: int, email: str = None, password: str = None):
    logger.debug(f"update_user_in_db called with user_id={user_id}, email={email}, password={'***' if password else None}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        fields = []
        values = []
        if email:
            fields.append("email = %s")
            values.append(email)
        if password:
            fields.append("password = %s")
            values.append(password)
        if not fields:
            logger.debug("No fields to update")
            return 0
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        values.append(user_id)
        cursor.execute(sql, tuple(values))
        conn.commit()
        logger.debug(f"update_user_in_db affected rows={cursor.rowcount}")
        return cursor.rowcount
    except Exception as e:
        logger.error(f"update_user_in_db exception: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("update_user_in_db connection closed")

def delete_user_in_db(user_id: int):
    logger.debug(f"delete_user_in_db called with user_id={user_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()
        logger.debug(f"delete_user_in_db affected rows={cursor.rowcount}")
        return cursor.rowcount
    except Exception as e:
        logger.error(f"delete_user_in_db exception: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
        logger.debug("delete_user_in_db connection closed")
