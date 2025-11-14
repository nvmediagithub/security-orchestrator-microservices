"""
Vulnerable API Service - Тестовый микросервис с уязвимостями для демонстрации
возможностей API анализатора безопасности.

ВНИМАНИЕ: Этот сервис содержит намеренные уязвимости безопасности!
НЕ используйте в продакшн среде!

Основные уязвимости:
1. Отсутствие аутентификации на admin endpoints
2. Отсутствие HTTPS
3. SQL injection уязвимости
4. XSS уязвимости
5. Information disclosure
6. Отсутствие rate limiting
7. Небезопасные прямые ссылки на объекты
8. Debug endpoints в production
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import sqlite3
import json
import hashlib
import secrets
import time
from typing import List, Optional, Dict, Any
import os

# Уязвимость: Хранение секретов в коде
ADMIN_PASSWORD = "admin123"  # НЕБЕЗОПАСНО!
SECRET_KEY = "super_secret_key_123"  # НЕБЕЗОПАСНО!
DATABASE_PATH = "vulnerable.db"

# Создание приложения без HTTPS и базовой безопасности
app = FastAPI(
    title="Vulnerable API Service",
    description="Тестовый API с уязвимостями для демонстрации",
    version="1.0.0",
    docs_url="/docs",  # Документация доступна всем
    redoc_url="/redoc"  # ReDoc доступен всем
)

# Уязвимость: CORS без ограничений
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создание базы данных с уязвимостями
def init_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: Создание таблиц с потенциальными SQL injection уязвимостями
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            role TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_name TEXT,
            amount REAL,
            status TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            order_id INTEGER,
            card_number TEXT,
            cvv TEXT,
            amount REAL,
            created_at TEXT
        )
    """)
    
    # Уязвимость: Добавление тестовых данных с секретной информацией
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email, role, created_at) VALUES (1, 'admin', 'admin123', 'admin@vulnerable.com', 'admin', datetime('now'))")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, email, role, created_at) VALUES (2, 'user1', 'password123', 'user1@vulnerable.com', 'user', datetime('now'))")
    
    cursor.execute("INSERT OR IGNORE INTO orders (id, user_id, product_name, amount, status, created_at) VALUES (1, 1, 'Premium Subscription', 99.99, 'completed', datetime('now'))")
    cursor.execute("INSERT OR IGNORE INTO payments (id, user_id, order_id, card_number, cvv, amount, created_at) VALUES (1, 1, 1, '4111111111111111', '123', 99.99, datetime('now'))")
    
    conn.commit()
    conn.close()

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    init_database()

# Уязвимость: Отсутствие аутентификации для health check
@app.get("/health")
async def health_check():
    """Проверка состояния сервиса - доступна без аутентификации"""
    return {
        "status": "healthy",
        "service": "vulnerable-api",
        "version": "1.0.0",
        "timestamp": time.time()
    }

# Уязвимость: Admin endpoints без аутентификации
@app.get("/admin")
async def admin_panel():
    """Уязвимость: Административная панель без аутентификации"""
    return HTMLResponse("""
    <html>
    <head><title>Admin Panel</title></head>
    <body>
        <h1>🛡️ ADMIN PANEL (НЕБЕЗОПАСНО!)</h1>
        <p><strong>Уязвимость:</strong> Доступ без аутентификации</p>
        <ul>
            <li><a href="/admin/users">User Management</a></li>
            <li><a href="/admin/config">System Configuration</a></li>
            <li><a href="/backend/management">Backend Management</a></li>
        </ul>
        <p><em>Этот endpoint не должен быть доступен без аутентификации!</em></p>
    </body>
    </html>
    """)

@app.get("/admin/users")
async def admin_users():
    """Уязвимость: Управление пользователями без аутентификации"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Уязвимость: Information disclosure - показываем пароли пользователей
    cursor.execute("SELECT id, username, password, email, role FROM users")
    users = cursor.fetchall()
    conn.close()
    
    return {
        "status": "success",
        "message": "Users list (Уязвимость: раскрытие паролей)",
        "users": [
            {
                "id": user[0],
                "username": user[1],
                "password": user[2],  # НЕБЕЗОПАСНО: показываем пароли!
                "email": user[3],
                "role": user[4]
            }
            for user in users
        ]
    }

@app.get("/admin/config")
async def admin_config():
    """Уязвимость: Раскрытие конфигурации системы"""
    return {
        "status": "success",
        "message": "System configuration (Уязвимость: раскрытие секретов)",
        "config": {
            "admin_password": ADMIN_PASSWORD,  # НЕБЕЗОПАСНО!
            "secret_key": SECRET_KEY,  # НЕБЕЗОПАСНО!
            "database_path": DATABASE_PATH,
            "debug_mode": True,
            "allow_origins": "*",
            "api_keys": [
                "sk-1234567890abcdef",  # НЕБЕЗОПАСНО!
                "pk-test-payment-key"   # НЕБЕЗОПАСНО!
            ]
        }
    }

@app.get("/backend/management")
async def backend_management():
    """Уязвимость: Backend управление без аутентификации"""
    return {
        "status": "success",
        "message": "Backend Management (НЕБЕЗОПАСНО!)",
        "endpoints": {
            "health": "/health",
            "users": "/api/v1/users",
            "orders": "/api/v1/orders",
            "payments": "/api/v1/payments",
            "login": "/api/auth/login",
            "admin": "/admin",
            "debug": "/debug/info"
        },
        "security_status": "COMPROMISED",
        "warnings": [
            "Отсутствие аутентификации",
            "Отсутствие HTTPS",
            "Раскрытие секретов",
            "SQL injection уязвимости",
            "XSS уязвимости"
        ]
    }

# Импорт маршрутов с уязвимостями
from src.routes import *

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Vulnerable API Service on http://localhost:8003")
    print("⚠️  WARNING: This service contains intentional security vulnerabilities!")
    print("📖 Documentation available at: http://localhost:8003/docs")
    uvicorn.run(app, host="0.0.0.0", port=8003)