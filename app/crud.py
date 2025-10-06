from config import get_db_connection
from pymysql.err import IntegrityError

def create_user_in_db(email: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
        cursor.execute(sql, (email, password))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except IntegrityError:
        raise ValueError("Email already exists")
    finally:
        cursor.close()
        conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, email FROM users")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_user_by_id(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_user_in_db(user_id: int, email: str = None, password: str = None):
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
            return 0
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        values.append(user_id)
        cursor.execute(sql, tuple(values))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()

def delete_user_in_db(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM users WHERE id = %s"
        cursor.execute(sql, (user_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()
