"""
Уязвимые API маршруты для Vulnerable API Service
Содержит множественные уязвимости безопасности для тестирования

Уязвимости в этом файле:
1. SQL Injection
2. XSS уязвимости  
3. Отсутствие аутентификации
4. Information disclosure
5. Insecure direct object references
6. Отсутствие rate limiting
7. Path traversal
8. Command injection
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import os
import subprocess
import json
import time
import hashlib
import secrets
import re

# Импортируем модели с уязвимостями
from src.models import *

router = APIRouter(prefix="", tags=["vulnerable-endpoints"])

# Глобальные переменные с секретами (НЕБЕЗОПАСНО!)
DATABASE_PATH = "vulnerable.db"
ADMIN_PASSWORD = "admin123"
SECRET_KEY = "super_secret_key_123"
DEBUG_MODE = True

# Уязвимость: Отсутствие rate limiting для login endpoint
@router.post("/api/auth/login")
async def login(request: UserLogin):
    """
    Уязвимость: Login endpoint без rate limiting и proper validation
    Также уязвим для brute force атак
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Уязвимость: SQL Injection - прямое использование user input в SQL
        query = f"SELECT * FROM users WHERE username = '{request.username}' AND password = '{request.password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Уязвимость: Слабое генерирование токена
            token = hashlib.md5(f"{user[1]}{time.time()}".encode()).hexdigest()
            
            return {
                "status": "success",
                "message": "Login successful",
                "token": token,
                "user_id": user[0],
                "username": user[1],
                "role": user[4],
                # Уязвимость: Возвращаем пароль в ответе
                "password": user[2]
            }
        else:
            return {
                "status": "error",
                "message": "Invalid credentials",
                "attempts_info": f"Failed login attempt for user: {request.username}"
            }
    except Exception as e:
        # Уязвимость: Information disclosure через error messages
        return {
            "status": "error",
            "message": f"Database error: {str(e)}",
            "query": f"Failed query for user: {request.username}"
        }


# Уязвимость: API без versioning
@router.get("/api/users")
async def get_users_unversioned():
    """
    Уязвимость: API endpoint без версии
    Также отсутствует аутентификация
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: SQL Injection в WHERE clause
    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "users": [
            {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[3]
            }
            for user in users
        ],
        "total": len(users)
    }


@router.get("/api/products")
async def get_products_unversioned():
    """
    Уязвимость: API endpoint без версии
    Отсутствует proper validation
    """
    return {
        "status": "success",
        "products": [
            {"id": 1, "name": "Premium Subscription", "price": 99.99, "secret_key": SECRET_KEY},
            {"id": 2, "name": "Basic Plan", "price": 29.99, "api_key": "pk-test-payment-key"},
            {"id": 3, "name": "Enterprise License", "price": 999.99, "admin_password": ADMIN_PASSWORD}
        ]
    }


@router.get("/api/orders")
async def get_orders_unversioned():
    """
    Уязвимость: API endpoint без версии
    Доступ к финансовой информации без аутентификации
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user_id, product_name, amount, status FROM orders")
    orders = cursor.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "orders": [
            {
                "id": order[0],
                "user_id": order[1],
                "product_name": order[2],
                "amount": order[3],
                "status": order[4],
                "internal_config": {
                    "database_path": DATABASE_PATH,
                    "secret_key": SECRET_KEY
                }
            }
            for order in orders
        ]
    }


# Версионированные API endpoints с уязвимостями
@router.get("/api/v1/users")
async def get_users_v1(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    username: Optional[str] = Query(None, description="Filter by username")
):
    """
    Уязвимость: Unprotected sensitive endpoint с множественными проблемами
    1. Отсутствие аутентификации
    2. SQL Injection в параметрах
    3. Information disclosure
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: SQL Injection через query parameters
    if user_id:
        query = f"SELECT id, username, password, email, role FROM users WHERE id = {user_id}"
    elif username:
        query = f"SELECT id, username, password, email, role FROM users WHERE username = '{username}'"
    else:
        query = "SELECT id, username, password, email, role FROM users"
    
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    
    # Уязвимость: Возвращаем пароли пользователей
    return {
        "status": "success",
        "users": [
            {
                "id": user[0],
                "username": user[1],
                "password": user[2],  # НЕБЕЗОПАСНО!
                "email": user[3],
                "role": user[4]
            }
            for user in users
        ]
    }


@router.get("/api/v1/orders")
async def get_orders_v1(
    user_id: Optional[int] = Query(None),
    min_amount: Optional[float] = Query(None),
    status: Optional[str] = Query(None)
):
    """
    Уязвимость: Финансовая информация без аутентификации
    Также SQL injection в параметрах
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: SQL Injection в фильтрах
    conditions = []
    if user_id:
        conditions.append(f"user_id = {user_id}")
    if min_amount:
        conditions.append(f"amount >= {min_amount}")
    if status:
        conditions.append(f"status = '{status}'")
    
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"SELECT id, user_id, product_name, amount, status FROM orders{where_clause}"
    
    cursor.execute(query)
    orders = cursor.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "orders": [
            {
                "id": order[0],
                "user_id": order[1],
                "product_name": order[2],
                "amount": order[3],
                "status": order[4],
                # Уязвимость: Раскрытие внутренней информации
                "processing_fee": order[3] * 0.05,
                "admin_notes": f"Order processed by system at {time.time()}"
            }
            for order in orders
        ]
    }


@router.get("/api/v1/payments")
async def get_payments_v1():
    """
    КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Платежные данные без аутентификации
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: Полное раскрытие платежных данных
    cursor.execute("SELECT id, user_id, order_id, card_number, cvv, amount FROM payments")
    payments = cursor.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "message": "Payment data exposed - CRITICAL VULNERABILITY!",
        "payments": [
            {
                "id": payment[0],
                "user_id": payment[1],
                "order_id": payment[2],
                "card_number": payment[3],  # КРИТИЧЕСКАЯ УЯЗВИМОСТЬ!
                "cvv": payment[4],          # КРИТИЧЕСКАЯ УЯЗВИМОСТЬ!
                "amount": payment[5],
                # Дополнительные уязвимости
                "full_card_data": {
                    "number": payment[3],
                    "cvv": payment[4],
                    "expiry": "12/25",
                    "cardholder": "John Doe"
                }
            }
            for payment in payments
        ]
    }


@router.post("/api/v1/payments")
async def create_payment_v1(payment: PaymentCreate):
    """
    Уязвимость: Создание платежей без proper validation
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Уязвимость: Не проверяем данные карты
        cursor.execute(
            "INSERT INTO payments (user_id, order_id, card_number, cvv, amount) VALUES (?, ?, ?, ?, ?)",
            (payment.user_id, payment.order_id, payment.card_number, payment.cvv, payment.amount)
        )
        payment_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Уязвимость: Возвращаем CVV в ответе
        return {
            "status": "success",
            "payment_id": payment_id,
            "cvv": payment.cvv,  # НЕБЕЗОПАСНО!
            "card_last_four": payment.card_number[-4:]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Payment processing error: {str(e)}"
        }


# Уязвимости поиска с SQL injection
@router.get("/api/v1/search")
async def search_users(
    query: str = Query(..., description="Search query"),
    category: str = Query("users", description="Search category")
):
    """
    Уязвимость: SQL injection в search endpoint
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: Непосредственное использование user input в SQL
    if category == "users":
        sql_query = f"SELECT id, username, email FROM users WHERE username LIKE '%{query}%' OR email LIKE '%{query}%'"
    elif category == "orders":
        sql_query = f"SELECT id, user_id, product_name, amount FROM orders WHERE product_name LIKE '%{query}%'"
    else:
        sql_query = f"SELECT * FROM {category} WHERE 1=1"  # Уязвимость: прямое использование table name
    
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()
        
        return {
            "status": "success",
            "query": query,
            "category": category,
            "results": results,
            "sql_query": sql_query  # Уязвимость: раскрываем SQL query
        }
    except Exception as e:
        conn.close()
        return {
            "status": "error",
            "message": f"Search error: {str(e)}",
            "sql_query": sql_query  # Уязвимость: раскрываем SQL query даже в ошибке
        }


# XSS уязвимости
@router.get("/api/v1/echo")
async def echo_message(message: str = Query(..., description="Message to echo")):
    """
    Уязвимость: XSS через reflected parameters
    """
    return {
        "status": "success",
        "echoed_message": message,  # Уязвимость: прямое отражение пользовательского ввода
        "html_response": f"<html><body><h1>Echo: {message}</h1></body></html>"
    }


@router.get("/api/v1/xss-test")
async def xss_test(payload: str = Query(..., description="XSS test payload")):
    """
    Уязвимость: XSS через query parameters
    """
    # Уязвимость: Не санитизируем HTML
    return HTMLResponse(content=f"""
    <html>
    <head><title>XSS Test</title></head>
    <body>
        <h1>XSS Vulnerability Test</h1>
        <div>
            <p>Payload received: {payload}</p>
            <p>Executed content: <script>alert('{payload}')</script></p>
        </div>
    </body>
    </html>
    """)


# Path traversal уязвимости
@router.get("/api/v1/download")
async def download_file(filename: str = Query(..., description="File to download")):
    """
    Уязвимость: Path traversal attack
    """
    try:
        # Уязвимость: Не проверяем path traversal
        file_path = f"/tmp/uploads/{filename}"
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            return {
                "status": "success",
                "filename": filename,
                "content": content,
                "file_path": file_path  # Уязвимость: раскрываем реальный путь
            }
        else:
            return {
                "status": "error",
                "message": "File not found",
                "attempted_path": file_path
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"File access error: {str(e)}"
        }


# Command injection уязвимости
@router.get("/api/v1/ping")
async def ping_host(host: str = Query(..., description="Host to ping")):
    """
    Уязвимость: Command injection через shell commands
    """
    try:
        # Уязвимость: Небезопасное выполнение shell commands
        result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
        
        return {
            "status": "success",
            "host": host,
            "output": result.stdout,
            "command_executed": f"ping -c 1 {host}"  # Уязвимость: раскрываем выполняемую команду
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ping error: {str(e)}"
        }


@router.get("/api/v1/execute")
async def execute_command(command: str = Query(..., description="Command to execute")):
    """
    КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Command injection
    """
    try:
        # КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Небезопасное выполнение команд
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        return {
            "status": "success",
            "command": command,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Execution error: {str(e)}",
            "command": command
        }


# Debug endpoints (НЕБЕЗОПАСНО для production)
@router.get("/debug/info")
async def debug_info():
    """
    КРИТИЧЕСКАЯ УЯЗВИМОСТЬ: Debug endpoint в production
    """
    import os
    import sys
    
    return {
        "status": "success",
        "message": "Debug information exposed - CRITICAL VULNERABILITY!",
        "system_info": {
            "python_version": sys.version,
            "platform": sys.platform,
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown",
            "current_dir": os.getcwd(),
            "user": os.getenv("USER", "unknown"),
            "home": os.getenv("HOME", "unknown")
        },
        "environment_variables": {
            # Уязвимость: Раскрываем все env vars
            key: value for key, value in os.environ.items()
        },
        "process_info": {
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "uid": os.getuid() if hasattr(os, 'getuid') else "unknown"
        }
    }


@router.get("/debug/sql")
async def debug_sql():
    """
    Уязвимость: Debug endpoint показывающий SQL queries
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: Раскрываем содержимое базы данных
    tables = ["users", "orders", "payments"]
    db_content = {}
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        db_content[table] = cursor.fetchall()
    
    conn.close()
    
    return {
        "status": "success",
        "message": "Database content exposed - CRITICAL VULNERABILITY!",
        "database_path": DATABASE_PATH,
        "tables": db_content,
        "credentials_exposed": True
    }


@router.post("/test/payload")
async def test_payload(payload: Dict[str, Any]):
    """
    Уязвимость: Тестовый endpoint для различных payload'ов
    """
    return {
        "status": "success",
        "payload_received": payload,
        "payload_processed": str(payload),
        "payload_length": len(str(payload)),
        "vulnerability_test": "Various payloads can be tested here",
        "note": "This endpoint should be removed in production"
    }


# Insecure Direct Object References
@router.get("/api/v1/user/{user_id}")
async def get_user_by_id(user_id: int):
    """
    Уязвимость: Insecure Direct Object Reference
    Пользователь может получить доступ к любым пользователям
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, password, email, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Уязвимость: Возвращаем пароль
        return {
            "status": "success",
            "user": {
                "id": user[0],
                "username": user[1],
                "password": user[2],  # НЕБЕЗОПАСНО!
                "email": user[3],
                "role": user[4]
            }
        }
    else:
        return {
            "status": "error",
            "message": f"User with ID {user_id} not found"
        }


@router.get("/api/v1/order/{order_id}")
async def get_order_by_id(order_id: int):
    """
    Уязвимость: Insecure Direct Object Reference для заказов
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user_id, product_name, amount, status FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    
    if order:
        return {
            "status": "success",
            "order": {
                "id": order[0],
                "user_id": order[1],
                "product_name": order[2],
                "amount": order[3],
                "status": order[4],
                # Уязвимость: Дополнительная информация
                "internal_notes": f"Order processed with fee: {order[3] * 0.05}",
                "admin_access_required": False
            }
        }
    else:
        return {
            "status": "error",
            "message": f"Order with ID {order_id} not found"
        }


# Missing API versioning example
@router.get("/api/categories")
async def get_categories():
    """
    Уязвимость: API endpoint без версии
    """
    return {
        "status": "success",
        "categories": [
            {"id": 1, "name": "Electronics", "internal_code": "ELEC001"},
            {"id": 2, "name": "Books", "internal_code": "BOOK002"},
            {"id": 3, "name": "Clothing", "internal_code": "CLTH003"}
        ]
    }


@router.get("/api/settings")
async def get_settings():
    """
    Уязвимость: Endpoint с настройками системы
    """
    return {
        "status": "success",
        "settings": {
            "database_url": f"sqlite:///{DATABASE_PATH}",
            "secret_key": SECRET_KEY,
            "admin_password": ADMIN_PASSWORD,
            "debug_mode": DEBUG_MODE,
            "api_versioning": False,
            "security_headers": False,
            "rate_limiting": False,
            "authentication": False
        }
    }


# JSON injection уязвимость
@router.post("/api/v1/process-json")
async def process_json_data(data: Dict[str, Any]):
    """
    Уязвимость: JSON injection через deserialization
    """
    try:
        # Уязвимость: Небезопасная обработка JSON
        processed_data = json.dumps(data, indent=2)
        
        # Дополнительная уязвимость: eval() на JSON data
        try:
            evaluated = eval(processed_data)
            return {
                "status": "success",
                "original_data": data,
                "processed_data": processed_data,
                "evaluated_data": str(evaluated),
                "vulnerability": "JSON data was evaluated as Python code"
            }
        except:
            return {
                "status": "success",
                "original_data": data,
                "processed_data": processed_data
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"JSON processing error: {str(e)}",
            "raw_data": str(data)
        }


# File upload с уязвимостями
@router.post("/api/v1/upload")
async def upload_file(
    file: str = Form(..., description="File content"),
    filename: str = Form(..., description="File name"),
    description: str = Form(None, description="File description")
):
    """
    Уязвимость: File upload без proper validation
    """
    try:
        # Уязвимость: Не проверяем path traversal в filename
        file_path = f"/tmp/uploads/{filename}"
        
        # Уязвимость: Не проверяем размер файла
        with open(file_path, 'w') as f:
            f.write(file)
        
        return {
            "status": "success",
            "filename": filename,
            "description": description,
            "file_path": file_path,
            "content_length": len(file),
            "upload_timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Upload error: {str(e)}"
        }