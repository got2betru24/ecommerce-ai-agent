import os
from dotenv import load_dotenv
import json
import mysql.connector

from .utils import json_serializer

load_dotenv()

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
)
cursor = connection.cursor(dictionary=True)


def find_order_by_id(order_id: str):
    cursor.execute("SELECT * FROM Orders WHERE id = %s", (order_id,))
    return cursor.fetchone()


def find_customers_by_last_name(last_name: str):
    cursor.execute("SELECT * FROM Customer WHERE LastName = %s", (last_name,))
    return cursor.fetchall()


def find_customers_by_name(last_name: str, first_name: str):
    cursor.execute(
        "SELECT * FROM Customer WHERE LastName = %s AND FirstName LIKE %s",
        (last_name, f"%{first_name}%"),
    )
    return cursor.fetchall()


def find_orders_by_customer_id(customer_id: int):
    cursor.execute("SELECT * FROM Orders WHERE CustomerId = %s", (customer_id,))
    return cursor.fetchall()


def find_product_by_id(product_id: str):
    cursor.execute("SELECT * FROM Product WHERE id = %s", (product_id,))
    return cursor.fetchone()


def find_products_by_name(search_words: list):
    conditions = " AND ".join(["ProductName LIKE %s" for _ in search_words])
    params = tuple(f"%{word}%" for word in search_words)
    cursor.execute(f"SELECT * FROM Product WHERE {conditions}", params)
    return cursor.fetchall()


def save_message(session_id: str, role: str, content, message_type: str = "text"):
    content_json = json.dumps(content, default=json_serializer)
    cursor.execute(
        """INSERT INTO ConversationHistory 
        (SessionId, Role, Content, MessageType) 
        VALUES (%s, %s, %s, %s)""",
        (session_id, role, content_json, message_type),
    )
    connection.commit()


def load_history(session_id: str) -> list:
    cursor.execute(
        """SELECT Role, Content, MessageType 
        FROM ConversationHistory 
        WHERE SessionId = %s 
        AND CreatedAt > NOW() - INTERVAL 3 DAY
        ORDER BY CreatedAt ASC""",
        (session_id,),
    )
    rows = cursor.fetchall()
    messages = []
    for row in rows:
        content = json.loads(row["Content"])
        messages.append({"role": row["Role"], "content": content})
    return messages
